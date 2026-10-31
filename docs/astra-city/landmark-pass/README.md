# Named landmark pass — HKS-202 / HKS-203 / HKS-204 / HKS-174

The viewer gains **59 detailed government building parts**: two IFC podiums, four Tai O Heritage Hotel parts, 36 Po Lin parts (including the previously omitted Grand Hall of Ten Thousand Buddhas), and 17 Ngong Ping visitor-village parts. Model assets total **821,735 compressed bytes**. [Compare the 17 reviewed views](comparison.html).

The corrected selection accounts for **87 source parts**, with **67 now detailed**, **19 without a separate exact-reference source entry in the checked sheet revisions**, and **one held model**. The 19 are 13 open-sided and six temporary structures. Some canopy geometry already exists inside neighbouring detailed meshes: Bank of China94.3%, Mui Wo pier88.8%, Tai O hotel100% horizontal triangle coverage. Those figures do not establish complete standalone models or justify automatic fallback suppression. This pass does not certify an entire landmark or region complete.

## Why the earlier script skipped them

The first batch reused locally staged, unambiguous models. The next pass retrieves missing exact-reference entries from the existing public Lands Department non-textured-model sheet index. IFC's irregular podiums exceeded the generic10m centroid threshold despite strong footprint overlap; their exact IDs and original geometry now have explicit, recorded review exceptions. The Grand Hall had a different name and was missing from the first explicit Po Lin list; it is added to the versioned selection. No general matching threshold was relaxed.

`context.json` contains the complete87-part source ledger. The source is `landsd_rcd_1742809441342_98380`, EPSG:2326 / Hong Kong Principal Datum; originals use a single translation `[-834500,0,816500]`. Original glTF attributes, node transforms and model elevations remain unchanged. Public source URLs, complete ZIP-directory evidence, revision dates, byte ranges and checksums are retained by the acquisition scripts. Models have no photographic textures; current procedural materials/window lighting remain in use. No historical map images were used.

## Placement decisions and terrain

- Ngong Ping receives a non-overlapping5m patch from the existing government DTM/native-TIN pipeline. Its three previously buried highest-roof diagnostics disappear. The59 installed models pass shared loader, source-surface collision/picking and rendered-terrain checks.
- The Hall of Great Hero is supported by a separate native podium:348 interior rays hit its platform within0.167m of the hall base. The Grand Hall has1062 platform hits. Neither hall is lowered onto bare terrain.
- Hua Yan Pagoda211847 remains basic: its available model floats at least3.23m above source ground with no neighbouring support. No artificial foundation or height shift is introduced.
- Tai O's original1m child2 is enlarged using retained native TIN. Main hotel67478 is revealed where the old edge transition buried it. The outbuilding239278 retains a small native ground/roof discrepancy (up to0.183m at the sampled current terrain maximum); no invented excavation is applied. Other local lower-vertex terrain intersections remain documented in the context report.
- Canopy240278 has no surveyed base/top. Its existing terrain-estimated base changes11.617→4.184m, with its3m estimated height retained. Its sloping-ground partial-burial diagnostic remains; this is an estimate, not a new surveyed model. All other building records, footprints and surveyed elevations are unchanged.

The publisher binds the original parent/child hashes, preserves unrelated terrain children and parent arrays, rejects overlapping/newly stale patches, and installs the manifest last with atomic rollback.924 stored seam checks pass. Six affected Tai O forms have no newly introduced diagnostic flags after the guarded estimated-base correction.

## Verification and review limits

228 city tests,20 batch tests and14 publisher tests pass. The new publisher tests include stale hashes, overlap/malformed grids, replacement guards, paired estimate guards and injected rollback. `live-validation.json` records the59 installed assets against the actual viewer terrain (the validator's generic `staged` label is not publication status; `publication.json` is).

The browser compares17 locations before/after, exercises day/night,390px mobile layouts, native source picking/collision, public arrival, walking, flying and failed-load fallback/Retry. Final `browser/after/verification.json` uses installed assets with no staged routes. Frame median is about16.7ms and p95 at most16.8ms in desktop Chrome, including mobile viewport emulation; this is not a physical-phone performance guarantee or complete route review.

All346,115 base forms remain. There are now2,157 progressive and1,859 embedded detailed models (4,016 total). R2 production delivery remains HKS-206; this feature branch does not merge or release production. HKS-202 and regional completion remain open for remaining acquisition/placement work; the delivered trial is for review under HKS-203/204.

**Vertical scale is fixed at1×.** Vertical exaggeration/“epic mountains” is explicitly excluded from Astra parity (HKS-117/131/182/187). Terrain corrections use actual source elevations; no multiplier is applied to geometry, collision, water or navigation.

Executors: Root (acquisition, Ngong terrain, integration, browser and publication); landmark_gap_audit (IFC/hotel/Grand Hall acquisition and native component checks); terrain_publication_guard (Tai O terrain and shared publisher guards/tests).

## Reproduce

Run from the Astra worktree with the existing source Python environment (`/tmp/astra-city-venv/bin/python` here) and Node24. Native source caches/staging and approved intermediates are ignored; deployed GLB.gz/catalogues and terrain are tracked under `3d-viewer/city/data/`.

1. Refresh `building-batch/inventory.py`; run `selection.py --config source-scripts/city/landmark-pass/selection.json --out source-scripts/city/landmark-pass/selection`.
2. Run `landmark-pass/acquire.py plan`, then `run`. Use `acquire_existing.py` and `acquire_grandhall.py` for exact exceptional groups. The shared range fetcher reuses retained original entries and keeps provenance.
3. Run `cached_models.py plan/run --selection landmark-pass-v2 --out source-scripts/city/landmark-pass/compact`; completed live detail is skipped. Do not overwrite an earlier reviewed candidate snapshot with a later no-op result.
4. Terrain staging: `landmark-pass/terrain.py` and `taio_terrain.py` (see its CLI). `validate_candidates.mjs` accepts `--candidates`, `--terrain-candidate`, and `--terrain-replacements` for read-only pre-publication checks.
5. `review.py prepare` and `publish` are deliberately pinned to this pre-publication snapshot. The recorded guard rejects replay after publication; restore the recorded baseline in an isolated worktree to reproduce this exact publication. Future passes require a new explicit reviewed set/plan, not forced repeated publication.
6. Browser: `REVIEW_CONFIG=source-scripts/city/landmark-pass/final-browser-config.json node source-scripts/city/building-batch/browser.mjs before`; use `live-browser-config.json ... after` for installed verification on local4176. `report.py` checks recorded baseline hashes and regenerates counts/gallery.
