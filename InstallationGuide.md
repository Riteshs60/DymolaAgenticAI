# Installation Guide (for the LLM agent)

**You are an LLM agent with CLI access.** The user asked you to install these
Dymola skills. Follow this guide, then confirm readiness with a small test.

## Step 1 — Keep the layout intact

Do **not** split skill folders from `scripts/`. Skills call
`../scripts/dymola_run.py`. Install/copy the whole repo as a unit.

## Step 2 — Python 3

```powershell
python --version
```

Need 3.8+. On Windows use **PowerShell** (not Git Bash).

## Step 3 — Make skills visible to the agent

**Claude Code:**

```powershell
./install.ps1
```

**Cursor / Codex / other:** add pointers in standing instructions (e.g.
`.cursor/rules` or `AGENTS.md`) naming each skill and its `SKILL.md`, **or**
read the matching `SKILL.md` on demand. No framework lock-in.

## Step 4 — Dymola

Check discovery:

```powershell
python scripts/dymola_run.py --mode info --json
```

If not found, set one of:

```powershell
$env:DYMOLA_HOME = "C:\Program Files\Dymola 2024x"
# or
$env:DYMOLA_EXE = "C:\Program Files\Dymola 2024x\bin64\Dymola.exe"
```

Optional library path:

```powershell
$env:DYMOLA_MODELICAPATH = "C:\MyLibs"
```

## Step 5 — Optional plotting venv warm-up

```powershell
python scripts/bootstrap_env.py
```

## Step 6 — Smoke test

Ask the user for a small `.mo` model (or use `examples/FirstOrder.mo`), then:

```powershell
python scripts/dymola_run.py --mode validate --model examples/FirstOrder.mo --name FirstOrder --json
```

If Dymola is unavailable, you can still unit-exercise `dsin_io.py` against a
sample dsin later — but validate/simulate need Dymola.

## Tell the user

Skills are ready. Suggested first prompts:

- “Validate `examples/FirstOrder.mo` in Dymola.”
- “Translate my plant model and list exposed parameters (including encrypted libs).”
- “Sweep `gain` with dymosim without recompiling.”
