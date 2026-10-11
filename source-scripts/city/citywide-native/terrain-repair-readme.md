# Native terrain repair — HKS-222

This separate pass processes only failed terrain entries from a completed native preparation run. It does not rerun buildings, download government payloads, modify the viewer or grant placement approval. Original source bundles remain immutable in R2.

```sh
/tmp/astra-city-venv/bin/python source-scripts/city/citywide-native/repair_terrain_run.py \
  --original-run ORIGINAL_RUN_ID --batch terrain-repair-20260909 --workers 6 \
  --env-file /absolute/path/to/private/.env.local
```

Use the configured modelling Python environment on another machine. The database connection remains pinned by the existing shared-modelling branch configuration. Only R2 variables are read from the supplied environment file. Identical frozen inputs resume across batch labels; do not edit the repair code while it runs.

Each sheet is leased under `native-terrain-repair`, using the original source and footprint SHA, a separate repair pipeline hash, and explicit `originalCacheKey`, `originalArtifact` and failed `sourceEntries`. The terrain SHA is null because this pass handles native source geometry, not sampled viewer terrain. It verifies complete R2 source bundles, writes token-isolated working files, uploads and reads back repaired artefacts, then commits through the existing fenced bulk result API.

Supported mechanical actions:

- Preserve native POSITION and index accessor bytes exactly, verified before and after derivation. Keep original buffers and source glTF in the artefact.
- Omit UVs and texture references because photographs are omitted. Regenerate missing/non-finite shading normals from unchanged triangles. Degenerate triangles remain; zero-length normals use a documented finite up-vector for shading only.
- Convert finite standard TRS into an equivalent source matrix in T × R × S order; validate unit quaternions and preserve declared source scale exactly (including inch-to-metre conversion). Existing source matrices and the city translation `[-834500, 0, 816500]` remain unchanged, at vertical scale 1.
- Remove only known material-only `KHR_materials_specular` and `KHR_materials_ior` extensions for geometry-only output. Other extensions, invalid TRS, invalid positions or invalid triangles remain explicit failures.
- Classify sources with zero mesh primitives as `source-empty`; never invent terrain for them.

Results contain an empty building `models` array and one `terrain` outcome per selected source entry: `prepared-geometry-only`, `source-empty`, or `failed`. Successful outcomes include original source hashes, repair actions and geometry proof. Proof records position/index SHA, world bounds, transforms and the absence of elevation scaling. This is preparation evidence, not a terrain publication decision.

Use `audit_run.py --terrain-repair-run REPAIR_RUN_ID` with the matching original run to inspect effective counts. The audit preserves original failures and overlays only matching original cache/source/entry identities. Local complete summaries and compressed result ledgers are under `local/terrain-repair/runs/REPAIR_RUN_ID/`; root checkpointing retains these in R2.

Tests: `python -m unittest discover -s source-scripts/city/citywide-native -p test_terrain_repair.py -v`. Nine tests cover source-byte preservation, translation equivalence, invalid-geometry refusal, unsupported extensions, genuine empty sources, degenerate triangles and complete verified-bundle processing.
