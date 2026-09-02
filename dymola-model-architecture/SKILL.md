---
name: dymola-model-architecture
description: "Architecture guidance for Dymola/Modelica models and libraries before writing equations. Use when structuring a new model, exposing parameters for encrypted deps, or organizing packages."
---

# Dymola / Modelica architecture

Use **before** writing a large model.

## Checklist

1. Reuse MSL / existing libraries before inventing components
2. Decompose into replaceable components with clear connectors
3. Keep top-level models thin: wire + parameters + experiments
4. For encrypted vendor libraries:
   - Put instances in a thin wrapper model
   - Expose only the parameters you want to calibrate as **top-level parameters** propagated into the instance modifiers — so they appear cleanly in `dsin.txt`
5. Prefer directory-form packages (`package.mo` + one class per file) for anything beyond a toy
6. Add a smoke-test example model that translates under Dymola

## Exposing parameters for agents

```modelica
model Plant
  parameter Real pumpSpeed = 1200;
  EncryptedLib.Pump pump(N = pumpSpeed);
end Plant;
```

This makes `pumpSpeed` an obvious dsin entry for `tune-parameters` without needing encrypted source.
