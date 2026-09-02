"""
Read / write Dymola ``dsin.txt`` (simulation input / parameter file).

After translation, Dymola writes every *exposed* parameter (including those
from encrypted library components) into ``dsin.txt``. Tunable parameters can
be changed here and ``dymosim`` re-run **without** recompiling.

This module never decrypts libraries — it only reads the public simulation
input surface that Dymola itself emits.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple


# Typical dsin double block line:
#   1.234e-3  # name description
_DOUBLE_LINE = re.compile(
    r"^\s*([+-]?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?)\s*(?:#\s*(.*))?$"
)
_INT_LINE = re.compile(r"^\s*(-?\d+)\s*(?:#\s*(.*))?$")


@dataclass
class DsinEntry:
    name: str
    value: str
    comment: str
    section: str
    line_index: int
    kind: str  # "double" | "integer" | "string" | "other"


@dataclass
class DsinFile:
    path: str
    raw_lines: List[str]
    entries: List[DsinEntry]
    sections: Dict[str, List[str]]  # section -> entry names in order

    def by_name(self) -> Dict[str, DsinEntry]:
        return {e.name: e for e in self.entries if e.name}


def _section_name(line: str) -> Optional[str]:
    s = line.strip()
    if s.startswith("#") and not s.startswith("##"):
        # "# initialConditions" style headers used by many Dymola versions
        body = s.lstrip("#").strip()
        if body and " " not in body.split("=")[0] and len(body) < 80:
            # Prefer explicit known headers
            return body
    if s.startswith("char ") or s.startswith("double ") or s.startswith("int "):
        return s.split("(")[0].strip()
    return None


def parse_dsin(path: Path) -> DsinFile:
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    entries: List[DsinEntry] = []
    sections: Dict[str, List[str]] = {}
    current = "header"
    sections.setdefault(current, [])

    # Dymola dsin formats vary. Strategy:
    # 1) Prefer "name = value" / "name value" forms with trailing comments.
    # 2) Also capture classic matrix-style blocks where a comment on the same
    #    line (or previous line) carries the variable name.
    name_eq = re.compile(
        r"^\s*([A-Za-z_][\w\.]*(?:\[[^\]]+\])?)\s*=\s*([^;#]+?)\s*(?:[;#]\s*(.*))?$"
    )
    prev_name_hint: Optional[str] = None

    for i, line in enumerate(lines):
        sec = _section_name(line)
        if sec:
            current = sec
            sections.setdefault(current, [])

        m = name_eq.match(line)
        if m:
            name, value, comment = m.group(1), m.group(2).strip(), (m.group(3) or "").strip()
            kind = "double"
            if re.fullmatch(r"-?\d+", value):
                kind = "integer"
            elif value.startswith('"') or value.startswith("'"):
                kind = "string"
            e = DsinEntry(name, value, comment, current, i, kind)
            entries.append(e)
            sections[current].append(name)
            continue

        # Comment-only line that looks like a variable name hint
        hint = re.match(r"^\s*#\s*([A-Za-z_][\w\.]*(?:\[[^\]]+\])?)\s*(.*)$", line)
        if hint and "=" not in line:
            prev_name_hint = hint.group(1)
            continue

        dm = _DOUBLE_LINE.match(line)
        if dm and prev_name_hint:
            value, rest = dm.group(1), (dm.group(2) or "").strip()
            name = prev_name_hint
            comment = rest
            e = DsinEntry(name, value, comment, current, i, "double")
            entries.append(e)
            sections[current].append(name)
            prev_name_hint = None
            continue

        im = _INT_LINE.match(line)
        if im and prev_name_hint and "." not in im.group(1):
            value, rest = im.group(1), (im.group(2) or "").strip()
            name = prev_name_hint
            e = DsinEntry(name, value, rest, current, i, "integer")
            entries.append(e)
            sections[current].append(name)
            prev_name_hint = None
            continue

        # Same-line: value then # name
        trailing = re.match(
            r"^\s*([+-]?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?)\s+#\s*([A-Za-z_][\w\.]*)\b(.*)$",
            line,
        )
        if trailing:
            value, name, rest = trailing.group(1), trailing.group(2), trailing.group(3).strip()
            e = DsinEntry(name, value, rest, current, i, "double")
            entries.append(e)
            sections[current].append(name)

    return DsinFile(str(path), lines, entries, sections)


def set_parameters(dsin: DsinFile, overrides: Dict[str, str]) -> Tuple[DsinFile, List[str], List[str]]:
    """Return updated DsinFile, list of applied names, list of missing names."""
    by = dsin.by_name()
    applied: List[str] = []
    missing: List[str] = []
    lines = list(dsin.raw_lines)

    for name, new_val in overrides.items():
        if name not in by:
            missing.append(name)
            continue
        e = by[name]
        old = lines[e.line_index]
        # Preserve comment / formatting when possible
        if "=" in old:
            lines[e.line_index] = re.sub(
                r"(=\s*)([^;#]+)",
                lambda m: m.group(1) + str(new_val),
                old,
                count=1,
            )
        else:
            lines[e.line_index] = re.sub(
                r"^(\s*)([+-]?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?)",
                lambda m: m.group(1) + str(new_val),
                old,
                count=1,
            )
        e.value = str(new_val)
        applied.append(name)

    updated = DsinFile(dsin.path, lines, dsin.entries, dsin.sections)
    return updated, applied, missing


def write_dsin(dsin: DsinFile, path: Optional[Path] = None) -> Path:
    out = Path(path) if path else Path(dsin.path)
    out.write_text("\n".join(dsin.raw_lines) + "\n", encoding="utf-8")
    return out


def entries_as_dict(dsin: DsinFile) -> List[dict]:
    return [asdict(e) for e in dsin.entries]


def filter_entries(
    dsin: DsinFile,
    *,
    substring: Optional[str] = None,
    section: Optional[str] = None,
    regex: Optional[str] = None,
) -> List[DsinEntry]:
    rx = re.compile(regex) if regex else None
    out = []
    for e in dsin.entries:
        if section and section.lower() not in e.section.lower():
            continue
        if substring and substring.lower() not in e.name.lower() and substring.lower() not in e.comment.lower():
            continue
        if rx and not rx.search(e.name):
            continue
        out.append(e)
    return out


def parse_override_string(s: str) -> Dict[str, str]:
    """Parse ``a=1,b=2.5,c.path=3`` into a dict."""
    out: Dict[str, str] = {}
    for part in s.split(","):
        part = part.strip()
        if not part:
            continue
        if "=" not in part:
            raise ValueError(f"override must be name=value, got: {part!r}")
        k, v = part.split("=", 1)
        out[k.strip()] = v.strip()
    return out


def main(argv: Optional[Iterable[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Inspect / edit Dymola dsin.txt parameter files")
    ap.add_argument("dsin", help="Path to dsin.txt")
    ap.add_argument("--list", action="store_true", help="List parameters")
    ap.add_argument("--json", action="store_true", help="JSON output")
    ap.add_argument("--filter", default=None, help="Substring filter on name/comment")
    ap.add_argument("--section", default=None, help="Section substring filter")
    ap.add_argument("--regex", default=None, help="Regex on parameter name")
    ap.add_argument("--get", default=None, help="Print one parameter value")
    ap.add_argument("--set", dest="overrides", default=None, help="name=val,name2=val2")
    ap.add_argument("--out", default=None, help="Write modified dsin to this path (default: overwrite)")
    ap.add_argument("--dry-run", action="store_true", help="Show what would change, do not write")
    args = ap.parse_args(list(argv) if argv is not None else None)

    path = Path(args.dsin)
    if not path.is_file():
        print(f"ERROR: dsin not found: {path}", file=sys.stderr)
        return 2

    dsin = parse_dsin(path)

    if args.get:
        e = dsin.by_name().get(args.get)
        if not e:
            print(f"ERROR: parameter not found: {args.get}", file=sys.stderr)
            return 1
        if args.json:
            print(json.dumps(asdict(e), indent=2))
        else:
            print(f"{e.name} = {e.value}  # {e.comment}".rstrip())
        return 0

    if args.overrides:
        overrides = parse_override_string(args.overrides)
        updated, applied, missing = set_parameters(dsin, overrides)
        payload = {"applied": applied, "missing": missing, "count_applied": len(applied)}
        if args.dry_run or args.json:
            print(json.dumps(payload, indent=2))
        if missing:
            print(f"WARNING: missing parameters: {', '.join(missing)}", file=sys.stderr)
        if not args.dry_run:
            out = write_dsin(updated, Path(args.out) if args.out else path)
            if not args.json:
                print(f"Wrote {out} ({len(applied)} overrides applied)")
        return 0 if not missing else 1

    entries = filter_entries(dsin, substring=args.filter, section=args.section, regex=args.regex)
    if args.json:
        print(json.dumps(entries_as_dict(DsinFile(dsin.path, dsin.raw_lines, entries, dsin.sections)), indent=2))
    else:
        print(f"# {path} — {len(entries)} parameters")
        for e in entries:
            print(f"{e.name}\t{e.value}\t{e.section}\t{e.comment}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
