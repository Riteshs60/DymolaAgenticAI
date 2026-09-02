---
name: tune-parameters
description: "Smart parameter tuning for Dymola models: edit dsin.txt, sweep with dymosim, or patch .mo assignments. Use when the user wants to change parameters, calibrate, sweep, or iterate without full rebuilds."
---

# Tune parameters (smart)

## Decision tree

1. **Is the model already translated?** (`dymosim` + `dsin.txt` present)
   - Yes → prefer dsin overrides / `smart_sweep.py`
   - No → `dymola_run.py --mode translate` or `list-params` first
2. **Is the parameter visible in dsin?**
   - Yes → runtime tunable
   - No → must edit `.mo` (open source) or a public modifier, then retranslate
3. **Is the target inside an encrypted library?**
   - Only exposed params in dsin are fair game (`expose-encrypted-params`)

## Commands

List / set dsin:

```bash
python "<scripts-dir>/dsin_io.py" dsin.txt --list --json
python "<scripts-dir>/dsin_io.py" dsin.txt --set "a.b=1.2,c=3" --out dsin_tuned.txt
```

Re-run:

```bash
python "<scripts-dir>/dymola_run.py" --mode run-dymosim --dymosim dymosim.exe --dsin dsin_tuned.txt --json
```

Sweep:

```bash
python "<scripts-dir>/smart_sweep.py" --dymosim dymosim.exe --dsin dsin.txt \
  --sweep "sensor.T=280:300:5" --outdir sweep_T --json
```

Patch open `.mo` (simple top-level names only):

```bash
python "<scripts-dir>/mo_params.py" Model.mo --set "k=0.4" --json
```

After runs, summarize with `result_summary.py` and recommend next values.

## Smart behaviors expected of the agent

- Keep a table of trial → key metrics (final value, overshoot, settle time)
- Stop when requirements are met; do not endless-sweep
- If sensitivity is ~0, flag possible structural/wrong parameter
- Offer to write successful dsin values back into `.mo` when source is open
