# The Repair Budget of a Tampered Model

<!-- **A standalone results document.** Self-contained: all quantities are defined here. Supersedes the Section 8 draft. Surface B (ReLU bias tampering) is deliberately excluded and deferred. -->

---

## 1. The question

A model is deployed. An adversary changes a small number of its parameters. You hold two things: a set of trusted input–output pairs recorded from the clean model, and a short string of protected bits that you were allowed to compute *before* the tampering and store somewhere the adversary cannot reach.

> **How many protected bits do you need to restore the model's function?**

The answer turns out to be governed by a single scalar — the largest functional change an adversary can make while remaining inside the precision of your trusted labels — and that scalar is a measurable spectral property of the network's own feature geometry.

---

## 2. Setup

### 2.1 Model

Let $\mathcal X$ be the input space and $P$ the deployment distribution on it. Fix a **trusted feature map**

$$\sigma : \mathcal X \to \mathbb R^{h},$$

which may itself be an arbitrary deep network. The **mutable parameters** are a vector $c \in \Theta \subseteq \mathbb R^h$, and the model is

$$f_c(x) \;=\; \langle c, \sigma(x)\rangle .$$

This is exact, not a linearization. It covers the output layer of any network — including the LM head of a transformer, where $\sigma(x)$ is the final hidden state (§10).

Assume $\mathbb E_{X\sim P}\|\sigma(X)\|_2^2 < \infty$.

### 2.2 Threat model

The adversary replaces $c$ by

$$\tilde c = c + e, \qquad e \in \mathcal T_{s,\rho} := \{e \in \mathbb R^h : \|e\|_0 \le s,\ \|e\|_\infty \le \rho\}.$$

The adversary is **defense-aware**: it knows $\sigma$, $P$, $\Theta$, the trusted set $D$, the encoder and decoder, and the stored certificate value. It chooses $e$ after all of these are fixed. It cannot modify $D$ or the certificate.

> **Standing consequence (uniformity requirement).** Because the adversary reads $D$ before choosing the support of $e$, every guarantee in this document must hold **uniformly over all supports** $S \subseteq [h]$ with $|S| \le s$. A per-support guarantee is worthless here: the adversary simply picks the worst support. This is not a technicality — §6 shows it is precisely what determines the sample complexity.

### 2.3 Trusted data, at finite precision

Draw $x_1,\dots,x_N \overset{\text{iid}}{\sim} P$ and record

$$D = \big((x_i, y_i)\big)_{i=1}^N, \qquad |y_i - f_c(x_i)| \le \gamma .$$

$\gamma \ge 0$ is the **label precision**: the resolution at which the trusted outputs were recorded and stored. Storing a label to precision $\gamma$ over a range $R$ costs $\beta \approx \log_2(R/\gamma)$ bits.

$\gamma$ is not a nuisance parameter. §5 shows it is the reason the problem is non-trivial at all.

Define the **trusted feature matrix**

$$\Phi_D = \begin{bmatrix} \sigma(x_1)^\top \\ \vdots \\ \sigma(x_N)^\top\end{bmatrix} \in \mathbb R^{N\times h},
\qquad
\widehat\Sigma_D = \tfrac1N \Phi_D^\top\Phi_D .$$

### 2.4 Functional distance

$$\Sigma \;=\; \mathbb E_{X\sim P}\big[\sigma(X)\sigma(X)^\top\big] \in \mathbb R^{h\times h}$$

is the **population feature second-moment matrix**. For $c, c' \in \Theta$,

$$d_P^2(c,c') \;=\; \mathbb E_{X\sim P}\big[(f_c(X)-f_{c'}(X))^2\big] \;=\; (c-c')^\top \Sigma (c-c') .$$

Repair to tolerance $\varepsilon$ means $d_P^2(\hat c, c) \le \varepsilon$. Write $r = \sqrt\varepsilon$.

For $k \le h$ define the restricted extreme eigenvalues

$$\lambda^{(k)}_{\min} = \min_{\|v\|_0\le k,\, v\ne 0} \frac{v^\top\Sigma v}{\|v\|_2^2},
\qquad
\lambda^{(k)}_{\max} = \max_{\|v\|_0\le k,\, v\ne 0} \frac{v^\top\Sigma v}{\|v\|_2^2}.$$

### 2.5 Certificate

An $L$-bit certificate scheme is a pair of deterministic maps

$$C : \Theta \times (\mathcal X\times\mathbb R)^N \to \{0,1\}^L,
\qquad
R : (\mathcal X\times\mathbb R)^N \times \widetilde\Theta \times \{0,1\}^L \to \Theta .$$

The certificate $\kappa = C(c, D)$ is computed **before** tampering. After tampering the decoder sees $(D, \tilde c, \kappa)$ and outputs $\hat c$. Define

$$L^\star_D(\varepsilon) \;=\; \min\Big\{L : \exists (C,R) \text{ with } \sup_{e\in\mathcal T_{s,\rho}} d_P^2\big(R(D,c+e,C(c,D)),\, c\big) \le \varepsilon \ \ \forall c \text{ consistent with } D\Big\}.$$

Only the certificate is charged. The trusted set is treated as given — see §9 for why.

---

## 3. The reduction

Everything follows from one line.

Let $\hat y_i = f_{\tilde c}(x_i)$ be the outputs the decoder can compute from the received model, and let $r_i = \hat y_i - y_i$ be the **residual**. Then

$$r_i = \langle \tilde c, \sigma(x_i)\rangle - y_i = \langle c + e, \sigma(x_i)\rangle - y_i,$$

so, up to the label precision,

$$\boxed{\;r \;=\; \Phi_D\, e \;+\; \xi, \qquad \|\xi\|_\infty \le \gamma, \qquad \|e\|_0 \le s,\ \|e\|_\infty \le \rho. \;}$$

> **Repairing a sparsely tampered output layer is sparse recovery whose sensing matrix is the network's own feature matrix on the trusted inputs, observed at the precision of the trusted labels.**

No assumptions were used: $\sigma$ arbitrary, $P$ arbitrary, depth arbitrary. Two candidates $c', c''$ are indistinguishable to the decoder exactly when $c'' - c'$ is (i) sparse enough to be reachable from a common received model, and (ii) quiet enough on $\Phi_D$ to hide inside the label precision.

**Remark (what is and isn't new here).** The identity $r = \Phi e$ is the classical error-correction-as-sparse-recovery formulation (Candès–Tao). The content of this document is not the identity; it is (a) the object $\Phi_D$ being the network's feature matrix and therefore *measurable*, (b) the pre-commitment quantifier in §2.5, which makes the converse non-trivial, and (c) the bit accounting. See §11.

---

## 4. The central quantity: residual ambiguity

Two candidates that could both have produced $D$ and could both have been tampered into the *same* received model must be separated by the certificate — unless they are functionally close.

Since candidates $c$ and $c + v$ both reach the common received model $\tilde c = c$ (the first by $e = 0$, the second by $e = -v$, which is admissible whenever $\|v\|_0 \le s$ and $\|v\|_\infty\le\rho$), and both agree with $D$ whenever $\|\Phi_D v\|_\infty \le 2\gamma$, define:

> ### Definition 4.1 (invisible set)
> $$\mathcal N(D;\,s,\rho,\gamma) \;=\; \big\{\, v \in \mathbb R^h \;:\; \|v\|_0 \le s,\ \ \|v\|_\infty \le \rho,\ \ \|\Phi_D v\|_\infty \le 2\gamma \,\big\}.$$

> ### Definition 4.2 (residual ambiguity)
> $$\boxed{\;\mathcal A(D) \;=\; \sup_{v \,\in\, \mathcal N(D;\,s,\rho,\gamma)} \big\| \Sigma^{1/2} v \big\|_2 \;}$$

In words: **the largest functional change an adversary can make while staying inside the precision of your trusted labels on every trusted sample.**

$\mathcal A(D)$ is one scalar. It is a sparse generalized eigenvalue problem with an $\ell_\infty$ constraint — NP-hard exactly, but computable by standard convex relaxation or greedy support search, and its maximizer *is* an eval-invisible attack (§12, E5).

Everything below is read off $\mathcal A(D)$ and off the polytope $\mathcal N(D)$ underneath it.

---

## 5. R2 — Why the hard kernel is the wrong object

### 5.1 The genericity collapse

Suppose $\gamma = 0$ and the features are continuous. Fix a support $S$, $|S| \le 2s$. Then $\Phi_{D,S} \in \mathbb R^{N\times 2s}$, and for $N \ge 2s$ the rows are in general position, so $\ker \Phi_{D,S} = \{0\}$ almost surely. There are only $\binom{h}{2s}$ supports, and a finite union of null sets is null. Hence:

> ### Proposition 5.1 (genericity)
> If $\gamma = 0$, $\Sigma \succ 0$ on every $2s$-sparse support, and the feature distribution is absolutely continuous on each such support, then for $N \ge 2s$,
> $$\Pr\big[\, \ker\Phi_{D,S} = \{0\} \ \ \text{for every } S \text{ with } |S|\le 2s \,\big] = 1,$$
> and consequently $L^\star_D(\varepsilon) = 0$ for every $\varepsilon \ge 0$.

**This is a one-line argument and it is devastating to the exact-arithmetic formulation.** It says $2s$ samples always suffice and no certificate is ever needed. Any theorem of the form "$N \gtrsim \tau^{-1} s\log(h/s)$ suffices to make $\ker\Phi_{D,S}$ trivial" is therefore proving something *strictly weaker* than Proposition 5.1, and is loose by a $\log(h/s)$ factor precisely in the regime it was meant to govern. The union bound over supports is doing no work: each event already has probability one.

The exact-kernel machinery only earns its keep when the features are **degenerate** — when exact zeros or exact linear dependencies occur with positive probability. That happens for one-hot or isolated-region feature maps and for dead ReLUs. It does not happen for the feature maps of real trained networks.

### 5.2 The fix: precision is what makes the null space real

The escape is not numerical tolerance. It is physical: **your trusted labels have finite precision.** With $\gamma > 0$, the invisible set $\mathcal N(D)$ is a symmetric convex body of positive volume, and Proposition 5.1 does not apply. The relevant object is not the *rank* of $\Phi_{D,S}$ but its *spectrum*.

> ### Proposition 5.2 (shape of the invisible set)
> Fix $S$ with $|S| \le s$ and let $\sigma_1 \ge \cdots \ge \sigma_{|S|} \ge 0$ be the singular values of $\Phi_{D,S}$. Then $\mathcal N(D)$ restricted to $S$ contains the ellipsoid with semi-axes
> $$a_i \;=\; \min\!\Big\{\rho,\ \frac{2\gamma}{\sigma_i}\Big\}, \qquad i = 1,\dots,|S|.$$
>
> *Proof.* $\|u\|_\infty \le \|u\|_2$, so $\|\Phi_{D,S}v\|_2 \le 2\gamma$ implies $\|\Phi_{D,S}v\|_\infty \le 2\gamma$; the set $\{v : \|\Phi_{D,S}v\|_2\le 2\gamma\}$ is the ellipsoid with semi-axes $2\gamma/\sigma_i$ in the right singular basis. Intersecting with $\|v\|_\infty\le\rho$ gives the cap. $\square$

So a direction is dangerous when its singular value is **small relative to the label precision**, not when it is zero. Directions with $\sigma_i \ll \gamma/\rho$ are fully free; directions with $\sigma_i \gg \gamma/\rho$ are pinned. The transition is smooth, and the whole problem lives in the band between.

### 5.3 Effective invisible dimension

> ### Definition 5.3
> $$d^\star(D;\eta) \;=\; \max_{|S|\le s}\ \#\Big\{ i : \sigma_i(\Phi_{D,S}) \le \eta \Big\}.$$

As $\eta \downarrow 0$ this recovers $\max_S \dim\ker\Phi_{D,S}$, which Proposition 5.1 says is $0$. For $\eta > 0$ it is the number of nearly-silent restricted directions, and it is what the certificate must pay for. The scale that matters is $\eta \asymp \gamma/\rho$.

### 5.4 Zero-bit criterion

> ### Theorem 5.4 (zero certificate bits)
> $$\mathcal A(D) \;\le\; \tfrac12\sqrt\varepsilon \quad\Longrightarrow\quad L^\star_D(\varepsilon) = 0,$$
> $$\mathcal A(D) \;>\; 2\sqrt\varepsilon \quad\Longrightarrow\quad L^\star_D(\varepsilon) \ge 1 .$$
>
> *Proof.* ($\Rightarrow$) Every candidate consistent with $D$ and reachable to the observed $\tilde c$ lies within $\Sigma^{1/2}$-distance $\mathcal A(D)$ of the least-squares candidate; taking that candidate as the output gives error at most $\mathcal A(D) \le \tfrac12\sqrt{\varepsilon}$, hence $d_P^2 \le \varepsilon$. ($\Leftarrow$) If $\mathcal A(D) > 2\sqrt\varepsilon$ there is $v \in \mathcal N(D)$ with $\|\Sigma^{1/2}v\|_2 > 2\sqrt\varepsilon$. The candidates $c$ and $c+v$ both agree with $D$ to precision $\gamma$, both reach the common received model $\tilde c = c$, and are separated by $d_P > 2\sqrt\varepsilon$. A zero-bit decoder is a single function of $(D,\tilde c)$ and cannot be within $\sqrt\varepsilon$ of both. $\square$

The factor-of-4 gap between the two conditions is the usual radius-versus-diameter slack and is not worth removing.

---

## 6. Sample complexity, and where the logarithm comes from

Proposition 5.1 says invertibility is free. Conditioning is not. Because the adversary picks the support after reading $D$ (§2.2), we need a bound on $\mathcal A(D)$ that holds **simultaneously for all supports**, and that is where the sample complexity lives.

> ### Assumption SB($\kappa,\tau,k$) — restricted small ball
> For every $v$ with $\|v\|_0\le k$ and $v^\top\Sigma v>0$,
> $$\Pr_{X\sim P}\Big[\,\big|\langle \sigma(X), v\rangle\big| \;\ge\; \kappa\,\big\|\Sigma^{1/2}v\big\|_2 \,\Big] \;\ge\; \tau .$$

This says: a functionally harmful sparse direction is not merely nonzero on the data — it is *loud* on a constant fraction of it. Both constants are measurable.

> ### Theorem 6.1 (uniform ambiguity bound)
> Under SB($\kappa,\tau,s$), there is a universal $C$ such that if
> $$N \;\ge\; \frac{C}{\tau^{2}}\Big( s\log\frac{e h}{s} \;+\; \log\frac1\delta \Big),$$
> then with probability at least $1-\delta$, simultaneously for every support of size $\le s$,
> $$\boxed{\ \mathcal A(D) \;\le\; \frac{2\gamma}{\kappa}\ }$$
>
> *Proof sketch.* Apply Mendelson's small-ball method to the class $T = \{v : \|v\|_0\le s,\ \|\Sigma^{1/2}v\|_2 = 1\}$, whose Gaussian width satisfies $w(T) \asymp \sqrt{s\log(eh/s)}$. With the stated $N$, w.p. $1-\delta$, uniformly over $T$ at least a $\tau/2$ fraction of samples satisfy $|\langle\sigma(x_i),v\rangle| \ge \kappa$. In particular at least one does. For $v \in \mathcal N(D)$ we have $\|\Phi_Dv\|_\infty \le 2\gamma$, so $\kappa\|\Sigma^{1/2}v\|_2 \le 2\gamma$. $\square$
>
> (The exact power of $\tau$ depends on which form of the small-ball inequality is invoked; $\tau^{-2}$ is the conservative statement.)

> ### Corollary 6.2 (zero bits from data alone)
> Under the hypotheses of Theorem 6.1, if the trusted labels are recorded at precision
> $$\gamma \;\le\; \tfrac14\,\kappa\,\sqrt\varepsilon,$$
> then $L^\star_D(\varepsilon) = 0$ with probability at least $1-\delta$.

### 6.3 What the logarithm is buying

This resolves the tension with Proposition 5.1 cleanly:

| Guarantee | Samples | What it is worth |
|---|---|---|
| $\ker\Phi_{D,S}=\{0\}$ for all $S$ | $N \ge 2s$, a.s. | Nothing. Fails the moment $\gamma>0$. |
| $\mathcal A(D)\le 2\gamma/\kappa$, uniformly over all $S$ | $N \asymp \tau^{-2}\,s\log(h/s)$ | Everything. Survives an adversary who reads $D$. |

> **The $\log(h/s)$ factor is not slack in the proof. It is the price of a guarantee that is uniform over the $\binom{h}{s}$ supports the adversary may choose from — i.e. it is the adaptive adversary's price.** A per-support guarantee costs $O(s)$ samples and is destroyed by an adversary who picks the worst support; a uniform guarantee costs $O(s\log(h/s))$ and cannot be. This matches the known $\Omega(s\log(h/s))$ lower bound for any matrix satisfying a restricted isometry property, so the rate is not improvable in general.

---

## 7. Converse: how many bits when data is not enough

> ### Theorem 7.1 (bit lower bound)
> Fix $D$ and a support $S$, $|S| \le s$. Let $\sigma_1\ge\cdots\ge\sigma_{|S|}$ be the singular values of $\Phi_{D,S}$, and set $a_i = \min\{\rho,\ 2\gamma/\sigma_i\}$. Then
> $$\boxed{\;L_D^\star(\varepsilon) \;\ge\; \sum_{i=1}^{|S|}\left[\log_2 \frac{a_i\sqrt{\lambda^{(s)}_{\min}}}{2\sqrt\varepsilon}\right]_+ \;}$$
> where $[z]_+ = \max\{z,0\}$.
>
> *Proof.* By Proposition 5.2, $\mathcal N(D)$ restricted to $S$ contains the ellipsoid $E$ with semi-axes $a_i$. Every $v\in E$ gives a candidate $c+v$ that (i) agrees with $D$ to precision $\gamma$, (ii) is reachable to the common received model $\tilde c=c$ via the admissible attack $e=-v$, since $\|v\|_0\le s$ and $\|v\|_\infty\le\rho$. For $v,v'\in E$, $d_P(c+v,c+v') \ge \sqrt{\lambda^{(s)}_{\min}}\,\|v-v'\|_2$. Hence a Euclidean $\big(2\sqrt\varepsilon/\sqrt{\lambda^{(s)}_{\min}}\big)$-separated packing of $E$ is a $2\sqrt\varepsilon$-separated packing in $d_P$, and such a packing of $E$ has size at least $\prod_i \max\{1,\ a_i\sqrt{\lambda^{(s)}_{\min}}/(2\sqrt\varepsilon)\}$. Two packing members sharing a certificate message would force the decoder — which sees the same $(D,\tilde c,\kappa)$ in both cases — to be within $\sqrt\varepsilon$ of both, contradicting the separation. Hence $2^L$ is at least the packing size. $\square$

Maximizing over $S$ gives the strongest form. Written per-direction, the bound reads:

> ### Corollary 7.2 (the exchange rate)
> $$L^\star_D(\varepsilon) \;\gtrsim\; \sum_{i}\Big[\log_2\frac{\gamma}{\sigma_i\sqrt{\varepsilon/\lambda^{(s)}_{\min}}}\Big]_+ .$$
> **You pay one protected bit for every factor of two by which a restricted singular direction is quieter than your label precision.** Directions with $\sigma_i$ large contribute nothing; directions with $\sigma_i$ below the precision floor contribute their full dynamic range $\log_2(\rho\sqrt{\lambda_{\min}}/\sqrt\varepsilon)$ each.

Note the two limits are consistent: as $\gamma\to0$ with $N \ge 2s$, all $\sigma_i>0$ and the bound vanishes, recovering Proposition 5.1; as $\sigma_i \to 0$ the $i$-th term saturates at the cap $a_i=\rho$.

---

## 8. R1 — Achievability: the data-free ceiling

The converse is data-dependent. The following upper bound is not: it holds for every $D$, including $D=\varnothing$. It is therefore a *ceiling* on the repair budget — you never need more than this, no matter how bad your trusted set is.

### 8.1 Construction

Assume $\Theta \subseteq [-B,B]^h$.

**Step 1 — quantizer step.** Set
$$\Delta \;=\; 2\sqrt{\frac{\varepsilon}{s\,\lambda^{(s)}_{\max}}}.$$

**Step 2 — modular symbols.** Let $k_j(\theta) = \lfloor (\theta_j + B)/\Delta\rfloor$ be the cell index of coordinate $j$, and let
$$M \;=\; \Big\lceil \tfrac{2\rho}{\Delta}\Big\rceil + 3 .$$
Define the symbol $y_j = k_j(c) \bmod M$. Working modulo $M$ rather than storing the full cell index is what makes $\rho$, rather than $B$, appear in the final rate.

**Step 3 — code.** Let $Q$ be a prime power with $Q \ge \max\{M,\ h\}$. Regard $y = (y_1,\dots,y_h) \in \mathbb F_Q^{h}$ as a word and store the $2s$ Reed–Solomon parity symbols of $y$:
$$\boxed{\;\kappa \;=\; \mathrm{RS}_{2s}(y), \qquad L \;=\; 2s\lceil \log_2 Q\rceil. \;}$$

### 8.2 Decoding

1. Form $\tilde y_j = k_j(\tilde c) \bmod M$.
2. On every unattacked coordinate $\tilde c_j = c_j$ exactly, so $\tilde y_j = y_j$. Hence $d_H(\tilde y, y) \le s$.
3. Run Berlekamp–Massey with the stored parity: $2s$ parity symbols correct $s$ symbol errors. This returns both $y$ and the error locator set $\hat S = \mathrm{supp}(e)$.
4. Set $\hat c_j = \tilde c_j$ for $j \notin \hat S$ — exact.
5. For $j \in \hat S$: lift the residue. We know $k_j(c) \equiv y_j \ (\mathrm{mod}\ M)$ and $|c_j - \tilde c_j|\le\rho$, so $|k_j(c) - k_j(\tilde c)| \le \rho/\Delta + 1$; since $M > 2\rho/\Delta + 2$ the residue determines $k_j(c)$ uniquely. Set $\hat c_j$ to that cell's centre.

### 8.3 Guarantee

> ### Theorem 8.1 (data-free ceiling)
> For every trusted set $D$ (including the empty one),
> $$\boxed{\;L^\star_D(\varepsilon) \;\le\; 2s\left\lceil \log_2 \max\left\{ \Big\lceil \rho\sqrt{\tfrac{s\,\lambda^{(s)}_{\max}}{\varepsilon}}\Big\rceil + 3,\ \ h \right\}\right\rceil \;=\; O\!\left(s\log h \;+\; s\log\Big(1+\rho\sqrt{\tfrac{s\lambda^{(s)}_{\max}}{\varepsilon}}\Big)\right).}$$
> The encoder and decoder run in time $\tilde O(h)$.
>
> *Proof.* Steps 1–5 above are exact except on $\hat S$, where $|\hat c_j - c_j| \le \Delta/2$. Since $|\hat S|\le s$,
> $$\|\hat c - c\|_2 \le \tfrac{\sqrt s\,\Delta}{2}, \qquad
> d_P(\hat c,c) \le \sqrt{\lambda^{(s)}_{\max}}\,\|\hat c-c\|_2 \le \sqrt{\lambda^{(s)}_{\max}}\cdot \tfrac{\sqrt s}{2}\cdot 2\sqrt{\tfrac{\varepsilon}{s\lambda^{(s)}_{\max}}} = \sqrt\varepsilon .$$
> The certificate depends only on $c$, so it is a valid pre-attack commitment, and the decoder never consults $D$. Correctness therefore holds against every $e \in \mathcal T_{s,\rho}$. $\square$

### 8.4 Reading the two bounds together

Converse (Cor. 7.2) and ceiling (Thm 8.1) have the same shape:

$$\underbrace{s\log h}_{\text{where the tampering is}} \;+\; \underbrace{s\log\big(\rho\sqrt{\lambda/\varepsilon}\big)}_{\text{how large it is}} .$$

The ceiling ignores $D$ entirely; the converse shrinks as $\Phi_D$'s restricted spectrum rises above the precision floor. Closing the gap between them — a *data-aware* achievability that shortens the code using $\mathrm{row}(\Phi_D)$ — is the main open problem (§13.1).

---

## 9. R4 — The ladder: detect, localize, repair

Three tasks, one object, and they are not equally expensive. Stated carefully, because the distinctions matter.

> ### Definition 9.1
> - **Bit-exact integrity:** decide whether $\tilde c = c$ as bit strings.
> - **Functional detection:** decide whether $d_P(\tilde c, c) > \varepsilon$.
> - **Localization:** output $\mathrm{supp}(\tilde c - c)$.
> - **Repair:** output $\hat c$ with $d_P^2(\hat c,c)\le\varepsilon$.

| Task | Protected bits | Conditions |
|---|---|---|
| Bit-exact integrity | $O(1)$ — a hash | See caveat below |
| Functional detection | $0$ | Given SB and $N$ as in Thm 6.1, with $\gamma \le \tfrac14\kappa\sqrt\varepsilon$ |
| Localization | $0$ if $\mathcal A(D)$ small enough to identify $\hat S$; else $\Theta(s\log(h/s))$ | |
| Repair to $\varepsilon$ | $0$ if $\mathcal A(D)\le\tfrac12\sqrt\varepsilon$; else Cor. 7.2 $\le L \le$ Thm 8.1 | |

> **Caveat on the top row — important, do not omit.** A cryptographic hash detects *any* bit change, including entirely benign ones: different floating-point rounding on a new accelerator, deployment-time quantization, a legitimate fine-tune. It is brittle in exactly the way practitioners complain about, and it yields nothing toward localization or repair. **The $O(1)$ figure is for bit-exact integrity only. Functional detection — is $d_P(\tilde c,c)>\varepsilon$? — is a distinct and harder problem, and it is the one the detection literature actually addresses.** This document does not claim to improve on that literature; it observes that under the conditions of Theorem 6.1 the trusted probes deliver functional detection at zero stored cost, and that the interesting gap is between detection and repair, not between hashing and everything else.

The separation worth stating is the last two rows: **detection can be free while repair is not.** Under Theorem 6.1's conditions the data tells you *that* something functionally significant happened, and even *where*, while the certificate is still required to recover *what the values were* — because localization is a discrete question the data answers, and amplitude is a continuous one it may not.

---

## 10. Worked instance: the LM head

Let $\sigma(x) \in \mathbb R^{d}$ be a transformer's final hidden state and $W \in \mathbb R^{V\times d}$ the unembedding matrix, so $z(x) = W\sigma(x)$ are the logits. Tampering is $\widetilde W = W + E$ with $\|E\|_0 \le s$.

Per output coordinate $v$,
$$\Delta z_v(x_i) \;=\; \langle E_v, \sigma(x_i)\rangle,$$
so **the problem decouples into $V$ independent instances of §3, all sharing the same sensing matrix** $\Phi_D \in \mathbb R^{N\times d}$. Consequences:

- A model with $V d$ mutable parameters is governed by **one $d\times d$ spectrum**. For Llama-3.1-8B: $V = 128{,}256$, $d = 4096$, $Vd \approx 5.25\times10^8$ parameters, one $4096\times4096$ object.
- Rows with $\Delta z_v \equiv 0$ across all probes are unaffected, so **the probes localize the affected rows for free**; each affected row is then a small sparse-recovery problem in $\mathbb R^{4096}$.
- Applying Theorem 8.1 to the flattened parameter vector with $h = Vd$: $\log_2 h \approx 29$, so for $s=14$ the ceiling is $L \le 2\cdot14\cdot29 \approx 812$ bits $\approx 102$ bytes, independent of $D$.
- Applying Theorem 6.1 with $d = 4096$, $s = 14$: $N \gtrsim \tau^{-2}(2\cdot14\cdot\log_2(4096/28)) \approx \tau^{-2}\cdot 200$.

The relevant empirical unknowns are $\kappa$, $\tau$, and the restricted spectrum of $\Phi_D$. Transformer final hidden states are known to be anisotropic and of low effective rank, so the spectrum decays sharply — which by Proposition 5.2 means a large invisible set at any fixed $\gamma$. Whether $\kappa$ is bounded away from zero on sparse supports is an empirical question and is the single most important measurement to make (§12).

**Relevance of the threat model.** Bit-flip attacks on the LM head are documented: targeted attacks report $3$–$14$ flips on 8B–14B models, with accuracy on unrelated benchmarks preserved. That last property is precisely the statement that the attack lies close to $\mathcal N(D)$ for the evaluation sets used.

---

## 11. Literature

### 11.1 Classical antecedents — cite, claim nothing

| | |
|---|---|
| Error correction as sparse recovery, $r=\Phi e$ | Candès & Tao, *Decoding by Linear Programming*, 2005 |
| Zero-error source coding with decoder side information $=$ chromatic number | Witsenhausen, 1976; Alon & Orlitsky, 1996; Orlitsky & Roche, 2001 |
| Syndrome coding with decoder side information | Slepian–Wolf; DISCUS (Pradhan–Ramchandran) |
| Restoring a corrupted copy from a short fingerprint | Document exchange (Belazzougui; Haeupler); set reconciliation (Minsky–Trachtenberg–Zippel); IBLTs |
| Sparse recovery with partially known support | Modified-CS (Vaswani–Lu) and successors |
| Restricted eigenvalue / RIP, small-ball method | Bickel–Ritov–Tsybakov; Mendelson |
| $\Omega(s\log(h/s))$ measurements necessary for RIP | Standard |
| Perturbations in the Jacobian null space leave predictions unchanged | Folklore across the NTK / Fisher / loss-landscape literature |

### 11.2 Behaviour determines the last layer

**Carlini et al., *Stealing Part of a Production Language Model* (ICML 2024)** recover a production LLM's final layer from API logits by collecting logit vectors and taking an SVD, requiring $n > h$ queries ($\approx 8192$ for Llama-65B). *The Geometry of Last-Layer Model Stealing* (2026) analyses the same construction geometrically.

This is the closest work to §3 and must be cited, but it solves a different problem. With no side information the only identifiable object is $\mathrm{col}(W)$, so recovery is **up to an unknown invertible gauge** — the attacker learns $W$ only modulo $O(h)$ — and the $n>h$ requirement is the cost of *spanning* that subspace from scratch. Here the received model $\tilde c$ is in hand: there is no subspace to span and no gauge to fix, and the unknown is an $s$-sparse residual. The two settings have different information structures and neither result implies the other. What Carlini et al. do supply is independent confirmation that $\Phi_D$ is the operative object and a published baseline for what behaviour alone costs.

### 11.3 Attacks

Progressive bit search (BFA, ICCV'19); T-BFA; TBT; ProFlip; DeepHammer (USENIX Sec'20); OneFlip (USENIX Sec'25, single-bit last-layer backdoor); and for transformers, AttentionBreaker, SilentStriker, and targeted LM-head flip attacks (2025–26). These establish that $s$ is genuinely small and that $\rho$ is bounded, and that attackers already optimize for invisibility on standard benchmarks.

### 11.4 Detection

Sensitive-Sample Fingerprinting (CVPR'19) — 2–8 probes, detection only, probes chosen by a first-order heuristic, no optimality theory. Model Equality Testing (ICLR'25) — MMD two-sample test for whether an API's model changed; detection only, no localization or repair, no sample-complexity theory. HASHTAG / AccHashtag, DeepDyve, VerIDeep, BitShield — hash- and signature-based integrity, detection only.

### 11.5 Recovery systems

RADAR; weight reconstruction (DAC'20); NeuroPots (USENIX Sec'23); Aegis; ObfusBFA; WeightSentry; NAPER; RangeGuard. For LLMs: LM-Fix (2025) uses fixed test vectors plus redundancy buffers costing **1.9–5% of model memory**; BitFlipScope (2025) localizes and recovers LLM bit flips. *Repair Brain Damage* (2026) imposes real-numbered linear constraints on weights and decodes with $\ell_1$. All are constructive and heuristic: none proves a lower bound, and none treats the trusted set as a measurement.

**Terminology collision:** *Provable Repair of Deep Neural Networks* (PLDI'21, PLDI'23) means repairing a network to satisfy a specification. Different problem. Consider naming the object here a *repair budget* or *restoration sketch* rather than a "certificate", which also collides with certified robustness.

### 11.6 What is left

1. A converse for the sparse-plus-side-information problem. Neither the coding literature (no behavioural side channel) nor the stealing literature (no lower bound, no sparsity) supplies one.
2. Identification of $\mathcal A(D)$ as the governing scalar, and its reading in terms of the restricted spectrum against label precision (§5, §7).
3. The observation that the $\log(h/s)$ is the adaptive adversary's price, not proof slack (§6.3).
4. The detect / localize / repair separation with its honest caveat (§9).
5. Measurement of these quantities on real networks (§12).

---

## 12. What to measure

The theory is only worth as much as $\mathcal A(D)$, $\kappa$, $\tau$ and the restricted spectrum turn out to be on real models. Five experiments, none of which verifies a theorem inside its own construction.

**E1 — the spectrum (essential).** For a real model, collect final hidden states over a large input corpus; measure the restricted singular spectrum of $\Phi_{D,S}$ over random and adversarially chosen supports; plot $\mathcal A(D)$ and $d^\star(D;\eta)$ against $N$, $s$, $\gamma$. Deliverable: **the number of trusted samples at which the repair budget hits zero**, and the residual budget below that.

**E2 — end-to-end repair against a real attack (essential).** Run a published bit-flip attack. Repair with (i) probes only, (ii) probes plus an $L$-bit certificate, $L \in \{0,16,32,64,128,256\}$. Plot recovered behaviour against $L$ for several $N$; overlay the converse of §7 and the ceiling of §8.

**E3 — the risked prediction.** Does sharper feature-spectrum decay imply a larger repair budget? Vary across model families and across public training checkpoints. Prediction: later, more converged checkpoints have faster spectral decay, larger $\mathcal A(D)$, and need more probes or more bits — i.e. *the better trained the model, the less its behaviour constrains its weights.* This is the one prediction that can fail. Report it either way.

**E4 — the practical bar.** Existing LLM recovery systems store 1.9–5% of model memory. Theorem 8.1 gives $\approx 10^2$ bytes for $s\approx14$. Demonstrate the gap end to end, and be scrupulous about what is paid instead: decode time, and invalidation under legitimate fine-tuning.

**E5 — the eval-invisible attack.** The maximizer of $\mathcal A(D)$ *is* an $s$-sparse edit that is invisible at your label precision on every trusted sample and maximally harmful under $P$. Construct it and show it survives a full benchmark suite while changing deployment behaviour. One figure; makes the abstraction concrete.

---

## 13. Future work

Explicitly out of scope here, in rough order of value.

### 13.1 Data-aware achievability
§8 gives a ceiling that ignores $D$. The matching upper bound should shorten the code using $\mathrm{row}(\Phi_D)$, so that the rate degrades to $\approx d^\star(D;\eta)\log(\rho/\sqrt\varepsilon)$ when the trusted set is informative. Unlike the isolated-feature case, $\Phi_D$ is not coordinate-aligned, so "shortening" is not literal and a basis adapted to $\mathrm{row}(\Phi_D)$ plus a support-identification syndrome is needed. This is the main open problem.

### 13.2 Probe design, as a minimax
This document uses i.i.d. probes, which is a deliberate simplification: it removes all design questions and makes $\Phi_D$'s law depend only on $P$. Allowing the defender to choose $x_1,\dots,x_N$ opens a genuinely different problem, and it must be posed correctly:

> **The right formulation is minimax, not optimization.** §2.2 grants the adversary full knowledge of the defense, so any designed probe set is public. The adversary then picks the $s$-sparse $e$ least visible on exactly those probes. The problem is
> $$\max_{\{x_i\}} \ \min_{\|e\|_0\le s} \ \text{visibility}(e; \Phi_D),$$
> not $\max_{\{x_i\}}$ of average or per-direction visibility. A design optimized for a fixed direction — which is what first-order "sensitive sample" heuristics produce — is silently defeated by an adaptive adversary. A *uniform*, RIP-style guarantee over all $2s$-sparse directions simultaneously leaves the adversary nowhere to hide and is the correct target.

An additional constraint makes this genuinely new rather than a corollary of compressed sensing: **the rows of $\Phi_D$ cannot be designed freely.** Each row must be a realizable feature vector $\sigma(x)$, so the design set is the network's feature manifold, not $\mathbb R^h$. Characterizing the minimum $N$ in terms of how that manifold spreads over sparse directions is open, and would subsume and improve on existing probe-selection heuristics.

### 13.3 Hidden-layer tampering
This document covers output-layer parameters, where the model is exactly linear in the mutable parameters. Hidden-layer tampering — e.g. ReLU bias perturbation — requires a controlled linearization with a margin condition, and multi-layer propagation requires a product-of-Jacobians remainder. Deferred.

### 13.4 Other open items
- **Randomized encoders.** §2.5 fixes deterministic maps. A private-coin version should be checked; the converse is expected to survive with constant-factor loss.
- **Noisy rather than quantized labels.** $\gamma$ here is a hard precision bound. A stochastic-noise version needs stable recovery under RIP rather than exact syndrome decoding.
- **Joint budget.** This document charges only $L$, on the grounds that trusted data is typically pre-existing — a public validation set, replicated and version-controlled, whose integrity is assured by other means. When it is not, storing $N$ labels at $\beta$ bits is itself a protected cost, and the honest question becomes *bits spent sketching behaviour versus bits spent sketching parameters*. Worth a section once §13.1 is settled.
- **Estimating $\Sigma$.** All statements treat $\Sigma$ as known. In practice it is estimated from held-out data and $\mathcal A(D)$ is therefore itself an estimate.
- **Computing $\mathcal A(D)$ exactly is NP-hard** (sparse generalized eigenvalue). Use convex relaxation or greedy support search; state the exact quantity as the information-theoretic object.
- **Adaptive / multi-round adversaries**, and adversaries who tamper repeatedly between audits.
