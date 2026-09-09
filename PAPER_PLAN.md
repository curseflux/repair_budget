# The repair budget: plan v2

Supersedes v1 (commit `bbfb13d`), revised after reading
`llm2_repair_paper_research_assessment.md` and the code.

**v1 had a wrong central claim.** It asserted a hard floor: perturbations invisible at output
precision `b` stay invisible for every `N`, so `L(N)` plateaus strictly above zero. LLM2's
boundary-crossing observation refutes this in the generic case, and its scalar threshold example
is an explicit counterexample. Equal codes imply a difference below one cell width, but the
converse fails: successive samples place *fresh* cell boundaries at fresh positions, so repeated
low-precision observations resolve differences far finer than one cell. A hard floor requires
degenerate features (`h_j` constant, or zero on the support of `P`), which is not the Llama case.
The corrected law is in §2. The interval machinery from v1 survives intact and becomes more
important, not less: it is the tool that measures the corrected law.

---

## 1. What the two reviews agree on

Independently, both converge on the same next step: **compute, from the retained records, the
exact set of original weight values still consistent with the transcript, using actual quantizer
cell positions rather than a cell-width relaxation.** v1 §3 Result 2 and LLM2's "exact repair
using the uncertainty left by actual prediction cells" are the same computation. Two independent
derivations landing on one experiment is a strong signal that it is the right one.

They also agree, with the source document's own §12.2, that the current package is not an ICML
paper: broad classical bounds, a classical conditional decoder, and a modest saving.

---

## 2. The corrected law

Per changed coordinate `(v,j)` with numerical change `delta`, the retained record imposes

```
delta * h_j(x_i)  in  [ lo_{v,i} - (Wz)_{v,i} ,  hi_{v,i} - (Wz)_{v,i} )    for i = 1..N
```

where `[lo,hi)` is the original output cell. Each sample gives a fresh interval; their
intersection `I_{v,j}` is an interval containing the true change. Because `z_{v,i}` varies
across inputs, the cell offset is effectively fresh each sample, so

```
width(I_{v,j})  ~  WIDTH / (N * |h_j|)
```

— shrinking like `1/N`, **not** stalling at one cell width. The number of admissible BF16
labels is `width(I) / ulp(w)`, so

```
L(N)  ~  s * log2(d/s)                       [locations]
      +  s * [ log2( WIDTH / (|h_j| * ulp(w)) ) - log2 N ]_+   [values]
```

Two terms, two mechanisms, two different ways the data pays:

- **The location term** is killed *discontinuously* by the mismatch screen: a changed row that
  moves any output code is identified outright.
- **The value term** decays *logarithmically* in `N` and terminates at zero once the interval
  narrows below one weight-alphabet step.

The value term hits zero at `N* ~ WIDTH / (|h_j| * ulp(w))`. With `WIDTH = 0.5`,
`|w| ~ 0.02`, `ulp_BF16(w) ~ w * 2^-8`, this gives `N* ~ 6400 / |h_j|`. The tamper generator
draws columns from `topk(feature_score, 512)`, i.e. the *highest-energy* features, so
`|h_j|` is large there and `N* = 256` may already be past threshold for the tested pools while
far short of it for typical columns. **That is a sharp, falsifiable prediction and it is the
experiment.**

A hard floor survives only as a boundary case: `h_j` constant across inputs, `h_j = 0` on the
support of `P`, saturated cells, or distinct labels with equal numerical value. State the
dichotomy; do not build the paper on the floor.

The v1 claim that "invisible = behaviorally irrelevant" remains true and remains the most
interesting *idea* in the project, but it is now one theorem and one paragraph of
interpretation, not an implemented branch. LLM2 is right that a second (behavioral) target
should not be built before the exact-recovery intervals are measured. If the intervals turn out
wide, promote it; if narrow, it stays a remark.

---

## 3. The budget ladder

Every rung is decided by the same interval computation. This is the paper's central figure.

| Scheme | Bits | Conditional on |
|---|---:|---|
| Data-free full-head Reed–Solomon (`2s` checks, `p = 2^31-1`) | 3,968 | nothing |
| **Current: ell-1 top-16 flags + RS** | **3,534** | as run |
| LLM2 row-summary code + complete row screen | 2,176 | screen catches all affected rows; one change per affected row |
| Exact interval localization + RS values (`e = s`, `u = 0`) | 1,984 | interval leaves one column per row |
| Row-locator code + interval column ID (`p = 2^17-1`) | 1,088 | both of the above |
| Intervals pin the label too | ~0 per resolved row | singleton `(column, label)` per row |

The current result sits on the second rung. The spread from rung 1 to rung 6 is 3,968 bits to
roughly nothing, and **which rung is reachable is an empirical question answerable this week from
caches that already exist.** That framing is worth more than any additional trial.

---

## 4. Three things LLM2 caught that v1 missed

1. **The 12.5% ceiling.** With `e = 16` erasures frozen against `s = 64` errors, the burden
   `e + 2u = 16 + 2(64-c)` is at best `112` when every flag is correct, against a `128`-check
   baseline. **The experiment could not have shown more than a 12.5% saving no matter how many
   samples were retained**, and 10.9% is nearly that ceiling. The reported curve measures the
   frozen configuration, not the information.
   The reason `e = 16` was selected is visible in the code: at ~25% localizer recall, `e = 64`
   would give `64 + 2*48 = 160` — worse than the baseline. **The binding constraint is the
   ell-1 localizer's recall, not the retained data.** Exact interval arithmetic replaces that
   heuristic directly; it is not a new research direction.
2. **Boundary crossing.** See §2. This corrects v1's central claim.
3. **`n_train` versus `N`.** "The model was trained on `N` iid samples" and "we retain `N`
   prediction records" are different resources, and conflating them lets the original class
   drift as `N` varies. Worse, if the original is reproducible from the retained data plus
   public deterministic training settings, unlimited-computation repair may need zero bits.
   The class definition must make the residual ambiguity explicit. v1 did not flag this.

---

## 5. Three things in the code that neither review used

1. **`len(bad_rows)` is already recorded** (`location_scores` returns it; `diagnostics` stores
   it). The row-screen completeness that decides the 2,176-bit rung may already be in the saved
   CSVs. Check before running anything.
2. **The tamper pools are narrow and public-rule-derived**: `row_pool = topk(mean_p, 256)`,
   `col_pool = topk(feature_score, 512)` — a 131,072-coordinate pool, not the 525M head. If that
   pool is a promise the decoder may use, the honest data-free baseline is
   `log2 C(131072, 64) ~ 796` location bits, not the full-head figure, and the 3,968-bit baseline
   is roughly 2x overstated. §9.7 of the source document raises this; it has to be resolved
   before any saving is reported.
3. **Only 8-bit codes are cached, but hidden states are.** So a `b`-sweep costs one
   `H @ W.T` per `b` (256 x 128256 x 4096, about a second), not a model forward pass. The
   precision axis is essentially free if it is wanted later.

---

## 6. The next move: one experiment, one afternoon

On the existing frozen dispersed instance and caches:

1. **Row-screen completeness.** How many of the 64 tampered rows appear in `bad_rows`; how many
   false rows appear. Decides the 2,176-bit rung. Possibly already recorded.
2. **Per-row interval count.** For each affected row `v`, compute `I_{v,j}` for all 4,096
   columns; count admissible BF16 labels in each; report the number of surviving
   `(column, label)` pairs. Cost: `64 x 4096 x 256` — instant.
3. **The `-log2 N` slope.** Repeat (2) for `N` in `1, 2, 4, ..., 256`, plot
   `log2(candidate count)` against `log2 N`. **This is the direct test of §2.** A slope near
   `-1` per coordinate confirms the corrected law; a plateau confirms a floor and revives v1.
4. **Whole-head ambiguity profile** (optional, GPU-minutes). The same interval reduction over
   all `128256 x 4096` coordinates on the untampered head, via min-of-ratio reductions
   (`1.3e11` fused ops, matmul-shaped). Gives the converse: a packing family of originals with a
   *common transcript and common damaged checkpoint*, hence an exact lower bound on every
   encoder — the same-class converse §9.6 says is missing.

**Decision rule.**

- Counts are mostly singletons -> rung 5 or 6. The paper is "retained predictions determine the
  repair almost completely; the residual budget is `s log(d/s)` location bits that the mismatch
  screen already supplies for free," with the measured `-log N` law as the mechanism. Strong.
- Counts shrink at the predicted rate but stay above one -> rung 3 or 4. The paper is the
  `L(N)` law with matching construction. Also strong, and the honest version of the original
  ambition.
- Counts stay large -> determine whether the cause is feature coverage, precision, or
  within-row combinations. Then the converse in step 4 has a real target, and the behavioral
  branch from v1 §2 comes back as the explanation for why exact recovery is the wrong ask.

All three outcomes are publishable, which is what makes this a safe next step rather than a bet.
What is *not* safe is running more trials at the current frozen configuration: §4.1 shows that
configuration cannot produce a saving above 12.5% regardless of `N`.

---

## 7. Prior art to check before writing anything

LLM2 flags **Gao and Lafferty, *Model Repair: Robust Recovery of Over-Parameterized Statistical
Models* (arXiv 2005.09912)** as the most consequential omission — recovering a corrupted model
from the original input design, connected to error correction. I have not read it and cannot
confirm the overlap from memory. **Read it first.** If it already covers repair from the input
design in a linear/random-feature setting, the surviving novelty is specifically the
*protected-bit budget as a function of retained finite-precision predictions*, and the framing
must be written around that from the start rather than adjusted afterward.

Also: quantized consistent reconstruction (Jacques), finite-alphabet sparse recovery over finite
fields (Das and Vishwanath), secure sketches (Dodis et al.), RADAR / DeepNcode for weight
protection, and Carlini et al. on last-layer extraction from logits.

---

## 8. What survives from v1

- The interval computation as both diagnostic and converse (v1 §3 Result 2). Now central.
- The spectral explanation of concentrated versus dispersed (v1 §3 Result 4): dispersed gives
  `N` constraints per unknown, concentrated gives `N/s`, and the feasible polytope is governed by
  `sigma_min(H_S)`. Confirmed by the code: concentrated puts all 64 changes in one row
  (`assert len(bad_rows) == 1`). Cheap and it explains the one clearly negative result.
- The cuts (v1 §6): Theorem 5, Proposition 12, the INT8/INT4 comparison, numerical-execution
  and provenance material to appendices, and compressing Theorems 1-3 to half a page conceding
  Witsenhausen and Slepian-Wolf.
- The exchange-rate honesty (v1 §1.2): 31.3 MiB of record buys 434 bits, ~600,000:1. Say in the
  introduction that protected bits are scarce because they must be signed, replicated and held
  offline, not because storage is scarce.
- The stopping discipline. Unchanged: when the ladder rung is established and the law is
  measured, stop.

## 9. What is retired from v1

- The hard floor as the central claim (§2).
- The `epsilon` phase transition as a headline result and E4 as a core experiment. Demoted to a
  theorem plus interpretation, contingent on step 6.2 showing wide intervals.
- The `b`-sweep as a core experiment. Cheap (§5.3), but it answers a question that only matters
  if the floor is real.
