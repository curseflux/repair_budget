# Strict Review: *The Repair Budget of a Tampered Model*

**Reviewing posture:** ICLR, area-chair-grade, calibrated to "would this be in the top decile?"
**Summary score as the document currently stands (assuming §12 experiments are run competently): 5 — marginally below acceptance threshold.**
**Score with the restructuring in §5 below: 8–9, spotlight/oral range.**

---

## 1. What the paper actually claims, stated back

A model's last layer is `f_c(x) = <c, σ(x)>`. An adversary flips ≤ `s` coordinates of `c` by ≤ `ρ` each. The defender holds `N` trusted input–output pairs recorded at precision `γ`, plus `L` bits committed before the attack. How large must `L` be to restore the function to within `ε`?

The reduction is one line: `r = Φ_D e + ξ`. Repair is sparse recovery whose sensing matrix is the network's own feature matrix. The governing scalar is `A(D)` — the largest functional change invisible at label precision. Below it: zero bits. Above it: a packing lower bound, and a Reed–Solomon ceiling of `O(s log h + s log(ρ√λ/√ε))` ≈ 100 bytes for Llama-scale.

The framing is clean and the writing is unusually honest (Prop 5.1 attacks the author's own earlier formulation; §9's hash caveat; §11.5's terminology-collision warning). That honesty is a real asset and should survive whatever restructuring happens.

---

## 2. The blunt novelty audit

I went through every result and asked: what would a reviewer who knows compressed sensing, distributed source coding, and coding theory say is new?

| Result | Verdict |
|---|---|
| §3 reduction `r = Φe` | **Known.** Candès–Tao 2005. The doc concedes this. |
| Prop 5.1 (genericity collapse) | **New but negative.** A one-line argument that demolishes the exact-arithmetic formulation. Valuable as intellectual hygiene, worth ~half a page, not a contribution. |
| Prop 5.2 (ellipsoid inside `N(D)`) | **Trivial.** Two lines, `‖·‖_∞ ≤ ‖·‖_2` plus an SVD. |
| Thm 5.4 (zero-bit criterion) | **Definitional**, and the positive direction is *wrong as stated* — see §3.1. |
| Thm 6.1 (uniform bound, `N ≳ τ⁻² s log(h/s)`) | **Standard.** Textbook Mendelson small-ball applied to the `s`-sparse sphere. No reviewer will credit this as novel. |
| Thm 7.1 (bit lower bound) | **Standard technique, new object.** Volume-packing with side information. The novelty is the information structure, not the argument. |
| **Thm 8.1 (RS ceiling)** | **Essentially known — this is the load-bearing weakness.** Recovering an `s`-sparse difference from an `O(s log h)`-bit sketch is exactly set reconciliation / IBLTs / ℓ0-sampling sketches. **§11.1 cites Minsky–Trachtenberg–Zippel and IBLTs itself.** A reviewer will connect those two pages and write "Theorem 8.1 is a known sketch with a quantizer bolted on." The mod-`M` trick that converts `B` into `ρ` is cute and is roughly one paragraph of novelty. |
| §9 (detect/localize/repair ladder) | **New and genuinely useful.** The separation "detection can be free while repair is not" is the most quotable thing in the document. |
| §10 (LM head decoupling) | **Correct and nice**, but see §3.3 — it silently assumes you record the full 128k-dim logit vector. |

**Net:** the technical contribution is a converse for an information structure nobody has formalized, plus a known achievability. That is a workshop paper or a solid-but-unremarkable conference paper. It is not top-decile ICLR.

**Where the actual novelty is hiding:** the *pre-commitment information structure* (encoder sees `c` and `D`; adversary sees everything including `κ`; decoder sees `D`, `c̃`, `κ`) is genuinely non-standard — the side information at the decoder is the source itself, passed through an adversarially chosen channel that has read the codebook. That is closer to Kuznetsov–Tsybakov defect-correcting codes, Bassalygo–Gelfand–Pinsker localized errors, and the AVC-with-informed-jammer literature than to Slepian–Wolf. **None of those three are cited.** Cite them, and then mine them — the data-aware achievability the doc calls its main open problem is much more likely to come from that corner than from compressed sensing.

---

## 3. Four things that will sink this in review

### 3.1 A real bug: Theorem 5.4's positive direction needs `2s`, not `s`

`N(D)` is defined (Def 4.1) with `‖v‖₀ ≤ s`, `‖v‖_∞ ≤ ρ`, justified by the special case `c̃ = c`. That is fine for the *converse*.

It is not fine for the achievability direction of Thm 5.4. The decoder's uncertainty set given `(D, c̃)` is

```
C = { c : c consistent with D,  c̃ − c ∈ T_{s,ρ} }
```

and for `c', c'' ∈ C`, the difference `c'' − c' = (c̃ − c') − (c̃ − c'')` is **2s-sparse with ℓ∞ ≤ 2ρ**. So the `d_P`-diameter of `C` is bounded by `2·A_{2s,2ρ}(D)`, not by `2·A_{s,ρ}(D)`. The claim "`A(D) ≤ ½√ε ⟹ L* = 0`" does not follow from the stated definition. The proof sentence — "every candidate ... lies within `Σ^{1/2}`-distance `A(D)` of the least-squares candidate" — is asserted, not proved, and the least-squares candidate need not lie in `C`.

Fix: define two quantities, `A_s` (converse) and `A_{2s}` (achievability), and note `A_s ≤ A_{2s} ≤ ` (a constant times `A_s` under RIP-type conditions). Cheap to repair, but a theory reviewer who finds it will lose confidence in everything else, and §11's own framing ("the content is the converse") invites exactly that scrutiny.

Related sloppiness: Thm 7.1's packing count `∏ max{1, a_i√λ/(2√ε)}` is not correct as a per-axis product for a thin ellipsoid — the volume argument needs the axes below the resolution handled jointly, not floored to 1 individually. It survives up to constants; state it as a volume ratio.

### 3.2 The accounting hole — this is the one that actually matters

§2.5: *"Only the certificate is charged. The trusted set is treated as given."*
§13.4: the joint budget is *"worth a section once §13.1 is settled."*

**This is backwards, and a hostile reviewer will build their entire negative review on it.** The headline results are "`L* = 0` under Cor 6.2" and "`L* ≤` 100 bytes." Both are obtained by moving cost into an uncharged resource. Corollary 6.2 requires `N ≳ τ⁻² s log(h/s)` labels stored at `β ≈ log₂(R/γ)` bits each, tamper-proof — because if the adversary can touch `D`, every guarantee in §6 evaporates. That is protected storage, and it is not free. For the Llama numbers in §10 with a full logit vector recorded, `D` is *larger than the layer you are protecting*.

The defense offered — "trusted data is typically pre-existing, a public validation set whose integrity is assured by other means" — is exactly the move the paper refuses to let the hashing literature make in §9. You cannot criticize a hash for being brittle to benign change and then assume a pristine, adversary-proof, free validation set with recorded real-valued outputs.

**The fix is not a caveat. The fix is to make the joint budget the question.** See §5.

### 3.3 The observation model is unrealistic *and* load-bearing

The document assumes the defender recorded `y_i ≈ f_c(x_i)` — a real number per output coordinate, to precision `γ`. For the LM head, "the problem decouples into `V` independent instances sharing one sensing matrix" (§10) is only true if you stored **all 128,256 logits** for every probe. Nobody does that. What actually exists is: generated text, or a top-`k` list, or an accuracy number on a benchmark.

Under top-`k` or argmax observation:
- The measurements become **non-linear and one-bit-like** (comparisons between logits), not `Φ_D e + ξ`.
- **Rows of `W` for tokens that never surface in the top-`k` are completely unconstrained by any number of probes.** `A(D)` for those rows is at its cap `ρ√λ_max` regardless of `N`. Theorem 6.1 does not apply, because the small-ball assumption fails outright for those directions (`τ = 0`).

So the regime the document treats as the whole problem — full real-valued observation at fine precision — is the *easy* regime, and the reason its answer keeps coming out "zero bits." The realistic regime is coarse observation, where the answer is emphatically not zero. **The paper is currently solving the easy half and calling the hard half "label precision `γ`."**

This is the single biggest missed opportunity in the document, and simultaneously its biggest available source of novelty.

### 3.4 Motivation is thin at exactly the point reviewers press

"Why not just keep a copy of the weights?" For an open-weight model on commodity hardware, the answer is: you should, and the paper is moot. §E4's baseline (LM-Fix at 1.9–5% of model memory) is a weak baseline — the strong baseline is *re-download the checkpoint*.

The setting where 100 bytes vs. 5% is decisive is where protected storage is genuinely tiny and expensive: TPM NV-RAM, on-chip fuses, secure-enclave sealed storage, an on-chain commitment, a hardware root of trust — all in the kilobyte range. Say this in the first paragraph, with the actual capacity numbers, or reviewers will assume the problem is invented.

Secondarily: bit-flip/rowhammer as *the* threat model reads as 2019. The threat people care about now is a malicious fine-tune or a poisoned LoRA adapter from a model hub. See §5.3 — that extension is nearly free and multiplies the paper's relevance.

Minor but worth catching: Thm 8.1's decoder assumes unattacked coordinates are **bit-exact** (`c̃_j = c_j`). Under any benign drift — a different accelerator, a re-quantization — a constant fraction of the `h` coordinates sitting near cell boundaries change symbol, `d_H(ỹ, y) ≫ s`, and Berlekamp–Massey fails catastrophically. Within the stated threat model this is legal, but it means **the §8 construction is brittle in precisely the way §9 criticizes hashing for being brittle.** Either state the assumption loudly or fix it with dithered/nested-lattice quantization — the fix is not hard and it converts a weakness into a contribution.

---

## 4. Is `L* > 0` ever actually the operative regime?

This determines whether the machinery earns its keep, and the document never asks it directly. Working it through:

`A(D)` is large exactly when there exists a sparse `v` with `|<σ(x_i), v>| ≤ 2γ` on **every** probe but `E[<σ(X), v>²]` large. That is not a spectral-decay phenomenon — fast decay of `Σ` produces directions that are quiet on the data *and* functionally harmless, which contribute nothing. It is a **tail phenomenon**: a direction that is silent on `N` draws but loud on a rare mode.

This means:
- `τ` in Assumption SB is literally *"how rare is the trigger"*. A feature direction active on 0.1% of inputs gives `τ = 10⁻³` and `τ⁻² = 10⁶` in Theorem 6.1. The sample complexity is not a constant-factor concern; it can be catastrophic, and it is **measurable**.
- `A(D)` is therefore best understood as **backdoor capacity**: the largest functional change an adversary can hide inside your evaluation set. Real LMs have massive activations, outlier features, and long-tailed token statistics — every ingredient for `τ` to be tiny on the directions that matter.

**This reframing is more interesting than anything currently in §5–6, and it makes E3's stated prediction wrong.** §12/E3 predicts "sharper spectral decay ⟹ larger `A(D)`." The right prediction is: **`A(D)` is governed by the tail of `<σ(X), v>` along sparse directions, and is essentially independent of the bulk spectrum.** Fix the prediction before you run the experiment, or you will measure the wrong thing and report a null result.

---

## 5. What would make this top-decile

The single change: **stop treating trusted data as free, and make the currency comparison the paper.**

### 5.1 The question the paper should ask

> **To be able to undo a tampering, is it cheaper to remember what a model *does*, or what a model *is*?**

Simple, non-jargony, memorable, and nobody has asked it. It contains the current document as its special case (`L`-only, with `D` free) but it is a strictly richer and more honest object.

Formally: charge a **total protected budget** `B = N·β + L`. Characterize the achievable region in `(N·β, L)` for repair to `ε`. `A(D)` is no longer the answer — it becomes the **exchange rate between the two currencies**, which is a much better job for it.

### 5.2 The answer is already visible, and it is contrarian

Sketch the two extremes with the document's own quantities:

- **Parameter-only:** `L ≈ s·log h + s·log(ρ√λ/√ε)`.
- **Behaviour-only:** `N ≈ τ⁻² s log(h/s)` labels at `β ≈ log(R/(κ√ε))` bits, i.e. `≈ τ⁻² · s log(h/s) · log(R/(κ√ε))` bits.

Behaviour is worse by roughly a factor of **`τ⁻²·β`**. Each label spends `β` bits to buy one scalar constraint in a direction you did not choose; each parity symbol is targeted. So:

> **Behaviour is an inefficient currency for model integrity — by a measurable factor that can be six orders of magnitude on a real LM.**

That claim cuts directly against the implicit premise of the entire sensitive-sample / fingerprinting / model-equality-testing literature, and it *explains* why deployed recovery systems need 1.9–5% of model memory. A result that explains an existing empirical landscape and reverses a community assumption is what top-decile looks like.

But the story must not stop there, because behaviour bits buy two things parameter bits cannot:
1. **Black-box applicability** — you can audit a model you cannot open.
2. **Drift tolerance** — behaviour survives re-quantization, hardware change, benign fine-tuning; the §8 syndrome does not (§3.4 above).

So the honest result is a **three-axis exchange**: *behaviour costs `τ⁻²β×` more per unit of repair, and that factor is the price of black-box access and drift tolerance.* Quantifying that price, on real models, is a genuinely new contribution and the kind of thing that gets cited outside its own subfield.

### 5.3 Four additions, ordered by value per unit of effort

**(a) Coarse observations — highest value.** Replace "real-valued at precision `γ`" with an *observation channel* `O` the defender chooses: full logits at `β` bits, top-`k`, argmax/text, or benchmark accuracy. Now `γ` is not a nuisance constant — it is a **design variable with a price**, and the defender's problem is to allocate `B` between resolution, probe count, and parity. One-bit compressed sensing (Boufounos–Baraniuk; Plan–Vershynin) gives you the tools for the argmax case; that literature is not cited and should be. This single change moves the theory out of classical CS and makes the technical contribution unambiguously new.

**(b) Data-aware achievability (currently §13.1) — mandatory, not future work.** As long as the ceiling ignores `D`, the paper is "a converse, and a known sketch that has nothing to do with it." Reviewers rate that as incomplete. You need `L ≈ d*(D;η)·log(ρ/√ε) + (support-identification syndrome)`, so the two bounds meet up to constants. Look at defect-correcting codes (encoder knows the defects) rather than compressed sensing — the encoder here *does* know `Φ_D`, which is precisely the Kuznetsov–Tsybakov structure.

**(c) Low-rank instead of coordinate-sparse — near-free relevance multiplier.** Everything survives replacing `‖e‖₀ ≤ s` with `e` in a known low-dimensional family: `N(D)` becomes a low-rank invisible set, the packing becomes Grassmannian, the syndrome becomes a low-rank sketch. The payoff: the paper becomes **"how many bits to undo a malicious LoRA / poisoned fine-tune"**, which is a 2026 problem with a real audience, instead of a rowhammer problem with a 2019 audience. Keep bit-flips as the clean special case where `ρ` and `s` are pinned by published attacks.

**(d) Minimax probe design (currently §13.2).** The formulation in §13.2 is *right* — `max_{x_i} min_{‖e‖₀≤s} visibility` — and the observation that rows must be realizable `σ(x)` (the feature manifold is not `ℝ^h`) is the thing that makes it not a corollary of compressed sensing. A greedy/submodular selection with a uniform guarantee, beating sensitive-sample heuristics empirically, is a self-contained contribution with an obvious baseline. Include it if there is room; it is the most directly usable piece for practitioners.

### 5.4 What to cut

- Prop 5.1 and the §5/§6.3 self-litigation: compress to one paragraph plus a remark. It is a debate with a previous draft, and readers do not have that context.
- Thm 8.1 as a headline: demote to "a data-free ceiling follows from standard sparse-recovery sketches (cite IBLT / set reconciliation); we record it for completeness and improve it in §X." Presenting it as a contribution invites the harshest available criticism.
- Prop 5.2, Thm 5.4: merge into one lemma.

---

## 6. Experiments: what to run and what to predict

The current §12 is a good list, mis-ordered and with one wrong hypothesis. Reordered by what a reviewer needs to believe:

**X1 — Measure `τ`, the rare-mode exponent (new, and the crux).** On an open LM, for random and adversarially chosen sparse supports, measure the distribution of `<σ(X), v>` and estimate `τ(κ)` directly. **Headline deliverable: `τ` on real feature geometry, and therefore whether Theorem 6.1's sample complexity is 10³ or 10⁹.** If `τ` is tiny — which the massive-activation literature suggests — you have proven that data cannot buy repair and bits must be paid. That is the result that makes the paper.

**X2 — `A(D)` vs. `N` under realistic observation channels.** Plot `A(D)` against `N` for full-logit, top-`k`, and argmax observation, at matched *total bit cost* `N·β`. Prediction to state in advance: full-logit `A(D)` collapses fast; top-`k` and argmax plateau at a floor set by the tail, and the plateau does not move with more probes. **A plateau is the money figure.** It is the visual proof that the problem is real.

**X3 — The eval-invisible attack (currently E5, should be near the front).** The maximizer of `A(D)` *is* a sparse edit invisible on your evals and maximally harmful under `P`. Construct it; show it passes a full benchmark suite while changing deployment behaviour. This is the figure that makes reviewers outside the subfield care, and it connects the paper to sandbagging / sleeper-agent / eval-integrity concerns that are currently entirely un-theorized.

**X4 — The rate region, end to end.** Repair a real published bit-flip attack (and a poisoned LoRA, per §5.3(c)) at matched total budget `B`, sweeping the split between behaviour bits and parameter bits. Overlay the converse and the data-aware ceiling. **Deliverable: the empirical exchange rate, and whether the predicted `τ⁻²β` factor shows up.**

**X5 — Drift tolerance, as the honest counterweight.** Re-quantize, change accelerator, apply a benign fine-tune. Show the §8 syndrome breaking and the behavioural route surviving. This is what stops the paper from reading as "just store parity" and turns the currency comparison into a genuine trade-off rather than a knockout.

Drop E3 as stated (spectral decay), or replace it with the tail-based prediction from §4 above.

---

## 7. Suggested structure

1. **A model is deployed. Someone changes it. What is the cheapest thing you could have written down beforehand to undo that?** — with the hardware-root-of-trust capacity numbers, immediately.
2. Setup, the reduction, and the *total* budget `B = N·β + L`. Charge everything.
3. `A(D)`: the largest functional change invisible to your evaluation. Define it once, interpret it as backdoor capacity.
4. Converse: the packing bound, in terms of `A(D)` and the restricted spectrum against observation resolution.
5. Achievability: data-aware, matching to constants. Data-free sketch as the degenerate corner.
6. **The exchange rate.** Behaviour vs. parameters; the `τ⁻²β` factor; the two things behaviour buys that parameters cannot.
7. Coarse observation: argmax/top-`k`, and the plateau.
8. Measurements X1–X5.
9. Detect / localize / repair ladder — keep, with the existing honest caveat.

Rename "certificate" (§11.5's own advice) — **repair budget** as the quantity, **restoration sketch** as the object.

---

## 8. Verdict

The instincts here are good and unusually self-critical, and the core object — `A(D)`, a measurable property of a trained network that says how much of it your evaluations actually pin down — is a genuinely good idea that the document undersells by burying it in a bit-counting exercise.

But as written, the theory is standard tools on a new information structure, the achievability is a known sketch, one theorem is stated incorrectly, the observation model dodges the hard case, and the headline "zero bits" is purchased with an uncharged resource. Reviewers 2 and 3 will find the accounting hole independently, and it is fatal on its own.

The path to top-decile is not more theorems. It is:
1. **Charge for everything** and make behaviour-vs-parameters the question.
2. **Make observations coarse** — argmax and top-`k` are the real world and the real difficulty.
3. **Match the bounds** — data-aware achievability, not future work.
4. **Measure `τ` on a real LM** and report the number, whichever way it falls.

Do those four and the paper answers a question anyone can state in a sentence, with an answer that is contrarian, falsifiable, and grounded in a measurement nobody has made. That is what the top of ICLR looks like.
