# Installed-model Meshopt follow-up — 13 October 2026

Executor Codex, using `hong-kong-model-optimisation`. The user authorised continuing compression after the latest Astra inventory check. The new committed installed snapshot contains 6,650 unique UIDs under `installed-v1`, with zero review-based exclusions. Nam Fung Court (`landsd/79099:0`) is the sole new source; all previous 6,649 revisions are unchanged. Preserve the previous immutable 12 October evidence.

Four unchanged pinned recipes produce lossless/original, high, balanced and lightweight candidates. The existing leased pipeline reuses all 26,596 completed same-source/same-recipe variants, processes the four additional candidates and independently re-audits all 26,600 current outputs. Processing results remain staged/unreviewed; original sources, reviews and runtime catalogues remain unchanged by compression. No historical-map reference images used.

## Reproducible commands

Set `MODELLING_ENV_FILE` to the existing pinned modelling credentials without using the application database. With the established Python environment:

```sh
python source-scripts/city/model-optimisation/run_installed_batch.py \
  --folder docs/astra-city/model-optimisation/installed-enhanced-meshopt-followup-v2-20261013 \
  --staging source-scripts/city/model-optimisation/staging/installed-enhanced-meshopt-followup-v2-20261013 \
  --workers 16
python source-scripts/city/model-optimisation/summarise_installed_batch.py \
  --folder docs/astra-city/model-optimisation/installed-enhanced-meshopt-followup-v2-20261013 --apply
```

A completed run must have all four independent audit checkpoints with exact Neon readback, then a final verified summary. No approval/publication is inferred from processing. Source error estimates are offline Float64/quadric diagnostics; rendered Float32 placement/terrain/support, visual/collision, physical-device memory/frame time and runtime publication require separate validation. These candidates establish download measurements, not FPS or resident-memory improvements; UInt32 index repacking can increase accessor estimates.
