# Progressive official building models — HKS-193

The compact runtime adapter is integrated with three live Central/corridor catalogues containing 37 exact government models. Actual desktop and mobile acceptance passes. This completes the bounded model-loading delivery, while geographic placement and continuous public routes remain open under HKS-193. See [browser evidence](browser/README.md).

The initial 17 models reuse the 16 packed Central landmarks/contact candidates and the independently matched West Wing podium. They contain 351,254 original source triangles, 9,070,445 compressed bytes and 39,283,074 decoded source geometry bytes. All 17 pass the actual native-gzip and vendored-GLTFLoader decoder against current city building UID, OBJECTID, BuildingCSUID, recorded base/top elevations and activity records. The 20 additional corridor models add 103,919 source triangles and 2,754,798 compressed bytes. All 37 total 455,173 triangles, 11,825,243 compressed bytes and 50,444,250 decoded geometry bytes. Full original sources remain separate; no expanded model JSON enters city tiles.

## App integration

```js
import {OfficialModelLayer} from './official-models.js';
const models = new OfficialModelLayer({
  stream,
  profile: innerWidth <= 760 ? 'mobile' : 'desktop',
  onChange: updateDiagnostics,
});
await models.loadCatalogue('city/data/official-models/central/catalogue.json');
// A separate catalogue can add the West Wing podium or later regional batches.
// Call from the existing render loop; planning is internally throttled to 180 ms.
models.plan(camera, {viewportHeight: innerHeight, selectedUid: selectedId});
// Existing Retry action:
await models.retry();
// Before disposing CityStreaming:
await models.dispose();
```

The catalogue accepts `official-model-catalogue` and the staged kind. Keep each catalogue under 1 MiB and 2,048 packed records; null/unbuilt assets are rejected. Each asset URL resolves relative to its catalogue. All three Central/corridor catalogues follow this contract; root translation stays `[-834500, 0, 816500]`, EPSG:2326 / HKPD.

The adapter uses the existing TileCache and CityStreaming. Exact UID replacements activate only after download, gzip, SHA-256, byte counts, primitive counts, source identity/heights, source bounds and footprint compatibility pass. Source models attach beneath the existing Buildings layer. Existing picking and source cards return the same original building with source-model provenance; collisions and aircraft clearance include actual model geometry. Existing baked government models and infrastructure replacements take precedence.

Stream helpers are `getLoadedBuilding(uid)` and async `setDetailedModel(uid, detailOrNull)`; normal application code only needs OfficialModelLayer. Fallback rendering and collision swap together. Model removal waits for the original outline to return before disposing source buffers. Failed restoration keeps the original detailed geometry and memory reservation until Retry succeeds. Late fetch/parse results are disposed. Brief camera turns retain nearby resident assets, so they do not trigger another decode or facade bake.

Original glTF positions, normals, colours, indices and node transforms are retained. Runtime materials clone their native settings and reuse the existing `facadeMaterial` night shader with per-building uniforms. No repeated window/light vertex attributes expand these compact buffers. Original node and material JSON stays in `record.modelSource`; window patterns remain illustrative.

## Budgets and limits

| Limit | Mobile | Desktop |
| --- | ---: | ---: |
| Concurrent source requests | 1 | 2 |
| Source geometry buffers | 48 MiB | 96 MiB |
| Total resident reservation | 128 MiB | 256 MiB |
| Models | 24 | 48 |
| Triangles | 450,000 | 900,000 |
| Landmark range | 1,800 m | 2,500 m |
| Other detail range | 300 m | 500 m |
| Minimum projected extent | 24 px | 18 px |

Resident reservation includes both source CPU/GPU buffers, exact Float64 collision positions, Uint32 collision indices, triangle bounds and a conservative spatial-index allowance. JavaScript object/index overhead is estimated, not a measured heap guarantee. Fetch/decode temporary memory is additional. Retiring buffers remain counted and subsequent model loads wait for their fallback restoration. The 17-model reservation totals 146,765,716 bytes; the mobile planner therefore selects a subset when necessary. It does not attempt to keep every initial asset resident. HSBC alone reserves 74,279,988 bytes, including its 20,093,640-byte source geometry.

Distance, frustum, projected size and memory/triangle budgets determine detail. Source tile readiness is required. Catalogue loading alone cannot cause all assets to download. Published coarse terrain can still intersect an exact model; model loading neither moves the source roof nor approves an undercroft/public route. All 37 passed actual source-card picking, native indexed geometry, compiled shared night materials and precise collision checks. Four representative models additionally passed both 390 and 320 px mobile profiles. Exact model and terrain placement measurements are retained for review; no source elevations were lifted or source podiums deleted.

## Reproduction

```sh
node --test 3d-viewer/city/tests/official-models.test.js
node 3d-viewer/city/tests/official-model-staged.mjs compact compact-followup compact-corridor
node 3d-viewer/city/tests/official-models-browser.mjs
node 3d-viewer/city/tests/official-models-browser.mjs --exports
node --test 3d-viewer/city/tests/streaming.test.js
```

The focused suite passes 12 tests covering source bytes/transforms/material provenance, native night uniforms, invalid hashes/sizes/heights/placement, picking and collision, failed-download Retry, late decode cancellation, fallback-restoration Retry, budget enforcement, existing-source precedence camera-turn reuse and cancellation during a pending fallback rebake. The existing 10 streaming/territory/source-arrival checks also pass. Actual 17-model decoder evidence is retained in `runtime-assets-verification.json`. The actual-browser results are in `browser/verification.json`; the separate selected-card upgrade and clean-export checks are in `browser/exports-verification.json`. Performance was measured in local headless desktop Chrome at mobile viewport sizes, not on physical phones.
