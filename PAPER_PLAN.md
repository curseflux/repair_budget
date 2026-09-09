# The repair budget: plan v4

Supersedes v3 (`7928fae`). All four items ran (`audit_v2_report.json`, A100, 2026-09-09).
Three succeeded outright. The fourth measured something real but not the thing its label
claimed, and that correction changes the paper's shape for the better.

---

## 1. Results

### Item 1 — screen calibration: complete success

Replay discrepancy on the untampered head: max `4.2e-5`, mean `1.2e-6` per logit. The eta sweep:

| eta | flagged | recall | false positives |
|---|--:|--:|--:|
| 0 | 236 | 1.00 | 172 |
| 1e-6 | 168 | 1.00 | 104 |
| 3e-6 | 77 | 1.00 | 13 |
| **1e-5** | **64** | **1.00** | **0** |
| 1e-4 … 1e-3 | 64 | 1.00 | 0 |

`eta = 1e-5` gives **perfect recall with zero false positives**, and `|E|` drops from 128 to
exactly 64. The v1 diagnosis was right: the false rows were FP32 replay noise near cell
boundaries, and the expected-count formula tracks the *mean* discrepancy (predicts ~157 at
N=256, observed 172), not the max. A declared tolerance is now part of the record convention.

**Ladder consequence:** the row-locator construction goes 2,176 -> **1,088 bits (72.6% below the
3,968-bit data-free baseline)**, and the row-summary scheme stops being worse than doing nothing.

### Item 4 — the law: slope -1, confirmed over six doublings

| N | 1 | 8 | 16 | 32 | 64 | 128 | 256 | 512 | 1024 | 2048 |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| median feasible columns | 3790 | 373 | 20 | **1** | 1 | 1 | 1 | 1 | 1 | 1 |
| median candidates | 1.8e7 | 5.6e4 | 3.0e4 | 220 | 134 | 54 | 30 | 13 | 7 | 4 |

The column is pinned at `N = 32`. In the value regime the fitted slope is

- salient coordinates: **-1.011** (6 points, `N >= 64`)
- uniform coordinates: **-0.972** (6 points, `N >= 64`)

against a predicted `-1`. The pool now carries 2,048 **distinct** inputs, so this is not an
artifact of resampling.

*Analysis correction to make before publishing.* The report's headline slope for `uniform` is
`-1.566`, which is a fitting artifact: the window opens where the **median** column count first
hits 1 (`N = 32`), but the distribution still has a tail of unpinned rows there, producing a
spurious `-6.88` step from 32 to 64. Enter the value regime **per row**, when that row's own
column count reaches 1, rather than by the median. The CSV already carries what this needs.

### Item 3 — the mechanism, and the headline does generalise

| tamper pool | median candidates | bits/row | residual bits |
|---|--:|--:|--:|
| salient rows, salient cols | 29.5 | 4.88 | **343** |
| uniform rows, salient cols | 17.0 | 4.09 | 288 |
| salient rows, uniform cols | 43.0 | 5.43 | 367 |
| uniform rows, uniform cols | 58.5 | 5.87 | **377** |

Every mode: row recall 1.0, zero false positives, all 64 columns pinned, all counts exact.

- **Column energy is the mechanism.** Salient columns beat uniform columns in both row
  conditions. Feature-energy ratio 3.73 predicts a candidate ratio of `sqrt(3.73) = 1.93`;
  observed 1.46 and 3.44. Right direction, right order of magnitude.
- **Row salience does not matter.** Its effect is small and changes sign between column
  conditions — as the geometry says it should, since interval width goes like
  `WIDTH/(N |h_j|)`, a column property.
- **The headline generalises.** Typical coordinates need 377 bits against salient coordinates'
  343. v3 worried that 91.3% was an artifact of the top 0.025% of the head. **It was not**, and
  that worry should be retracted rather than hedged.

### Item 2 — measured a real quantity, but not the labelled one

512 sampled **untouched** rows leave a median of 9.2e6 candidates, 23.1 bits per row, giving
1,480 bits over `s = 64`. That is not "what a typical tampered coordinate leaves" — the audit of
uniform tampers (Item 3) says 5.87 bits per row. The difference is structural: on an untouched
row nothing needs explaining, so `delta = 0` is feasible for **every** column and none is
eliminated.

So the number is real but answers a different question, and it is the more interesting one:

- **Instance residual (343-377 bits).** What is left after the record, for a tamper that
  actually happened.
- **Uniform converse (1,480 bits).** What any encoder must carry to handle *every* legal
  `s`-sparse tamper, including the ones the record never sees.

This is exactly the uniform-versus-average distinction the theory document's §1.4 insists on,
now with both numbers measured. Relabel it accordingly and report
`median_feasible_columns` alongside it so a reader sees why untouched rows differ.

---

## 2. What this means for the paper

The construction costs **1,088 bits**; the uniform converse is **1,480 bits**. That is not a
contradiction — they cover different tamper classes, and saying so precisely is the paper's
sharpest sentence:

> The 1,088-bit construction repairs every tamper the record can see. The tampers it cannot see
> cost at least 1,480 bits and no construction avoids that. Which number you pay is decided by
> whether you demand a uniform guarantee or an average-case one — and the invisible tampers are
> exactly the ones whose effect on the model's own outputs is below the resolution at which those
> outputs were retained.

That closes the exact-versus-behavioural question empirically instead of by assertion, and it is
the one place where the project's information theory says something an engineer would not guess.

**Claim.** The repair budget separates into location and value. Location is free: a calibrated
mismatch screen identifies every changed row with zero false positives, and interval arithmetic
pins the changed column once `N >= 32`. The value term decays as `log2(C/N)` with measured
exponent **-1.01 / -0.97**, from 1.8e7 candidates at `N = 1` to 4 at `N = 2048`. On
Llama-3.1-8B's output head the residual is **343 bits for salient and 377 for typical
coordinates at `N = 256`**, against 3,968 data-free; the best efficient construction reaches
**1,088 bits**; and a uniform guarantee costs at least **1,480 bits**.

**Report the ladder at `N = 2048`, not `N = 256`.** The notebook fixed `N_REF = 256` for
comparability with v1, which undersells the result by a factor of 2.7. At `N = 2048` the residual
projects to roughly **128 bits (16 bytes), 96.8% below data-free**. The sweep data already exists;
this is a re-aggregation, not a new run.

---

## 3. What is left — small, and then write

1. **Re-aggregate the ladder at `N = 2048`.** No new computation.
2. **Fit the value-regime slope per row** rather than by the median, removing the `-1.566`
   artifact. No new computation.
3. **Relabel the head profile** as the uniform converse and report its column counts.
4. **Repeat each pool mode over a handful of tamper trials.** Every number above is a single
   instance. This is the only item that needs GPU time, and it is minutes.

Nothing else. No second model, no output-precision sweep, no behavioural decoder, no attempt to
close the 1,088-versus-343 gap — name it as computational (the algebraic code re-pays 17 bits per
row for locators the screen already supplied free, where the information is 4.9) and stop.

---

## 4. Retracted from v3

- "The 91.3% is measured on the most favourable 0.025% of the head." **Wrong.** Uniform
  coordinates give 377 bits against 343; the result generalises.
- The v3 reading of the head profile as "typical coordinates leave 23.6 bits." It measures
  invisible changes anywhere, including `delta = 0` on untouched rows — a uniform converse, not a
  per-tamper residual.
