#!/usr/bin/env python3
"""Parse Dymola translation / simulation logs (dslog.txt, command logs)."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import List


ERROR_RX = re.compile(r"(?i)\berror\b[:\s].+")
WARN_RX = re.compile(r"(?i)\bwarning\b[:\s].+")
FATAL_RX = re.compile(r"(?i)\b(fatal|translation of .* failed|simulation of .* failed).+")


def parse_log(text: str) -> dict:
    lines = text.splitlines()
    errors: List[str] = []
    warnings: List[str] = []
    fatals: List[str] = []
    for line in lines:
        s = line.strip()
        if not s:
            continue
        if FATAL_RX.search(s):
            fatals.append(s)
        elif ERROR_RX.search(s):
            errors.append(s)
        elif WARN_RX.search(s):
            warnings.append(s)

    suggestions = []
    blob = "\n".join(errors + fatals).lower()
    if "undeclared" in blob or "not found in scope" in blob:
        suggestions.append("Check class names / library load order (--load package.mo) and MODELICAPATH.")
    if "singular" in blob or "structural singularity" in blob:
        suggestions.append("Model may be structurally singular — review equations vs unknowns; use diagnose-dymola skill.")
    if "encrypted" in blob and "cannot" in blob:
        suggestions.append("Encrypted component internals are inaccessible; only use public/exposed parameters via dsin.txt.")
    if "license" in blob:
        suggestions.append("Dymola license issue — verify license server / seat availability.")
    if "differentiable" in blob or "no event" in blob:
        suggestions.append("Numerical / event issue — try different solver settings or smooth approximations.")

    return {
        "error_count": len(errors),
        "warning_count": len(warnings),
        "fatal_count": len(fatals),
        "errors": errors[:100],
        "warnings": warnings[:100],
        "fatals": fatals[:50],
        "suggestions": suggestions,
        "ok_guess": len(fatals) == 0 and len(errors) == 0,
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Parse Dymola log files")
    ap.add_argument("log", help="Path to dslog.txt or .log")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    path = Path(args.log)
    if not path.is_file():
        print(f"ERROR: log not found: {path}", file=sys.stderr)
        return 2
    report = parse_log(path.read_text(encoding="utf-8", errors="replace"))
    report["path"] = str(path)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"fatals={report['fatal_count']} errors={report['error_count']} warnings={report['warning_count']}")
        for e in report["errors"][:20]:
            print("  ERROR:", e)
        for s in report["suggestions"]:
            print("  HINT:", s)
    return 0 if report["ok_guess"] else 1


if __name__ == "__main__":
    sys.exit(main())
