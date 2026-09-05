# The Repair Budget of a Tampered Model

<!-- Standalone results document. Self-contained: all quantities are defined here.
     §13.1 (data-aware achievability) is no longer open — it is §7–§11. -->

---

## 1. The question

A model is deployed. An adversary changes a small number of its parameters. You hold two things: a set of trusted input–output pairs recorded from the clean model, and a short string of protected bits that you were allowed to compute *before* the tampering and store somewhere the adversary cannot reach.

> **How many protected bits do you need to restore the model's function?**

The answer is governed by one geometric object — the set of parameter changes that are invisible at the precision of your trusted labels — and by two numbers read off it: its **radius**, which decides whether you can *detect* tampering, and its **chromatic number**, which decides what it costs to *repair* it.

---

## 2. Setup

### 2.1 Model

Let $\mathcal X$ be the input space and $P$ the deployment distribution. Fix a **trusted feature map** $\sigma : \mathcal X \to \mathbb R^{h}$, which may itself be an arbitrary deep network. The **mutable parameters** are $c \in \Theta \subseteq [-B,B]^h$, and the model is

$$f_c(x) \;=\; \langle c, \sigma(x)\rangle .$$

This is exact, not a linearization. It covers the output layer of any network, including the LM head of a transformer, where $\sigma(x)$ is the final hidden state (§14). Assume $\mathbb E_{X\sim P}\|\sigma(X)\|_2^2 < \infty$.

### 2.2 Threat model

The adversary replaces $c$ by

$$\tilde c = c + e, \qquad e \in \mathcal T_{s,\rho} := \{e \in \mathbb R^h : \|e\|_0 \le s,\ \|e\|_\infty \le \rho\}.$$

The adversary is **defense-aware**: it knows $\sigma$, $P$, $\Theta$, the trusted set $D$, the encoder and decoder, and the stored certificate value. It chooses $e$ after all of these are fixed. It cannot modify $D$ or the certificate.

> **Standing consequence.** Because the adversary reads $D$ before choosing the support of $e$, every guarantee must hold **uniformly over all supports**. A per-support guarantee is worthless: the adversary picks the worst support.

### 2.3 The difference set

The decoder never sees $e$; it sees $\tilde c$ and must distinguish candidates. Two candidates reachable to a common received model differ by an element of

$$\boxed{\ \mathcal D_{s,\rho} \;:=\; \mathcal T_{s,\rho} - \mathcal T_{s,\rho}\ }$$

and this set — not $\mathcal T_{2s,2\rho}$ — is the operative one.

> **Lemma 2.1.** $\mathcal T_{2s,\rho} \subsetneq \mathcal D_{s,\rho} \subsetneq \mathcal T_{2s,2\rho}$.
>
> *Proof.* First inclusion: split the support of $v\in\mathcal T_{2s,\rho}$ into $S_1,S_2$ of size $\le s$ and take $e' = v|_{S_1}$, $e'' = -v|_{S_2}$. Second: a difference has at most $2s$ nonzeros, each of magnitude at most $2\rho$. Strictness of the second: the vector equal to $2\rho$ on $2s$ coordinates lies in $\mathcal T_{2s,2\rho}$, but writing it as $e'-e''$ forces $e'_j=\rho,\ e''_j=-\rho$ on all $2s$ coordinates, so $\|e'\|_0 = 2s > s$. $\square$

Conflating $\mathcal D_{s,\rho}$ with $\mathcal T_{2s,2\rho}$ overstates the ambiguity; conflating it with $\mathcal T_{s,\rho}$ understates it. Earlier drafts of this document used $\mathcal T_{s,\rho}$ throughout, which is why the positive direction of the old zero-bit criterion did not follow. It is fixed in §5.

### 2.4 Trusted data, at finite precision

Draw $x_1,\dots,x_N \overset{\text{iid}}{\sim} P$ and record $D = ((x_i,y_i))_{i=1}^N$ with $|y_i - f_c(x_i)| \le \gamma$. The **label precision** $\gamma \ge 0$ is the resolution at which the trusted outputs were recorded. It is not a nuisance parameter: §6 shows it is one of exactly two reasons the problem is non-trivial.

Write $\Phi_D \in \mathbb R^{N\times h}$ for the **trusted feature matrix** with rows $\sigma(x_i)^\top$, and $\widehat\Sigma_D = \tfrac1N \Phi_D^\top\Phi_D$. Let

$$\Theta_D \;=\; \{c'\in\Theta : |\langle c',\sigma(x_i)\rangle - y_i| \le \gamma \ \ \forall i\}$$

be the set of parameters **consistent with $D$**.

### 2.5 Functional distance

$\Sigma = \mathbb E_{X\sim P}[\sigma(X)\sigma(X)^\top]$ is the population feature second-moment matrix, and

$$d_P^2(c,c') \;=\; \mathbb E_{X\sim P}\big[(f_c(X)-f_{c'}(X))^2\big] \;=\; (c-c')^\top \Sigma (c-c') .$$

Repair to tolerance $\varepsilon$ means $d_P^2(\hat c, c) \le \varepsilon$.

### 2.6 Certificate

An $L$-bit certificate scheme is a pair of deterministic maps

$$C : \Theta \times (\mathcal X\times\mathbb R)^N \to \{0,1\}^L,
\qquad
R : (\mathcal X\times\mathbb R)^N \times \widetilde\Theta \times \{0,1\}^L \to \Theta .$$

The certificate $\kappa = C(c,D)$ is computed **before** tampering. After tampering the decoder sees $(D,\tilde c,\kappa)$ and outputs $\hat c$. Define

$$L^\star_D(\varepsilon) \;=\; \min\Big\{L : \exists (C,R) \text{ with } \sup_{e\in\mathcal T_{s,\rho}} d_P^2\big(R(D,c+e,C(c,D)),\, c\big) \le \varepsilon \ \ \forall c \in \Theta_D\Big\}.$$

Only the certificate is charged; §17 records why this accounting is the document's weakest point.

---

## 3. The reduction

Let $\hat y_i = f_{\tilde c}(x_i)$ and $r_i = \hat y_i - y_i$. Then $r_i = \langle c+e, \sigma(x_i)\rangle - y_i$, so

$$\boxed{\;r \;=\; \Phi_D\, e \;+\; \xi, \qquad \|\xi\|_\infty \le \gamma, \qquad e \in \mathcal T_{s,\rho}. \;}$$

> **Repairing a sparsely tampered output layer is sparse recovery whose sensing matrix is the network's own feature matrix on the trusted inputs, observed at the precision of the trusted labels.**

No assumptions were used: $\sigma$ arbitrary, $P$ arbitrary, depth arbitrary.

**What is and isn't new.** The identity $r = \Phi e$ is the classical error-correction-as-sparse-recovery formulation (Candès–Tao). The content here is (a) $\Phi_D$ being the network's own feature matrix and therefore *measurable*, (b) the pre-commitment quantifier of §2.6, and (c) the bit accounting of §7–§11.

---

## 4. The invisible set

> ### Definition 4.1 (invisible set)
> $$\mathcal N(D) \;=\; \big\{\, v \in \mathcal D_{s,\rho} \;:\; \|\Phi_D v\|_\infty \le 2\gamma \,\big\},
> \qquad
> \mathcal N^-(D) \;=\; \big\{\, v \in \mathcal T_{s,\rho} \;:\; \|\Phi_D v\|_\infty \le 2\gamma \,\big\}.$$

$\mathcal N^-\subseteq\mathcal N$. The first is what an adversary can realize as a single attack; the second is what the decoder cannot rule out.

> ### Definition 4.2 (residual ambiguity, dangerous vectors)
> $$\mathcal A(D) \;=\; \sup_{v \in \mathcal N(D)} \big\| \Sigma^{1/2} v \big\|_2 ,$$
> and $v$ is **dangerous at level $\theta$** if $v\in\mathcal N(D)$ and $\|\Sigma^{1/2}v\|_2 > \theta$.

In words: $\mathcal A(D)$ is **the largest functional change an adversary can make while staying inside the precision of your trusted labels on every trusted sample.** It is a sparse generalized eigenvalue problem with an $\ell_\infty$ constraint — NP-hard exactly, but §12 shows only *sound upper bounds* are ever needed, and gives cheap ones.

Note that if $c'\in\Theta_D$ and $c''\in\Theta_D$ then $\|\Phi_D(c''-c')\|_\infty \le 2\gamma$ automatically; so on $\Theta_D$ the invisible set *is* the set of differences between indistinguishable candidates.

---

## 5. Detection: the radius

> ### Theorem 5.1 (zero certificate bits)
> $$\mathcal A(D) \le \sqrt\varepsilon \quad\Longrightarrow\quad L^\star_D(\varepsilon) = 0,$$
> $$\sup_{v\in\mathcal N^-(D)}\|\Sigma^{1/2}v\|_2 > 2\sqrt\varepsilon \quad\Longrightarrow\quad L^\star_D(\varepsilon) \ge 1 .$$
>
> *Proof.* ($\Rightarrow$) Given $(D,\tilde c)$ the decoder's candidate set is $\mathcal C(\tilde c) = \{c'\in\Theta_D : \tilde c - c' \in \mathcal T_{s,\rho}\}$. For $c',c''\in\mathcal C(\tilde c)$ we have $c''-c' = (\tilde c - c') - (\tilde c - c'') \in \mathcal D_{s,\rho}$ and $\|\Phi_D(c''-c')\|_\infty\le2\gamma$, so $c''-c'\in\mathcal N(D)$ and $d_P(c',c'')\le\mathcal A(D)$. Returning any candidate gives error at most $\mathcal A(D)$. ($\Leftarrow$) Take $v\in\mathcal N^-$ with $\|\Sigma^{1/2}v\|_2>2\sqrt\varepsilon$. Both $c$ and $c+v$ lie in $\Theta_D$ and both reach the common received model $\tilde c = c$ — the first by $e=0$, the second by $e=-v\in\mathcal T_{s,\rho}$. A zero-bit decoder is a single function of $(D,\tilde c)$ and cannot be within $\sqrt\varepsilon$ of both. $\square$

The gap between $\sqrt\varepsilon$ and $2\sqrt\varepsilon$ is the usual radius-versus-diameter slack. **It is not free** — §11 records what it costs in certificate length — but it is not removable by this argument.

**Detection.** Deciding whether $d_P(\tilde c,c)>\varepsilon$ is possible at zero stored cost exactly when $\mathcal A(D)$ is small. Detection is governed by the *radius* of the invisible set. Repair, as §7 shows, is governed by a different functional of the same object.

---

## 6. Where ambiguity comes from

The following replaces the small-ball machinery of earlier drafts. It needs **no assumption at all**.

> ### Theorem 6.1 (ambiguity decomposition)
> For every $D$,
> $$\boxed{\ \mathcal A(D)^2 \;\le\; 4\gamma^2 \;+\; \sup_{v\in\mathcal N(D)} v^\top\big(\Sigma - \widehat\Sigma_D\big)v\ }$$
>
> *Proof.* $v^\top\Sigma v = v^\top\widehat\Sigma_D v + v^\top(\Sigma-\widehat\Sigma_D)v$, and $v^\top\widehat\Sigma_D v = \tfrac1N\|\Phi_D v\|_2^2 \le \|\Phi_D v\|_\infty^2 \le 4\gamma^2$. $\square$

> **A sparse change hides from your trusted set for exactly two reasons: your labels are too coarse to see it, or your probes have not visited the inputs on which it acts. Nothing else contributes.**

Consequences:

- Sample complexity becomes **restricted covariance estimation** — a standard problem with known rates under stated tail conditions — rather than an assumption about anti-concentration constants nobody can report. A restricted small-ball condition still yields $N \asymp \tau^{-2}s\log(eh/s)$ by Mendelson's method; Theorem 6.1 explains what $\tau$ *is*: the rarity of the input mode on which a harmful direction acts.
- Both terms are **measurable** on a real network.
- It is also a **computational screen** (§12).

**Genericity, and why it is not the point.** If $\gamma = 0$ and the feature distribution is absolutely continuous on every $2s$-sparse support, then for $N\ge 2s$ the restricted kernels are trivial almost surely and $L^\star_D(\varepsilon)=0$ for all $\varepsilon$. This is a one-line argument and it is fatal to any exact-arithmetic formulation of the problem. It is also inapplicable: real feature maps carry exact and near-exact linear relations among columns, and §10 exhibits a mechanism — a relation that holds on every sampled input and breaks only on a rare one — by which the restricted kernel is nontrivial *and* functionally harmful. The relevant object is never the rank of $\Phi_{D,S}$; it is its spectrum against $\gamma$, which is what Theorem 6.1 measures.

---

## 7. Repair: the chromatic number

> ### Definition 7.1
> $G_D(t)$ is the graph on $\Theta_D$ with $c' \sim c''$ iff $c''-c' \in \mathcal N(D)$ and $d_P(c',c'')>t$. Adjacency depends only on the difference.

> ### Theorem 7.2 (characterization)
> $$\big\lceil \log_2 \chi\big(G_D(2\sqrt\varepsilon)\big)\big\rceil \;\le\; L^\star_D(\varepsilon)
> \qquad\text{and}\qquad
> L^\star_D(4\varepsilon) \;\le\; \big\lceil \log_2 \chi\big(G_D(2\sqrt\varepsilon)\big)\big\rceil .$$
>
> *Proof.* (Left) Let $(C,R)$ repair to $\varepsilon$ and set $\kappa = C(\cdot,D)$. If $\kappa(c')=\kappa(c'')$ on an edge, the decoder sees identical $(D,\tilde c,\kappa)$ in both worlds — $\tilde c$ exists because $c''-c'\in\mathcal D_{s,\rho}$ — and must be within $\sqrt\varepsilon$ of both, so $d_P(c',c'')\le2\sqrt\varepsilon$, contradicting the edge. Hence $\kappa$ is a proper colouring. (Right) Given a proper colouring, let the decoder return any $c'\in\mathcal C(\tilde c)$ carrying the received colour; the truth is such a candidate. Two same-coloured members of $\mathcal C(\tilde c)$ differ by an element of $\mathcal N(D)$ and are non-adjacent, so $d_P \le 2\sqrt\varepsilon$. $\square$

This is Witsenhausen's zero-error-source-coding-with-side-information framework. The two bounds differ by the same radius-versus-diameter factor as Theorem 5.1; **the characterization is a sandwich, not an equality**, and closing it is not attempted here.

The value is that it collapses the theory. Writing $\omega$ for the clique number and $\Delta$ for the maximum degree:

| | becomes |
|---|---|
| zero bits (Thm 5.1) | $\chi = 1 \iff G_D$ has no edges $\iff \operatorname{diam}_{d_P}\mathcal N(D) \le 2\sqrt\varepsilon$ |
| converse (§8) | $\chi \ge \omega$; a $d_P$-packing of $\mathcal N^-(D)$ is a clique |
| ceiling (§9) | $\chi \le \Delta+1$; dropping the $\Phi_D$ constraint gives $\binom{h}{2s}(2\rho/\Delta)^{2s}$ |

> **Detection is governed by the radius of the invisible set. Repair is governed by its chromatic number.**

**Caveat, load-bearing.** A clique requires *pairwise* differences in $\mathcal N(D)$. Candidates on supports whose union exceeds $2s$ are **not** confusable, so the converse is a maximum over supports while the covering bound is a sum. A converse that sums over supports is wrong.

---

## 8. Converse

### 8.1 Per-support packing

> ### Theorem 8.1
> Fix a support $S$, $|S|\le s$, let $\sigma_1\ge\cdots\ge\sigma_{|S|}$ be the singular values of $\Phi_{D,S}$, and set $a_i = \min\{\rho,\ 2\gamma/\sigma_i\}$. Then
> $$L_D^\star(\varepsilon) \;\ge\; \Big[\log_2 \operatorname{vol}\big(\Sigma_{SS}^{1/2}E_S\big) - |S|\log_2\big(2\sqrt\varepsilon\big) - \log_2 V_{|S|}\Big]_+ ,$$
> where $E_S\subseteq\mathbb R^S$ is the ellipsoid with semi-axes $a_i$ and $V_k$ is the volume of the unit $k$-ball.
>
> *Proof.* $\|u\|_\infty\le\|u\|_2$ gives $E_S\subseteq\mathcal N^-(D)$. Every $v\in E_S$ yields a candidate $c+v\in\Theta_D$ reachable to the common $\tilde c=c$ via $e=-v$. A $2\sqrt\varepsilon$-separated subset of $E_S$ in $d_P$ is a clique in $G_D(2\sqrt\varepsilon)$, and its size is at least $\operatorname{vol}(\Sigma_{SS}^{1/2}E_S)/\operatorname{vol}(2\sqrt\varepsilon\,B_2^{|S|})$. Apply Theorem 7.2. $\square$

The per-axis product form of earlier drafts, $\prod_i\max\{1,a_i\sqrt{\lambda_{\min}}/2\sqrt\varepsilon\}$, is not correct for a thin ellipsoid: axes below the resolution cannot be floored to $1$ independently. The volume ratio is the right statement.

**Reading it.** You pay one protected bit for every factor of two by which a restricted singular direction is quieter than your label precision. Directions with $\sigma_i$ large contribute nothing; directions with $\sigma_i$ below the precision floor contribute their full dynamic range.

### 8.2 A converse in the achievability's own quantities

Theorem 8.1 is per-support and says nothing about locating the tampering. The following does, and it is the one that matches §11.

> ### Theorem 8.2
> Suppose $D$ admits $m$ pairwise disjoint singleton dangerous supports $\{j_1\},\dots,\{j_m\}$ and values $v^{(1)}_i,\dots,v^{(n)}_i$ on coordinate $j_i$ with $|v^{(t)}_i|\le\rho/2$, such that
> 1. every combination $\sum_i v^{(t_i)}_i$ lies in $\mathcal N(D)$ (automatic when the $\Phi_D$-columns of $j_1,\dots,j_m$ vanish), and
> 2. any two combinations differing in at least one and at most $2s$ blocks are $d_P$-separated by more than $2\sqrt\varepsilon$.
>
> Then
> $$L^\star_D(\varepsilon)\;\ge\;\log_2\Big[\textstyle\sum_{i\le s}\binom{m}{i}(n-1)^i\Big]\;\ge\; s\log_2(n-1) + s\log_2(m/s).$$
>
> *Proof.* The $n^m$ candidates $c+\sum_i v^{(t_i)}_i$ lie in $\Theta_D$ by (1). Two differing in $k\le 2s$ blocks differ by a $k$-sparse vector with entries at most $\rho$, hence in $\mathcal T_{2s,\rho}\subseteq\mathcal D_{s,\rho}$ (Lemma 2.1), and are $d_P$-separated by (2): they are adjacent in $G_D(2\sqrt\varepsilon)$. By Theorem 7.2 a certificate is a proper colouring, so each colour class is a code of length $m$ over an alphabet of size $n$ with minimum distance at least $2s+1$. The Hamming bound caps each class at $n^m/\sum_{i\le s}\binom{m}{i}(n-1)^i$. $\square$

Hypothesis (1) is exactly the *silent* regime of §10 and holds verbatim for coordinates whose input mode the probes never visit — which §16 argues is the dominant case.

---

## 9. Achievability I: the data-free ceiling

Assume $\Theta\subseteq[-B,B]^h$. Set $\Delta = 2\sqrt{\varepsilon/(s\lambda^{(s)}_{\max})}$ where $\lambda^{(s)}_{\max} = \max_{\|v\|_0\le s}v^\top\Sigma v/\|v\|_2^2$. Let $k_j(\theta)=\lfloor(\theta_j+B)/\Delta\rfloor$, $M=\lceil 2\rho/\Delta\rceil+3$, $y_j = k_j(c)\bmod M$, and store the $2s$ Reed–Solomon parity symbols of $y$ over $\mathbb F_Q$ with $Q\ge\max\{M,h\}$.

> ### Theorem 9.1 (data-free ceiling)
> For every trusted set $D$, including the empty one,
> $$L^\star_D(\varepsilon) \;\le\; 2s\Big\lceil \log_2 \max\big\{ \lceil 2\rho/\Delta\rceil+3,\ h \big\}\Big\rceil \;=\; O\!\left(s\log h + s\log\big(1+\rho\sqrt{s\lambda^{(s)}_{\max}/\varepsilon}\big)\right).$$

The decoding is standard: unattacked coordinates are bit-identical so $d_H(\tilde y,y)\le s$; Berlekamp–Massey recovers $y$ and the error locator; the modulus $M>2\rho/\Delta+2$ lifts each residue uniquely.

**This is not new and should not be presented as though it were.** Recovering an $s$-sparse difference from an $O(s\log h)$-bit sketch is set reconciliation / invertible Bloom lookup tables (Minsky–Trachtenberg–Zippel; Eppstein–Goodrich). The only novelty is the modulo-$M$ step that puts $\rho$ rather than $B$ in the rate. It is recorded because §11 must be compared against it.

**It is also brittle in exactly the way a hash is.** The decoder assumes unattacked coordinates are bit-exact. Under benign drift — a different accelerator, a re-quantization — coordinates near cell boundaries change symbol, $d_H(\tilde y,y)\gg s$, and decoding fails. Within the stated threat model this is legal; as a criticism of hash-based integrity it would be hypocritical. Dithered or nested-lattice quantization is the fix and is not written down here.

---

## 10. What the data can and cannot remove

Before constructing a data-aware code, it is worth knowing what shape the invisible set has, because the obvious construction fails for a specific reason.

**The obstruction.** Reed–Solomon corrects a sparse error because sparsity and the code live in the same basis: coordinates are polynomial evaluations, and "few coordinates wrong" is what an MDS code sees. The trusted set contributes $\|\Phi_D v\|_\infty\le2\gamma$, which is **rotationally arbitrary**. Whitening it means applying $\Phi_{D,S}^{-1}$, and rotation destroys sparsity. "Shortening the code using $\operatorname{row}(\Phi_D)$" cannot work either: shortening deletes coordinates the decoder knows, and the decoder knows no *coordinate* of $e$ — only linear functionals of it, in general position with respect to the coordinate basis.

**Rotated danger is real.** Take coordinates whose feature columns satisfy a linear relation $\Phi_{D,G}\lambda = 0$ exactly on every sampled input, broken only on a rare mode. Then $v=\lambda$ is perfectly invisible while $\lambda^\top\Sigma\lambda>0$, and every individual coordinate is loudly exercised, hence safe alone. Such traps exist, are minimal dangerous supports of size $\ge2$, and §16 exhibits them.

**But they need every coordinate free.** Fix any one coordinate of such a group and the remaining slice is no longer in the kernel, so the data sees it. Measured on planted traps (§16): pinning any single coordinate collapses $\mathcal A$ from $0.377$ and $0.463$ to $\approx 0.026$, a factor of $15$–$18$, far below tolerance.

> **A rotated invisible direction ceases to exist as soon as one of its coordinates is pinned. Orientation therefore never has to be represented — only broken, and breaking it is a combinatorial act in the coordinate basis.**

That is the whole trick. The geometry is solved offline by the encoder, which knows $\Phi_D$, and hands the algebraic code two objects that live in the coordinate basis. Nothing rotates.

---

## 11. Achievability II: the data-aware code

### 11.1 The three quantities

All are functions of $D$ alone, computable before deployment.

> ### Definition 11.1 (invisible width, fragility)
> $$\alpha_j(D) \;=\; \sup\{\,|v_j| \;:\; v \in \mathcal N(D)\,\},
> \qquad
> \phi_j(D) \;=\; \frac{\alpha_j(D)\sqrt{\Sigma_{jj}}}{\sqrt\varepsilon}.$$

$\phi_j$ is **how far weight $j$ can drift without your evaluations noticing, measured in units of how much you would care.** Both factors are essential: a coordinate that is wholly unconstrained but functionally irrelevant costs nothing, and a uniform quantizer step pays for it anyway.

> ### Definition 11.2 (fragile coordinates)
> Let $\mathcal F_\theta$ be the family of **minimal** supports of vectors in $\mathcal N(D)$ that are dangerous at level $\theta$. A set $J^\star$ is a **fragile set** if it is a hitting set for $\mathcal F_\theta$: $J^\star\cap S\ne\emptyset$ for every $S\in\mathcal F_\theta$.

A hitting set, not a union. The decoder's obligation is that every residual $w\in\mathcal N(D)$ with $w|_{J^\star}=0$ is safe; since $\operatorname{supp}(w)\cap J^\star=\emptyset$, it suffices to **hit** each dangerous support. Two readings: an isolated fragile coordinate must be protected itself, but of a near-collinear cluster carrying a rotated dangerous direction, protecting **any one member** suffices (§10). Numerically the union gives $|J^\star|=h$ and the hitting set gives $|J^\star|=2$.

### 11.2 The code

Fix $\theta\in(0,1)$. Set

$$\Delta_j \;=\; \frac{\theta\sqrt\varepsilon}{2s\,\sqrt{\Sigma_{jj}}},
\qquad
M_j \;=\; \Big\lceil \frac{\alpha_j}{\Delta_j}\Big\rceil + 3 \;=\; \Big\lceil \frac{2s\,\phi_j}{\theta}\Big\rceil+3,$$

let $J^\star$ be a fragile set at level $(1-\theta)\sqrt\varepsilon$, and define the quantization slack

$$\eta_\Delta \;=\; \max_{|T|\le 2s}\ \max_i\ \sum_{j\in T}\Delta_j\,|(\Phi_D)_{ij}| .$$

All of $\alpha_j$, $\mathcal F_\theta$ and $J^\star$ are computed for $\mathcal N(D)$ taken at the inflated precision $2\gamma+\eta_\Delta$. There is no circularity: $\Delta_j$ depends only on $\varepsilon,s,\Sigma$.

**Encoder** (knows $c$, $D$). $k_j(c)=\lfloor (c_j+B)/\Delta_j\rfloor$; $y_j = k_j(c)\bmod M_j$ for $j\in J^\star$; store
$$\kappa \;=\; \mathrm{RS}_{2s}\big(y|_{J^\star}\big)\ \text{ over } \mathbb F_Q,\quad Q\ge\max\{|J^\star|,\ \max_j M_j\},$$
or $y|_{J^\star}$ outright when that is shorter.

**Decoder** (sees $D$, $\tilde c$, $\kappa$).
1. Form $\tilde y_j = k_j(\tilde c)\bmod M_j$ for $j\in J^\star$ and Berlekamp–Massey against $\kappa$ to recover $y|_{J^\star}$.
2. Return any $\hat c = \tilde c - \hat e$ with $\hat e\in\mathcal T_{s,\rho}$, $\hat c\in\Theta_D$, and $k_j(\hat c)\equiv y_j \pmod{M_j}$ for every $j\in J^\star$.

> ### Theorem 11.3 (data-aware ceiling)
> $$\boxed{\;L^\star_D(\varepsilon) \;\le\; \min\Big\{\ \sum_{j\in J^\star}\big\lceil\log_2 M_j\big\rceil,\ \ 2s\Big\lceil\log_2\max\big\{|J^\star|,\ \max_{j\in J^\star}M_j\big\}\Big\rceil\ \Big\}\;}$$
> and the decoder's output satisfies $d_P(\hat c,c)\le\sqrt\varepsilon$. Encoder and decoder run in $\tilde O(h)$ plus one $s$-sparse recovery solve on $\Phi_D$.
>
> *Proof.* The truth $c=\tilde c-e$ satisfies every constraint in step 2, so the search is non-empty. Step 1 succeeds because unattacked coordinates are bit-identical, so $d_H(\tilde y,y)\le|\operatorname{supp}(e)\cap J^\star|\le s$ and $2s$ parity symbols correct $s$ symbol errors.
>
> Let $\hat c$ be any candidate and $w = c-\hat c = \hat e - e \in \mathcal D_{s,\rho}$. Both $c,\hat c\in\Theta_D$, so $\|\Phi_D w\|_\infty\le2\gamma$ and $w\in\mathcal N(D)$.
>
> Fix $j\in J^\star$. Then $k_j(c)\equiv k_j(\hat c) \pmod {M_j}$, while $|k_j(c)-k_j(\hat c)| \le |w_j|/\Delta_j + 1 \le \alpha_j/\Delta_j+1 < M_j$. An integer congruent to $0$ mod $M_j$ with absolute value below $M_j$ is $0$, so $k_j(c)=k_j(\hat c)$ and $|w_j|<\Delta_j$.
>
> Split $w = w'+w''$ with $w'=w|_{J^\star}$. Since $|\operatorname{supp}(w)|\le 2s$,
> $$d_P(w') \;\le\; \sum_{j\in\operatorname{supp}(w')}|w'_j|\sqrt{\Sigma_{jj}} \;<\; 2s\cdot\Delta_j\sqrt{\Sigma_{jj}} \;=\; \theta\sqrt\varepsilon .$$
> Also $w''$ is a restriction of $w$, hence in $\mathcal D_{s,\rho}$, and $\|\Phi_D w''\|_\infty \le \|\Phi_D w\|_\infty + \|\Phi_D w'\|_\infty \le 2\gamma+\eta_\Delta$, so $w''\in\mathcal N(D)$ at the inflated precision. Since $\operatorname{supp}(w'')\cap J^\star=\emptyset$ and $J^\star$ hits every minimal dangerous support at level $(1-\theta)\sqrt\varepsilon$, $w''$ is not dangerous: $d_P(w'')\le(1-\theta)\sqrt\varepsilon$. Hence $d_P(w)\le\theta\sqrt\varepsilon+(1-\theta)\sqrt\varepsilon=\sqrt\varepsilon$. $\square$

**Extremes.** $J^\star=\emptyset$ gives $L=0$, recovering Theorem 5.1. $J^\star=[h]$ with $\alpha_j=2\rho$ recovers Theorem 9.1 up to the constant in $\Delta$. **Theorem 11.3 interpolates between them and is never worse than either.**

**The role of $\theta$.** Larger $\theta$ coarsens the quantizer (smaller $M_j$) but tightens the danger threshold (larger $J^\star$). The split is a free parameter of the construction and should be optimized numerically; §16 reports both $\theta$ regimes and the cost of the tighter one.

### 11.3 How tight is it?

Write $m=|J^\star|$ and $\phi=\max_{j\in J^\star}\phi_j$. Theorem 11.3 gives $L \lesssim 2s\log_2\max\{m,\,2s\phi/\theta\}$, while Theorem 8.2 with $n\asymp\phi$ gives $L^\star\gtrsim s\log_2\phi + s\log_2(m/s)$. Converse and achievability are in **the same two quantities**: how many coordinates are fragile, and how fragile they are.

> **DARC is within a factor $2$ of the sphere-packing bound whenever $\phi \gtrsim m$.** When $\phi < m$ the residual gap is exactly the classical alphabet-versus-length gap — Reed–Solomon needs $Q\ge$ the code length, and for small alphabets algebraic-geometry or BCH codes do better. That is a known coding-theoretic gap, not a defect of the reduction.

---

## 12. Computing the quantities

$\mathcal A(D)$, $\alpha_j$ and the minimum hitting set are all NP-hard, so a construction requiring them exactly would be vacuous. It does not require them.

> ### Proposition 12.1 (soundness of relaxation)
> Theorem 11.3 remains valid if $\alpha_j$ is replaced by any upper bound, $\mathcal F_\theta$ by any family containing it, and $J^\star$ by any hitting set of that family. Each substitution can only lengthen the certificate; none can break correctness.

So:

- **$\alpha_j$ without support enumeration.** Relax $\|v\|_0\le2s$ to $\|v\|_1\le 4s\rho$ and solve one LP per coordinate — $h$ LPs, no enumeration. Measured against exhaustive enumeration over all $\binom{18}{\le4}$ supports: width ratio $1.00$–$1.46$, costing $0$–$2\%$ of certificate bits, at $80$–$190\times$ lower cost.
- **Fragility screening.** For a support $S$, with $\|v\|_2 \le \min\{2\rho\sqrt{|S|},\ 2\gamma/\sqrt{\lambda_{\min}(\widehat\Sigma_{SS})}\}$,
  $$\mathcal A_S \;\le\; \min\Big\{\sqrt{\lambda_{\max}(\Sigma_{SS})}\,\|v\|_2,\ \ \sqrt{4\gamma^2 + \|\Sigma_{SS}-\widehat\Sigma_{SS}\|_{\mathrm{op}}\|v\|_2^2}\Big\},$$
  the second being Theorem 6.1. Both cost one small eigendecomposition and are sound; they are complementary, the second winning when $\widehat\Sigma\approx\Sigma$ and the first when $\lambda_{\min}(\widehat\Sigma_{SS})$ is large. Measured pruning: **45–80%** of supports discarded before any hard solve.
- **Hitting set.** NP-hard, but greedy is a $\log$-approximation and any hitting set is sound.

---

## 13. The second currency, and its limit

The certificate is *any* function of $(c,D)$, so it has a dialect beyond parity: **extra mantissa bits on trusted labels.** The encoder knows $f_c(x_i)$ exactly; since the decoder holds $y_i$ to $\pm\gamma$, transmitting which $2^{-b}$ sub-cell the true value occupies costs $b$ bits and replaces $\gamma$ by $\gamma/2^b$ on that row. Parity pins *coordinates* and is basis-locked; refinement tightens *halfspaces* at arbitrary orientation. Refinement only shrinks $\mathcal N(D)$, so dangerous supports leave and never enter, and the split can be optimized greedily.

Call $v\in\mathcal N(D)$ **silent** if $\Phi_D v = 0$ and **audible** otherwise, and let $\mathcal N^0 = \mathcal N(D)\cap\ker\Phi_D$ be the **silent core**.

> ### Theorem 13.1 (the two dialects)
> 1. *(Refinement floor.)* No refinement of any subset of rows to any depth removes a single element of $\mathcal N^0$. If $\mathcal N^0$ contains a dangerous vector, parity bits are **mandatory**, and $L^\star_D(\varepsilon)$ is bounded below by Theorem 8.2 applied to the silent core.
> 2. *(Refinement rate.)* For an audible dangerous direction $\hat v$ with $\|\hat v\|_\infty=1$, per-unit harm $p=\|\Sigma^{1/2}\hat v\|_2$ and audibility $z=\max_i|\langle\sigma(x_i),\hat v\rangle|$, refining the row attaining $z$ by $b = \lceil\log_2(2\gamma p/(z\sqrt\varepsilon))\rceil$ bits removes it. When label precision rather than the $\ell_\infty$ cap binds, this is exactly $b=\lceil\log_2(\mathcal A_S/\sqrt\varepsilon)\rceil$.
> 3. *(Parity rate.)* Hitting the same support by parity costs $\lceil\log_2 M_j\rceil$ for the cheapest $j\in S$, **independent of audibility**.
> 4. *(Crossover.)* Parity's cost is flat in audibility; refinement's grows as $\log_2(1/z)$ and diverges at $z=0$. Each dangerous direction therefore has a single crossover.
>
> *Proof of (1).* If $\Phi_D v=0$ then $|\langle\sigma(x_i),v\rangle| = 0 \le 2\gamma/2^b$ for every row and every depth. The constraint is satisfied vacuously. $\square$

**The catch, and it is the point.** By Theorem 6.1, a direction is dangerous only insofar as $v^\top(\Sigma-\widehat\Sigma_D)v$ is large — only insofar as it acts on inputs the probes under-sample. In the limiting case, a mode never sampled, the direction is *exactly silent*, and refinement has nothing to sharpen. **Danger pushes audibility toward zero.** In §16 all three minimal dangerous supports are exactly silent and the hybrid degenerates to pure parity.

> **Spending the certificate on behaviour buys resolution on directions the probes already see, and danger lives precisely where they do not.**

Refinement adds precision to existing rows; it cannot add rows. A *new probe* that activates the missing mode does convert silent into audible, which is what the sample-size sweeps of §16 show. So the three resources are strictly ordered:

| resource | acts on | clears the silent core? |
|---|---|---|
| sharper labels | existing rows | **no** |
| more probes | the row space | **yes**, if they hit the mode |
| parity bits | coordinates | **yes**, always, at cost per fragile coordinate |

**Rows beat precision; and when the right row does not exist, only parity works.**

---

## 14. The ladder: detect, localize, repair

> ### Definition 14.1
> **Functional detection:** decide whether $d_P(\tilde c,c)>\varepsilon$. **Localization:** output $\operatorname{supp}(\tilde c-c)$. **Repair:** output $\hat c$ with $d_P^2(\hat c,c)\le\varepsilon$.

| Task | Protected bits | Governed by |
|---|---|---|
| Bit-exact integrity | $O(1)$ — a hash | nothing; see caveat |
| Functional detection | $0$ iff $\mathcal A(D)\le\sqrt\varepsilon$ | **radius** of $\mathcal N(D)$ |
| Localization | $\log_2$ of the number of dangerous supports | **support structure** of $\mathcal N(D)$ |
| Repair to $\varepsilon$ | Theorem 8.2 $\le L^\star \le$ Theorem 11.3 | **chromatic number** of $G_D$ |

The three tasks are three functionals of one object, which is the content of §7.

> **Caveat on the top row.** A cryptographic hash detects *any* bit change, including benign ones: different floating-point rounding on a new accelerator, deployment-time quantization, a legitimate fine-tune. It is brittle in exactly the way practitioners complain about, and yields nothing toward localization or repair. The $O(1)$ figure is for bit-exact integrity only. This document does not claim to improve on the functional-detection literature; it observes that when $\mathcal A(D)$ is small the trusted probes deliver detection at zero stored cost, and that the interesting gap is between detection and repair. Note also that §9's construction shares the hash's brittleness under drift.

**The separation worth stating** is the last two rows: detection can be free while repair is not. The data tells you *that* something functionally significant happened, and often *where*; the certificate is still required to recover *what the values were*.

---

## 15. Worked instance: the LM head

Let $\sigma(x)\in\mathbb R^{d}$ be a transformer's final hidden state and $W\in\mathbb R^{V\times d}$ the unembedding, so $z(x)=W\sigma(x)$. Tampering is $\widetilde W = W+E$, $\|E\|_0\le s$. Per output coordinate $v$, $\Delta z_v(x_i)=\langle E_v,\sigma(x_i)\rangle$, so **the problem decouples into $V$ instances of §3 sharing one sensing matrix** $\Phi_D\in\mathbb R^{N\times d}$. For Llama-3.1-8B: $V=128{,}256$, $d=4096$, $Vd\approx5.25\times10^8$ mutable parameters governed by one $4096\times4096$ object. Applying Theorem 9.1 with $h=Vd$ gives $\log_2 h\approx29$, so $s=14$ costs $L\le 2\cdot14\cdot29\approx812$ bits $\approx102$ bytes, independent of $D$; Theorem 11.3 can only improve on that.

**Two caveats that matter more than the arithmetic.**

The decoupling assumes you recorded the **full logit vector** at every probe. Nobody does. Under top-$k$ or argmax observation the measurements become non-linear and comparison-based, and rows of $W$ for tokens that never surface are unconstrained by any number of probes — $\alpha_j$ sits at its cap and Theorem 6.1's second term never shrinks. The regime treated here is the easy one.

Bit-flip attacks on the LM head are documented, reporting $3$–$14$ flips on 8B–14B models with accuracy on unrelated benchmarks preserved. That last property is precisely the statement that the attack lies close to $\mathcal N(D)$ for the evaluation sets used.

---

## 16. Measurements

All quantities below are computed on synthetic feature geometry with **exact** invisible sets, not estimated. The purpose is to validate the construction, not to characterize real networks; §17 lists what is missing.

**Setting A ($s=1$, $h=44$).** 32 densely-exercised coordinates, 12 coordinates active only on a $\tau_j$-fraction of inputs ($\tau$ from $0.5$ to $1.2\times10^{-4}$), and 6 near-duplicate pairs. Invisible set computed by halfspace intersection over all $\binom{44}{2}$ supports.

```
     N    A(D)   |J*|         J*      Thm 11.3   Thm 9.1
     4   1.273     36  [0,...,40]           12        12
    16   0.636     28  [2,...,40]           10        12
    32   0.300     16  [0,...,40]            8        12
    64   0.300      2    [38, 39]            4        12
   256   0.181      1        [39]            2        12
  1024   0.141      0          []            0        12
```

Graceful degradation $12\to10\to8\to4\to2\to0$ against a ceiling pinned at $12$; $J^\star$ converges to exactly the coordinates whose input mode the probes have not visited.

**Near-collinearity contributes almost nothing.** Forcing near-duplicate pairs at separation $\delta$ and measuring exactly, the gain in $\mathcal A$ from pairing over a single coordinate is $1.3\times$ at $\delta=0.2$ and $1.0\times$ at $\delta=0.002$. The $\ell_\infty$ cap binds first, and the direction it permits is functionally null — consistent with Theorem 6.1, since $\Sigma\approx\widehat\Sigma_D$ on well-sampled directions.

**Setting B ($s=2$, $h=18$), with planted rotated traps.** Two groups constructed as in §10 — $\{13,14\}$ with $\lambda=(1,-1)$ and $\{15,16,17\}$ with $\lambda=(1,1,-1)$ — plus three isolated rare coordinates. All $4047$ supports of size $\le4$ enumerated.

```
     N   screened   minimal dangerous supports        J*           Thm 11.3   Thm 9.1
    64   2231/4047  (11,), (13,14), (15,16,17)   [11,13,16]              11        20
   256   1039/4047  none                         []                       0        20
  1024    830/4047  none                         []                       0        20
```

The minimal dangerous supports recovered are **exactly** the three planted structures, and the greedy hitting set takes one coordinate from each. Pinning any single coordinate of a trap collapses $\mathcal A$ from $0.377$/$0.463$ to $\approx0.026$.

**The two dialects.** On a trap family with tunable audibility $\delta$ ($N=64$, $\sqrt\varepsilon=0.1414$):

```
   delta   audibility   refine bits   parity bits   cheaper
  0.0000     0.00e+00           inf             5   parity
  0.0010     1.82e-03             6             5   parity
  0.0030     7.22e-03             4             5   refine
  0.0300     7.86e-02             1             5   refine
```

A single crossover at $\delta\approx2\times10^{-3}$, where $\log_2(1/\delta)$ meets the flat parity cost. On Setting B itself, all three minimal dangerous supports have audibility exactly $0$: refinement is impossible and the hybrid is pure parity.

**End-to-end decoding.** Under adversarial evaluation — the attacker plays the $\mathcal A(D)$-maximizer and the decoder returns the *worst* candidate consistent with labels, sparsity and congruences — Theorem 11.3's guarantee holds with **zero violations** across all settings, at observed error $0.22$–$0.24\,\sqrt\varepsilon$ against the $\sqrt\varepsilon$ bound. The looser constant $\theta$ that yields $d_P\le3\sqrt\varepsilon$ produces the small certificates tabulated above; tightening to $d_P\le\sqrt\varepsilon$ roughly doubles $|J^\star|$ and adds about two bits per fragile coordinate. **The radius-versus-diameter slack of §5 is not free.**

---

## 17. Limitations

Stated plainly, because several of these are more important than the results above.

**The accounting is incomplete, and this is the central weakness.** Only $L$ is charged. The trusted set is treated as given, on the grounds that it is typically pre-existing. But every guarantee in §6 and §11 requires $D$ to be *tamper-proof*: if the adversary can touch $D$, they all evaporate. That is protected storage, and at the scale of §15 it is larger than the layer being protected. The honest object is a joint budget $N\beta + L$ — bits spent sketching behaviour versus bits spent sketching parameters — and §13 is only the first step toward it.

**The observation model is the easy one.** §2.4 records a real number per probe at precision $\gamma$. The realistic regime is top-$k$ or generated text, where measurements are comparison-based and rarely-surfaced output rows are unconstrained by any $N$ (§15).

**Other gaps.**
- $\Sigma$ is treated as known; in practice it is estimated, so $\mathcal A(D)$, $\phi_j$ and $J^\star$ are themselves estimates.
- Theorem 7.2 is a sandwich, not an equality; the factor-$4$ gap is not closed.
- The chromatic number between $\omega$ and $\Delta+1$ is not located; Theorem 11.3 sits strictly inside.
- §9 and §11 both assume unattacked coordinates are bit-exact and break under benign drift.
- Randomized encoders are not considered; §2.6 fixes deterministic maps.
- Hidden-layer tampering is out of scope: the model is exactly linear only in the output-layer parameters.
- All measurements are on synthetic geometry. Nothing here has been measured on a real network, and §16's settings were built to exercise the construction, not sampled from nature.

---

## 18. Literature

**Classical antecedents — cite, claim nothing.** Error correction as sparse recovery, $r=\Phi e$ (Candès–Tao 2005). Zero-error source coding with decoder side information as a chromatic number (Witsenhausen 1976; Alon–Orlitsky 1996; Orlitsky–Roche 2001) — the framework of §7. Syndrome coding with decoder side information (Slepian–Wolf; DISCUS). Restoring a corrupted copy from a short fingerprint: document exchange (Belazzougui; Haeupler), set reconciliation (Minsky–Trachtenberg–Zippel), IBLTs — **§9 is an instance of these**. Coding for memories with defects known to the encoder (Kuznetsov–Tsybakov) and for localized errors (Bassalygo–Gelfand–Pinsker) — the closest classical analogues to §2.6's information structure, in which the decoder's side information is the source itself passed through an adversarially chosen channel that has read the codebook. Restricted eigenvalue and small-ball methods (Bickel–Ritov–Tsybakov; Mendelson). Hamming and Singleton bounds; algebraic-geometry codes for the small-alphabet regime of §11.3. One-bit compressed sensing (Boufounos–Baraniuk; Plan–Vershynin) for the observation model §17 says is missing.

**Behaviour determines the last layer.** Carlini et al., *Stealing Part of a Production Language Model* (ICML 2024), recover a production model's final layer from API logits by SVD, requiring $n>h$ queries. This is the closest work to §3 and solves a different problem: with no side information the identifiable object is $\operatorname{col}(W)$, so recovery is up to an unknown gauge, and the $n>h$ requirement is the cost of spanning that subspace from scratch. Here $\tilde c$ is in hand — no subspace to span, no gauge to fix — and the unknown is an $s$-sparse residual. Neither result implies the other; what they supply is independent confirmation that $\Phi_D$ is the operative object.

**Attacks.** Progressive bit search (BFA, ICCV'19); T-BFA; TBT; ProFlip; DeepHammer (USENIX Sec'20); OneFlip (USENIX Sec'25); and for transformers AttentionBreaker, SilentStriker, and targeted LM-head flip attacks. These establish that $s$ is small, $\rho$ bounded, and that attackers already optimize for invisibility on standard benchmarks.

**Detection.** Sensitive-Sample Fingerprinting (CVPR'19) — detection only, first-order heuristic probes, no optimality theory; §13 is a direct argument against its implicit premise. Model Equality Testing (ICLR'25). HASHTAG / AccHashtag, DeepDyve, VerIDeep, BitShield.

**Recovery systems.** RADAR; weight reconstruction (DAC'20); NeuroPots (USENIX Sec'23); Aegis; ObfusBFA; WeightSentry; NAPER. For LLMs, LM-Fix uses fixed test vectors plus redundancy buffers costing 1.9–5% of model memory; BitFlipScope localizes and recovers LLM bit flips. All are constructive and heuristic: none proves a lower bound, and none treats the trusted set as a measurement. Note that the strong baseline is not these systems but *re-downloading the checkpoint*; the setting where a $10^2$-byte budget is decisive is one where protected storage is genuinely scarce — a TPM's NV region, on-chip fuses, a sealed enclave, an on-chain commitment.

**Terminology.** *Provable Repair of Deep Neural Networks* (PLDI'21, PLDI'23) means repairing a network to satisfy a specification: a different problem. "Certificate" collides with certified robustness. **Repair budget** for the quantity and **restoration sketch** for the object are the names used here.

---

## 19. What is left

1. **The joint budget.** Charge $N\beta+L$ and characterize the achievable region. §13 shows the two currencies are not interchangeable — one of them cannot buy the silent core at all — which makes the region's shape a real question rather than a rate comparison.
2. **Coarse observations.** Top-$k$ and argmax, where $\gamma$ becomes a priced design variable rather than a constant.
3. **Probe design as a minimax.** §13 reduces this to a concrete stake: every input mode the probe set misses becomes a silent core payable only in parity. The defender chooses $\{x_i\}$, the adversary then chooses the least visible $s$-sparse $e$, so the problem is $\max_{\{x_i\}}\min_{\|e\|_0\le s}\text{visibility}(e;\Phi_D)$ — not a maximization of average or per-direction visibility, which is what first-order heuristics produce and what an adaptive adversary defeats. The rows of $\Phi_D$ cannot be designed freely: each must be a realizable $\sigma(x)$, so the design set is the network's feature manifold, not $\mathbb R^h$. That constraint is what makes the problem more than a corollary of compressed sensing.
4. **Measurement on real networks.** $\Sigma-\widehat\Sigma_D$ on sparse supports, $\phi_j$, and $|J^\star|$ for an actual LM head. Everything in §16 is synthetic.
5. **Drift-robust quantization**, closing the gap §9 and §11 share with hashing.
6. **Hidden-layer tampering**, which needs a controlled linearization with a margin condition.
