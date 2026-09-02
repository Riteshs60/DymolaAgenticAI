---
name: diagnose-dymola
description: "Diagnose Dymola translation or simulation failures using logs, dsin/dymosim inspection, and suggested fixes. Use when a model fails to check, translate, or simulate."
---

# Diagnose Dymola failures

## Workflow

1. Collect artifacts from the failed temp dir (`dslog.txt`, `*.log`, `dymola_stdout.txt`, `summary.json`).
2. Parse logs:

```bash
python "<scripts-dir>/diagnose_log.py" "<temp>/dslog.txt" --json
python "<scripts-dir>/diagnose_log.py" "<temp>/simulate.out.log" --json
```

3. If translate succeeded but simulate failed / params look wrong:

```bash
python "<scripts-dir>/dymosim_inspect.py" "<temp>" --out "<temp>/inspect.json"
```

4. Classify the issue and act:

| Symptom | Likely fix |
|---------|------------|
| Class not found | `--load` library `package.mo`, fix MODELICAPATH |
| Encrypted / cannot open | Ensure licensed library path; only use exposed params |
| Structural singularity | Review connectors / equations; reduce systems |
| Parameter override ignored | Structural param → edit `.mo` + retranslate |
| License errors | User must fix Dymola license |

5. Propose a minimal patch, re-validate, then re-simulate.

Never delete the user's models to "start clean."
