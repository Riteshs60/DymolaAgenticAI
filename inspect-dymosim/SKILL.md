---
name: inspect-dymosim
description: "Inspect dymosim.exe, generated dsmodel.c, and dsin.txt to see tunable vs structural parameters and guide .mo or dsin edits. Use when the user asks what the compiled model exposes, how to change parameters without rebuild, or to analyze dymosim artifacts."
---

# Inspect dymosim / generated C / dsin

## Workflow

1. Point at a workdir that already contains compile artifacts (after `translate` or `simulate`):

```bash
python "<scripts-dir>/dymosim_inspect.py" "<workdir>" --out "<workdir>/inspect.json"
```

2. Read `inspect.json`:
   - `artifacts` — what files exist
   - `dsin_parameter_count` — runtime-tunable surface
   - `dsmodel_c.parameter_hints` — names mentioned in generated C
   - `classification` — overlap / C-only (maybe structural) / dsin-only

3. Decide the edit path:

| Goal | Action |
|------|--------|
| Tune exposed value quickly | `dsin_io.py --set` + `dymola_run.py --mode run-dymosim` |
| Change structure / replace component / encrypted-internal behavior | Edit open `.mo` (or public modifiers) + retranslate |
| Understand failure | `diagnose_log.py` on `dslog.txt` |

4. Optionally sync a successful dsin override back into open `.mo` with `mo_params.py`
   (top-level simple assignments only).

## Safety

- Read strings / comments / dsin only — do not disassemble for secrets
- Encrypted source will not appear in `dsmodel.c` as Modelica text
