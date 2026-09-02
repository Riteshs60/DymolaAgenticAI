#!/usr/bin/env python3
"""Plot selected variables from a Dymola result .mat file."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from _env import reexec_under_managed_venv

reexec_under_managed_venv(["DyMat", "matplotlib", "numpy"])


def main(argv=None) -> int:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    from DyMat import DyMatFile

    ap = argparse.ArgumentParser(description="Plot variables from Dymola .mat")
    ap.add_argument("mat")
    ap.add_argument("--vars", required=True, help="Comma-separated variable names")
    ap.add_argument("--out", required=True, help="Output PNG path")
    ap.add_argument("--title", default=None)
    args = ap.parse_args(argv)

    dm = DyMatFile(args.mat)
    # abscissa
    try:
        t = np.asarray(dm.abscissa(args.vars.split(",")[0].strip(), valuesOnly=True), dtype=float)
    except Exception:
        t = None

    plt.figure(figsize=(10, 5))
    for v in [x.strip() for x in args.vars.split(",") if x.strip()]:
        y = np.asarray(dm.data(v), dtype=float).ravel()
        x = t if t is not None and len(t) == len(y) else np.arange(len(y))
        plt.plot(x, y, label=v)
    plt.xlabel("t" if t is not None else "index")
    plt.ylabel("value")
    plt.legend()
    plt.title(args.title or Path(args.mat).name)
    plt.tight_layout()
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out, dpi=120)
    print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
