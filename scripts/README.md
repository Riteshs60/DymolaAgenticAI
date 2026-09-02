# Dymola skills — shared scripts

These scripts are shared by every skill in this repo. Keep `scripts/` as a
**sibling** of the skill folders (do not install skills without it).

**New here?** Start with the human walkthrough: [`../USER_GUIDE.md`](../USER_GUIDE.md).  
Agent setup: [`../InstallationGuide.md`](../InstallationGuide.md).  
Future work: [`../ROADMAP.md`](../ROADMAP.md).

Override the scripts location with `$DYMOLA_SKILLS_SCRIPTS` if needed.

## Quick map

| Script | Purpose |
|--------|---------|
| `dymola_run.py` | Discover Dymola, run validate / translate / simulate / list-params / run-dymosim |
| `dsin_io.py` | List / get / set parameters in `dsin.txt` (exposed params, incl. from encrypted libs) |
| `dymosim_inspect.py` | Inspect `dymosim.exe`, `dsmodel.c`, classify tunable vs structural |
| `mo_params.py` | List / set simple assignments in open `.mo` source |
| `diagnose_log.py` | Parse `dslog.txt` / command logs into errors + hints |
| `smart_sweep.py` | Parameter sweep via dsin + dymosim (no retranslate) |
| `result_summary.py` | min/max/mean/final for `.mat` variables |
| `plot_result.py` | Plot `.mat` variables to PNG |
| `bootstrap_env.py` | Pre-warm managed venv (DyMat / matplotlib / numpy / scipy) |

## Environment

| Variable | Meaning |
|----------|---------|
| `DYMOLA_HOME` | Install root containing `bin/Dymola.exe` |
| `DYMOLA_EXE` | Full path to the executable |
| `DYMOLA_MODELICAPATH` | Extra library paths |
| `DYMOLA_SKILLS_VENV` | Managed venv location |
| `DYMOLA_SKILLS_SCRIPTS` | Absolute path to this `scripts/` folder |

## Encrypted libraries — what is / isn't allowed

**Allowed (and implemented):**
- Translate the model in Dymola so it emits `dsin.txt`
- Read every **exposed** parameter name/value Dymola placed in `dsin.txt`
- Change those values and re-run `dymosim` without recompiling
- Inspect generated `dsmodel.c` comments / symbols for hints

**Not allowed / not implemented:**
- Decrypting `.moe` / encrypted packages
- Recovering hidden equations or protected source

## Examples

```bash
python dymola_run.py --mode info
python dymola_run.py --mode list-params --model Model.mo --name Model
python dsin_io.py path/to/dsin.txt --filter pump --json
python dsin_io.py path/to/dsin.txt --set "pump.N=1500" --out dsin_new.txt
python dymola_run.py --mode run-dymosim --dymosim path/dymosim.exe --dsin dsin_new.txt
python dymosim_inspect.py path/to/workdir --out inspect.json
python smart_sweep.py --dymosim dymosim.exe --dsin dsin.txt --sweep "k=0.5,1,2" --outdir sweeps
```

On Windows PowerShell use `python` (not `python3`).
