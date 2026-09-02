# User guide — install & use

This guide is for **you** (the human). If you want the AI assistant to set
things up automatically, open the repo in your agent and say:

> Read `InstallationGuide.md` and install these skills for me.

---

## 1. What you need

| Requirement | Why |
|-------------|-----|
| **Windows or Linux** | Dymola is most common on Windows; Linux also works |
| **Python 3.8+** on `PATH` | All CLI tools |
| **Licensed Dymola** | Validate / translate / simulate / list encrypted exposed params |
| **An AI coding agent** | Cursor, Claude Code, Codex, etc. with shell access |
| **This repo checked out** | Skills + `scripts/` must stay together |

Plotting (`result_summary.py`, `plot_result.py`) installs its own packages into a
**managed venv** on first use — you do not need to `pip install` globally.

---

## 2. Get the code

```powershell
git clone https://github.com/Riteshs60/DymolaAgenticAI.git
cd DymolaAgenticAI
git checkout feature/dymola-agentic-skills
```

Confirm layout:

```text
DymolaAgenticAI/
  README.md
  USER_GUIDE.md          ← you are here
  InstallationGuide.md   ← for the agent
  install.ps1 / install.sh
  scripts/               ← shared Python tools (required)
  validate-dymola/
  simulate-dymola/
  ... other skill folders ...
  examples/
```

---

## 3. Connect your AI assistant

### Cursor (recommended for this repo)

1. **File → Open Folder** → select the `DymolaAgenticAI` directory.  
2. A rule is already present at `.cursor/rules/dymola-agentic-ai.mdc`.  
3. In chat, try: *“List the Dymola skills in this repo and verify Dymola with `python scripts/dymola_run.py --mode info`.”*

No extra install script is required for Cursor when the whole repo is the workspace.

### Claude Code

```powershell
.\install.ps1          # junctions into %USERPROFILE%\.claude\skills
# or
.\install.ps1 -Copy    # copy instead of junction
```

Linux/macOS:

```bash
chmod +x install.sh
./install.sh           # or: ./install.sh --copy
```

Then **start a new session** so skills are picked up.

### Codex / other agents

Point the project at this folder and either:

- Ask the agent to read each relevant `*/SKILL.md` when needed, or  
- Add short pointers in `AGENTS.md` / standing instructions naming skill paths.

---

## 4. Point the tools at Dymola

### Auto-discovery

```powershell
python scripts/dymola_run.py --mode info --json
```

Success looks like JSON with `dymola_home` and `dymola_exe`.

### Manual override (when auto-detect fails)

| Variable | Example |
|----------|---------|
| `DYMOLA_HOME` | `C:\Program Files\Dymola 2024x` |
| `DYMOLA_EXE` | `C:\Program Files\Dymola 2024x\bin64\Dymola.exe` |
| `DYMOLA_MODELICAPATH` | `C:\MyLibs;D:\VendorLib` (extra libraries) |
| `DYMOLA_SKILLS_SCRIPTS` | Absolute path to `scripts/` if layout is non-standard |
| `DYMOLA_SKILLS_VENV` | Optional managed venv location |

PowerShell (current session):

```powershell
$env:DYMOLA_HOME = "C:\Program Files\Dymola 2024x"
$env:DYMOLA_MODELICAPATH = "C:\Carrier\Libs"
```

Persistent (user env var) — set via Windows “Environment Variables” UI, or:

```powershell
[System.Environment]::SetEnvironmentVariable("DYMOLA_HOME", "C:\Program Files\Dymola 2024x", "User")
```

Restart the terminal / Cursor after changing user env vars.

### Compiler / license

Headless translate uses the **same** Dymola license and compiler setup as the GUI.
If interactive Dymola cannot translate a model, the agent cannot either — fix that first.

---

## 5. Day-to-day workflows

### A. Validate a model

**You say:** “Validate `examples/FirstOrder.mo`.”

**Or run:**

```powershell
python scripts/dymola_run.py --mode validate `
  --model examples/FirstOrder.mo --name FirstOrder --json
```

### B. Simulate

```powershell
python scripts/dymola_run.py --mode simulate `
  --model examples/FirstOrder.mo --name FirstOrder --stop-time 5 --json
```

Artifacts appear under `_dymola_simulate_temp/` (next to the model):  
`dsres.mat`, `dsin.txt`, `dymosim.exe`, `dsmodel.c`, logs.

Plot:

```powershell
python scripts/plot_result.py path\to\dsres.mat --vars "y" --out y.png
python scripts/result_summary.py path\to\dsres.mat --vars "y" --json
```

### C. Encrypted library — list exposed parameters

**You say:** “Translate my plant and list exposed parameters from the encrypted lib.”

**Or run:**

```powershell
python scripts/dymola_run.py --mode list-params `
  --model MyPlant.mo --name MyPlant `
  --load "C:\Libs\VendorEncrypted\package.mo" --json
```

Then:

```powershell
python scripts/dsin_io.py _dymola_list_params_temp\dsin.txt --filter "pump" --json
```

`exposed_parameters.json` is written in the temp folder.  
**No decryption** — only what Dymola put in `dsin.txt`.

### D. Tune without recompiling

```powershell
python scripts/dsin_io.py path\dsin.txt --set "pump.N=1500,T=0.8" --out path\dsin_tuned.txt
python scripts/dymola_run.py --mode run-dymosim `
  --dymosim path\dymosim.exe --dsin path\dsin_tuned.txt --json
```

### E. Parameter sweep

```powershell
python scripts/smart_sweep.py `
  --dymosim path\dymosim.exe --dsin path\dsin.txt `
  --sweep "gain=0.5,1,1.5,2" --outdir sweeps --json
```

### F. Inspect compiled artifacts

```powershell
python scripts/dymosim_inspect.py path\to\workdir --out inspect.json
```

Use this to see what is **dsin-tunable** vs likely **structural** (needs `.mo` edit + retranslate).

### G. Diagnose a failure

```powershell
python scripts/diagnose_log.py path\to\dslog.txt --json
```

---

## 6. Example prompts for the agent

Copy-paste starters:

1. *“Read `USER_GUIDE.md`. Verify Python and Dymola (`--mode info`), then validate `examples/FirstOrder.mo`.”*  
2. *“Open `MyPlant.mo`, load our encrypted HVAC library, translate, and give me a table of exposed parameters matching `compressor`.”*  
3. *“Using the existing dymosim in `_dymola_simulate_temp`, sweep `setpoint` from 20 to 26 in steps of 1 and plot the final `T_zone`.”*  
4. *“Simulation failed — diagnose the log and propose the smallest `.mo` fix.”*  
5. *“Refactor so encrypted-library parameters I care about are top-level parameters on the plant model (for clean dsin names).”*

---

## 7. Decision cheat-sheet

| Situation | Do this |
|-----------|---------|
| First time / structure unclear | `dymola-model-architecture` |
| Edit or create `.mo` | `edit-modelica-dymola` |
| Does it check? | `validate-dymola` |
| Need results / plots | `simulate-dymola` |
| Encrypted lib — what can I tune? | `expose-encrypted-params` |
| Have dymosim — change numbers fast | `tune-parameters` |
| Override ignored / weird compile | `inspect-dymosim` + `diagnose-dymola` |

| Change type | Mechanism |
|-------------|-----------|
| Exposed numeric parameter | `dsin.txt` + `dymosim` (fast) |
| Structural / new equations / new component | Edit `.mo` + translate |
| Inside encrypted source | **Impossible** — only public modifiers / exposed dsin entries |

---

## 8. Troubleshooting

| Problem | Fix |
|---------|-----|
| `Could not locate a Dymola installation` | Set `DYMOLA_HOME` or `DYMOLA_EXE` (include `bin64`) |
| `wsm_run` / wrong toolkit | You’re in the System Modeler repo — use **this** repo’s `dymola_run.py` |
| `dymola_run.py not found` | `scripts/` missing beside skills — re-clone or set `DYMOLA_SKILLS_SCRIPTS` |
| License / translate fails in GUI too | Fix Dymola license / compiler first |
| `--set` says parameter missing | Name must match **exactly** what is in `dsin.txt` (use `--list` / `--filter`) |
| Override has no effect | Likely structural — `inspect-dymosim`, then edit `.mo` and retranslate |
| Plot script slow first time | Normal — managed venv bootstrap; or run `python scripts/bootstrap_env.py` |
| Git Bash weird errors on Windows | Use **PowerShell** |

Cleanup temp dirs when done:

```powershell
Remove-Item -Recurse -Force .\_dymola_*_temp -ErrorAction SilentlyContinue
```

---

## 9. Safety & IP rules (please keep)

- Do **not** ask the agent to decrypt `.moe` / protected packages.  
- Do **not** commit proprietary models, licenses, or vendor libs to a public fork.  
- Prefer committing only **your** open `.mo` wrappers and experiment scripts.  
- Treat `dsin.txt` / result mats as potentially sensitive (plant parameters).

---

## 10. Optional: warm up plotting env

```powershell
python scripts/bootstrap_env.py
python scripts/bootstrap_env.py --print-python
```

---

## Next reading

- [InstallationGuide.md](InstallationGuide.md) — agent auto-setup  
- [scripts/README.md](scripts/README.md) — full CLI flags  
- [ROADMAP.md](ROADMAP.md) — upcoming features & optimizations  
