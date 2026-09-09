"""Re-aggregate the audit outputs. No GPU, no model, no new measurement.

Reads `sweep_vs_N.csv` written by the v2 notebook and produces:

  * the value-regime slope fitted PER ROW, entering the regime when that row's own
    column count reaches 1 (the report's median-based window opens too early and
    produced a spurious -1.566 for the uniform pool);
  * the residual information in bits at every N, so the ladder can be quoted at the
    largest N measured rather than at N=256;
  * the full ladder at a chosen N, given the flagged-row count |E| at that N.

|E| is the one number this script cannot derive: the screen has to be re-run at the
target N (see llama_audit_v3.ipynb). It defaults to 64 -- the calibrated value at
N=256 -- and the output says so.

    python finalize_audit.py --dir repair_runs/audit_v2 --at-n 2048 --flagged 64
"""
from __future__ import annotations

import argparse, json, math
from pathlib import Path

import numpy as np
import pandas as pd


def per_row_slope(sweep: pd.DataFrame, mode: str, min_points: int = 3) -> dict:
    """Fit log2(candidates) against log2(N) within each row's own value regime."""
    sub = sweep[sweep["mode"] == mode]
    fits = []
    for row, g in sub.groupby("row"):
        g = g.sort_values("N")
        pinned = g[g["feasible_columns"] <= 1]
        if pinned.empty:
            continue                                   # column never pinned in this grid
        n0 = int(pinned["N"].min())
        live = g[(g["N"] >= n0) & (g["candidates"] > 1)]
        if len(live) < min_points:
            continue                                   # saturated too early to fit
        slope = float(np.polyfit(np.log2(live["N"].to_numpy(float)),
                                 np.log2(live["candidates"].to_numpy(float)), 1)[0])
        fits.append({"row": int(row), "N_pinned": n0, "slope": slope, "points": len(live)})
    if not fits:
        return {"rows_fitted": 0}
    s = np.array([f["slope"] for f in fits])
    p = np.array([f["N_pinned"] for f in fits])
    return {"rows_fitted": len(fits),
            "rows_skipped": int(sub["row"].nunique() - len(fits)),
            "slope_mean": float(s.mean()), "slope_median": float(np.median(s)),
            "slope_std": float(s.std(ddof=1)) if len(s) > 1 else 0.0,
            "slope_p10": float(np.quantile(s, .10)), "slope_p90": float(np.quantile(s, .90)),
            "N_pinned_median": float(np.median(p)),
            "predicted_slope": -1.0}


def residual_by_n(sweep: pd.DataFrame, mode: str) -> pd.Series:
    """Sum of log2(candidates) over rows: the information the record leaves, per N."""
    sub = sweep[sweep["mode"] == mode]
    return sub.groupby("N")["candidates"].apply(
        lambda c: float(np.log2(np.maximum(c.to_numpy(float), 1.0)).sum()))


def ladder(n_flagged: int, residual_bits: float, s: int = 64,
           p_row_bits: int = 17, p_full_bits: int = 31) -> pd.DataFrame:
    """Certificate cost of each scheme, in bits."""
    base = 2 * s * p_full_bits
    rows = [("data-free full-head RS (2s checks)", base),
            ("row-summary code + screen (2|E| checks)", 2 * n_flagged * p_row_bits),
            ("row locators + interval column ID (|E| checks)", n_flagged * p_row_bits),
            ("information left by the record (counting bound)", int(math.ceil(residual_bits)))]
    df = pd.DataFrame(rows, columns=["scheme", "bits"])
    df["bytes"] = np.ceil(df["bits"] / 8).astype(int)
    df["vs_data_free"] = (1 - df["bits"] / base).map(lambda x: f"{100 * x:.1f}%")
    return df


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="repair_runs/audit_v2")
    ap.add_argument("--at-n", type=int, default=None, help="default: largest N in the sweep")
    ap.add_argument("--flagged", type=int, default=64, help="|E| from the screen at --at-n")
    ap.add_argument("--sparsity", type=int, default=64)
    args = ap.parse_args()

    d = Path(args.dir)
    sweep = pd.read_csv(d / "sweep_vs_N.csv")
    at_n = args.at_n or int(sweep["N"].max())
    if at_n not in set(sweep["N"]):
        raise SystemExit(f"N={at_n} is not in the sweep; available: {sorted(set(sweep['N']))}")

    out = {"source": str(d), "at_N": at_n, "flagged_rows_assumed": args.flagged}
    for mode in sorted(sweep["mode"].unique()):
        res = residual_by_n(sweep, mode)
        fit = per_row_slope(sweep, mode)
        L = ladder(args.flagged, res.loc[at_n], args.sparsity)
        L.to_csv(d / f"ladder_{mode}_N{at_n}.csv", index=False)
        out[mode] = {"residual_bits_by_N": {int(k): float(v) for k, v in res.items()},
                     "residual_bits_at_N": float(res.loc[at_n]),
                     "per_row_slope": fit,
                     "ladder": L.to_dict(orient="records")}

        print(f"\n=== {mode} ===")
        print("residual information (bits) by N:")
        print("  " + "  ".join(f"{int(n)}:{v:.0f}" for n, v in res.items()))
        if fit.get("rows_fitted"):
            print(f"value-regime slope, fitted per row: "
                  f"{fit['slope_mean']:+.3f} +/- {fit['slope_std']:.3f} "
                  f"(median {fit['slope_median']:+.3f}, "
                  f"p10 {fit['slope_p10']:+.3f}, p90 {fit['slope_p90']:+.3f}; "
                  f"{fit['rows_fitted']} rows, {fit['rows_skipped']} skipped)")
            print(f"column pinned at median N = {fit['N_pinned_median']:.0f}")
        print(f"\nladder at N={at_n} (|E|={args.flagged}):")
        print(L.to_string(index=False))

    (d / "finalize_report.json").write_text(json.dumps(out, indent=2))
    print(f"\nwrote {d / 'finalize_report.json'}")
    print(f"NOTE: |E|={args.flagged} is the screen's flagged-row count. It was calibrated at "
          f"N=256; re-run the screen at N={at_n} and pass --flagged with that value before "
          "quoting the construction rungs.")


if __name__ == "__main__":
    main()
