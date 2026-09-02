#!/usr/bin/env python3
"""
Inspect a compiled Dymola simulation binary (``dymosim`` / ``dymosim.exe``)
and the generated C sources (``dsmodel.c``, ``dsmodel.h``).

Purpose for the agent:
  - Discover which parameters are baked into the compiled model
  - Cross-check against ``dsin.txt`` (runtime-tunable surface)
  - Flag likely *structural* vs *tunable* parameters
  - Never attempts binary decryption or unpacking of encrypted Modelica

This reads text-facing surfaces only: PE/ELF size metadata, ``--help``-style
stdout if the binary prints it, and UTF-8 strings / comments in generated C.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set


PARAM_IN_C = re.compile(
    r"""(?ix)
    (?:
      /\*\s*Parameter:\s*([A-Za-z_][\w\.]*)\s*\*/ |
      \bparameter\b[^;]*?\b([A-Za-z_][\w\.]*)\s*= |
      \#define\s+([A-Za-z_][\w]*)\s+([+-]?\d[\w\.]*)
    )
    """
)

# Common Dymola-generated markers
STRINGS_INTEREST = re.compile(
    rb"[\x20-\x7e]{4,}"  # printable runs
)


def file_meta(path: Path) -> dict:
    st = path.stat()
    return {
        "path": str(path.resolve()),
        "size_bytes": st.st_size,
        "mtime": st.st_mtime,
        "exists": True,
    }


def try_dymosim_help(path: Path, timeout: int = 10) -> dict:
    out = {"stdout": "", "stderr": "", "returncode": None}
    for args in ([str(path), "-h"], [str(path), "-help"], [str(path)]):
        try:
            cp = subprocess.run(
                args,
                capture_output=True,
                timeout=timeout,
                cwd=str(path.parent),
            )
            out["returncode"] = cp.returncode
            out["stdout"] = (cp.stdout or b"").decode("utf-8", "replace")[:4000]
            out["stderr"] = (cp.stderr or b"").decode("utf-8", "replace")[:4000]
            if out["stdout"] or out["stderr"]:
                break
        except Exception as e:
            out["error"] = str(e)
    return out


def extract_c_strings(path: Path, limit: int = 5000) -> List[str]:
    data = path.read_bytes()
    found = []
    for m in STRINGS_INTEREST.finditer(data):
        s = m.group().decode("ascii", "ignore")
        if any(k in s.lower() for k in ("param", "model", "dymola", "error", "dsin", "dsres")):
            found.append(s)
        if len(found) >= limit:
            break
    return found


def parse_dsmodel_c(path: Path) -> dict:
    text = path.read_text(encoding="utf-8", errors="replace")
    params: Set[str] = set()
    defines: Dict[str, str] = {}
    for m in PARAM_IN_C.finditer(text):
        if m.group(1):
            params.add(m.group(1))
        if m.group(2):
            params.add(m.group(2))
        if m.group(3):
            defines[m.group(3)] = m.group(4)

    # Also harvest dotted identifiers near "parameter" comments
    for m in re.finditer(r"/\*[^*]*?\*/", text):
        block = m.group()
        for idm in re.finditer(r"\b([A-Za-z_][\w]*\.[A-Za-z_][\w\.]*)\b", block):
            params.add(idm.group(1))

    return {
        "path": str(path),
        "size_bytes": path.stat().st_size,
        "parameter_hints": sorted(params),
        "defines": defines,
        "has_external_object_markers": "external" in text.lower(),
        "line_count": text.count("\n") + 1,
    }


def classify_against_dsin(c_params: Set[str], dsin_names: Set[str]) -> dict:
    """
    Heuristic:
      - in dsin → runtime-tunable via dsin / dymosim re-run
      - only in C → likely structural / constant-folded (needs retranslate)
      - only in dsin → normal exposed parameter
    """
    both = sorted(c_params & dsin_names)
    only_c = sorted(c_params - dsin_names)
    only_dsin = sorted(dsin_names - c_params)
    return {
        "tunable_via_dsin": sorted(dsin_names),
        "mentioned_in_c_and_dsin": both,
        "c_only_maybe_structural": only_c[:200],
        "dsin_only": only_dsin[:500],
        "counts": {
            "dsin": len(dsin_names),
            "c_hints": len(c_params),
            "overlap": len(both),
        },
    }


def inspect_workdir(workdir: Path) -> dict:
    workdir = Path(workdir)
    report: dict = {"workdir": str(workdir.resolve()), "artifacts": {}}

    for name in ("dymosim.exe", "dymosim", "dsin.txt", "dsu.txt", "dsfinal.txt",
                 "dslog.txt", "dsres.mat", "dsmodel.c", "dsmodel.h", "build.log"):
        p = workdir / name
        if p.is_file():
            report["artifacts"][name] = file_meta(p)

    dymosim = None
    for n in ("dymosim.exe", "dymosim"):
        if n in report["artifacts"]:
            dymosim = workdir / n
            break

    if dymosim:
        report["dymosim"] = {
            **file_meta(dymosim),
            "help": try_dymosim_help(dymosim),
            "interesting_strings_sample": extract_c_strings(dymosim, limit=80),
        }

    c_params: Set[str] = set()
    if (workdir / "dsmodel.c").is_file():
        cinfo = parse_dsmodel_c(workdir / "dsmodel.c")
        report["dsmodel_c"] = cinfo
        c_params = set(cinfo["parameter_hints"])

    dsin_names: Set[str] = set()
    if (workdir / "dsin.txt").is_file():
        # Local import to keep this script usable standalone
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from dsin_io import parse_dsin
        dsin = parse_dsin(workdir / "dsin.txt")
        dsin_names = set(dsin.by_name())
        report["dsin_parameter_count"] = len(dsin_names)

    if c_params or dsin_names:
        report["classification"] = classify_against_dsin(c_params, dsin_names)

    report["guidance"] = [
        "Change values in dsin.txt and re-run dymosim to tune exposed parameters without retranslate.",
        "If a change has no effect, it may be structural — edit the .mo and translate again.",
        "Encrypted library source is not readable; only exposed parameters appear in dsin.txt.",
        "Do not attempt to decrypt .moe / encrypted packages.",
    ]
    return report


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Inspect dymosim + generated C + dsin")
    ap.add_argument("workdir", help="Directory containing dymosim / dsin.txt / dsmodel.c")
    ap.add_argument("--json", action="store_true", default=True)
    ap.add_argument("--out", help="Write report JSON to this path")
    args = ap.parse_args(argv)

    workdir = Path(args.workdir)
    if not workdir.is_dir():
        print(f"ERROR: not a directory: {workdir}", file=sys.stderr)
        return 2

    report = inspect_workdir(workdir)
    text = json.dumps(report, indent=2)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
        print(args.out)
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
