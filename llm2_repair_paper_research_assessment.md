**Research assessment: How many protected bits does model repair need?**

Prepared from `repair_theory_and_evidence_consolidated.md` and a targeted primary-source literature review, 9 September 2026. The attached proof document is the only project artifact inspected in this review. Its descriptions of previous source inspection, tests, and Llama runs are reported evidence, not work independently reproduced here. Two additional elementary derivations below are analysis from this review, not claimed research novelties.

**The question is worth pursuing; the present results do not yet meet the requested novelty bar.**

My recommendation is a bounded continuation of the existing project, with no expansion of model sizes, benchmarks, applications, or behavioral objectives. The current document supports a sound formulation and a working proof of concept. It does not yet establish a sufficiently sharp answer to the proposed sample–certificate question, nor an algorithmic advance that would justify describing it as a likely exceptional ICML paper. There is no basis for guaranteeing acceptance or placement in the top percentile, even after the proposed work.

The scientific gap is larger than manuscript polish. Most of the general theory consists of valid applications of established information and coding arguments. The most distinctive theorem gives a sufficient budget through quantities not established for the tested model. The practical construction has a classical conditional guarantee and produces a modest saving against a baseline that can potentially be strengthened substantially under the experiment's structure.

I would preserve the central question almost verbatim:

> Given a damaged model, a known class of permitted changes, and N intact records of the original model's predictions, how many additional protected bits, written before damage, are needed to recover the original model?

The potential paper is about the information that those records replace. It should not become a general paper about fault tolerance, behavioral geometry, LLM security, and error correction simultaneously.

**Four choices determine which problem the paper actually answers.**

First, knowing the training labels does not generally mean knowing the original model's predictions. An original training pair `(x, y)` and a retained pair `(x, Q_b(f_theta(x)))` are different resources. They coincide only under an explicitly justified interpolation and output convention. The experiments retain full vocabulary logits, rather than ordinary training targets. State this in the opening definition.

Second, keep the original model fixed while varying the number of retained records N. If N instead changes the size of the dataset used to train a new model, the object being repaired changes too. The document's monotonicity theorem then no longer directly describes that experiment. A clear notation is `n_train` for original training-set size and N for the number of its available prediction records, or for a separate retained probe set. This distinction preserves the intended question rather than silently substituting a different one.

Third, use exact stored-model recovery as the main target. It matches the implemented certificate and gives an unambiguous success criterion. Behavioral recovery is a legitimate different problem, but the present metric, relevance reduction, and unimplemented behavioral allocation introduce a second paper without resolving the first. Exact recovery can be defined on canonical finite numerical representations if signed-zero distinctions are unwanted; that convention must precede the theorem.

Fourth, choose and label the probability guarantee. The document's uniform quantity asks for one setup that works for every original and every legal tamper. Its experiments test sampled faults against one head. These cannot share an unlabeled “required bits” curve. A theoretical curve can be uniform for a specified linear-head family, while the Llama curve is an achieved budget at an explicitly stated empirical reliability. That is a coherent paper if the relationship is explained.

Training-data reuse needs care, but there is a useful nuance: dependence of the trained parameter on the sample is not automatically fatal to a theorem that already holds simultaneously for every parameter in a fixed, sample-independent class. Such a uniform event also covers the selected parameter. Conversely, fixing a feature extractor learned from those same inputs and then treating its feature vectors as iid conditional on that extractor is not automatically valid. The last-layer geometric theorem needs an independent feature map, an appropriate uniform argument, or a separate dependence analysis. Fresh retained probe inputs are the cleanest option if the original training records are not essential to the scientific claim.

If the full original is reproducible from retained data and public deterministic training settings, unlimited-computation repair may need zero additional bits. The unknown training randomness or other ambiguity must therefore be explicit in the original-model class. “Trained on this dataset” should either impose an actual public constraint on that class or remain motivation; it cannot quietly strengthen a lower bound while being absent from its definition.

**The proof audit supports the mathematics, but narrows its significance.**

I did not identify a substantive mathematical error in the main stated results under their explicit assumptions. This is a direct proof review, not a formal verification. The following judgments distinguish correctness, applicability, and novelty.

| Result in the source | Audit judgment | Role in a paper |
|---|---|---|
| Theorem 1: separated candidates force bits | Correct pigeonhole and triangle-inequality argument. The candidates must share the same transcript and damaged checkpoint. | Essential lower-bound tool; not yet a quantitative converse. |
| Theorem 2: exact partition characterization | Correct, including the requirement that one encoding partition work across all damaged checkpoints. | Useful precise definition; general formulation rather than the main advance. |
| Corollary 2.1: zero bits, covers, refinement | Correct for the stated reconstruction class and nested records. | Short preliminary result. |
| Proposition 3: graph bounds | Correct. Exact at zero tolerance for the chosen metric; a behavioral pseudometric still does not distinguish identical-behavior symbols. | Established side-information coding connection. |
| Theorem 4: pair survival | Correct under iid inputs and a fixed per-input observation map. Uniformity across a predetermined class matters. | Standard union-bound baseline. |
| Theorem 5: intermediate graph bound | Correct use of Markov's inequality and the minimum edge count of a critical graph. Potentially very loose. | Appendix unless needed for a specific comparison. |
| Proposition 6: coverage and precision obstructions | Correct. Demonstrates that N alone cannot determine a universal rate. | A short motivating impossibility example. |
| Theorems 7–8: sparse random certificate | Correct collision-and-survival argument, with the declared field, independence, and bounded-cell assumptions. | Most relevant current theoretical component, but an existence bound with exhaustive feasibility decoding. |
| Proposition 9: moment visibility | Correct small-ball argument. It supplies visibility only above a scale set by quantizer width and the moment constants. | Conditional sufficient assumption, not a demonstrated property of Llama or an exact-symbol theorem. |
| Theorem 10: error-and-erasure decoding | Correct Vandermonde uniqueness and constructive recurrence argument. Implementations may fail or miscorrect outside the stated radius. | Reliable algorithmic component; classical mechanism. |
| Proposition 11 and Corollary 11.1 | Correct accounting and conditional implication. They do not establish the data rule's sample dependence. | Useful interface between prediction processing and coding. |
| Proposition 12: rounding bridge | Correct on a uniform grid. BF16's global minimum spacing makes the naive specialization weak. | Peripheral unless the new method actually estimates values. |
| Proposition 13: relevance reduction | Correct subject to reconstruction membership and the uniform relevance assumption. | Remove from the main exact-recovery story. |

In particular, the graphical lower bound and the maximum candidate-set size are not generally interchangeable. For exact recovery, `log_2(max_z |F_l(z)|)` is a valid lower bound, but the certificate must color the whole confusability graph within the transcript fiber. Different checkpoints can create mutually incompatible encoding requirements. Do not announce an optimal certificate by counting one post-tamper list and storing its index: the encoder did not know that checkpoint when it wrote the bits.

The same issue applies to random hashing. A short hash that separates one fixed candidate list with high probability does not automatically work against every checkpoint an attacker can choose after seeing the hash. Theorem 7 avoids this problem by excluding every relevant harmful difference simultaneously. Any replacement must preserve the intended quantifiers.

**Theorem 8 is not yet the promised law of L versus N.**

Its core guarantee is

\[
\Pr(\text{some allowed recovery fails})
\leq p^{-t}\sum_{\sigma}(1-\beta_b(\sigma))^N.
\]

This is a useful way to combine samples and a certificate. Under uniform visibility it yields the sufficient allocation

\[
t\geq \frac{\ln K_\varepsilon+\ln(1/\delta)-\kappa N}{\ln p},
\]

with truncation at zero and integer rounding. It does not prove that the optimal bit budget decreases linearly, that the rate is tight, or that the implemented decoder achieves it. The harmful-signature count is an outer count; the visibility constant is unverified; and the geometric condition discards information about actual quantizer boundaries.

That last issue is particularly consequential. Equal quantized outputs imply differences no larger than a cell width, but the converse is false. If two outputs differ by a small amount, they can still lie on opposite sides of a boundary. Different iid inputs may repeatedly provide new boundary constraints, eventually resolving differences far smaller than one output cell. Replacing the cells by generic bounded noise can lose this effect. Conversely, repeated observations of the same constant output in the same cell may reveal nothing new. Whether additional examples resolve fine precision depends on the input distribution and the observation map, not just on b.

The document recognizes the outer-relaxation distinction, but it does not exploit actual cell positions to derive a useful repair-bit rate. This is the most promising place to focus further theory. It is also an area with serious prior work, discussed below; simply importing a quantized recovery theorem and appending a hash is not automatically enough novelty.

There are exact-symbol obstructions that should be removed by definition or explicitly tolerated. If two distinct labels represent the same numerical value and those symbol changes are allowed, no prediction record can distinguish them. If some features vanish on the input distribution, changes in the corresponding weights remain invisible. Clipping can also create equal-code families. A uniform exact-recovery theorem over all finite BF16 heads should not assume these away implicitly. In particular, proving a useful positive visibility constant over that entire class is not a sensible open-ended objective.

**The relevant literature is broader than the current document suggests.**

The most consequential omission is Gao and Lafferty's *Model Repair: Robust Recovery of Over-Parameterized Statistical Models*. It studies recovering a model after parameter corruption using the original input design, without the training responses. Its recovery mechanism exploits the subspace structure of estimators and connects model repair to error correction. The paper covers linear models, random features, and neural-network settings under its assumptions. Thus “repair a corrupted trained model from the original inputs” is already an established research question. Your potential distinction is the quantitative additional protected-bit budget after finite-precision prediction records are supplied, without relying on precisely the same training-induced redundancy. [Gao and Lafferty, 2020](https://arxiv.org/pdf/2005.09912).

| Prior work | Established overlap | What it does not by itself settle here |
|---|---|---|
| Gao and Lafferty | Exact model repair using original input design and estimator structure. | The proposed tradeoff between protected bits and retained finite-precision predictions. |
| Secure sketches and fuzzy extractors | Recovering an object from a nearby object plus a precomputed sketch, including syndrome constructions and coding lower bounds. | The effect of this particular additional prediction transcript on the optimal sketch. |
| Finite-alphabet compressed sensing | Sparse finite-symbol recovery using coding constructions and information/sample complexity analysis. | The combination of a damaged dense head, fixed numerical prediction records, and additional pre-tamper bits. |
| Quantized consistent recovery | How sets of signals compatible with quantized observations shrink with more measurements. | A sharp protected-certificate tradeoff with the damaged model and the correct encoder timing. |
| RADAR and DeepNcode | Checksum- or encoding-based protection of neural weights. | The same exact restoration target, retained-record resource, and sample–certificate theorem. |

The secure-sketch connection is direct, not merely an analogy. A recovery sketch need not be novel because its object is a checkpoint. Privacy and entropy-loss goals in that literature differ from this project's storage objective, but the recovery constructions remain relevant. [Dodis, Ostrovsky, Reyzin, and Smith, 2008](https://arxiv.org/pdf/cs/0602007).

Das and Vishwanath explicitly use finite-field coding for finite-alphabet sparse recovery. Treating stored weights as finite labels and exploiting coding structure therefore needs positioning as an application or adaptation unless the prediction-dependent rate is new. [Das and Vishwanath, 2013](https://arxiv.org/abs/1303.3943).

Jacques studies consistent reconstruction from quantized Gaussian projections, including sparse signals, obtaining error decay as the number of measurements increases under a dithered observation model. This is directly relevant to the proposed use of cell geometry. Its assumptions, especially dithering and the measurement model, cannot silently be assigned to the existing undithered Llama records. [Jacques, 2014 preprint](https://arxiv.org/abs/1406.0022). Near-matching sample bounds for one-bit recovery with generative priors also illustrate how developed this area already is. [Liu et al., ICML 2020](https://proceedings.mlr.press/v119/liu20d/liu20d.pdf).

RADAR uses securely stored group signatures and mitigates detected corruption by zeroing groups; this is accuracy recovery, not the same exact-symbol objective. DeepNcode protects quantized networks through redundant encodings. These are relevant for motivation and positioning, but should not substitute for the strongest elementary coding baseline under the paper's own promises. [RADAR](https://arxiv.org/abs/2101.08254), [DeepNcode](https://arxiv.org/abs/2405.13891).

This was a targeted priority check, not an exhaustive systematic survey. I did not find a source in this search establishing precisely the proposed full tradeoff. That does not establish priority. The remaining novelty claim must be checked against the specific theorem and protocol eventually obtained.

**The present experimental result is useful, but cannot carry the main claim.**

The source reports exact recovery of 64 changed BF16 weights in the full output head using 256 retained full-logit predictions and a frozen 3,534-bit certificate. The final scan and recovery demonstrate that the construction can actually be executed at this scale. The source also reports about 9.4 seconds for repair after the head and features are available. Those are meaningful feasibility results.

The reported saving is 434 meaningful bits, or 54 serialized bytes, against a 3,968-bit certificate-only construction. The intact output record occupies 31.3125 MiB. That comparison is meaningful only if those records already exist and the marginal protected-storage budget is the intended resource. It is weak motivation for a system whose purpose is simply to save total storage: the data-free baseline already stores only 496 bytes. A strong paper here should earn its importance through the scientific characterization, rather than presenting 54 bytes as a transformative deployment saving.

The following limitations matter to the paper's central interpretation:

- Only three positive N values are reported, and they describe a development-selected sufficient budget, not an estimated information optimum.
- At the frozen choice of 16 flags for 64 errors, even perfect location flags reduce the check count only from 128 to 112, a 12.5% saving. The observed 10.9% is close to this imposed ceiling. More samples cannot produce an unrestricted information curve while that localization-only configuration stays fixed.
- The localization-only rule cannot go below s field checks when all s locations are known. This is a method-specific floor; the optimum can be zero when the records identify the original.
- Dispersed and concentrated faults differ in how they interact with separate output rows. The failed convex localization in concentrated rows is not an impossibility result.
- The sampled tamper distribution uses selected pools and particular numerical changes. It does not verify an adaptive adversarial guarantee at the reduced budget.
- The reported 30/30 successes per setting, if confirmed by artifacts, support a pilot result; the stated one-sided 95% lower endpoint of approximately 0.905 is correct under independent fixed-pipeline trials.
- Historical test use and source descriptions of debugging mean that a final frozen confirmation should be separate if a confirmatory reliability claim is needed.

These are reasons to change the next scientific measurement, not to run a much larger benchmark grid.

**A concrete stronger baseline deserves one bounded check.**

Here is a conditional construction derived during this review. It is ordinary coding algebra, not a proposed new main contribution. Its value is that it exposes a potentially large baseline gap.

Assume a head with R rows and D columns, labels in `{0,...,65535}`, at most s affected rows, and at most one changed symbol in each affected row. Assume the decoder can obtain a set E containing all affected rows from the retained records, with `|E| <= s`. In ideal rowwise execution, if every changed row changes at least one recorded output code, the mismatch screen supplies exactly that set. The certificate encoder does not need E.

Take a prime `p > max(R,D,65535)` and distinct nonzero row and column locators gamma_r and beta_j. Define the two row summaries

\[
A_r=\sum_j a_{rj}\pmod p,
\qquad B_r=\sum_j\beta_j a_{rj}\pmod p.
\]

Before damage, store

\[
U_k=\sum_r\gamma_r^k A_r\pmod p,
\qquad V_k=\sum_r\gamma_r^k B_r\pmod p,
\quad k=0,\ldots,s-1.
\]

This is 2s field elements for the entire head, rather than two stored checks per row.

After damage, compute the same summaries from the damaged head and subtract. The residual row summaries are zero outside E. For each of A and B, use the first `|E|` equations to solve the known-location Vandermonde system. This recovers `Delta A_r` and `Delta B_r` for each flagged row.

For a truly changed row with corrupted column j and original-minus-damaged label difference d,

\[
\Delta A_r=d\ne0\pmod p,
\qquad \Delta B_r=\beta_j d\pmod p.
\]

Thus `beta_j = Delta B_r / Delta A_r` gives the column, and d gives the original label. A false flagged row has zero residual summaries. Distinct labels have nonzero difference because their absolute difference is below p. This proves exact recovery under the assumptions. All checks were written before the tamper.

For the supplied head, `R=128256`, `D=4096`, and `p=131071=2^17-1` is prime and sufficient. Therefore

\[
L=2s\lceil\log_2p\rceil=2\cdot64\cdot17
=2176\text{ bits}=272\text{ bytes}.
\]

I verified primality and checked this algebra on 100 small randomized finite-symbol instances, obtaining exact recovery in all 100. That validates the construction's arithmetic, not its applicability, speed, or reliability on the Llama records.

The key missing empirical fact is the number of distinct affected rows actually exposed by the retained output codes. The count of 5,934 changed output cells does not answer it. If some affected rows are invisible, the stated 2,176-bit bound does not apply. If there can be several errors per affected row, the two local summaries do not generally suffice. If numerical execution produces false mismatch rows, the set-size condition needs rechecking.

The claim is consequently not that 2,176 bits already beats the existing method on its full tamper class. It is that a simple baseline can beat it under a plausible, explicitly testable event in the dispersed experiment. If dispersed faults are a public promise, competitors should use that promise. Even without that promise, exactly s genuine mismatching rows under an at-most-s scalar-change rule force one error in every such row; this observation alone does not establish a uniform guarantee for other transcripts.

A positive outcome should not start a separate row-code project. Use the baseline to determine which part of the retained predictions actually creates the saving. If the result is simply row localization plus classical checks, the novelty claim should be reduced accordingly.

**One small exact example explains why the rate itself needs investigation.**

This is a sanity model and an elementary derivation, not a proposed ICML contribution. It stays inside finite-parameter, iid-input, protected-certificate recovery and shows that even very simple problems need not have a linear bit-versus-sample law.

Let the only mutable parameter be

\[
\theta_j=(j+1/2)/q,\qquad j=0,\ldots,q-1.
\]

Inputs are iid uniform on `[0,1]`, and the recorded prediction is one bit, `1{theta_j >= X}`. Equivalently, the model has an unknown bias, an intact fixed slope, and records the sign of `theta_j-X`. Allow the single stored parameter to be overwritten by any other allowed value. All originals therefore share a possible damaged checkpoint.

For a fixed input sequence, each transcript is a consecutive block of grid labels between sampled thresholds. Let M_N be the largest number of labels in any such block. Then the smallest budget that works for every transcript is exactly

\[
L_X^{\max}=\lceil\log_2 M_N\rceil.
\]

The lower bound follows because all M_N candidates in the largest block share a transcript and a possible checkpoint. For achievability, the encoder stores the original label's index within its transcript block. The block is known before damage and shared with the decoder. Equivalently, `j mod M_N` works because each block has at most M_N consecutive integer labels. No post-tamper information is used by the encoder.

There are at most N+1 blocks, so deterministically

\[
M_N\geq\left\lceil\frac{q}{N+1}\right\rceil.
\]

If some block contains k grid labels, at least one interval spanning k consecutive labels contains no sample. Such an interval has length `(k-1)/q`. A union bound over its possible starting labels yields

\[
\Pr(M_N\geq k)
\leq(q-k+1)\left(1-\frac{k-1}{q}\right)^N
\leq q e^{-N(k-1)/q},\quad 2\leq k\leq q.
\]

Thus for N>0, with probability at least `1-delta`,

\[
M_N\leq\min\left\{q,
\left\lceil\frac{q}{N}\ln\frac{q}{\delta}\right\rceil\right\}.
\]

In the intermediate regime, these bounds place the bit budget near `log_2(q/N)`, up to an additive logarithmic factor, with truncation at zero. They also give a sufficient zero-bit threshold of `N >= q ln(q/delta)`. The exact finite-sample quantity is the maximum block occupancy, not an extrapolated straight line in N.

The example illustrates two points. First, repeated low-bit predictions on different iid inputs can resolve a much more precise parameter. Second, the simple visibility union bound is not generally a sharp intermediate certificate law. The valuable research question is which geometry controls that law for sparse repair of a head. This scalar example does not answer the high-dimensional case, and a paper containing only this example plus coding would still be too incremental for the stated ambition.

**The one direction I recommend is exact repair using the uncertainty left by actual prediction cells.**

Keep a fixed feature extractor, finite weight alphabet, a public sparse-tamper class, and the existing retained-output convention. Study the remaining uncertainty in both locations and original values as N grows. This is the same question as the original proposal, made operational enough to test.

The immediate diagnostic can be much more exact than the current continuous proposal in rows known to have at most one change. Write z for a damaged row, H for its retained features, and `[l_i,u_i)` for its original output cells. If column j changed by numerical amount v, then

\[
l_i-(Hz)_i\leq H_{ij}v<u_i-(Hz)_i
\quad\text{for every }i.
\]

For each column, intersect these scalar constraints with the magnitude bound, then intersect the resulting interval with the set of allowed original weight values `z_j+v`. Negative features reverse interval inequalities; zero features impose a consistency test. Preserve open endpoints, clipping conventions, and an explicit numerical-error treatment. For BF16, count allowed finite numerical values in the interval rather than pretending its spacing is uniform. Canonicalize or separately account for duplicate numerical labels.

This produces the actual finite candidates under the ideal one-change row model, or a conservatively validated superset when arithmetic bounds are used. It can separate uncertainty about the column from uncertainty about the original value. Computing the intervals costs order ND per row and need not enumerate every possible BF16 value. This makes it a practical diagnostic before investing in a new general decoder.

The diagnostic must not assume away hidden errors in other rows. Its use is justified by an explicit one-per-row model or by a transcript that exhausts the public error budget through genuinely mismatching rows. A whole-head lower bound requires assembling alternatives into valid original heads with the same complete transcript and the same complete damaged head. Do not multiply unrelated row counts if the global tamper promise couples their feasibility.

Three outcomes are scientifically decisive:

1. **Most relevant candidate sets are already singletons.** The current certificate budget largely reflects a decoder limitation. Pursue a simpler exact reconstruction method only if it yields a substantive contribution; do not claim the current plateau is necessary information.
2. **Small but nontrivial candidate sets shrink systematically with N.** This is evidence for the proposed residual-information story. The next theorem should explain their rate of shrinkage, and the next encoder should exploit it with the correct pre-tamper timing.
3. **Large ambiguity persists.** Determine whether it is caused by finite precision, feature coverage, or combinations of sparse changes. A converse then has a realistic target. Persisting ambiguity caused solely by signed zero or a deliberately unobserved coordinate is a useful edge case, but not enough novelty by itself.

A promising eventual result would give upper and lower bounds with the same leading N-dependence for a nontrivial sparse linear-head family, under explicit assumptions on the inputs and quantizer, and a concrete construction that captures that benefit. The theorem need not characterize arbitrary neural networks or every BF16 Llama head. A clean theoretical model with carefully bounded real-head evidence can be enough for a strong paper. However, the new result must do more than attach familiar coding to a familiar recovery theorem without resolving a meaningful interaction between them.

The main technical risk is real: finite candidate sets can still be computationally enormous for several errors in the same row. A useful information bound does not imply efficient list generation, and local lists do not automatically give an optimal global pre-tamper certificate. This is why I recommend an exact one-row diagnostic first, rather than promising an efficient minimax decoder for arbitrary sparse neural changes.

**Use a finite sequence of decisions, not an expanding wish list.**

| Stage | Concrete output | Proceed only if |
|---|---|---|
| 1. Freeze the scientific protocol | One page specifying original class, N, records, tamper promise, exact target, and quantifiers. | It matches both the motivating question and the intended experiment. |
| 2. Audit the existing record information | Affected-row visibility, exact or certified candidate counts in the simple subcase, and the conditional row-code comparison. | There is useful unresolved structure beyond the present heuristic's failures. |
| 3. Attempt one core theorem | A quantitative N-dependent converse and construction in the same meaningful sparse-head setting, or another comparably substantive resolution of the central tradeoff. | The result adds insight beyond existing sketching and quantized recovery results. |
| 4. Run one focused validation | One N-versus-bits figure with strong comparable baselines, the mechanism diagnostic, and a frozen reliability check. | The real-head evidence supports the mechanism rather than contradicting it. |
| 5. Write and stop | A compact paper centered on the question and the new result. | Claims, assumptions, and evidence align. Additional breadth is unnecessary. |

Do not require both an optimal efficient decoder for arbitrary neural networks and a sharp Llama-specific minimax lower bound. That would make the project unnecessarily risky. Do require one genuinely informative result about the sample–certificate tradeoff. A proof of the current locator's performance could contribute, but merely proving it finds a few flags under restrictive conditions is unlikely by itself to satisfy the requested novelty bar.

If stage 2 shows that ordinary row information and known coding explain essentially all the saving, and stage 3 yields only another loose survival bound, stop treating this as a likely exceptional ICML submission. The correct response would be a narrower paper or a decision to stop, rather than accumulating experiments and terminology.

If stage 3 succeeds and stage 4 supports it, stop adding results. A sharp central theorem, a credible construction, and one convincing real-model demonstration tell a complete story. Nonzero behavioral tolerance, backbone tampering, active probe selection, privacy, languages, multiple model scales, and a precision sweep are not prerequisites.

**The manuscript can be short in concept even when its proofs are detailed.**

A suitable working title is *How Many Protected Bits Does Model Repair Need?* The first page should define the resources with one simple example and state what the eventual theorem actually establishes. Then give the rate and its assumptions, explain the construction, and use experiments to test the mechanism. Put the general graph characterization, detailed coding derivation, numerical caveats, and archival evidence inventory in appendices as appropriate. Remove the behavior-sensitive branch from this exact-recovery manuscript.

The central figure should eventually put N on the horizontal axis and protected bits on the vertical axis, with the data-free baseline, the strongest prediction-assisted baseline, the proposed achieved budget, and valid bounds where available. Theory and empirical reliability curves must be labeled separately. A small companion diagnostic showing remaining candidate counts or unresolved value precision would explain why the curve moves. Do not use successful solver convergence or support recall alone as a proxy for information necessity.

The strongest claim supportable today remains narrower: retained full-logit predictions supplied useful location hints in controlled dispersed faults, enabling a lower sufficient certificate budget for a classical exact decoder. That claim is honest, but the source file's own cautious assessment of its novelty is broadly correct.

**Only a small slice of the code is needed next.**

The useful material is the retained-logit quantizer and cache convention; the tamper generator and its public promises; the row mismatch screen and candidate-selection rule; and the per-trial results table with frozen budgets and seeds. For the new diagnostic, a compact sanitized example containing damaged rows, retained hidden vectors, output codes, and public numerical settings would be especially valuable. The original and true support may be retained separately for evaluation but must not be inputs to reconstruction.

There is no need to upload the entire codebase now. The immediate question is what the records already reveal, not whether the existing full-head scan can be made faster. That evidence can make the next research decision much more grounded without starting another large implementation effort.
