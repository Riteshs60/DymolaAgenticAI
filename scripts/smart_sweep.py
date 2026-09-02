#!/usr/bin/env python3
"""
Smart parameter sweep using a compiled ``dymosim`` + ``dsin.txt``.

Runs multiple simulations without retranslating — ideal for exposed parameters
from encrypted libraries that appear in dsin.txt.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import time
from pathlib import Path
from typing import Dict, List

from dsin_io import parse_dsin, set_parameters, write_dsin
from dymola_run import run_dymosim


def parse_sweep(spec: str) -> Dict[str, List[str]]:
    """
    Formats:
      k=1,2,3
      k=1:3:0.5   (start:stop:step)  — numeric
      a=1,2;b=3,4  (cartesian later — for now one name per call recommended)
    """
    out: Dict[str, List[str]] = {}
    for chunk in spec.split(";"):
        chunk = chunk.strip()
        if not chunk:
            continue
        if "=" not in chunk:
            raise ValueError(chunk)
        name, rest = chunk.split("=", 1)
        name = name.strip()
        rest = rest.strip()
        if ":" in rest and "," not in rest:
            parts = [float(x) for x in rest.split(":")]
            if len(parts) == 2:
                start, stop = parts
                step = 1.0 if stop >= start else -1.0
            elif len(parts) == 3:
                start, stop, step = parts
            else:
                raise ValueError(rest)
            vals = []
            x = start
            if step == 0:
                raise ValueError("step cannot be 0")
            # inclusive-ish
            if step > 0:
                while x <= stop + abs(step) * 1e-9:
                    vals.append(str(x))
                    x += step
            else:
                while x >= stop - abs(step) * 1e-9:
                    vals.append(str(x))
                    x += step
            out[name] = vals
        else:
            out[name] = [v.strip() for v in rest.split(",") if v.strip()]
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Sweep parameters via dsin + dymosim")
    ap.add_argument("--dymosim", required=True)
    ap.add_argument("--dsin", required=True)
    ap.add_argument("--sweep", required=True, help='e.g. "gain=0.5,1,2" or "T=1:5:1"')
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--timeout", type=int, default=300)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    dymosim = Path(args.dymosim)
    dsin_src = Path(args.dsin)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    sweeps = parse_sweep(args.sweep)
    if len(sweeps) != 1:
        print("ERROR: currently one parameter per --sweep invocation (use name=v1,v2 or name=start:stop:step)", file=sys.stderr)
        return 2
    (pname, values), = sweeps.items()

    base = parse_dsin(dsin_src)
    results = []
    for i, val in enumerate(values):
        run_dir = outdir / f"run_{i:03d}_{pname}={val}".replace("/", "_")
        if run_dir.exists():
            shutil.rmtree(run_dir)
        run_dir.mkdir(parents=True)
        shutil.copy2(dymosim, run_dir / dymosim.name)
        # copy sibling dlls if present
        for sib in dymosim.parent.glob("*.dll"):
            shutil.copy2(sib, run_dir / sib.name)
        updated, applied, missing = set_parameters(base, {pname: val})
        if missing:
            print(f"ERROR: parameter not in dsin: {missing}", file=sys.stderr)
            return 1
        write_dsin(updated, run_dir / "dsin.txt")
        t0 = time.time()
        cp = run_dymosim(run_dir / dymosim.name, dsin=run_dir / "dsin.txt", workdir=run_dir, timeout=args.timeout)
        # collect result mats
        mats = list(run_dir.glob("*.mat"))
        results.append({
            "index": i,
            "param": pname,
            "value": val,
            "returncode": cp.returncode,
            "elapsed_s": round(time.time() - t0, 3),
            "run_dir": str(run_dir),
            "mat_files": [str(m) for m in mats],
        })

    summary = {"sweep": sweeps, "runs": results}
    (outdir / "sweep_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2) if args.json else f"Wrote {outdir / 'sweep_summary.json'} ({len(results)} runs)")
    return 0 if all(r["returncode"] == 0 for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
