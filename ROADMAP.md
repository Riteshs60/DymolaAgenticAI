# Roadmap — features & optimizations

Prioritized ideas for growing this toolkit. **P0** = highest leverage next;
**P2** = nice-to-have.

---

## Recommended next features (P0)

### 1. Robust official `dsin` / `dsfinal` parser
Today’s `dsin_io.py` uses heuristics across Dymola versions. Add fixtures from
real Dymola 2023x/2024x/2025x `dsin.txt` files and a version-aware parser
(double/int/char arrays, `# matrix` blocks). This unlocks reliable encrypted-param
catalogs.

### 2. Requirement / KPI checker
After simulate or sweep, assert limits in JSON, e.g.:

```json
{ "y": { "max": 1.2, "final_between": [0.9, 1.1] } }
```

Emit pass/fail for agent loops (“raise gain until overshoot < 10%”).

### 3. Sensitivity ranking (one-at-a-time)
Auto-perturb each exposed dsin parameter ±ε, score impact on a target signal,
return a ranked table. Huge for encrypted plants where intuition is limited.

### 4. Calibration / least-squares fit
Given measured CSV + target variables, optimize a small set of dsin parameters
(scipy.optimize) by repeated `dymosim` runs — no retranslate.

### 5. Stable JSON contract
Every mode of `dymola_run.py` should always write `summary.json` with the same
top-level keys (`ok`, `mode`, `artifacts`, `errors[]`) so agents never scrape
stdout.

---

## Strong features (P1)

| Idea | Why |
|------|-----|
| **FMU export skill** | `translateModel` → FMU for use outside Dymola |
| **Multi-param cartesian / DOE sweeps** | Extend `smart_sweep.py` beyond one parameter |
| **dsu.txt input profiles** | Time-varying inputs without rebuilding |
| **Library registry** | `libraries.json` mapping short names → `package.mo` paths |
| **Result comparison** | Diff two `.mat` runs (baseline vs candidate) |
| **Annotation experiment helper** | Sync `annotation(experiment(...))` with CLI `--stop-time` |
| **Wrapper generator for encrypted libs** | Generate thin `.mo` that re-exposes selected parameters as top-level |
| **Parallel sweep workers** | Run N dymosim copies in parallel (license permitting) |

---

## Optimizations (do these even without new features)

| Item | Impact |
|------|--------|
| **Cache translates** | Hash `(model sources + libs + flags)` → reuse `dymosim` folder; avoid retranslate on pure param work |
| **bin64 / multi-version discovery** | Partially done — also prefer newest year, support `Dymola 2025x Refresh 1` paths |
| **Faster headless flags** | Document/test `/s` vs `/nowindow` per Dymola version; avoid GUI splash delays |
| **Temp-dir reuse flag** | `--keep-temp` / `--reuse-temp` so agents don’t delete a good dymosim between turns |
| **Copy runtime DLLs smartly** | `smart_sweep` already copies `*.dll`; also handle Linux `.so` and `dsmodel` sidecars |
| **Unit tests + CI** | pytest on `dsin_io`, `mo_params`, `diagnose_log` with checked-in fixtures (no Dymola needed) |
| **Type hints + `ruff`** | Keep scripts agent-readable and consistent |
| **Structured logging** | Replace ad-hoc prints with `--json` everywhere |

---

## Agent-experience improvements

1. **Single “orchestrator” skill** — `dymola-agent` that routes to sub-skills (less wrong-skill selection).  
2. **Prompt library** in `USER_GUIDE.md` expanded with Carrier/HVAC-style examples (sanitized).  
3. **Session state file** — `.dymola-agent/state.json` remembering last workdir, dymosim path, last overrides.  
4. **Guardrails skill section** — refuse decrypt requests explicitly with a canned explanation.  
5. **Cursor custom commands** — e.g. `/dymola-validate`, `/dymola-sweep`.  

---

## Integrations (P2)

- Export sweep results to CSV/Parquet for Excel / Power BI  
- Optional MLflow / simple SQLite run tracking  
- OpenModelica fallback for **open** models only (clearly labeled; not for encrypted Dassault libs)  
- GitHub Action that runs pytest (and optional Dymola job on a self-hosted runner)

---

## What not to build

- Anything that attempts to **decrypt** or reverse protected libraries  
- A full second Modelica compiler — stay a thin automation layer on Dymola  
- GUI automation via screenshots when `.mos` scripting exists  

---

## Suggested milestone order

1. Golden `dsin` fixtures + parser tests  
2. `--reuse-temp` + translate cache  
3. KPI checker + sensitivity ranking  
4. Calibration loop  
5. FMU export + library registry  

Contributions welcome — open a PR against `feature/dymola-agentic-skills` (or `main` after merge) and link the roadmap item you address.
