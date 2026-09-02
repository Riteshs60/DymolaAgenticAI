# Dymola Agentic AI Toolkit

**Teach your AI coding assistant to build, simulate, diagnose, and tune
[Dymola](https://www.3ds.com/products/catia/dymola) / Modelica models — including
models that depend on encrypted libraries.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Platforms](https://img.shields.io/badge/Platforms-Windows%20%7C%20Linux-lightgrey.svg)

A bundle of **agent skills** (instructions + Python CLI tools) so Cursor, Claude
Code, Codex, or any CLI-capable assistant can:

1. **Write & edit** standard Modelica `.mo` files for Dymola  
2. **Validate / translate / simulate** via headless Dymola  
3. **Read exposed parameters** from encrypted libraries (via `dsin.txt` — no decryption)  
4. **Inspect** `dymosim.exe` and generated `dsmodel.c`  
5. **Tune & sweep** parameters by editing `dsin.txt` and re-running `dymosim` without recompile  
6. **Diagnose** translation/simulation failures from logs  

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

## What's inside

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

Shared tools live in [`scripts/`](scripts/README.md).

## Encrypted libraries (important)

| Allowed | Not allowed |
|---------|-------------|
| Read parameters Dymola writes to `dsin.txt` after translate | Decrypt `.moe` / protected source |
| Change those values and re-run `dymosim` | Recover hidden equations |
| Propagate top-level parameters into encrypted instance modifiers | Bypass Dymola licensing |

## Requirements

- **Python 3.8+**
- **Dymola** (licensed) for validate / translate / simulate  
- Plotting scripts auto-provision a managed venv (`DyMat`, `matplotlib`, `numpy`, `scipy`)

## Quick start

1. Clone this repo and keep the folder layout intact (`scripts/` beside skills).  
2. Point your AI assistant at this folder.  
3. Ask: *“Read `InstallationGuide.md` and set these skills up for me.”*  
4. Try: *“Translate my model and list exposed parameters from the encrypted library.”*

```bash
python scripts/dymola_run.py --mode info
```

## Branch note

Active development of the skill pack lives on `feature/dymola-agentic-skills`.

## License

MIT — see [LICENSE](LICENSE).
