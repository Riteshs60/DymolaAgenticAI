# Dymola Agentic AI Toolkit

**Teach your AI coding assistant to build, simulate, diagnose, and tune
[Dymola](https://www.3ds.com/products/catia/dymola) / Modelica models — including
models that depend on encrypted libraries.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Platforms](https://img.shields.io/badge/Platforms-Windows%20%7C%20Linux-lightgrey.svg)

A bundle of **agent skills** (Markdown instructions + Python CLI tools) so
[Cursor](https://cursor.com), Claude Code, Codex, or any CLI-capable assistant can
work with Dymola the same way a skilled user would — from the terminal.

| Doc | Audience |
|-----|----------|
| **[USER_GUIDE.md](USER_GUIDE.md)** | Humans — install, day-to-day use, example prompts |
| **[InstallationGuide.md](InstallationGuide.md)** | AI agents — automated setup checklist |
| **[scripts/README.md](scripts/README.md)** | CLI reference for every script |
| **[ROADMAP.md](ROADMAP.md)** | Planned features & optimization ideas |

---

## What it does (30-second version)

```text
You (plain English)
        ↓
AI assistant (Cursor / Claude / Codex)
        ↓
This toolkit (skills + scripts/)
        ↓
Dymola  →  check / translate / simulate
        ↓
dymosim.exe + dsin.txt + dsres.mat
```

1. **Write & edit** standard Modelica `.mo` files for Dymola  
2. **Validate / translate / simulate** via headless Dymola  
3. **Read exposed parameters** from encrypted libraries (via `dsin.txt` — no decryption)  
4. **Inspect** `dymosim.exe` and generated `dsmodel.c`  
5. **Tune & sweep** parameters by editing `dsin.txt` and re-running `dymosim` (no recompile)  
6. **Diagnose** translation/simulation failures from logs  

## Encrypted libraries (important)

| Allowed | Not allowed |
|---------|-------------|
| Read parameters Dymola writes to `dsin.txt` after translate | Decrypt `.moe` / protected source |
| Change those values and re-run `dymosim` | Recover hidden equations |
| Propagate top-level parameters into encrypted instance modifiers | Bypass Dymola licensing |

## Requirements

| Piece | Required? | Notes |
|-------|-----------|--------|
| Python 3.8+ | Yes | On Windows use PowerShell + `python` |
| Dymola (licensed) | For simulate/validate | Set `DYMOLA_HOME` if auto-detect fails |
| C/C++ toolchain | Usually via Dymola’s own compile setup | Same as interactive Dymola translate |
| Plotting packages | Auto | Managed venv: DyMat, matplotlib, numpy, scipy |

## Install in 3 steps

### 1. Clone (keep the folder together)

```powershell
git clone https://github.com/Riteshs60/DymolaAgenticAI.git
cd DymolaAgenticAI
git checkout feature/dymola-agentic-skills
```

Do **not** move `scripts/` away from the skill folders.

### 2. Open this folder in your AI tool

- **Cursor:** File → Open Folder → this repo (`.cursor/rules` is already included)
- **Claude Code:** run `.\install.ps1` (Windows) or `./install.sh` (Linux/macOS)
- **Other agents:** open the repo and ask the agent to read `InstallationGuide.md`

### 3. Verify Dymola + Python

```powershell
python --version
python scripts/dymola_run.py --mode info --json
```

If Dymola is not found:

```powershell
$env:DYMOLA_HOME = "C:\Program Files\Dymola 2024x"
# or explicitly:
$env:DYMOLA_EXE  = "C:\Program Files\Dymola 2024x\bin64\Dymola.exe"
```

Full walkthrough (Cursor vs Claude, libraries, troubleshooting): **[USER_GUIDE.md](USER_GUIDE.md)**.

## Try it

Ask your assistant things like:

- “Read `USER_GUIDE.md`, then validate `examples/FirstOrder.mo` in Dymola.”
- “Translate my plant model and list every exposed parameter (including encrypted libs).”
- “Change `pump.N` in dsin and re-run dymosim without recompiling.”
- “Sweep `gain` from 0.5 to 2.0 and summarize the final output.”

Or run yourself:

```powershell
python scripts/dymola_run.py --mode validate --model examples/FirstOrder.mo --name FirstOrder --json
python scripts/dsin_io.py examples/sample_dsin.txt --list
```

## Skills

| Skill | Role |
|-------|------|
| `dymola-model-architecture` | Structure models; expose params for tuning |
| `edit-modelica-dymola` | Create/edit `.mo` for Dymola |
| `validate-dymola` | `checkModel` headlessly |
| `simulate-dymola` | Simulate, or re-run `dymosim` |
| `expose-encrypted-params` | Catalog public params from encrypted deps |
| `inspect-dymosim` | Analyze `dymosim` / `dsmodel.c` / `dsin` |
| `tune-parameters` | Overrides, sweeps, calibration loop |
| `diagnose-dymola` | Log parsing + fix suggestions |

## License

MIT — see [LICENSE](LICENSE).
