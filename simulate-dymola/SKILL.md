---
name: simulate-dymola
description: "Translate and simulate Modelica models with Dymola, or re-run dymosim.exe with modified dsin.txt parameters. Use when the user asks to simulate, run, or get results from a Dymola model."
---

# Simulate with Dymola

Two paths:

| Path | When |
|------|------|
| Full `simulate` | Need a fresh translate + simulate from `.mo` |
| `run-dymosim` | Already have `dymosim` + `dsin.txt`; only parameters change |

## Full simulate

```bash
python "<scripts-dir>/dymola_run.py" --mode simulate --model "Model.mo" --name ModelName --stop-time 10 --json
```

Artifacts land in `_dymola_simulate_temp/`: `dsres.mat`, `dsin.txt`, `dymosim.exe`, `dsmodel.c`, logs.

Summarize / plot:

```bash
python "<scripts-dir>/result_summary.py" "<temp>/dsres.mat" --vars "x,y" --json
python "<scripts-dir>/plot_result.py" "<temp>/dsres.mat" --vars "x,y" --out "<temp>/plot.png"
```

Display the PNG with the Read tool.

## Fast re-run (no retranslate)

```bash
python "<scripts-dir>/dymola_run.py" --mode run-dymosim \
  --dymosim "<path>/dymosim.exe" --dsin "<path>/dsin.txt" \
  --override "component.param=1.5,other=3" --json
```

Or sweep:

```bash
python "<scripts-dir>/smart_sweep.py" --dymosim dymosim.exe --dsin dsin.txt \
  --sweep "gain=0.5,1,2" --outdir sweeps --json
```

## Agent rules

- Prefer `run-dymosim` / `smart_sweep` when iterating on **exposed** parameters.
- If an override has no effect, inspect with `inspect-dymosim` — it may be structural; then edit `.mo` and retranslate.
- Never attempt to decrypt encrypted libraries; use exposed dsin parameters only.
