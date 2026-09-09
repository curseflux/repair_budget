# The repair budget: a plan for turning this into an ICML paper

Assessment and restructuring plan for `repair_theory_and_evidence_consolidated.md`.

---

## 0. Verdict, stated plainly

**The question is excellent. The current answer to it is not, and I agree with §12.2's own
self-assessment: as written this is a borderline-reject paper.** It is a correct, careful,
well-hedged document whose novel content — after you subtract Witsenhausen-style zero-error
side information, Reed–Solomon errors-and-erasures, Chambolle–Pock, and secure sketches — is
"we ran a syndrome decoder on a Llama head and the retained logits saved 10.9% of the checks."
That is not a top-percentile ICML contribution and no amount of extra trials will make it one.

**But the direction is salvageable into a genuinely strong paper by one reframing, and I think
that reframing produces a top-tier result.** The reframing is not an addition. It is mostly a
*subtraction* plus one new theorem and one new measurement, both of which run on caches you
already have.

The short version of the reframing:

> You are currently trying to show that `L` decreases with `N`. It does not, past a small `N`,
> and **that is the interesting finding.** `L(N)` is not a tradeoff curve; it is a threshold
> phenomenon with a strictly positive floor, the floor is set by the *precision* of the retained
> outputs rather than their *number*, and the floor vanishes exactly when you relax from exact
> weight recovery to behavioral recovery. Your own flat 3968/3968/3534 table is evidence for
> this, not against it.

---

## 1. Diagnosis: three specific things that are wrong

### 1.1 The theory predicts one shape and the experiment shows a different shape

Theorem 8 / eq. (29) says

```
t ≈ ( ln K_eps + ln(1/delta) − kappa·N ) / ln p
```

i.e. `L(N)` decays **linearly in N** and hits zero at `N* = (ln K_eps + ln 1/delta)/kappa`.

The experiment reports `L` = 3968, 3968, 3534 at `N` = 64, 128, 256 — **flat**. The paper
therefore contains a theorem whose predicted shape its only experiment does not exhibit, and
no discussion of why. A reviewer will notice this in five minutes. Right now the honest reading
is "the bound is a loose union bound and the constant `kappa` was never measured", which is
true but is not a paper.

The correct reading — which I believe is the actual physics of the problem — is that eq. (29)
is missing a term. There is a set of perturbations with `beta_b(sigma) = 0` exactly: changes
whose logit effect never crosses a quantizer cell boundary anywhere on the support of `P`.
For those, `(1 − beta)^N = 1` for every `N`. Split the sum in (27):

```
sum_sigma (1 − beta)^N  =  |{beta = 0}|  +  sum_{beta > 0} (1 − beta)^N
                        =  FLOOR(b, P)   +  TRANSIENT(N)
```

`TRANSIENT` dies exponentially in `N`. `FLOOR` never moves. So the true law is

```
L(N, b) = L_floor(b, P, s) + O(exp(−kappa N))
```

and the whole content of the problem is in `L_floor`. Section 3's Proposition 6 already contains
this observation ("two weights in the same quantizer cell ... separation probability is zero"),
but files it as a caveat instead of recognising it as the main term.

### 1.2 The exchange rate is bad and the paper does not confront it

From §9.5: the retained record is 31.3 MiB = 2.6e8 ordinary bits, and it buys 434 protected
bits. That is an exchange rate of roughly **600,000 ordinary bits per protected bit.** A
reviewer will compute this. If the paper's thesis is "retained predictions substitute for
protected storage", that number refutes the thesis on a raw-storage basis.

The defensible position — and it must be stated explicitly, in the introduction, not buried —
is: *the eval record is already on disk and is not the resource being economised. Protected
bits are scarce because they must be signed, replicated, and held offline; eval logs are
cheap and plentiful.* That is fine. But you have to say it, and you have to report the
exchange curve rather than letting a reviewer derive it.

### 1.3 The certificate being measured is a heuristic's budget, not an information quantity

`L` = 3534 is "what the ℓ1 localisation rule needed on ten development tampers." It confounds
three things: the information genuinely left after the transcript, the packing/covering slack
of Reed–Solomon, and the quality of one convex optimiser. §11 already admits the third is
unbridged. The consequence is that **you never actually measure the object your title is about.**

This is the single biggest fixable problem, and the fix is the good news below: for your exact
experimental setting the information quantity is not just definable, it is **exactly computable
on the hardware you already used.**

---

## 2. The reframing

### 2.1 One question, one answer

**Question.** A model's own predictions are already retained. How many *protected* bits must be
written in advance to undo sparse damage — and how does that number depend on how many
predictions you kept (`N`), at what precision (`b`), and how exactly you need the model
restored (`eps`)?

**Answer (the whole paper in four lines).**

1. `L` collapses to **zero** after `N ≈ s·log(dq)/kappa(eps)` retained predictions, **provided**
   the repair tolerance `eps` exceeds the resolution of the retained outputs.
2. Below that tolerance `L` is bounded below by a **strictly positive floor that no `N` removes**,
   because some weight changes are invisible in `b`-bit outputs on the whole support of `P`.
3. The floor is `s·log(d/s) + s·log q_inv(b)` and — this is the part that makes it a paper —
   **we compute it exactly, not asymptotically, for the output head of Llama-3.1-8B.**
4. Consequently: **output precision `b` is the lever, not sample count `N`.** `N` kills the
   transient exponentially; only `b` lowers the floor. Your flat table is this fact.

### 2.2 Why the floor and the behavioral tolerance are the same object

This is the conceptual core and it is, as far as I can tell, new.

*Invisible* means: the perturbation `u` never moves a `b`-bit output code on any sample.
*Behaviorally irrelevant* means: `‖u‖_M` is small under `M = E[A(X)^T A(X)]`.

These are the same set, up to a uniform-convergence gap. Hence:

- **Exact-symbol recovery (`eps = 0`)** forces you to pay for the behaviorally irrelevant part
  of the damage. That part is exactly what the data cannot see. So the floor is unavoidable, and
  you are spending protected bits on detail that does not affect the model's behavior.
- **Behavioral recovery (`eps > eps_c`)** does not. The floor vanishes and `L(N) -> 0`.

So the dichotomy is not a caveat, it is the theorem: **the repair budget is positive for all `N`
if and only if you insist on restoring detail your own retained outputs cannot resolve.** That is
a clean, quotable, falsifiable statement, and it explains why the existing experiment (which
targets exact SHA-256-identical symbols) saturates.

### 2.3 The phase diagram

The paper's central figure. Axes `eps` (repair tolerance) and `b` (retained output precision),
with `N` as the third parameter.

```
             ^  eps  (repair tolerance)
             |
  L(N) -> 0  |        ZERO-BUDGET REGIME
  at finite  |        L*(N) = 0 for N >= N*(eps,b)
  N*(eps,b)  |        N*(eps,b) ~ s log(dq) / kappa(eps,b)
             |
  eps_c(b) --+------------------------------------------  critical tolerance
             |
  L(N) >=    |        FLOOR REGIME
  L_floor    |        L*(N) >= s log(d/s) + s log q_inv(b) for ALL N
  > 0        |        (no amount of retained data suffices)
             +--------------------------------------------> b (output precision)
```

`eps_c(b)` is the behavioral distance corresponding to one output quantizer cell, scaled by the
feature anisotropy: `eps_c(b) ≈ w_b · E[h_j^2]^{1/2} / max_i |h_j(x_i)|`. It shrinks as `b`
grows. `N*` diverges as `eps` approaches `eps_c` from above — a genuine critical divergence,
not a smooth tradeoff.

---

## 3. The four results to prove

Only #2 and #3 are new work. #1 is a compression of what you have; #4 is a corollary you can
almost read off.

### Result 1 (compress, do not headline). The abstract characterization is classical

`L*` is a chromatic number on the transcript fiber — Theorem 2 and Proposition 3, which are
Witsenhausen / Körner–Orlitsky zero-error side information, and in the average case just
`H(theta | z, ell)` by Slepian–Wolf. **Say this in half a page and move on.** Do not sell it as
new information theory; §12.1 is right that this would be the fastest way to lose a reviewer.

The honest and much stronger framing: *the abstract answer has always been a conditional entropy;
the contribution is that for a transformer head this conditional entropy is exactly computable,
and computing it reveals a phase structure nobody predicted.*

Cut Theorem 5 entirely. It is cute and load-bearing on nothing.

### Result 2 (NEW, the converse). The floor, computed exactly for a real model

**Statement.** For the last-layer class with one changed weight per row (your "dispersed"
setting), the ambiguity set factorizes exactly across rows, and for each row the set of
invisible perturbations of weight `(v,j)` is an **interval**

```
I_{v,j} = intersection over i of { delta : Q_b(z_{v,i} + delta·h_j(x_i)) = Q_b(z_{v,i}) }
```

Therefore

```
L*_ell(0) >= log2 |F_ell(z)| = log2 [ sum over supports S of prod_{(v,j) in S} |BF16 ∩ I_{v,j}| ]
```

and this is a **finite, exact, non-asymptotic lower bound on every possible encoder**, evaluable
by direct computation.

**Why it works.** Take `theta_r = z − u_r` over all `s`-sparse `u_r` lying inside the invisible
intervals. Every `theta_r` produces the *identical* transcript `ell` (not merely "within a cell
width" — actually identical codes), every `theta_r` reaches the *same* damaged checkpoint `z`
by changing its own `s` coordinates, so they form a legitimate Theorem 1 packing family with a
common transcript and a common checkpoint. This is exactly the family §9.6 says you are missing
("A lower bound requires multiple actual originals with common transcript and common
checkpoint"). It is not hard to construct — it just requires looking at intervals rather than
at optimizer failures.

**Why it is computable at Llama scale.** The interval endpoints are min-of-ratio reductions:
with `A_{v,i} = lo_{v,i} − z_{v,i} <= 0` and `B_{v,i} = hi_{v,i} − z_{v,i} >= 0`,

```
I_{v,j} = [ max_i (A or B)/h_{j,i} ,  min_i (B or A)/h_{j,i} ]   (branch on sign of h_{j,i})
```

That is a `128256 x 256 x 4096` reduction — matmul-shaped, ~1.3e11 fused ops, a GPU-minute.
Counting BF16 labels in an interval is a bit-pattern range count because BF16 is monotone in its
bit pattern within a sign. Memory: `z` is `128256 x 256` fp32 = 131 MB.

**This is the headline number of the paper.** "The exact information-theoretic repair floor of
Llama-3.1-8B's output head under 64 dispersed BF16 faults, given 256 retained 8-bit full-logit
predictions, is X bits" is a sentence people remember. Non-vacuous information-theoretic bounds
on real 8B models are rare; almost all such bounds in ML are vacuous by many orders of magnitude.
Yours will not be, because it is a direct count rather than a chain of union bounds.

### Result 3 (NEW, the achievability bridge). Data => behavior

**Statement (the missing link Corollary 11.1 asks for).** With probability `1 − delta` over the
sample, simultaneously for every `2s`-sparse `u` with `‖u‖_inf <= 2rho` that is invisible on all
`N` samples,

```
‖u‖_M  <=  c1·w_b  +  c2·rho·sqrt( s·log(d·m/delta) / N )·(feature scale)
```

**Corollary.** If `eps >= c1·w_b + c2·rho·sqrt(s log(dm/delta)/N)`, then `rad(F_ell(z)) <= eps`
for every `z`, and by Corollary 2.1, **`L*(N, eps) = 0`.** Rearranged:

```
N*(eps, b)  ~  C · s · log(d·m/delta) / (eps − c1·w_b)^2
```

— the compressed-sensing sample complexity, appearing as a *repair budget* statement, and
diverging exactly at `eps_c = c1·w_b`. That divergence is the phase transition.

**Honesty about novelty here.** The technical core is close to consistency bounds in quantized
compressed sensing (Boufounos–Baraniuk, Plan–Vershynin, Jacques et al.). Do not present the
concentration inequality as the contribution. What is genuinely yours: the measurements are
*transformer features*, not Gaussians (heavy-tailed, low effective rank, "massive activations"),
the signal alphabet is *finite* (BF16 labels), and the conclusion is a *bit budget* rather than
an estimation error. Prove it under stated moment conditions on real features and **measure the
fourth-moment ratio `C` on the cached activations** — §5's Proposition 9 already sets this up
and then explicitly declines to measure it. Measure it. It is one line of numpy on caches you
have and it converts an unverified assumption into a reported constant.

### Result 4 (NEW but nearly free). Why concentrated tampers are hard

This is the theoretical question §12.3 says would strengthen the paper, and the reframing
answers it almost immediately.

**Dispersed** (one change per row): row `v`'s logits depend only on row `v`'s weights, so you
get `N` scalar constraints on **one** unknown. Massively over-determined; interval collapses.

**Concentrated** (`s` changes in one row): `N` constraints on **`s`** unknowns, and the feasible
set is the polytope `{ delta in R^s : ‖H_S·delta‖_inf <= w_b }`, whose lattice-point count is
governed by `sigma_min(H_S)` — the smallest singular value of the retained feature matrix
restricted to the tampered columns.

So the right variable is not `N` versus `s`, it is **measurements per unknown**, and:

```
L_floor(concentrated) − L_floor(dispersed)  ≈  −(1/2)·log2 det(H_S^T H_S) + s·log2(max_i |h_j|)
```

Transformer activations are strongly anisotropic and low-effective-rank, so `sigma_min(H_S)` is
small and the concentrated polytope is large. **This predicts your empirical failure, quantitatively,
and predicts that concentrated tampers become tractable at `N ≈ s·cond(H_S)·N_dispersed`.** That
is a falsifiable prediction you can test by rerunning concentrated at `N` = 1024 and 4096.

"The repair budget is governed by the spectrum of your retained activations" is a memorable,
ML-native statement, and it turns your one clearly negative empirical result into a predicted
and explained one. That is a large upgrade in how the paper reads.

---

## 4. Experiments: five, all on caches you already have

I want to be explicit that this list is **closed**. Do not add model sizes, languages, precision
grids beyond `b`, or applications. Every item below either measures a quantity the new theory
names, or tests a prediction the new theory makes.

| # | Experiment | What it establishes | Cost |
|---|---|---|---|
| E1 | Exact invisible-interval count on the Llama head | The **floor**, exactly. The paper's headline number. | GPU-minutes on existing caches |
| E2 | `L` vs `N` swept well past 256 (e.g. 32 → 8192) | The predicted shape: fast transient, hard plateau at E1's floor. Fixes the 3-point flat table. | Cheap; existing pipeline |
| E3 | `L` vs `b` at fixed `N` (`b` ∈ 4,6,8,12,16) | **Precision is the lever.** Floor moves with `b`, not `N`. The actionable finding. | Cheap *if* raw logits are cached; one re-forward pass if only 8-bit codes are |
| E4 | `L` vs `eps`: the phase transition | Budget collapses above `eps_c`, floors below. The central claim. | Needs one new decoder mode (§5 below) |
| E5 | Concentrated vs dispersed against `sigma_min(H_S)`, and concentrated at large `N` | Result 4's prediction. Converts a negative result into an explained one. | Cheap |

Plus one measurement, not an experiment: the fourth-moment ratio `C` of Proposition 9 on real
features, and the exchange curve (protected bits vs. `N·m·b` ordinary bits) from §1.2 above.

**E4 needs the one piece of new implementation in the whole plan.** A behavioral-tolerance
decoder: repair only coordinates whose invisible interval is wider than the `eps`-equivalent
threshold, leave the rest damaged, and verify the resulting behavioral distance. This is
Proposition 13's `J` set, made data-driven instead of declared. It is a natural extension of
your existing localisation stage, not a new system.

**The existing full-head run stays**, demoted from "the contribution" to "an end-to-end
demonstration". Reframe the 10.9% as: *"the implemented decoder lands `Y` bits above the
computed information floor"* — which turns a weak number into an informative one, and gives you
a legitimate place to state the computational-versus-informational gap (Reed–Solomon spends
`2s·log p ≈ 62s` bits where counting says `s·log(d/s) + s·log q ≈ 39s`; the factor is a
*computational* cost of efficient algebraic decoding, not an information cost).

---

## 5. Paper outline

1. **Introduction.** The question in three sentences. The threat model in one paragraph with a
   real referent (rowhammer / bit-flip attacks on deployed nets, silent data corruption at scale,
   supply-chain checkpoint tampering). The "why not just re-download / store a hash" paragraph —
   a hash detects but does not repair, and the original may be unavailable, offline, or expensive
   to move; 442 bytes versus 16 GB. The phase-diagram figure.
2. **Setup** (compressed §1). Transcript, tamper class, certificate ordering, the four costs.
   Half a page.
3. **The abstract budget is a conditional entropy** (compressed §2–3). State it, cite Witsenhausen
   and Slepian–Wolf, note it is classical, and pivot: the content is evaluating it. Half a page.
4. **The floor** (Result 2). Theorem + the exact Llama computation. **This is the paper.**
5. **The bridge and the threshold** (Result 3). Theorem + `N*(eps,b)`.
6. **What makes a tamper hard** (Result 4). The spectral characterization.
7. **An implementable decoder** (compressed §6–7). Reed–Solomon errors-and-erasures, the ℓ1
   localiser, the full-head run, the gap to the floor.
8. **Experiments** (E1–E5).
9. **Limitations.** Linear tampered layer; sampled rather than adversarial faults; pilot-scale
   trial counts; the exchange rate.

Working titles: *"The Repair Budget: How Many Protected Bits Does a Model Need, Given Its Own
Predictions?"* or *"Repairing a Model From Its Own Predictions Has a Floor."*

---

## 6. What to cut

Cutting is most of the work and it will feel bad. Do it anyway.

- **Theorem 5** (Markov + critical-graph edge count). Load-bearing on nothing.
- **Proposition 12** (value accuracy -> symbol accuracy). Explicitly unused; §7.1 says the
  experiment does not use value proposals. To the appendix at best.
- **The INT8 / INT4 comparison** (§9.3). §9.3 itself concludes it establishes nothing about
  repair difficulty. One sentence, or gone.
- **§5.1 numerical-execution caveats**, **§9.5 timing breakdown**, **§10 provenance discipline**,
  **Appendix A/B.** All correct, all appendix material. They currently occupy roughly a third of
  the document and none of it is a result.
- **Proposition 13 in its current form.** Replace with the invisible-equals-irrelevant lemma,
  which does the same job and is the actual theorem.

Roughly: the current document is ~40% classical restatement, ~35% caveats and provenance,
~25% results. The paper wants that inverted.

---

## 7. Positioning, and the three objections a reviewer will raise

**Prior work to cite and differentiate explicitly:**

- *Zero-error side information / source coding with side information*: Witsenhausen 1976,
  Körner–Orlitsky, Slepian–Wolf. **The abstract form of your answer.** Concede it fully.
- *Fuzzy extractors / secure sketches*: Dodis et al. Recover an object from a close version plus
  a short sketch. **Your new axis is observational side information about a function of the
  object.** Already cited; make the distinction load-bearing.
- *Quantized / one-bit compressed sensing*: Boufounos–Baraniuk, Plan–Vershynin, Jacques et al.
  **Nearest neighbour to Result 3.** Cite prominently and honestly.
- *Model extraction from logits*: Carlini et al., "Stealing part of a production language model"
  (2024) — literally recovers the final layer from logit queries. **This is your closest ML
  relative and it helps you:** it establishes that last-layer information is substantially
  present in logits. Different question (extraction vs. repair budget), same geometry.
- *Bit-flip attacks and DNN integrity*: Rakin et al. (BFA), Hong et al. "Terminal Brain Damage"
  (USENIX'19), and checksum/ECC defenses. **Your application anchor.** Also Meta's "Silent Data
  Corruptions at Scale" and Google's "Cores that don't count" for the SDC framing.
- *ABFT*: Huang–Abraham 1984. Already cited.

**Objection A — "Is this a real problem?"** Answer with the threat-model paragraph above, and
be careful not to oversell it as a security system against adaptive adversaries. It is a theory
paper with a demonstration.

**Objection B — "Your theory is a linear last layer; real damage hits the whole network."**
Answer: (i) the head is the single largest matrix in the model, 525M parameters, 6.6% of an 8B;
(ii) the analysis applies verbatim to *any* single tampered linear layer given cached inputs to
that layer — your `A(x)` formulation already says this; (iii) demonstrate it by rerunning E1 on
one mid-stack MLP layer. That third item is cheap and closes the objection properly. Scope the
claim honestly rather than gesturing at deep networks.

**Objection C — "Union bounds and counting; where is the depth?"** Answer: the depth is that
the bounds are *evaluated*, not merely stated, and are non-vacuous on a real 8B model; that the
converse is an explicit construction rather than an existence argument; and that the uniform
convergence over sparse directions with heavy-tailed anisotropic transformer features is not a
textbook exercise at `d = 5.25e8`. If you want a fourth contribution, the computational-versus-
informational gap in §4 above is a clean one — but only if it falls out, do not go hunting for it.

---

## 8. Feasibility and stopping

**Feasibility: high.** Nothing here requires new infrastructure. Result 2 is a reduction you can
write in an afternoon and run in minutes. Result 4 is a singular-value computation. Result 3 is
the only real theorem-writing, and it has a well-trodden template to adapt. E4 is the only new
code. Estimate 6–10 weeks, which fits a cycle.

**Is it top-percentile ICML?** With Results 2 and 3 proved and E1–E5 coming out as predicted:
yes, I think this is a spotlight-class paper. It has a single memorable question, a surprising
and falsifiable answer, matching-in-shape upper and lower bounds, a *computed* non-vacuous
information bound on a real 8B model, a working end-to-end system, and it explains its own
negative result. That is a strong package.

Without them — i.e. shipping the current document with more trials — it is a weak reject, for
exactly the reasons §12.2 already gives itself.

**Stopping condition, stated so it can be enforced.** The paper is done when:

1. The floor is computed exactly for the Llama head (E1).
2. `L(N)` is shown to plateau at that floor (E2), and `L(b)` is shown to move it (E3).
3. The `eps` phase transition is demonstrated (E4).
4. Concentrated-versus-dispersed is explained by `sigma_min(H_S)` and the prediction is tested (E5).

**When those four hold, stop.** Do not add a second model family, a second modality, adversarial
tampers, a security analysis, or a deeper-network extension beyond the single mid-stack layer in
Objection B. Every one of those weakens the story by diluting a single clean claim, and the
document's own §12.3 warning against "adding languages, model sizes, precision grids, or
unrelated applications to conceal a gap" applies equally to adding them once the gap is closed.

If E1 comes back showing the floor is negligible — i.e. 256 retained 8-bit logit vectors nearly
determine the head — that is **not** a failure. It is a striking result in its own right
("`N` retained predictions almost fully pin an 8B model's output head") and it points the paper
at the `b` and `eps` axes instead. Either outcome is publishable; that is what makes this a safe
direction rather than a gamble.
