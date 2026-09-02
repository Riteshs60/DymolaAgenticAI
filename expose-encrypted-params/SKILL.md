---
name: expose-encrypted-params
description: "List exposed / public parameters from models that use encrypted Dymola libraries. Use when the user mentions encrypted .moe packages, protected libraries, or asking what parameters are available to tune without source."
---

# Exposed parameters from encrypted libraries

Encrypted Modelica libraries hide source, but Dymola still emits **public /
exposed** parameters into `dsin.txt` after translation. This skill uses that
surface only — **no decryption**.

## Workflow

1. Translate and export the catalog:

```bash
python "<scripts-dir>/dymola_run.py" --mode list-params \
  --model "Model.mo" --name ModelName \
  --load "C:/path/to/EncryptedLib/package.mo" --json
```

2. Open `exposed_parameters.json` in the temp dir (also raw `dsin.txt`).

3. Filter for what the user cares about:

```bash
python "<scripts-dir>/dsin_io.py" "<temp>/dsin.txt" --filter "pump" --json
python "<scripts-dir>/dsin_io.py" "<temp>/dsin.txt" --get "pump.N" --json
```

4. Propose safe experiments: change values via `dsin_io.py` / `run-dymosim`,
   not by inventing internals of encrypted classes.

5. Tell the user clearly:
   - Which parameters are **exposed** (tunable via dsin)
   - That encrypted equations / protected components remain inaccessible
   - That structural parameters still need a `.mo`-level change + retranslate

## Do not

- Attempt to unpack, brute-force, or reverse encrypted `.moe` / protected code
- Claim hidden parameters exist without evidence from dsin / Dymola messages
