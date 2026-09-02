#!/usr/bin/env python3
"""
Safe, span-aware helpers to read / update simple parameter assignments in
Modelica ``.mo`` source (public modifiers and top-level parameter bindings).

Does **not** decrypt encrypted libraries. For encrypted components, use
``dymola_run.py --mode list-params`` + ``dsin_io.py`` instead.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple


# Matches: parameter Real k = 1.0 "doc";  OR  k=1.0  inside modification
ASSIGN = re.compile(
    r"(?P<prefix>(?:^|\n)\s*(?:parameter\s+)?(?:(?:Real|Integer|Boolean|String|Modelica\.[A-Za-z0-9_.]+)\s+)?"
    r"(?P<name>[A-Za-z_][\w]*)\s*)"
    r"(?P<eq>=\s*)(?P<value>[^;,\n]+)",
    re.M,
)


def list_assignments(text: str) -> List[dict]:
    out = []
    for m in ASSIGN.finditer(text):
        out.append({
            "name": m.group("name"),
            "value": m.group("value").strip(),
            "start": m.start("value"),
            "end": m.end("value"),
        })
    return out


def set_assignments(text: str, overrides: Dict[str, str]) -> Tuple[str, List[str], List[str]]:
    applied: List[str] = []
    missing = [k for k in overrides if k not in {a["name"] for a in list_assignments(text)}]
    # Apply from end to start to keep spans valid
    matches = [m for m in ASSIGN.finditer(text) if m.group("name") in overrides]
    # last occurrence wins per name
    by_name = {}
    for m in matches:
        by_name[m.group("name")] = m
    ordered = sorted(by_name.values(), key=lambda m: m.start("value"), reverse=True)
    chars = list(text)
    for m in ordered:
        name = m.group("name")
        new = str(overrides[name])
        start, end = m.start("value"), m.end("value")
        chars[start:end] = list(new)
        applied.append(name)
    return "".join(chars), sorted(set(applied)), missing


def parse_override_string(s: str) -> Dict[str, str]:
    out: Dict[str, str] = {}
    for part in s.split(","):
        part = part.strip()
        if not part:
            continue
        if "=" not in part:
            raise ValueError(part)
        k, v = part.split("=", 1)
        out[k.strip()] = v.strip()
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="List/set simple parameter assignments in a .mo file")
    ap.add_argument("model", help="Path to .mo file")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--set", dest="overrides", default=None, help="name=val,name2=val2")
    ap.add_argument("--out", default=None, help="Write result (default: overwrite input)")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)

    path = Path(args.model)
    text = path.read_text(encoding="utf-8", errors="replace")

    if args.overrides:
        overrides = parse_override_string(args.overrides)
        # Only support unqualified top-level names here; dotted paths need component surgery.
        dotted = [k for k in overrides if "." in k]
        if dotted:
            print(
                "ERROR: dotted paths are not rewritten in .mo by this tool. "
                "Use dsin_io.py for compiled-parameter overrides, or edit the component modification manually: "
                + ", ".join(dotted),
                file=sys.stderr,
            )
            return 2
        new_text, applied, missing = set_assignments(text, overrides)
        payload = {"applied": applied, "missing": missing}
        if args.json:
            print(json.dumps(payload, indent=2))
        else:
            print(f"applied={applied} missing={missing}")
        if missing:
            return 1
        if not args.dry_run:
            out = Path(args.out) if args.out else path
            out.write_text(new_text, encoding="utf-8")
            if not args.json:
                print(f"Wrote {out}")
        return 0

    assigns = list_assignments(text)
    if args.json:
        print(json.dumps(assigns, indent=2))
    else:
        for a in assigns:
            print(f"{a['name']} = {a['value']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
