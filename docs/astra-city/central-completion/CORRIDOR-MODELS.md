# Wan Chai–Central–Sheung Wan: retained-source expansion

This stages 20 additional exact government models from source sheets already retained for the Central work. It uses the unchanged native geometry decoder and compact packer; no source download, city tile edit or live catalogue publication was performed.

The 22 nominated source forms produced 20 accepted unique matches: four in section 01.4, eleven in 02.1 and five in 02.2. They include both Shun Tak forms, Western Market, The Center, Central Plaza, Immigration and Revenue towers, Hopewell Centre, four Blue House forms, Southorn Stadium/Centre, Three Pacific Place, HKCEC, Hong Kong Arts Centre and three HKAPA forms. The separate initial 17-model batch is unchanged.

Every accepted record has an exact GeoRefNo and unique model/BuildingCSUID component. Reused matching rules require at least 50% overlap of the smaller projected model hull/footprint and at most 10 m between their centroids. Several eastern buildings were outside the original narrow Central selection, so the same screen was applied to their current government source records. No thresholds were relaxed.

Two specific gaps retain their original footprints:

- **Man Mo Temple (`landsd/254567:0`)**: no native model with its exact GeoRefNo was present in the retained source inventory.
- **HKAPA Administration Block (`landsd/69025:0`)**: its available source model overlaps 99.97% of the smaller footprint, but the 11.159 m centroid difference fails the existing 10 m screen. It needs an explicit source review before replacement.

The staged catalogue is `source-scripts/city/central-completion/compact-corridor/catalogue.json`. Its assets total 2,754,798 gzip bytes, 11,161,176 decoded source geometry bytes and 103,919 original triangles. Their summed runtime memory reservation is 43,379,044 bytes. They use the same distance, projected-size and cache budgets as the initial batch; the catalogue is not an eager download list.

All 20 pass the actual `loadOfficialModel` decoder: compressed hashes, counts, original transforms/bounds, current UID/OBJECTID/CSUID and recorded heights, preserved activity, indexed geometry and source material/node provenance. Evidence is in `corridor-models.json` and `corridor-runtime-verification.json`. Existing section review, public street/deck access, continuous navigation, terrain placement and rendered desktop/mobile acceptance remain separate work; this is not a complete district claim.

Reproduce from the Astra worktree:

```sh
/private/tmp/astra-city-venv/bin/python -B source-scripts/city/central-completion/corridor_models.py
node 3d-viewer/city/tests/official-model-staged.mjs compact-corridor
```
