# HKS-209 browser acceptance and HKS-211 screening

Three Asia Society parts are approved for bounded source-model replacement, with measured local terrain residuals retained. **They are staged, not published by this task.** The root task independently inspected the corrected views and approved this limited replacement. This does not complete the whole campus, surrounding terrain or ground-floor access.

| UID | Review result | Retained terrain limitation |
|---|---|---|
| `landsd/3089:0` | Native small rectangular part visible in normal scene and north-west foundation view | Bottom 53.526 m HKPD; sampled ground 52.215–53.485 m. Local gap up to 1.311 m. |
| `landsd/3090:0` | Native adjoining small part visible in normal scene and north-west foundation view | Bottom 53.526 m HKPD; sampled ground 52.260–53.506 m. Local gap up to 1.266 m. |
| `landsd/4314:0` | Miller Theater sawtooth roofs and lower elevations replace the flat-roof extrusion | Bottom 53.798 m HKPD; sampled ground 53.186–54.390 m. Local gap up to 0.612 m and clipping up to 0.592 m. |

These extrema compare a common native model bottom with sampled terrain; they are not exhaustive door/access measurements. Geometry, source identity, source elevations and the current terrain remain unchanged at **1× HKPD**. Source materials are untextured; procedural windows are not a record of actual openings.

## Browser evidence

Matched before/after views live in `browser/before/` and `browser/after/`. The most informative full assembly comparison is `asia-society-followup-landsd-4314-0-day.png`. The theatre changes from a flat extrusion to the native sawtooth roof form.

The final normal-scene desktop harness passed all three source-identity, active-model, triangle-contact collision, source picking and render/sampler-agreement checks. It also passed budget checks, a 390 px mobile viewport check of 3089, forced model-download failure with fallback preservation, and successful retry. No reported application/shader/HTTP errors occurred. Group navigation smoke checks walked without arrival collision and flew about 70 m; this is not a walking route through the Asia Society campus.

Desktop and emulated-mobile frame times were median 16.7 ms, p95 16.8/16.7 ms in this local Chrome run. Physical-phone performance is unverified. Cache figures cover the viewed scene, not all Hong Kong. The three source assets total **5,507 gzip bytes and 142 triangles**.

`foundations/` contains initial opposite diagonal diagnostics. **The south-east views are partly or wholly obscured by foreground terrain and are not foundation acceptance images.** North-west views of the two small parts are informative. `foundations-elevated/` adds east/west camera positions kept above intervening terrain; the model and terrain are unchanged, and unrelated building groups are hidden only for this diagnostic. The corrected normal scenes retain all ordinary buildings. Accepted image hashes are explicit in `visual-acceptance.json`.

## Exact staged publication

The three assets and reviewed catalogue are under ignored `source-scripts/city/landmark-visual-review/approved/`. Tracked `approved-catalogue.json`, `publication-plan.json`, `guard.json` and `visual-acceptance.json` retain provenance, destination and checksums. No new terrain asset is included.

Run from the Astra worktree immediately before the root task publishes:

```sh
/tmp/astra-city-venv/bin/python source-scripts/city/landmark-visual-review/prepare_publication.py
```

This verifies all reviewed terrain, source catalogue, current manifest, runtime, screenshots and test report hashes; rejects already-published UIDs; and rebuilds the staged plan/assets. It does not publish. The root task can then apply the existing `island-detail-integration/publish.py` with this `publication-plan.json`, followed by an actual installed-route check. The publisher remains responsible for installation/rollback. Re-run visual review if guarded geometry, runtime or terrain changes.

## Next 25 staged candidates

All **25 HKS-211 models pass CPU loader, source-surface picking/collision and sampled-terrain execution checks**. These checks took about 0.98 seconds and inspected 2,017,624 compressed model bytes. All source/asset/input hashes were verified. Classification retains every UID:

- **2 ready for browser review:** `landsd/69002:0` Pedder Building; `landsd/101313:0` THE CENTER part. Pedder is the clearer standalone next target. THE CENTER source part is only 19.35 m high; reviewing it does not complete the main tower.
- **7 existing holds:** E Hall 114964, JC Cube 330467, Asia Society 223348/223783, Opus 322573, Peak Tower 248218 and Hua Yan Pagoda 211847.
- **16 need assembly or foundation context:** many are elevated towers/podiums. CPU base-gap flags alone do not establish unsupported geometry. These should proceed through source-support and browser review without moving source elevations.

`hks211-screening.json` records each UID, label, source sheet/revision, asset hash, native bounds, terrain values, disposition and next action. No additional models were reconstructed or acquired. Existing holds were preserved.

Reproduce the CPU screening and classification:

```sh
/Users/williamli/.nvm/versions/node/v24.17.0/bin/node source-scripts/city/building-batch/validate_candidates.mjs --candidates source-scripts/city/landmark-bulk/compact --out docs/astra-city/landmark-visual-review/hks211-validation.json
/tmp/astra-city-venv/bin/python source-scripts/city/landmark-visual-review/screen_batch.py
```

The classification script uses no network or AI calls and does not write the shared inventory. Browser review makes local app requests; no fresh government source data was downloaded. Existing shared validators and browser harnesses were reused. The only adapted harness is `foundation-browser.mjs`, derived from the existing diagnostic harness with terrain-aware east/west camera positions.

## Root installation checkpoint

Root applied the existing guarded publisher after reviewing the corrected views. Three parts are now in `city/data/official-models/asia-society-followup/catalogue.json`; no terrain or source elevations changed. The actual installed-catalogue browser run passed all three model loads, picking/contact, night/mobile and failure/retry checks with no application errors. Evidence: `installed-browser/after/verification.json` and `publication/`. Inventory refreshed to 4,054 detailed parts (1,859 embedded +2,195 progressive); total forms remain346,115. This is bounded component acceptance, not complete Asia Society campus or ground-access approval.
