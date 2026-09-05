# Data-Aware Achievability — A Clean Derivation

*Replaces §13.1 of `repair_budget_standalone.md`. Numerics in `scratchpad/` (unversioned).*

---

## 0. The question, and why the obvious route fails

§8 gives a ceiling that ignores `D` entirely. §13.1 asks for a matching upper bound that *uses* the trusted set, degrading to zero as `D` becomes informative. Its own suggestion — "shorten the code using `row(Φ_D)`" — cannot work, and the reason is worth stating precisely because it shapes everything below.

Reed–Solomon corrects a sparse error because **sparsity and the code live in the same basis**: coordinates are polynomial evaluations, and "few coordinates wrong" is exactly what an MDS code sees. The trusted set contributes a constraint of a different type, `‖Φ_D v‖_∞ ≤ 2γ`, which is **rotationally arbitrary**. Whitening it means applying `Φ_{D,S}^{-1}`, and rotation destroys sparsity. Shortening, meanwhile, deletes coordinates the decoder already knows — but the decoder knows no *coordinate* of `e`, only some *linear functionals* of it, in general position with respect to the coordinate basis.

The resolution is not to reconcile the two structures inside one code. It is:

> **The encoder solves the geometry offline — it knows `Φ_D` — and hands the algebraic code two objects that live in the coordinate basis: which coordinates must be protected, and how far each can move. Nothing rotates, because orientation is never encoded. It is destroyed.**

§7 makes the last clause precise; §9 shows it holds against deliberately planted rotated adversaries.

---

## 1. Setup

Fix `s, ρ, γ, ε`; write `d_P(a,b)² = (a−b)ᵀΣ(a−b)` and `Σ̂_D = Φ_DᵀΦ_D/N`. Two invisible sets:

```
V⁻ = { v : ‖v‖₀ ≤  s, ‖v‖_∞ ≤  ρ, ‖Φ_D v‖_∞ ≤ 2γ }      (converse)
V⁺ = { v : ‖v‖₀ ≤ 2s, ‖v‖_∞ ≤ 2ρ, ‖Φ_D v‖_∞ ≤ 2γ }      (achievability)
```

`V⁺` is the correct achievability object: given `(D, c̃)`, two candidates differ by `(c̃−c′) − (c̃−c″)`, which is `2s`-sparse and `2ρ`-bounded. **The standalone document uses the `s`-sparse set for both, which is why Theorem 5.4's positive direction does not follow as stated.** Write `A(D) = sup_{v ∈ V} ‖Σ^{1/2}v‖₂` for the radius, and call `v` *dangerous* if `‖Σ^{1/2}v‖₂ > √ε`.

---

## 2. Theorem 1 — the repair budget is a chromatic number

> **Theorem 1.** Let `G_D(ε)` be the graph on `Θ` with `c′ ~ c″` iff `c″−c′ ∈ V⁺` and `d_P(c′,c″) > 2√ε`. A deterministic `L`-bit certificate repairing to `ε` exists iff `G_D(ε)` is `2^L`-colourable:
> ```
> L*_D(ε) = ⌈ log₂ χ(G_D(ε)) ⌉.
> ```

*Proof.* (≥) If `κ(c′) = κ(c″)` on an edge, the decoder sees identical `(D, c̃, κ)` in both worlds and must land within `√ε` of both, contradicting `d_P > 2√ε`. So `κ` is a proper colouring. (≤) Given a proper colouring, the decoder returns any candidate carrying the received colour; same-coloured candidates in its uncertainty set are non-adjacent, hence within `2√ε`. ∎

This is Witsenhausen's zero-error-source-coding-with-side-information framework — cited in §11.1 and then never used. Using it collapses the theory:

| standalone result | becomes |
|---|---|
| Thm 5.4 (zero bits) | `χ = 1` ⟺ `G` has no edges ⟺ `diam_{d_P}(V⁺) ≤ 2√ε` |
| Thm 7.1 (converse) | `χ ≥ ω`; a `d_P`-packing of `V⁻` is a clique |
| Thm 8.1 (ceiling) | `χ ≤ Δ+1`; drop the `Φ_D` constraint → `C(h,2s)(4ρ/Δ)^{2s}` |

Four theorems are one statement at three resolutions, and the slogan sharpens:

> **Detection is governed by the *radius* of the invisible set. Repair is governed by its *chromatic number*.**

The detect / localise / repair ladder of §9 stops being a table of separate claims and becomes a factorisation of one quantity.

**Caveat, load-bearing.** A clique needs *pairwise* differences in `V⁺`. Points on supports with `|S₁ ∪ S₂| > 2s` are **not** confusable, so the converse is a max over supports while the covering bound is a sum. A converse that sums over supports is wrong. My first pass made this error.

---

## 3. Theorem 2 — where ambiguity comes from, and a screen

Two lines, **no assumptions** — this replaces Assumption SB and Theorem 6.1 entirely.

> **Theorem 2.** For every `D`,
> ```
> A(D)²  ≤  4γ²  +  sup_{v ∈ V⁺} vᵀ(Σ − Σ̂_D) v.
> ```

*Proof.* `vᵀΣv = vᵀΣ̂_D v + vᵀ(Σ−Σ̂_D)v`, and `vᵀΣ̂_D v = ‖Φ_D v‖₂²/N ≤ ‖Φ_D v‖_∞² ≤ 4γ²`. ∎

> **A sparse change hides from your trusted set for exactly two reasons: your labels are too coarse to see it (`γ`), or your probes have not visited the inputs on which it acts (`Σ ≠ Σ̂_D` on sparse directions). Nothing else contributes.**

Consequences:

- Sample complexity becomes **restricted covariance estimation** — standard, with known rates under stated tail conditions — instead of an opaque `(κ, τ)` nobody can report. The `τ⁻²` of Theorem 6.1 is the price of estimating `Σ` along a direction active on a `τ`-fraction of inputs.
- Both terms are **measurable** on a real model.
- **It is also a computational screen.** For a support `S`, with `‖v‖₂ ≤ min(2ρ√|S|, 2γ/√λ_min(Σ̂_SS))`,
  ```
  A_S ≤ min{ √λ_max(Σ_SS)·‖v‖₂ ,  √(4γ² + dev_S·‖v‖₂²) },   dev_S = ‖Σ_SS − Σ̂_SS‖.
  ```
  Both bounds cost one small eigendecomposition and are **sound**, so any support failing the screen can be discarded without ever solving the NP-hard problem. The two are complementary: the second wins when `Σ̂ ≈ Σ`, the first when `λ_min(Σ̂_SS)` is large. Measured pruning: **45–80%** of supports.

---

## 4. Three data-derived quantities

**(i) Invisible width.** `α_j = sup{ |v_j| : v ∈ V⁺ }` — how far coordinate `j` can move invisibly.

**(ii) Fragility.**
```
              α_j · √Σ_jj
     φ_j  =  ─────────────
                  √ε
```
> How far weight `j` can drift without your evaluations noticing, measured in units of how much you would care.

Both factors are essential. A coordinate that is wholly unconstrained (`α_j = 2ρ`) but functionally irrelevant (`Σ_jj` tiny) costs **nothing**, and the standalone document's uniform quantiser step `Δ` pays for it anyway. In the `s=1` sweep this alone separated a bound stuck at the data-free value from one that decays.

**(iii) Fragile coordinates — a hitting set, not a union.** Let `F` be the family of *minimal* supports of dangerous `v ∈ V⁺`. Then
```
   J*(D) = any hitting set of F        (J* ∩ S ≠ ∅ for every S ∈ F)
```

This is the move that makes the construction work. The decoder's proof obligation is: *every residual `w ∈ V⁺` with `w|_{J*} = 0` is safe*. Since `supp(w) ∩ J* = ∅`, it suffices that `J*` **hits** every dangerous support — not that it **contains** them. Numerically the union gave `|J*| = 44` (every coordinate, because every pair containing one fragile coordinate inherits its danger); the hitting set gave `|J*| = 2`. Vacuous versus useful.

Set `Δ_j = 2√ε/(2s·√Σ_jj)` and `M_j = ⌈α_j/Δ_j⌉ + 3` (so `M_j ≍ s·φ_j`).

---

## 5. Theorem 3 — DARC, the achievability

**Encoder** (pre-attack; knows `c`, `D`): `k_j(c) = ⌊(c_j+B)/Δ_j⌋`; `y_j = k_j(c) mod M_j` for `j ∈ J*`;
`κ = RS_{2s}(y|_{J*})` over `F_Q`, `Q ≥ max{|J*|, max_j M_j}` — or store `y|_{J*}` outright if that is shorter.

**Decoder** (sees `D`, `c̃`, `κ`):
1. `ỹ_j = k_j(c̃) mod M_j` for `j ∈ J*`. Unattacked coordinates are bit-identical, so `d_H(ỹ,y) ≤ s`; Berlekamp–Massey returns `y|_{J*}`.
2. Return any `ĉ = c̃ − ê` with `‖ê‖₀ ≤ s`, `‖ê‖_∞ ≤ ρ`, `‖Φ_D ĉ − y_D‖_∞ ≤ γ`, and `k_j(ĉ) ≡ y_j (mod M_j)` for all `j ∈ J*`.

> **Theorem 3.** With `V⁺` taken at inflated precision `2γ + η_Δ`, `η_Δ = max_{|T|≤2s} max_i Σ_{j∈T} Δ_j|Φ_ij|`,
> ```
> L*_D(ε) ≤ min{ Σ_{j∈J*} ⌈log₂ M_j⌉ ,  2s⌈ log₂ max{ |J*|, max_{j∈J*} M_j } ⌉ }
> ```
> and `d_P(ĉ,c) ≤ 3√ε`. Encoder and decoder run in `Õ(h)` plus one `s`-sparse recovery solve.

*Proof.* The truth is a candidate, so step 2 is non-empty. Let `ĉ` be any candidate, `w = c − ĉ ∈ V⁺`. For `j ∈ J*`: `k_j(c) ≡ k_j(ĉ) (mod M_j)` and `|k_j(c) − k_j(ĉ)| ≤ α_j/Δ_j + 1 < M_j`, so the cell indices are **equal** and `|w_j| ≤ Δ_j`. Split `w = w′ + w″` with `w′` on `J*`, `w″` off it. Then `d_P(w′) ≤ Σ_{j ∈ supp(w′)} Δ_j√Σ_jj ≤ 2s·(2√ε/2s) = 2√ε`. And `w″ ∈ V⁺` (the `η_Δ` inflation absorbs `Φ_D w′`) with `supp(w″) ∩ J* = ∅`, so by the hitting-set property `w″` is not dangerous: `d_P(w″) ≤ √ε`. ∎

**Extremes.** `J* = ∅` gives `L = 0` (Theorem 5.4). `J* = [h]`, `α_j = 2ρ` gives Theorem 8.1. **Theorem 3 interpolates and is never worse than either.**

---

## 6. Theorem 4 — a converse in the same quantities

Achievability alone would not close §13.1; the bound has to be shown near-optimal.

> **Theorem 4.** Suppose `D` admits `m` pairwise disjoint *singleton* minimal dangerous supports `{j₁},…,{j_m}`, each carrying `n ≥ 2` perturbations pairwise `d_P`-separated by more than `2√ε`, whose `2s`-sparse combinations remain in `V⁺`. Then
> ```
> L*_D(ε) ≥ log₂ [ Σ_{i≤s} C(m,i)(n−1)^i ]  ≥  s·log₂(n−1) + s·log₂(m/s).
> ```

*Proof.* The candidates `c + Σ_i v_i^{(t_i)}`, `t ∈ [n]^m`, are mutually confusable whenever their Hamming distance is at most `2s`. By Theorem 1 a certificate is a proper colouring, so every colour class is a code of length `m`, alphabet `n`, minimum distance `> 2s`. The Hamming bound caps each class at `n^m / Σ_{i≤s}C(m,i)(n−1)^i`, so at least that many classes are needed. ∎

Since `n ≍ φ/2`, converse and achievability are in the **same two quantities** — the number of fragile coordinates and their fragility:

```
   s·log₂ φ + s·log₂(m/s)     ≤   L*_D(ε)   ≤   2s·log₂ max{ |J*|, s·φ_max }
              converse                                    DARC
```

**DARC is within a factor 2 of optimal whenever the fragile coordinates are individually wide (`φ ≳ |J*|`).** When `φ < |J*|` the residual gap is exactly the classical alphabet-versus-length gap: Reed–Solomon requires `Q ≥ n`, and for small alphabets algebraic-geometry or BCH codes beat it. That is a known coding-theoretic gap, not a defect of the reduction — which is the right place for §13.1's difficulty to end up.

---

## 7. Why the marriage works: orientation is broken, not encoded

Theorem 3 pays for the **bounding box** of the invisible set where the entropy target is its **volume**, so it appears to throw away orientation. Last revision I argued this was second-order because quiet directions of `Φ_D` are also functionally null. **That argument was incomplete, and the `s=2` experiment refutes it as stated.**

Genuinely rotated dangerous directions *do* exist. Construct coordinates whose feature columns satisfy a linear relation `C_G λ = 0` exactly on the commonly-seen inputs, broken only on a rare mode. Then `v = λ` is perfectly invisible while `λᵀΣλ > 0`, and every individual coordinate is loudly exercised, hence safe alone. Planting two such traps — `{13,14}` with `λ=(1,−1)` and `{15,16,17}` with `λ=(1,1,−1)` — the exact geometry finds them as *minimal* dangerous supports of size 2 and 3.

But they cost nothing, and the reason is the hitting set:

```
trap [13,14]:      A = 0.3771  DANGEROUS        (threshold √ε = 0.1414)
  pin 13 → [14]:   A = 0.0251  safe
  pin 14 → [13]:   A = 0.0251  safe
trap [15,16,17]:   A = 0.4629  DANGEROUS
  pin 15 → [16,17]: A = 0.0261  safe
  pin 16 → [15,17]: A = 0.0256  safe
  pin 17 → [15,16]: A = 0.0270  safe
```

Pinning **any one** coordinate collapses the ambiguity by 15–18×, far below tolerance. So:

> **A rotated invisible direction needs all of its coordinates free. Fix any one and the direction ceases to exist — the remaining slice is no longer in the kernel, so the data sees it. Orientation therefore never has to be represented; it only has to be broken, and breaking it is a combinatorial act in the coordinate basis.**

This is the actual answer to the algebra/geometry problem. The interface `(J*, {α_j})` is coordinate-basis not because the geometry is conveniently axis-aligned — it is not — but because *hitting* a rotated structure is cheaper than *describing* it. A `k`-coordinate rotated trap costs one protected coordinate, not `k`, and not a rotation.

---

## 8. Computing everything

`A(D)` is NP-hard (sparse generalised eigenvalue), so a construction that needed it exactly would be vacuous. It does not:

**Only sound upper bounds are required.** A larger `α_j`, a larger `J*`, a hitting set that is not minimum — each inflates certificate length and none breaks correctness. So relaxations are legitimate throughout.

- **`α_j` without support enumeration.** Relax `‖v‖₀ ≤ 2s` to `‖v‖₁ ≤ 4sρ`: one LP per coordinate, `h` LPs total. Measured against exact enumeration over all `C(18,≤4)` supports: `α` ratio **1.00–1.46**, and after the `⌈log₂ M_j⌉` rounding the cost is **0–2% of certificate bits**, at **80–190× lower** cost (0.5 s versus 41–78 s).
- **Fragility screening** by Theorem 2's bound: prunes **45–80%** of supports before any hard solve.
- **Hitting set** is NP-hard but greedy is a `log`-approximation, and any hitting set is sound.

---

## 9. Numerical validation

**`s = 1`** — `h = 44` (32 common + 12 rare-mode coordinates, activation rates `0.5 → 1.2×10⁻⁴`, plus 6 near-duplicate pairs). Invisible set computed exactly by halfspace intersection over all `C(44,2)` supports.

```
     N    A(D)   |J*|         J*      L_DARC   L_free
     4   1.273     36  [0,...,40]        12       12
    16   0.636     28  [2,...,40]        10       12
    32   0.300     16  [0,...,40]         8       12
    64   0.300      2    [38, 39]         4       12
   256   0.181      1        [39]         2       12
  1024   0.141      0          []         0       12
```

Graceful degradation `12→10→8→4→2→0` against a ceiling pinned at 12; `J*` converges to exactly the coordinates whose input mode the probes have not hit. End to end under adversarial evaluation — attacker plays the `A(D)`-maximiser, decoder returns the *worst* consistent candidate — the certificate cuts worst-case `d_P` from `0.367` to `0.257` at `N = 64,128`, with residual tracking the quantiser cell width as Theorem 3 predicts.

**`s = 2`** (`2s = 4`) — `h = 18`, all `4047` supports of size `≤ 4`, with the two planted rotated traps of §7.

```
     N   screened   dangerous   minimal supports              |J*|          L_DARC  L_free
    64   2231/4047        970   (11,), (13,14), (15,16,17)    [11,13,16]        11      20
   256   1039/4047          0   —                             []                 0      20
  1024    830/4047          0   —                             []                 0      20
  4096      —                0   —                            []                 0      20
```

The minimal dangerous supports recovered are **exactly** the three planted structures — one isolated rare coordinate and both rotated traps — and the greedy hitting set takes **one coordinate from each**. This is the `s ≥ 2` check: the construction survives contact with rotated adversaries built specifically to break it.

---

## 10. What remains

**Settled.** Theorems 1–4: exact characterisation, the decomposition (conceptual and computational), DARC, and a converse in matching quantities. The hitting-set formulation, the fragility index, and the orientation-is-broken-not-encoded mechanism. Computability via sound relaxations. Validated at `s = 1` and `s = 2`, the latter against planted rotated traps.

**Open.**
- The alphabet gap when `φ < |J*|` — algebraic-geometry codes should shrink it.
- The exact `χ` between `ω` and `Δ+1`; Theorem 3 sits strictly inside.
- Theorem 2's second inequality is loose by ~10² when crudely bounded (`‖v‖₂² ≤ 8sρ²`); the screen uses the sharper data-dependent form.
- The `s = 2` transition is sharp rather than graded — an artefact of only three rare coordinates in that model, not a claim about real geometry.
- **Drift.** Everything assumes unattacked coordinates are bit-exact. Under benign drift the RS layer fails at cell boundaries — the same brittleness `REVIEW.md` §3.4 flags in Theorem 8.1. Dithered or nested-lattice quantisation is the fix and is not written down.
- The hybrid of §6 in the previous revision — certificates may also spend bits on extra mantissa bits of trusted labels, which reshape `V⁺` rotationally where parity bits cannot. Stated, not solved; it is the bridge to the behaviour-versus-parameters accounting in `REVIEW.md` §5.
