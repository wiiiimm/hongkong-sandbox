# Local building inventory — HKS-199 / HKS-200

Run from the Astra worktree root (Python standard library only):

```sh
python3 source-scripts/city/building-batch/inventory.py
python3 -m unittest discover -s source-scripts/city/building-batch -p 'test_inventory.py' -v
```

The first command writes `source-scripts/city/building-batch/local/buildings.sqlite`, which is ignored by Git and not deployed. Use `--db` for another location and `--viewer` for another input snapshot. Do not run concurrently with a publisher changing the viewer assets; the inventory has a single SQLite writer transaction. Reading/hashing local inputs is deliberate even on repeated runs so changed bytes cannot silently look complete.

Inputs are the existing city manifest, 452 tile files, official-model catalogues/assets and 132 review-section definitions. There are no network or AI dependencies. SHA-256 fingerprints skip unchanged tile decoding/import. Models retain native asset paths and metadata; embedded geometry remains in its original tile with a content fingerprint. Source manifest/version metadata, footprints, source IDs, recorded/estimated heights, placement notes and local coordinates are retained. Coordinates are Astra local metres, x=E-834500, z=816500-N; heights are HKPD. Section definitions are retained, but geographic section/building membership is HKS-201 work.

Refreshes upsert changed records, retain removed buildings as inactive history, and preserve separate selections/reviews. Use `WHERE active=1` for current coverage. A failed or interrupted import rolls back to the previous committed inventory; restart the command to retry. This is transaction-based inventory recovery, not the future leased multi-worker processing system. Invalid/duplicate identities, missing files, model hashes and count mismatches fail closed. Existing model presence is not a new quality approval. This script does not re-run model conversion, modify the live map or declare any region complete.

Tables: `buildings`, `models`, `inputs`, `settings`, `sections`, `selections`, `reviews`. Source geometry/text stay separate from review state. The later job ledger and stage adapters belong to HKS-202; no placeholder job is marked successful here.

## Verified 7 September 2026

Initial local run: 346,115 forms, 342,223 distinct government IDs, 1,859 embedded and 1,020 progressive model references, 132 sections. 14.56 s, 482,910,208-byte SQLite database. Repeat: 1.17 s, all 452 tiles skipped, zero building updates. All 1,020 external model assets verified against catalogue SHA-256/size. Six tests exercise repeat/preserved selection, change/removal, duplicate rollback, interruption/resume, missing input, and model identity/checksum failures. Evidence JSON is in `docs/astra-city/building-batch/`.

## Execution issues

All belong to the Astra Living Hong Kong milestone; parent HKS-199.

- HKS-200: inventory (implemented; review pending), 4 points.
- HKS-201: tourist landmark and surrounding-area selection, 4 points.
- HKS-202: resumable local processing adapters and worker ledger, 8 points.
- HKS-203: validation, compact exception reports and guarded publication, 8 points.
- HKS-204: measured Central/Mui Wo/Tai O/Ngong Ping trial, 4 points.
- HKS-205: trial-gated rollout across 132 sections, 4 points.

Existing regional issues remain the quality owners. HKS-198 optional government photo imagery is separate. A tourist selection and read-only metadata preflight have now run; actual model conversion and fresh placement validation remain open.

## Tourist trial selection — HKS-201

The selector uses Shapely 2 (already present in the source pipeline environment) and SQLite R-tree; it makes no network/AI calls. Activate the existing source Python environment or install the project source dependencies. In this workspace the existing interpreter is `/tmp/astra-city-venv/bin/python`.

```sh
python source-scripts/city/building-batch/selection.py
python source-scripts/city/building-batch/runner.py plan --dry-run
python source-scripts/city/building-batch/runner.py plan
python source-scripts/city/building-batch/runner.py run --workers 2 --limit 10000
python source-scripts/city/building-batch/runner.py report
python -m unittest discover -s source-scripts/city/building-batch -p 'test_*.py' -v
```

`tourist-trial.json` holds explicit local-grid crops and existing section IDs, plus 86 expected landmark source identities across eight named groups. These identify building records, not 86 separate attractions. The selector includes every intersecting footprint (including edge touches), subtracts courtyard holes, deduplicates overlaps and adds explicitly verified landmark UIDs. Missing/changed landmark identities appear as exceptions, never fuzzy matches. Spatial index bounds are rebuilt only when inventoried inputs change. Invalid source rings are repaired only in the temporary intersection calculation, without changing stored geometry. Manual `selections` and `reviews` stay separate from generated `selection_members` and versioned `selection_sets`. Refresh selection after inventory changes.

Results: Central3265; Mui Wo section10.6:2371; Tai O crop1430; Ngong Ping crop476; union7542. These trial boundaries differ from earlier detail-completion denominators. All86 identities matched. The versioned summary retains bounds, area polygon, selected IDs, hashes, source rationale and exceptions. Open `local/trial/selection.html` to review footprints and hover for names/IDs. A committed review snapshot is under `docs/astra-city/building-batch/trial/`. Big Buddha is a non-building attraction; this inventory does not establish a statue model exists.

## Initial runner checkpoint — HKS-202 remains In Progress

The first adapter is `audit-input-v1`: it reads inventory records, records current detail availability and groups stored terrain flags and height-source concerns. It does NOT acquire, convert, upgrade, freshly sample terrain or publish models. Job completion means this diagnostic stage ran, not that the building is finished. Recorded terrain notes may be stale; HKS-203 must revalidate against current drawn terrain before changing geometry. The remaining acquisition/conversion/packing adapters and broader resource/download limits remain open under HKS-202.

Jobs are fingerprinted by UID, input content and adapter code. Section/selection membership references shared jobs, preventing duplicated processing across overlapping areas. SQLite transactions claim jobs with owner tokens and30s leases; expired claims can be recovered with at most3attempts. Late results from replaced owners are rejected. Transient timeout retries have2/4s backoff, and a future invocation picks up delayed work; this initial runner does not sit waiting for retries. Permanent exceptions are recorded immediately. Each invocation has a positive job limit and1–4workers. Keep inventory/selection refreshes and viewer publication separate from an active run. Stale selection/plan generations fail closed before execution; unchanged completed inputs are skipped.

Actual preflight:7542complete, no failed jobs,34.77s with2workers. Existing detail:1859embedded+279progressive=2138;5404basic. Next actions:4105source-lookups,1384recorded-placement reviews,2053existing-detail reuse. Concerns overlap:1381heights not from a government base/top pair,406recorded wholly buried roofs,671partly buried,713elevated bases. These are diagnostic metadata counts, not new confirmed source defects. All7542jobs were reused on the repeat plan and repeat execution took0.06s. No new models, AI calls or network requests.

Six further tests cover exact area intersections/holes, stable membership, landmark identity mismatch, overlapping selections sharing jobs, concurrent claims/expired-owner rejection, changed-input invalidation, stale-plan rejection and bounded lease retries. Combined inventory+trial suite:12tests. Chrome review map renders4panels/7542footprints with zero page errors; exported screenshot inspected. This is a selection map, not a rendered-city before/after comparison. HKS-204 stays Backlog until processing and fresh validation are ready.

## Cached government model stage — HKS-202

`cached_models.py` reuses the existing `prepare_model_sample.model_geometry` decoder and `central-completion/pack_models.py` exact-attribute GLB packer. It scans retained staged manifests, matches government CSUID/OBJECTID against current selected footprints, verifies source hashes and checks footprint overlap/centroid distance. It skips already embedded/progressive detail. There are no AI or network calls. Missing cached models, missing government identities and ambiguous source identities remain separate dispositions, not claims that government models do not exist.

```sh
python source-scripts/city/building-batch/cached_models.py plan --dry-run
python source-scripts/city/building-batch/cached_models.py plan
python source-scripts/city/building-batch/cached_models.py run --workers 2 --limit 6000
node source-scripts/city/building-batch/validate_candidates.mjs
```

The defaults keep the SQLite database and candidate assets under ignored `local/`. For another snapshot use `--root`, `--db` and `--out` on the Python adapter; the validator takes `--root`, `--db`, `--candidates` and `--out`. Use Node 24+ for its built-in read-only SQLite API. Do not run plan, inventory refresh or publication concurrently with an executing stage. Completed unchanged jobs are reused, with candidate source/output hashes checked again. Missing or corrupt generated assets are recreated from verified sources. Fix a failed job's source and use `run --retry-failed` to request another attempt. Frozen source metadata changes require a new plan. Resource-limit dispositions are terminal review exceptions; raising a budget alone does not retry those jobs.

Workers renew their 30-second leases every five seconds. Each model is bounded to 32 MiB of retained input and 500,000 declared source vertices; default cumulative compressed output budget is 1 GiB (`--max-output-mib`). Jobs also have a per-invocation limit and one to four workers. Existing compact files are reused only when identity, revision, geometry metadata and hashes agree; reuse does not approve placement. Native source coordinates, node transforms, attributes and materials stay intact. No basic building is removed and no viewer file is written by this stage.

`catalogue.json` is the full review inventory, not a directly loadable runtime catalogue. `catalogue-index.json` points to runtime-compatible catalogues of at most 1,024 entries. Assets are content-addressed gzip GLBs. `proofs.json` records source manifests/archive and file hashes plus geometric match evidence. `exceptions.json` lists unmatched and failed jobs; `report.json` provides counts. These outputs are candidates until HKS-203 placement/browser acceptance and guarded publication.

## Candidate validation checkpoint — HKS-203

`validate_candidates.mjs` reads the current viewer tiles and rejects changed inventory hashes. It uses the actual `loadOfficialModel`, source triangle picking, `BuildingIndex` collision, terrain sampler and rendered terrain mesh. Every candidate gets a roof ray and footprint-vertex/midpoint/interior terrain samples. It validates source identity, compressed bytes, attributes, bounds, collisions and sampler/mesh agreement without altering live records. A model can pass the loader and still have a placement exception. Missing terrain surfaces, buried roofs and bottom/ground gaps remain explicit. Piers, slopes and overhangs need contextual interpretation: these checks are not an automatic placement approval.

No GPU/browser performance, complete architectural inspection, exhaustive foundation test or publication is implied by this CPU validation. Fresh evidence is under `docs/astra-city/building-batch/cached-models/`. HKS-202 remains In Progress for the explicitly bounded acquisition adapter; HKS-203 remains In Progress for exception review and guarded publication. HKS-204/205 stay gated. Live detailed-model counts and regional readiness have not changed.

## Visible trial — HKS-203 / HKS-204

The conservative publisher has installed 1,078 models (1,075 Central and three Mui Wo) in the feature viewer; 1,797 candidates remain basic fallbacks. Approved GLBs/catalogues are tracked under `3d-viewer/city/data/official-models/tourist-trial-*`. The original coordinates, source building records and terrain are unchanged. Actual desktop/mobile browser checks cover thirteen locations, including failed-load fallback and Retry. See [trial report and comparison gallery](../../../docs/astra-city/building-batch/visual-trial/README.md) for exact boundaries, counts, commands, tests and remaining limitations. This supersedes the earlier staged-only checkpoint; R2 production offload remains HKS-206.

## Current refinement status

`python3 source-scripts/city/building-batch/status.py` provides a read-only, no-network snapshot. It verifies the inventory's recorded input hashes, reconciles candidate source IDs against current installed details, and separates current job-set membership from superseded ledger history. `--output docs/astra-city/building-batch/current-status.json` saves a reviewable snapshot. Run `inventory.py` first if viewer data has changed. A completed conversion job is not an approved placement or a completed region.
