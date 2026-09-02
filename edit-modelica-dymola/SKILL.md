---
name: edit-modelica-dymola
description: "Create or edit Modelica .mo files intended for Dymola, including public modifiers that expose parameters from encrypted components. Use when writing models, wiring components, or exposing tuneable parameters."
---

# Edit Modelica for Dymola

## Practices

- Prefer standard Modelica + MSL; avoid tool-only vendor language unless required
- For encrypted library components, set **public parameters via modifications** at the instance site, e.g.:

```modelica
EncryptedLib.Pump pump(
  N = 1500,
  useHeatTransfer = false
);
```

- After edits: `validate-dymola`, then `list-params` to confirm exposure in `dsin.txt`
- Use `mo_params.py` only for simple top-level assignments; for nested modifiers, edit the `.mo` carefully yourself

## Workflow

1. Read existing model / library layout
2. Make the smallest change that satisfies the request
3. Validate with Dymola
4. If tuning is needed next, hand off to `tune-parameters` / `expose-encrypted-params`
