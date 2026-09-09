# The repair budget: plan v3

Supersedes v2 (`0b92f5d`). v2 predicted a two-term law and a `-1` slope; the interval audit
(`interval_audit_report.json`, A100, 2026-09-09) measured both. This version is written against
data, not predictions.

---

## 1. What the audit found

**The law has two regimes and the tail exponent is exactly the predicted one.**

| N | 1 | 2 | 4 | 8 | 16 | 32 | 64 | 128 | 256 |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| median candidates / changed row | 1.26e8 | 7.1e6 | 8.0e5 | 1.8e5 | 3.1e4 | 250 | 124 | 69 | 33 |
| local slope | | -4.15 | -3.14 | -2.19 | -2.49 | -6.96 | **-1.01** | **-0.85** | **-1.06** |

- **Location regime (`N < 32`).** Steep, irregular decay while columns are eliminated. Ends
  abruptly between 16 and 32, where the changed column becomes unique.
- **Value regime (`N >= 32`).** Mean slope **-0.975** against a predicted **-1**. Every doubling
  of N halves the surviving weight values. This is `width(I) ~ WIDTH/(N |h_j|)` measured directly.

So `L(N) = [location term] + [value term]`, the location term dies discontinuously and the value
term decays as `log2(C/N)`. That is the answer to the question the project started with.

**The record pins location completely and value partially.**

- Row screen: **64/64 changed rows caught**, 100% recall.
- Columns: **64/64 rows have exactly one feasible column.** Against the l1 localizer's 25%
  coordinate recall, this is not an improvement in degree.
- Values: median 33 survivors per row, all 64 rows counted exactly (not upper bounds).
- **Residual information: 344 bits**, against a 3,968-bit data-free baseline — **91.3%**.

**The ladder, measured.**

| bits | vs data-free | scheme |
|--:|--:|---|
| 3,968 | — | data-free full-head Reed-Solomon (`2s` checks, `p=2^31-1`) |
| 3,534 | 10.9% | as reported: l1 top-16 flags + RS |
| 4,352 | **-9.7%** | row-summary code + screen — *worse than doing nothing*, because `\|E\|=128` |
| 3,968 | 0.0% | interval localization + RS values (`p=2^31-1`) |
| **2,176** | **45.2%** | row locators + interval column ID (`p=2^17-1`) |
| *1,088* | *72.6%* | *the same, once the 64 false rows are removed* |
| **344** | **91.3%** | information actually left by the record (counting bound, not a construction) |

**Concentrated tampers.** The single-change-per-row hypothesis is rejected outright: 0 feasible
columns. Predicted, and it is the cheap version of "dispersed gives `N` constraints per unknown,
concentrated gives `N/s`."

**The self-check earned its place.** On the real arithmetic, slack 0 undercounted in 4/38 trials;
`1e-4` never undercounts but is exactly tight in only 4/38. Verification, not the raw interval,
carries every number above.

---

## 2. Two problems the audit also found

### 2.1 The 64 false rows are numerical, and they cost 1,088 bits

The screen flagged 128 rows: 64 true, **64 false**. Every construction pays per flagged row, so
the false half doubles the cost — and it is what makes the row-summary scheme (`2|E|` checks)
land *above* the data-free baseline.

Diagnosis: the audit recomputes current codes from a resampled `(256, 4096)` batch while the
cached codes came from a different batch composition, so FP32 accumulation order differs. Expected
false rows are `V * (1 - (1 - 2*eps/WIDTH)^N)`; the observed 64 corresponds to
`eps ~ 5e-7`, exactly the relative FP32 error on logits of magnitude ~10. Nothing is wrong with
the theory; the replay is not bit-identical.

**Fix:** recompute the screen under the same batching as the cache, or declare a deterministic
reduction order and regenerate. Falsifiable prediction: false rows scale linearly in `N` and in
`V`. This is the highest value-per-hour item in the project — one bug fix worth 1,088 bits.

### 2.2 The 91.3% is measured on the most favourable 0.025% of the head

`row_pool = topk(mean_p, 256)`, `col_pool = topk(feature_score, 512)`. Large `|h_j|` gives narrow
intervals, so the tamper generator selected precisely the coordinates where the record is most
informative. The head profile makes the size of the effect explicit:

| coordinates | candidates / row | bits / row | 64-row total |
|---|--:|--:|--:|
| tampered (salience pools) | 33 | 5.04 | **344** |
| 512 sampled untouched rows | 1.3e7 | 23.64 | **1,513** |

Against a 1,558-bit location-only counting bound, a typical coordinate leaves nearly everything
unresolved. **The honest headline is therefore a range, not a number:** the record supplies most
of the repair information for high-salience weights and much less for typical ones.

Read the right way this is the paper's best result, not its weakness: **the information a
retained prediction record carries about a weight is proportional to that weight's influence on
the retained predictions.** Obvious in hindsight, quantified here for the first time, and it
grounds the exact-versus-behavioural dichotomy in measurement rather than speculation — the
coordinates the record cannot resolve are exactly the coordinates whose perturbation barely
moves the outputs.

**Caveat that must be fixed before this is published:** `fraction_exact = 0.0` for the head
profile. All 512 rows hit the 200k verification cap, so 1.3e7 is an interval upper bound. The
converse rests on this number; it needs verifying.

---

## 3. The paper

**Title.** *How many protected bits does model repair need, given the model's own predictions?*

**Claim.** The budget splits into a location term and a value term. The location term is supplied
free and discontinuously by a code-mismatch screen. The value term decays as `log2(1/N)` with a
measured exponent of `-0.98`, and its magnitude is set by how strongly the weight influences the
retained outputs. On Llama-3.1-8B's output head with 256 retained 8-bit logit vectors: **344 bits
for salient weights, ~1,500 for typical ones, against 3,968 data-free.** Efficient constructions
reach 1,088–2,176 bits; the residual factor of 3 is computational, not informational.

**Sections.**
1. The question, the threat model, and why a hash is not enough.
2. Setup, compressed. Concede Witsenhausen / Slepian-Wolf in half a page.
3. **The two-regime law**, with the interval derivation and the measured exponent.
4. **The converse**: the candidates form a packing family sharing a transcript *and* a damaged
   checkpoint, so `sum_v log2 |A_v|` lower-bounds every encoder. Salient and typical coordinates.
5. **Constructions**: the ladder, and the gap.
6. Experiments: the audit, plus the random-coordinate control (§4.1).
7. Limitations: linear tampered layer, sampled faults, one model, pool-size ceiling on N.

**The gap, stated crisply, because it is a contribution.** The best construction spends 17 bits
per flagged row where the information is 5.04. The waste is entirely one thing: **the algebraic
code re-pays for the row locators that the screen already supplied for free.** A field large
enough to index 128,256 rows costs 17 bits; the residual value alphabet needs 5. Naming that as a
computational-informational gap is worth more than a rushed attempt to close it.

---

## 4. What to do next — four items, then stop

1. **Fix the replay noise.** Deterministic reduction or matched batching; re-run the audit. Worth
   1,088 bits and it removes the embarrassing negative row in the ladder.
2. **Verify the head profile.** Raise `verify_cap`, or verify a random subsample per row and
   report an estimate with an interval. The converse currently rests on an unverified count.
3. **Random-coordinate control.** Re-run the audit with uniformly sampled rows and columns
   instead of the salience pools. This is the single biggest threat to the headline and it is
   one line of change. Report both numbers side by side; do not replace one with the other.
4. **Enlarge the text pool.** `N=256` drawn with replacement from 384 texts is ~193 distinct, so
   the curve is already near the pool's ceiling. The `-1` slope extrapolates to a single
   surviving value at `N ~ 8,400`; testing that needs a larger pool. Also add
   `feasible_columns` to the N-sweep so the regime crossover is recorded rather than inferred.

**Then stop.** Do not build the residual-alphabet code, the behavioural decoder, a second model,
or an output-precision sweep. The law is measured, the converse exists, the ladder is complete,
and the remaining gap is better named than half-closed.

---

## 5. Retired from v2

- The `-1` slope as a *prediction*: it is now a measurement (`-0.975` over `N >= 32`).
- Any expectation that the row-summary code would win: at `|E| = 128` it loses to doing nothing.
- The hard floor, already retired in v2, stays retired — the value term keeps decaying at `-1`
  out to `N = 256` with no sign of a plateau.
