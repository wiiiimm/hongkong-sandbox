# Whole-Hong-Kong government source catalogue — HKS-221

The retained official index contains **3,456 sheets**, all checked successfully. The directory catalogue lists **216,976 unique model identifiers** and **216,724 geographic references**, with no repeated model identifiers across the checked sheets. These are model/source identifiers, not a count of exact matched buildings or accepted landmarks.

The initial acquisition transferred **243,653,483 bytes** of archive tails and central directories. The listed compressed glTF/bin members total **1,646,793,894 bytes** across this snapshot. That is a planning figure for the listed non-textured native members, not an all-inclusive textured-scene download budget. External glTF dependencies still require inspection. No model-member acquisition or conversion was performed by this stage.

Source: the Lands Department non-textured 3D Visualisation Map geographic download index, retrieved **8 September 2026 at 19:29:49 UTC**. The exact input hash is retained in `summary.json`. This is pinned-source coverage, not a claim that all present-day construction appears in the government dataset.

- [Official dataset](https://data.gov.hk/en-data/dataset/hk-landsd-openmap-3d-visualisation-map-non-textured-models)
- [Official geographic index](https://portal.csdi.gov.hk/server/rest/services/common/landsd_rcd_1742809441342_98380/FeatureServer/0)
- Script and unattended commands: `source-scripts/city/citywide-source/README.md`.
- `summary.json`: final scan coverage, source/pipeline fingerprints and transfer totals.
- `catalogue-counts.json`: deduplicated directory identifiers and listed member sizes.
- `reuse-verification.json`: two-run proof with actual new HTTP request/byte deltas.

The full `directories.json.gz` and raw ZIP-directory caches are ignored by Git and included in the HKS-221 R2 checkpoint. Per-sheet records are queryable in pinned Neon `astra_modelling.city_source_directories`; the run pointer is in `city_source_discovery_runs`. Native acquisition, exact CSUID/footprint matching, conversion, terrain checks and visual acceptance remain separate stages. Existing installed models and the paused manual-review ledger are unchanged.

## Verified working checkpoint

`R2-CHECKPOINT.json` records the immutable R2 manifest and source Git commit. The archive is **109,697,065 bytes**, containing **10,387 files** (304,801,063 bytes unpacked). Upload and fresh-cache remote readback passed. Every extracted file matched its recorded hash; the restored checkout then reused **all 346,115** audit results with **zero new checks**, in **28.92 seconds**. This was tested on the same Mac using the existing runtime/private configuration, not another operating system.

The same receipt is queryable in pinned Neon `astra_modelling.city_working_checkpoints`, keyed by the manifest SHA. The current source directory run and full audit count were rechecked from Neon before registering it. This working checkpoint is separate from runtime asset publication and does not change the viewer.
