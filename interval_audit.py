"""Exact interval arithmetic for the repair-budget audit.

Under the one-change-per-row model, the set of numerical changes to column j of row v
consistent with N retained output codes is an interval. These routines compute it, count
the admissible weight labels in it, and verify or estimate the count exactly.

Nothing here reads the original checkpoint or the tamper. Callers pass the damaged row,
the retained features, and the retained codes.

All reductions are chunked over samples, so N is bounded by the retained record rather
than by device memory.
"""
from __future__ import annotations

import math

import numpy as np
import torch

__all__ = [
    "bf16_table", "cell_bounds", "row_intervals", "count_candidates",
    "verify_row", "estimate_row", "value_consistent",
    "replay_discrepancy", "screen_rows", "screen_eta_sweep",
]


# ---------------------------------------------------------------- alphabet

def bf16_table():
    """Ascending finite BF16 values and their bit patterns.

    Returned as a pair so counting a range is a searchsorted rather than bit twiddling.
    Signed zeros both appear: exact-symbol recovery distinguishes them.
    """
    pat = torch.arange(65536, dtype=torch.int32)
    val = pat.to(torch.int16).view(torch.bfloat16).float().numpy()
    finite = np.isfinite(val)
    order = np.argsort(val[finite], kind="stable")
    values = val[finite][order].astype(np.float32)
    labels = pat.numpy()[finite][order].astype(np.int64)
    assert np.all(np.diff(values) >= 0)
    return values, labels


# ---------------------------------------------------------------- cells

def cell_bounds(codes, R, width):
    """Lower and upper edges of the quantizer cells named by `codes`."""
    q = codes.to(torch.float32)
    return (-R + q * width), (-R + (q + 1) * width)


# ---------------------------------------------------------------- intervals

def row_intervals(z, h, codes_row, R, width, slack, rho, chunk=1024):
    """Feasible delta interval per column for one row.

    z          (D,)   damaged weight row
    h          (N, D) retained features
    codes_row  (N,)   retained ORIGINAL codes for this row
    slack             numerical tolerance; must cover the float64-vs-float32 gap for the
                      interval to be an OUTER bound (calibrate with `replay_discrepancy`)

    Returns (lo, hi, feasible) as float64/bool numpy arrays of length D.

    Reduced in sample chunks, so peak memory is O(chunk * D) rather than O(N * D).
    """
    D = z.shape[0]
    lo = torch.full((D,), -float(rho), device=z.device, dtype=torch.float64)
    hi = torch.full((D,), float(rho), device=z.device, dtype=torch.float64)
    dead = torch.zeros(D, dtype=torch.bool, device=z.device)
    for s in range(0, h.shape[0], chunk):
        hb = h[s:s + chunk]
        cur = (hb @ z).double()
        a_edge, b_edge = cell_bounds(codes_row[s:s + chunk], R, width)
        a = a_edge.double() - cur - slack
        b = b_edge.double() - cur + slack
        hb = hb.double()
        pos, neg = hb > 0, hb < 0
        zer = ~(pos | neg)
        safe = torch.where(zer, torch.ones_like(hb), hb)
        inf = torch.tensor(float("inf"), device=z.device, dtype=torch.float64)
        lo_c = torch.where(pos, a[:, None] / safe, torch.where(neg, b[:, None] / safe, -inf))
        hi_c = torch.where(pos, b[:, None] / safe, torch.where(neg, a[:, None] / safe, inf))
        lo = torch.maximum(lo, lo_c.amax(0))
        hi = torch.minimum(hi, hi_c.amin(0))
        # A zero feature cannot explain a sample whose damaged logit left the original cell.
        dead |= (zer & ((a[:, None] > 0) | (b[:, None] < 0))).any(0)
    feasible = (lo <= hi) & ~dead
    return lo.cpu().numpy(), hi.cpu().numpy(), feasible.cpu().numpy()


def count_candidates(z, lo, hi, feasible, values):
    """Admissible labels per column: BF16 values in [z+lo, z+hi].

    Closed ends plus the slack make this an UPPER bound on the true count.
    Returns (counts, left, right) with left/right indexing `values`.
    """
    zc = z.double().cpu().numpy()
    left = np.searchsorted(values, (zc + lo).astype(np.float32), side="left")
    right = np.searchsorted(values, (zc + hi).astype(np.float32), side="right")
    counts = np.where(feasible, np.maximum(right - left, 0), 0).astype(np.int64)
    return counts, left, right


# ---------------------------------------------------------------- exact / estimated counts

def _codes_match(z, h, codes_row, j, cand, R, width, chunk, eta=0.0):
    """Boolean mask over `cand`: does putting cand[k] at column j reproduce every code?

    A logit counts as consistent with its retained cell when it falls inside that cell
    widened by `eta`. At eta = 0 this is exactly an equality test on the codes, since
    Q(x) == q iff the cell edges bracket x.

    `eta` must be the declared record tolerance whenever the cached codes were produced by
    a different arithmetic path from `h @ z` -- a different batch shape is enough. Otherwise
    FP32 replay noise rejects genuine candidates, the true original among them, at a rate of
    about N * 5e-6 per row on the Llama head.
    """
    cur = h @ z
    hj = h[:, j]
    lo_e, hi_e = cell_bounds(codes_row, R, width)
    out = torch.zeros(len(cand), dtype=torch.bool, device=h.device)
    for s in range(0, len(cand), chunk):
        d = cand[s:s + chunk] - z[j]
        zlog = cur[None, :] + d[:, None] * hj[None, :]
        out[s:s + chunk] = ((zlog >= lo_e[None, :] - eta)
                            & (zlog < hi_e[None, :] + eta)).all(1)
    return out


def value_consistent(z, h, codes_row, j, value, R, width, eta=0.0, chunk=4096):
    """Does putting `value` at column j of this row reproduce the whole retained record?

    A one-candidate `_codes_match`. Use it to check a specific weight -- for instance the
    true original during evaluation -- without enumerating the column.
    """
    cand = torch.as_tensor([float(value)], device=h.device, dtype=h.dtype)
    return bool(_codes_match(z, h, codes_row, int(j), cand, R, width, chunk, eta)[0])


def verify_row(z, h, codes_row, left, right, counts, values, R, width, cap,
               chunk=4096, eta=0.0):
    """Exact count: keep only labels that reproduce every retained code.

    Sound because the interval is an outer bound. Returns (total, per_column) or
    (None, None) when the total exceeds `cap`.
    """
    if int(counts.sum()) > cap:
        return None, None
    per_col = np.zeros_like(counts)
    for j in np.nonzero(counts > 0)[0]:
        cand = torch.as_tensor(values[left[j]:right[j]], device=h.device, dtype=h.dtype)
        per_col[j] = int(_codes_match(z, h, codes_row, int(j), cand, R, width,
                                      chunk, eta).sum())
    return int(per_col.sum()), per_col


def estimate_row(z, h, codes_row, left, right, counts, values, R, width,
                 n_samples=2048, rng=None, conf=0.95, chunk=4096, eta=0.0):
    """Unbiased estimate of the exact count when the interval set is too large to enumerate.

    Draws labels uniformly from the interval set (columns weighted by their share), verifies
    them, and scales the hit rate by the interval total. Returns a dict including a one-sided
    lower confidence bound, which is what a converse may quote.
    """
    rng = rng or np.random.default_rng(0)
    total = int(counts.sum())
    if total == 0:
        return {"interval_total": 0, "estimate": 0.0, "lower": 0.0, "upper": 0.0,
                "hits": 0, "draws": 0, "method": "empty"}
    cols = np.nonzero(counts > 0)[0]
    probs = counts[cols] / total
    draws = min(n_samples, total)
    picked = rng.choice(len(cols), size=draws, p=probs)
    hits = used = 0
    for ci in np.unique(picked):
        j = int(cols[ci])
        k = int((picked == ci).sum())
        # Uniform within the column, with replacement: the pair (column, index) is then
        # uniform over the whole interval set, so hits/used estimates the surviving share.
        idx = left[j] + rng.integers(0, right[j] - left[j], size=k)
        cand = torch.as_tensor(values[idx], device=h.device, dtype=h.dtype)
        hits += int(_codes_match(z, h, codes_row, j, cand, R, width, chunk, eta).sum())
        used += k
    draws = used
    p = hits / draws
    # Wilson interval: valid at p = 0 or 1, unlike the normal approximation.
    zc = {0.90: 1.6449, 0.95: 1.9600, 0.99: 2.5758}[conf]
    denom = 1 + zc * zc / draws
    centre = (p + zc * zc / (2 * draws)) / denom
    half = zc * math.sqrt(p * (1 - p) / draws + zc * zc / (4 * draws * draws)) / denom
    return {"interval_total": total, "estimate": p * total,
            "lower": max(0.0, centre - half) * total,
            "upper": min(1.0, centre + half) * total,
            "hits": hits, "draws": draws, "method": "subsample"}


# ---------------------------------------------------------------- replay noise and the screen

def replay_discrepancy(h, head, R, width, batches=(32, 8), chunk=32):
    """Measure how far recomputed logits move when only the batch shape changes.

    Returns the max and mean absolute difference between two recomputations of the same
    logits at different batch sizes, plus the implied fraction of (sample, row) pairs that
    could flip a cell. This is the numerical quantity a screen tolerance must cover; it uses
    no cached codes and no original checkpoint.
    """
    b1, b2 = batches
    max_abs = 0.0
    sum_abs = 0.0
    n = 0
    for s in range(0, h.shape[0], chunk):
        hb = h[s:s + chunk]
        a = torch.cat([hb[i:i + b1] @ head.T for i in range(0, len(hb), b1)])
        b = torch.cat([hb[i:i + b2] @ head.T for i in range(0, len(hb), b2)])
        d = (a - b).abs()
        max_abs = max(max_abs, float(d.max()))
        sum_abs += float(d.sum())
        n += d.numel()
    mean_abs = sum_abs / max(n, 1)
    return {"max_abs_logit_diff": max_abs, "mean_abs_logit_diff": mean_abs,
            "cells": width, "implied_flip_fraction": min(1.0, 2 * max_abs / width)}


def screen_rows(h, codes, head, R, width, eta, chunk=32):
    """Rows whose recomputed logits leave the retained cell by more than `eta`.

    eta = 0 reproduces an exact code comparison. A positive eta declares a numerical
    tolerance, so replay noise near a cell boundary no longer counts as a change.
    Returns (flagged_row_indices, worst_excursion_per_row).
    """
    V = head.shape[0]
    flagged = torch.zeros(V, dtype=torch.bool, device=head.device)
    worst = torch.zeros(V, dtype=torch.float32, device=head.device)
    for s in range(0, h.shape[0], chunk):
        cur = h[s:s + chunk] @ head.T
        a_edge, b_edge = cell_bounds(codes[s:s + chunk].to(head.device), R, width)
        excursion = torch.maximum(a_edge - cur, cur - b_edge)   # >0 means outside the cell
        worst = torch.maximum(worst, excursion.amax(0))
        flagged |= (excursion > eta).any(0)
    return torch.nonzero(flagged).flatten().cpu().numpy(), worst.cpu().numpy()


def screen_eta_sweep(h, codes, head, R, width, etas, true_rows, chunk=32):
    """Recall and false positives of the screen as the tolerance varies.

    A row is flagged at tolerance eta exactly when its worst excursion exceeds eta, so one
    pass over the record answers every eta. `true_rows` is evaluator-side scoring only: pick
    the smallest eta that keeps recall at 1.0 while removing the numerical false positives.
    """
    truth = set(int(r) for r in np.unique(true_rows))
    _, worst = screen_rows(h, codes, head, R, width, float("inf"), chunk)
    rows = []
    for eta in etas:
        got = set(int(r) for r in np.nonzero(worst > eta)[0])
        rows.append({"eta": float(eta), "flagged": len(got),
                     "caught": len(got & truth), "recall": len(got & truth) / max(1, len(truth)),
                     "false_positives": len(got - truth)})
    return rows, worst
