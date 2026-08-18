# Data-Aware Achievability (§13.1), Derived

*Working note. Companion to `repair_budget_standalone.md`. Numerics in `scratchpad/`.*

---

## 0. The obstruction, stated exactly

Reed–Solomon corrects a sparse error because **sparsity and the code live in the same basis**: coordinates are polynomial evaluations, and "few coordinates wrong" is what an MDS code is built to see. The trusted set contributes a constraint of a completely different type — `‖Φ_D v‖_∞ ≤ 2γ` — which is a **rotationally arbitrary** condition. Whitening it means applying `Φ_{D,S}^{-1}`, and rotation destroys sparsity. There is no basis in which both structures are simultaneously natural.

The naive reading of §13.1 ("shorten the code using `row(Φ_D)`") cannot work: shortening deletes coordinates the decoder already knows, and the decoder does not know any *coordinate* of `e`. It knows some *linear functionals* of `e`, in general position with respect to the coordinate basis.

**The resolution is not to marry them.** It is to notice that the geometry, once digested, exposes exactly two objects that live in the coordinate basis — *which* coordinates can hide a harmful change, and *how far* each one can move — and that an algebraic code consumes precisely those two objects. The geometry is solved offline, by the encoder, which knows `Φ_D`; the algebra runs on its output. The interface between them is coordinate-basis, so nothing rotates.

Everything below makes that precise. §5 then shows the part the interface *does* throw away — orientation — is second-order for real feature geometry, and says what buys it back when it is not.

---

## 1. Notation

Fix `s, ρ, γ, ε`, and write `d_P(a,b)² = (a−b)ᵀΣ(a−b)`. Two invisible sets:

```
V⁻ = { v : ‖v‖₀ ≤  s, ‖v‖_∞ ≤  ρ, ‖Φ_D v‖_∞ ≤ 2γ }      (converse)
V⁺ = { v : ‖v‖₀ ≤ 2s, ‖v‖_∞ ≤ 2ρ, ‖Φ_D v‖_∞ ≤ 2γ }      (achievability)
```

`V⁺` is the right object for achievability: given `(D, c̃)`, any two candidates differ by
`(c̃−c′) − (c̃−c″)`, which is `2s`-sparse and `2ρ`-bounded. **The standalone document uses `V⁻` for both, which is why Theorem 5.4's positive direction does not follow** (flagged separately in `REVIEW.md`).

Write `Σ̂_D = Φ_DᵀΦ_D / N`, and `A(D) = sup_{v∈V} ‖Σ^{1/2}v‖₂` (the radius of the invisible set).

---

## 2. Theorem 1 — the repair budget is a chromatic number

This is the exact characterisation. It replaces the sandwich of Theorems 5.4 / 7.1 / 8.1 with one object.

> **Theorem 1.** Let `G_D(ε)` be the graph on `Θ` with `c′ ~ c″` iff `c″−c′ ∈ V⁺` and `d_P(c′,c″) > 2√ε`. Then a deterministic `L`-bit certificate scheme repairing to `ε` exists iff `G_D(ε)` is `2^L`-colourable, so
> ```
> L*_D(ε) = ⌈ log₂ χ(G_D(ε)) ⌉.
> ```

*Proof.* (≥) A certificate is a map `κ : Θ → {0,1}^L`. If `κ(c′) = κ(c″)` for an edge, the decoder sees identical `(D, c̃, κ)` in both worlds and must land within `√ε` of both, contradicting `d_P > 2√ε`. So `κ` is a proper colouring. (≤) Given a proper colouring, the decoder returns any candidate carrying the received colour; all same-coloured candidates in its uncertainty set are non-adjacent, hence within `2√ε`. ∎

This is Witsenhausen's zero-error-source-coding-with-side-information framework — cited in §11.1 of the standalone document and then never used. Using it collapses the theory:

| standalone result | becomes |
|---|---|
| Thm 5.4 (zero bits) | `χ = 1` ⟺ `G` has no edges ⟺ `diam_{d_P}(V⁺) ≤ 2√ε` |
| Thm 7.1 (converse) | `χ ≥ ω`; a `d_P`-packing of `V⁻` is a clique |
| Thm 8.1 (ceiling) | `χ ≤ Δ+1 ≤ |V⁺ ∩ grid|`; drop the `Φ_D` constraint → `C(h,2s)·(4ρ/Δ)^{2s}` |

So the four theorems are one statement read at three resolutions, and the slogan sharpens:

> **Detection is governed by the *radius* of the invisible set. Repair is governed by its *entropy*.**

The detect / localise / repair ladder of §9 stops being a table of separate claims and becomes a factorisation of one quantity:

```
log₂ N(V⁺, d_P, √ε)   ≈   log₂ |S*(D)|   +   max_{S ∈ S*} log₂ N(E_S, d_P, √ε)
    repair                  localise                  amplitude
```

**Caveat, load-bearing.** A clique requires *pairwise* differences in `V⁺`. Points on supports `S₁, S₂` with `|S₁ ∪ S₂| > 2s` are **not** confusable. So the converse is a max over supports and the covering bound is a sum: the localisation term is exactly the max-to-sum gap, and a converse that sums over supports is wrong. My first numerical pass made this error.

---

## 3. Theorem 2 — where ambiguity actually comes from

Before constructing anything, it is worth knowing what makes `A(D)` large. Two lines suffice, and they need **no assumption at all** — in particular they replace Assumption SB(κ,τ) and Theorem 6.1.

> **Theorem 2 (ambiguity decomposition).** For every `D`,
> ```
> A(D)²  ≤  4γ²  +  sup_{v ∈ V⁺} vᵀ(Σ − Σ̂_D) v   ≤   4γ²  +  8sρ² · δ_{2s}(D),
> ```
> where `δ_{2s}(D) = sup{ |uᵀ(Σ − Σ̂_D)u| : ‖u‖₀ ≤ 2s, ‖u‖₂ = 1 }`.

*Proof.* `vᵀΣv = vᵀΣ̂_D v + vᵀ(Σ−Σ̂_D)v`, and `vᵀΣ̂_D v = ‖Φ_D v‖₂²/N ≤ ‖Φ_D v‖_∞² ≤ 4γ²`. ∎

Read it:

> **A sparse change can hide from your trusted set for exactly two reasons: your labels are too coarse to see it (`γ`), or your probes have not visited the inputs on which it acts (`δ_{2s}`). Nothing else contributes.**

Consequences worth having:

- It converts the sample-complexity question into **restricted covariance estimation**, which is standard and has known rates under stated tail conditions — instead of an opaque `κ, τ` whose values nobody can report. `τ⁻²` in Theorem 6.1 is exactly the price of estimating `Σ` along a direction active on a `τ`-fraction of inputs.
- Both terms are **directly measurable** on a real model. `δ_{2s}` is the interesting one and nobody has plotted it.
- The second bound's constant is crude (numerically loose by ~10²; the `‖v‖₂² ≤ 8sρ²` step is the culprit). The *structure* is the contribution; the sharp version should bound `‖v‖₂` by the invisible set's own radius and is self-improving.

---

## 4. Theorem 3 — DARC, the explicit data-aware code

### 4.1 The two objects the geometry hands to the algebra

**(i) Fragility of a coordinate.** Let `α_j = sup{ |v_j| : v ∈ V⁺ }` — how far coordinate `j` can move invisibly. Define

```
                α_j · √Σ_jj
       φ_j  =  ─────────────
                    √ε
```

> `φ_j` is how far weight `j` can drift without your evaluations noticing, measured in units of how much you would care.

Both factors are essential and the standalone document's uniform `Δ` misses this: a coordinate that is totally unconstrained (`α_j = 2ρ`) but functionally irrelevant (`Σ_jj` tiny) costs **nothing**, and a uniform quantiser step pays for it anyway. In my sweep this alone was the difference between a bound stuck at the data-free value and one that decays.

**(ii) Fragile coordinates — a hitting set, not a union.** Let `F` be the family of *minimal* supports of vectors `v ∈ V⁺` with `d_P(v) > √ε`. Then

```
   J*(D)  =  any hitting set of F   (J* ∩ S ≠ ∅  for every S ∈ F)
```

This is the step that makes the construction work, and I got it wrong first. The decoder's proof obligation is: *every residual `w ∈ V⁺` with `w|_{J*} = 0` is safe.* Since `supp(w) ∩ J* = ∅`, it suffices that `J*` **hits** every dangerous support — not that it **contains** them. In the numerics the union gave `|J*| = h = 44` (every coordinate, because every *pair* containing one fragile coordinate inherits its danger) while the hitting set gave `|J*| = 2`. That is the difference between a vacuous bound and a useful one.

Two readings, both practically meaningful:
- an **isolated** fragile coordinate must be protected itself;
- of a **near-collinear cluster** whose joint direction is fragile, protecting **any one member** suffices — pinning one coordinate leaves the other individually visible.

Minimum hitting set is NP-hard, but **any hitting set is sound**, and greedy gives a `log`-approximation; looseness costs certificate length, never correctness. Same for `α_j` and `J*`: **only upper bounds are needed**, so convex relaxations are legitimate. This matters — it is what makes the scheme implementable given that `A(D)` itself is NP-hard.

### 4.2 The code

Per-coordinate quantiser step and alphabet:

```
   Δ_j = √ε / (s √Σ_jj)          M_j = ⌈ α_j / Δ_j ⌉ + 3   ( ≈ s·φ_j + 3 )
```

**Encoder** (pre-attack; knows `c`, `D`): `k_j(c) = ⌊(c_j+B)/Δ_j⌋`; `y_j = k_j(c) mod M_j` for `j ∈ J*`;
`κ = RS_{2s}( y|_{J*} )` over `F_Q`, `Q ≥ max{ |J*|, max_j M_j }` — or store `y|_{J*}` outright when `|J*| ≤ 2s`.

**Decoder** (sees `D`, `c̃`, `κ`):
1. `ỹ_j = k_j(c̃) mod M_j` for `j ∈ J*`. Unattacked coordinates are bit-identical, so `d_H(ỹ, y) ≤ s`; Berlekamp–Massey returns `y|_{J*}`.
2. Return any `ĉ = c̃ − ê` with `‖ê‖₀ ≤ s`, `‖ê‖_∞ ≤ ρ`, `‖Φ_D ĉ − y_D‖_∞ ≤ γ`, and `k_j(ĉ) ≡ y_j (mod M_j)` for all `j ∈ J*`.

> **Theorem 3.** With `V⁺` defined at inflated precision `2γ + η_Δ`, `η_Δ = max_{|T|≤2s} max_i Σ_{j∈T} Δ_j|Φ_ij|`,
> ```
> L*_D(ε)  ≤  min{  Σ_{j∈J*} ⌈log₂ M_j⌉ ,   2s ⌈ log₂ max{ |J*|, max_{j∈J*} M_j } ⌉  }
> ```
> and the decoder's output satisfies `d_P(ĉ, c) ≤ 3√ε`. Encoder and decoder run in `Õ(h)` plus one `s`-sparse recovery solve on `Φ_D`.

*Proof.* The truth is a candidate, so step 2 is non-empty. Let `ĉ` be any candidate and `w = c − ĉ ∈ V⁺`. For `j ∈ J*`: `k_j(c) ≡ k_j(ĉ) (mod M_j)` and `|k_j(c) − k_j(ĉ)| ≤ α_j/Δ_j + 1 < M_j`, so the cell indices are **equal** and `|w_j| ≤ Δ_j`. Split `w = w′ + w″`, `w′` on `J*` with `|w′_j| ≤ Δ_j`, `w″` off `J*`. Then `d_P(w′) ≤ Σ_{j∈supp(w′)} Δ_j√Σ_jj ≤ 2s·√ε/s = 2√ε`. And `w″ ∈ V⁺` (the `η_Δ` inflation absorbs `Φ_D w′`) with `supp(w″) ∩ J* = ∅`, so by the hitting-set property `w″` is not dangerous: `d_P(w″) ≤ √ε`. ∎

**Degenerate cases.** `J* = ∅` gives `L = 0`, recovering Theorem 5.4. `J* = [h]` with `α_j = 2ρ` gives `2s⌈log₂ max{h, 2ρ/Δ+3}⌉` — Theorem 8.1. **Theorem 3 interpolates between them and is never worse than either.**

---

## 5. Why the marriage works — and what it still throws away

The interface `(J*, {α_j})` is coordinate-basis by construction, so the algebraic code consumes it without rotating anything. Stated as a principle:

> **A syndrome code can adapt to the invisible set's coordinate *widths* — that keeps the basis in which sparsity is defined. It cannot adapt to its *orientation*, because whitening rotates. The obstruction is rotational, not algebraic.**

So Theorem 3 pays for the **bounding box** of `E_S` where the entropy target is its **volume**. The loss is the *isotropy defect* `∏_j α_j(S) / ∏_i a_i(S) ≥ 1` — computable, and exactly the price of the mismatch.

**But that defect is second-order for real feature geometry, and Theorem 2 says why.** A rotated quiet direction of `Φ_D` — a near-collinear cluster — is also nearly null for `Σ`, because `Σ ≈ Σ̂_D` on directions many samples exercise. Quiet *and* harmless contributes nothing to `A(D)`. Danger requires `vᵀ(Σ−Σ̂_D)v` large, i.e. an input mode the probes have **not** visited — and that is a *coordinate-aligned*, rare-mode phenomenon, not a rotational one.

I checked this rather than assuming it. Forcing near-duplicate feature pairs (correlation up to `1−2×10⁻³`) and measuring the invisible set exactly:

```
 δ (pair separation)   A(pair)   A(coord 0 alone)   gain from pairing
      0.20              0.079         0.062              1.3×
      0.05              0.078         0.058              1.3×
      0.01              0.068         0.065              1.0×
      0.002             0.071         0.071              1.0×
```

**Near-collinearity contributes essentially nothing.** The `ℓ_∞` cap binds first, and the direction it permits is functionally null. The dangerous invisible directions were, in every configuration I ran, single rarely-exercised coordinates. This is a load-bearing empirical claim and belongs in the paper as a measurement, not an assumption — it is also the same tail phenomenon flagged in `REVIEW.md` §4.

---

## 6. The two dialects — and the bridge to behaviour-vs-parameters

The certificate is *any* function of `(c, D)`, so it has a second dialect nobody has used: **extra mantissa bits on trusted labels.** The encoder knows `c` and `x_i`, so it can compute `f_c(x_i)` exactly and store refinement bits. Refining `|I|` labels from `γ` to `γ′` costs `|I|·log₂(γ/γ′)` and *shrinks `V⁺` itself*.

The two dialects are structurally different, and that is the interesting part:

| | buys | cannot buy |
|---|---|---|
| **Parity bits** (RS on `J*`) | *location* — `2s` symbols carry `s log h` bits of support | orientation (sparsity is basis-locked) |
| **Label bits** (refine `y_i`) | *orientation* — each adds a halfspace at arbitrary tilt, reshaping `E_S` | location (real sketches need `s log(h/s)` measurements, not `2s` symbols) |

So the optimal certificate is a **mixture**, and the split is computable from `Φ_D` offline:

```
L*_D(ε)  ≤  min over (I, γ′)  [  |I|·log₂(γ/γ′)  +  L_DARC( V⁺ refined at γ′ )  ]
```

Per unit of amplitude resolution the two are priced roughly **1:1** (refining the `d*` labels that matter buys `d*` bits of amplitude). They are not interchangeable in *kind*. This is the same behaviour-vs-parameter exchange from `REVIEW.md` §5, now with a mechanism instead of a slogan — and it is a much better home for §13.1 than "shorten the code".

---

## 7. What the numerics established

`h = 44` (32 common + 12 rare-mode coordinates, activation rates `0.5 → 1.2×10⁻⁴`, plus 6 near-duplicate pairs), `s = 1`, `ρ = 0.5`, `γ = 0.1`, `√ε = 0.141`. Invisible set computed **exactly** by halfspace intersection over all `C(44,2)` supports.

```
     N    A(D)   #isolated  #pairs  |J*|          J*        L_DARC   L_free
     4   1.273       24       104     36     [0,...,40]        12       12
    16   0.636        6       264     28     [2,...,40]        10       12
    32   0.300        2       109     16     [0,...,40]         8       12
    64   0.300        2         0      2       [38, 39]         4       12
   256   0.181        1         0      1           [39]         2       12
  1024   0.141        0         0      0             []         0       12
```

1. **Graceful degradation**: `12 → 10 → 8 → 4 → 2 → 0` bits, against a data-free ceiling pinned at 12. The standalone document's Theorem 8.1 pays the full price at every `N`.
2. **`J*` is interpretable**: it converges to exactly the coordinates whose input mode the probes have not yet hit.
3. **The codec is correct end to end.** Under adversarial evaluation — attacker plays the `A(D)`-maximiser, decoder returns the *worst* consistent candidate — the certificate cuts worst-case `d_P` from `0.367` to `0.257` at `N = 64,128`. Residual error tracks the quantiser cell width, as Theorem 3 predicts.
4. The observed constant is `≈ 1.8 √ε`, consistent with the `s→2s`, `ρ→2ρ` conservatism — the factor-of-4 slack the standalone document already declines to remove.

---

## 8. Honest status

**Settled.** Theorem 1 (exact characterisation, and the collapse of four theorems into one). Theorem 2 (decomposition, assumption-free, replaces SB/Thm 6.1). Theorem 3 (explicit, efficiently decodable, interpolating data-aware code) — the answer to §13.1. The hitting-set formulation. The `φ_j` fragility index. The rotational-obstruction principle. All numerically validated at `s = 1`.

**Not settled.**
- `s ≥ 2` numerics. The geometry code enumerates `2`-supports exhaustively; `s ≥ 2` needs the convex relaxation for `α_j` and greedy support search. No reason to expect a different conclusion, but it is unverified and should not be claimed.
- The exact chromatic number between `ω` and `Δ+1`. Theorem 3 sits strictly inside the sandwich; how far from `χ` is open.
- Theorem 2's constant (loose by ~10²).
- The hybrid optimisation of §6 is stated, not solved.
- Everything here assumes unattacked coordinates are **bit-exact**. Under benign drift the RS layer fails at cell boundaries — the same brittleness `REVIEW.md` §3.4 flags in Theorem 8.1. Dithered or nested-lattice quantisation is the fix and is not written down.
