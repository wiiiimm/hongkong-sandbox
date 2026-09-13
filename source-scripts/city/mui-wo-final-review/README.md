# Staged Mui Wo source refinements

HKS-192 checkpoint only. These scripts read live data but **do not publish it**. See the [review and remaining checklist](../../../docs/astra-city/mui-wo-final-review/README.md).

Reuse the retained original assets from `mui-wo-models`, `mui-wo-completion` and the original model-sample review. Run `fetch_terrain.py` to restore only adjoining sheet 10-SW-8C through the existing byte-range downloader. It retains two unmodified TERRAIN glTF/bin members; no buildings or photographs are requested. Caches and raw extracted geometry are ignored, but index, manifest, ranges and source hashes are retained. A clean checkout needs the earlier packages' documented cache-restoration commands before rerunning the native audit.

From the worktree root, run `audit.py`, `fetch_terrain.py`, `refine.py`, `verify.py`, `runtime_checks.mjs`, then `test_refinements.py`; Python uses `/tmp/astra-city-venv/bin/python`, JavaScript uses Node. Exact commands are in the review README.

Outputs:

- `terrain-refinements.json`: five child grids for the existing `city/data/terrain-mui-wo.json` parent. `coarseCells` indexes that **parent's 5 m lattice**. Raw source samples are separately retained in `source-grids/`; display samples include the explicit outer transition. Spacing is not surveyed accuracy.
- `building-estimate-updates.json`: two dependent derived-base updates, guarded by UID, previous base, null official vertical values and absence of detailed geometry. Preserve source fields, footprints and the existing 3.5 m estimated height.
- `diagnostic-updates.json`: six derived `terrainAudit` flag changes after terrain integration. No source geometry/elevation changes.
- `staged/10-SW-8C`: source manifest and original 5 m samples, not a replacement live patch.

`geo.js` already samples nested patches. Root must integrate nested patch rendering into the existing `world.js` chunk path, apply the guarded payloads together, then validate live seams, roofs, collisions, day/night/mobile exports and performance. This checkpoint deliberately contains no renderer or live-data changes.
