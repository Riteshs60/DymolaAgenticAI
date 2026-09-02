#!/usr/bin/env python3
"""Summarize variables from a Dymola result .mat (DyMat)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from _env import reexec_under_managed_venv

reexec_under_managed_venv(["DyMat", "numpy"])


def main(argv=None) -> int:
    import numpy as np
    from DyMat import DyMatFile

    ap = argparse.ArgumentParser(description="Summarize Dymola .mat results")
    ap.add_argument("mat", help="Path to dsres.mat / result .mat")
    ap.add_argument("--vars", default=None, help="Comma-separated variable names (default: list some)")
    ap.add_argument("--list", action="store_true", help="List variable names")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--limit", type=int, default=50)
    args = ap.parse_args(argv)

    path = Path(args.mat)
    if not path.is_file():
        print(f"ERROR: mat not found: {path}", file=sys.stderr)
        return 2

    dm = DyMatFile(str(path))
    names = list(dm.names())
    if args.list:
        payload = names[: args.limit] if args.limit else names
        print(json.dumps(payload, indent=2) if args.json else "\n".join(payload))
        return 0

    wanted = [v.strip() for v in args.vars.split(",")] if args.vars else names[: min(10, len(names))]
    rows = []
    for v in wanted:
        try:
            data = np.asarray(dm.data(v), dtype=float).ravel()
            rows.append({
                "name": v,
                "min": float(np.nanmin(data)),
                "max": float(np.nanmax(data)),
                "mean": float(np.nanmean(data)),
                "final": float(data[-1]) if data.size else None,
                "n": int(data.size),
            })
        except Exception as e:
            rows.append({"name": v, "error": str(e)})

    if args.json:
        print(json.dumps(rows, indent=2))
    else:
        for r in rows:
            if "error" in r:
                print(f"{r['name']}\tERROR\t{r['error']}")
            else:
                print(f"{r['name']}\tmin={r['min']:.6g}\tmax={r['max']:.6g}\tmean={r['mean']:.6g}\tfinal={r['final']:.6g}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
