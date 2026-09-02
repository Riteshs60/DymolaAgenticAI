---
name: validate-dymola
description: "Validate Modelica models with Dymola (checkModel). Use when the user asks to validate, check, or verify a Modelica model in Dymola, or after creating/editing a .mo file."
---

# Validate with Dymola

Flatten/check a Modelica model via Dymola headless scripting (`checkModel`).

## Before you run

Resolve `<scripts-dir>`:

1. `$env:DYMOLA_SKILLS_SCRIPTS` (PowerShell) / `$DYMOLA_SKILLS_SCRIPTS` (bash), if set
2. `../scripts` relative to this skill folder
3. Repo `scripts/` beside the skill directories

On Windows use **PowerShell** and `python` (not `python3`).

Working directory: `_dymola_validate_temp/` next to the model (created by the launcher).

## Workflow

1. Identify the `.mo` file and Modelica class name (parse `model Name`, do not guess from filename alone).
2. Run:

```bash
python "<scripts-dir>/dymola_run.py" --mode validate --model "Model.mo" --name ModelName --timeout 120 --json
```

Extra libraries:

```bash
python "<scripts-dir>/dymola_run.py" --mode validate --model "Model.mo" --name Pkg.Model --load "C:/libs/MyLib/package.mo"
```

3. Read `summary.json` and the `.log` in the temp dir. If check failed, run:

```bash
python "<scripts-dir>/diagnose_log.py" "<temp>/validate.out.log" --json
```

4. Report pass/fail with the first actionable errors. Then delete the temp dir.

## Notes

- Needs a licensed Dymola install (`DYMOLA_HOME` if not auto-found).
- Encrypted dependencies are fine for check **if** Dymola can load them; you still cannot read their source.
