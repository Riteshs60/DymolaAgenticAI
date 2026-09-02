# Installation Guide (for the LLM agent)

**You are an LLM agent with CLI access.** The user asked you to install or set
up these Dymola skills. Follow this checklist end-to-end, then tell the user
what works and what is still missing.

Humans should prefer **[USER_GUIDE.md](USER_GUIDE.md)**. You may still cite it.

---

## Step 0 — Confirm you are in the right repo

You should see `scripts/dymola_run.py` and folders like `validate-dymola/`,
`expose-encrypted-params/`. If you only see `wsm_run.py`, you are in the
**System Modeler** toolkit — stop and open `DymolaAgenticAI` instead.

---

## Step 1 — Keep the layout intact

Do **not** move skill folders apart from `scripts/`. Skills resolve tools as
`../scripts/dymola_run.py`. Install/copy the **whole** repo as a unit.

Resolve `<scripts-dir>` in this order:

1. `$env:DYMOLA_SKILLS_SCRIPTS` / `$DYMOLA_SKILLS_SCRIPTS` if set  
2. `../scripts` relative to the skill directory  
3. `<repo-root>/scripts`

---

## Step 2 — Python 3

```powershell
python --version
```

Need **3.8+**. On Windows use **PowerShell** (not Git Bash). Prefer `python`
over `python3` on Windows.

If missing: help the user install Python (e.g. `winget install Python.Python.3.12`)
and ensure “Add to PATH” is enabled. Then open a **new** terminal.

---

## Step 3 — Make skills visible to the agent

### If you are Claude Code

```powershell
./install.ps1
# or: ./install.ps1 -Copy
```

```bash
./install.sh          # or ./install.sh --copy
```

Tell the user to **start a new session**, then list skills
(`validate-dymola`, `simulate-dymola`, `expose-encrypted-params`, …).

### If you are Cursor

The repo already includes `.cursor/rules/dymola-agentic-ai.mdc`. Confirm the
workspace root **is** this repo. No junction install required.

### If you are Codex / other

Create or update `AGENTS.md` (or the agent’s standing instructions) with short
pointers to each `*/SKILL.md`, **or** commit to reading the matching skill on
demand. Skills are plain Markdown + CLI — no framework lock-in.

---

## Step 4 — Discover Dymola

```powershell
python scripts/dymola_run.py --mode info --json
```

On success, show the user `dymola_home` and `dymola_exe`.

On failure, search common paths (`Program Files\Dymola*`, `bin64\Dymola.exe`)
and ask the user to set:

```powershell
$env:DYMOLA_HOME = "C:\Program Files\Dymola 2024x"
# or
$env:DYMOLA_EXE  = "C:\Program Files\Dymola 2024x\bin64\Dymola.exe"
```

Offer to set a **User** environment variable for persistence. Re-run `--mode info`.

Optional libraries:

```powershell
$env:DYMOLA_MODELICAPATH = "C:\MyLibs"
```

**License check:** if info works but validate fails with license errors, tell
the user to fix the Dymola license in the GUI first — the agent cannot bypass it.

---

## Step 5 — Optional plotting venv warm-up

```powershell
python scripts/bootstrap_env.py
```

Not required for validate/translate; required path for plots/summaries will
auto-bootstrap on first use anyway.

---

## Step 6 — Smoke tests

### Without Dymola (always)

```powershell
python scripts/dsin_io.py examples/sample_dsin.txt --list
python scripts/mo_params.py examples/FirstOrder.mo --list
```

### With Dymola

```powershell
python scripts/dymola_run.py --mode validate `
  --model examples/FirstOrder.mo --name FirstOrder --timeout 120 --json
```

Report pass/fail clearly. On fail, run `diagnose_log.py` on the generated log
and summarize the first actionable errors.

---

## Step 7 — Tell the user

Say they are ready when:

- [ ] Python OK  
- [ ] Skills visible (or Cursor rule present)  
- [ ] `dymola_run.py --mode info` OK **or** user was told how to set `DYMOLA_HOME`  
- [ ] At least the dsin/mo smoke test passed  

Suggested first prompts:

- “Validate `examples/FirstOrder.mo` in Dymola.”  
- “Translate my plant and list exposed parameters from the encrypted library.”  
- “Sweep `gain` with dymosim without recompiling.”  
- “Read `USER_GUIDE.md` and walk me through encrypted-parameter tuning.”  

Point them to **[USER_GUIDE.md](USER_GUIDE.md)** for day-to-day workflows and
**[ROADMAP.md](ROADMAP.md)** for upcoming ideas.

---

## Appendix — environment variables

| Variable | Purpose |
|----------|---------|
| `DYMOLA_HOME` | Install root |
| `DYMOLA_EXE` | Full path to executable |
| `DYMOLA_MODELICAPATH` | Extra Modelica libraries |
| `DYMOLA_SKILLS_SCRIPTS` | Absolute `scripts/` path |
| `DYMOLA_SKILLS_VENV` | Managed venv override |
| `MODELICAPATH` | Also honored if `DYMOLA_MODELICAPATH` unset (via Dymola itself) |
