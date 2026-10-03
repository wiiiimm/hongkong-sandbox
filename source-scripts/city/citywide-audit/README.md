# Citywide deterministic source audit — HKS-221

This is a scripted audit of every source form in the current viewer manifest. It performs no AI calls, new source acquisition, model conversion or publication. It writes only its scoped cache/run/member tables and existing shared job records on the pinned `astra-modelling` Neon branch. It never changes `model_reviews`, source files, SQLite or installed assets.

## Run

Use the existing modelling Python environment and Node 22+ from the repository root. Configure the pinned branch using `shared-modelling/configure.py` first on a new device. Only run the migration when installing this new schema:

```sh
python source-scripts/city/citywide-audit/audit.py migrate
python source-scripts/city/citywide-audit/audit.py run --batch hong-kong-audit-v1
python source-scripts/city/citywide-audit/audit.py run --batch hong-kong-audit-repeat
```

`--node /absolute/path/to/node`, `--out PATH` and `--chunk-size 8192` are available. An unchanged run with another batch label reuses the same results. `report --run-id ID` queries the current shared outcome. Local `local/` contains compressed plans/results and compact reports for the R2 checkpoint; it is ignored by Git. Native payload downloads are deliberately unavailable here.

## Checks and limits

The engine checks canonical government source UID syntax, government identity availability, ring coordinate validity/closure/non-zero area, finite positive height and surveyed height-pair ordering. Holes contribute to net footprint area. It identifies embedded geometry using the existing `modelGeometry` field and verifies each current native catalogue's local asset SHA and its CSUID correspondence. It does not label a missing local file as absent from the government dataset.

Terrain checks reuse `makeTerrainSampler` and its native TIN support at unchanged real elevations. Samples include ring vertices, edge midpoints and an interior bounding-box centre when applicable. Output marks envelope roof/base flags against those finite samples. Outside-domain and failed sampler checks remain explicit. These checks do **not** establish native roof, podium or collision correctness: a source footprint envelope may legitimately flag a native stepped building. Ring self-intersection, native triangle geometry/collision and visual acceptance are explicitly not checked. Findings are diagnostic candidates, not automatic rejection or approval.

## Cache and concurrency

Each cache key hashes canonical UID, the exact source record, current native model metadata/asset availability, engine/sampler implementation and relevant terrain dependencies. The root terrain is a dependency; only intersecting ordered sibling/nested terrain patches are included. A sibling patch outside the source footprint does not invalidate its result. Terrain hashes cover entire relevant layer bodies rather than individual sampled triangles, so edits elsewhere in the same relevant layer conservatively invalidate checks. Base-terrain or pipeline changes invalidate affected keys.

Runs are immutable memberships keyed by the compressed deterministic plan fingerprint, independent of user batch labels. Registration uses PostgreSQL COPY and bulk inserts. Missing results are grouped into stable source chunks; existing `jobs.claim` leases with `SKIP LOCKED` and UUID fencing coordinate devices. The supervisor renews live chunks every 15 seconds with a five-minute lease. Up to eight chunks share a bounded COPY/upsert transaction. Cache writes and completion share that transaction and a final server-clock token check: an expired worker cannot leave accepted cache records behind. Canonical key/result checks reject conflicting output. Interrupted completed chunks are retained; unfinished chunks become reclaimable after lease expiry. Resuming can claim only available chunks, and reports an incomplete run rather than claiming another worker's result prematurely.

No per-building database connections or AI sessions are used. Source planning still reads the current files and hashes relevant inputs, even on a cache-only rerun. Models must already be restored on each device; missing-file availability is part of the key.

## Verification

```sh
node --test source-scripts/city/citywide-audit/test_engine.mjs
MODELLING_INTEGRATION_TEST=1 python -m unittest discover -s source-scripts/city/citywide-audit -p test_store.py -v
```

The opt-in integration tests create only uniquely named small audit fixtures in the pinned branch. They verify partial-transaction rollback, cross-label cache reuse, concurrent chunk claims, selective input invalidation, expired-owner fencing, corrupted fingerprint rejection, and rollback of the entire group when one lease expires after COPY. Fixture records remain as provenance; tests never delete other work.
