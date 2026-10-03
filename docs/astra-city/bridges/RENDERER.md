# Bridge rendering — Astra implementation

`3d-viewer/city/bridges.js` renders the prepared, source-connected pedestrian bridge inventory supplied by `bridge-data.js`. It adds solid decks, side faces, modest guardrails/posts and a simple canopy only where `covered` is explicitly `true` or `yes`. It does not draw invented major-bridge cables, ground piers or foundations. Rendered bridges do not yet provide walking collision or route access.

## Geometry and evidence

Every deck centreline coordinate and top elevation comes directly from the prepared `deckPath`. The deck width is the prepared `width`. The renderer does not raise routes using terrain, floor levels or OSM layer tags. `elevationBasis`, `estimatedElevation`, `widthBasis`, names, tags and source links remain on the original record returned by picking. Source interpretation and height estimation belong to the resolver, not this module.

The deck is a closed swept solid with an illustrative 0.24 m thickness. Bounded miter joins follow bends without large corner spikes. Steps use the supplied sloping profile and a distinct deck material; no surveyed riser dimensions are implied. Rails are 1.05 m high, with small posts at no more than about 3.2 m along each segment. Explicitly covered spans receive a simple 0.08 m thick canopy 2.8 m above the supplied deck, with supports at no more than about 5 m. These construction details are visual estimates and are not architectural reconstructions.

## Runtime contract

```js
const bridges = new BridgeLayer({scene, sampler, onChange});
if (await bridges.load('city/data/bridges.json')) {
  stream.suppressBridgeRoads(bridges.loadedIds);
}
bridges.plan(focusX, focusZ, 3000, camera.position);
const hit = raycaster.intersectObjects(bridges.pickMeshes())[0];
const record = hit && bridges.featureAt(hit);
const selectedGeometry = record && bridges.geometryFor(record);
```

- `group` is the public Three.js group for visibility controls.
- `records` is a `Map` keyed by prepared record ID. `loadedIds` contains those IDs and original `way/123` source IDs for suppressing old draped bridge-road geometry after successful loading.
- `load(url)` and `retry()` resolve to booleans. Failed loading preserves existing bridge records and does not introduce suppression IDs from a failed batch. Errors are retained for retry; repeated in-flight loads share a request.
- `geometryFor(record)` is both an exported function and an instance method. It returns the same solid deck geometry used by the visible meshes, suitable for a selection highlight.
- Deck vertices carry the integer `bridgeFeature` attribute. `featureAt(intersection)` returns the complete prepared record, including its source evidence. Hidden or evicted decks are excluded from picking.
- `stats` exposes `spans`, `visibleSpans`, `tiles`, `pending`, `errors`, `covered` and `estimatedElevation`.
- `dispose()` aborts pending requests, releases tile buffers, shared geometry and materials, and removes the group. Late fetch or preparation completion cannot recreate geometry. Planning and loading after teardown are no-ops.

## Batching and distance detail

Complete spans are assigned to 1,600 m tiles using their supplied bounds. Nearby tiles are sorted by distance and limited to **24 live tiles**, with a maximum planning radius of 5 km. Bounds include additional allowance for the mitered width; source spans are not cut at tile edges.

Each tile uses at most two merged deck draws (ordinary paths and steps), one merged canopy draw, and one instanced rail/post draw. Distant tiles release their geometry and instance buffers. Shared rail geometry and materials survive individual tile eviction.

Rail/post visibility uses a 1,400 m detail threshold:

`hypot(horizontal distance from focus to tile bounds, max(0, camera height - terrain height at focus))`

The optional fourth `plan` argument supplies the camera position. Existing three-argument calls use horizontal distance alone until a camera position has been supplied. High aerial views therefore keep decks and canopies but skip tiny rail/post detail. Rails do not cast individual shadows; the solid decks and canopies do.

## Validation

Run:

```sh
node --test 3d-viewer/city/tests/bridges-render.test.js
```

Eleven focused tests cover supplied elevations and width, solid face normals, bends and steep changes, explicit canopy tags, merged deck picking, source-ID suppression, failed loads and retries, atomic batch validation, the 24-tile bound, disposal of distant buffers, late fetch/preparation teardown, hidden detail, and aerial-camera behaviour.

A local Node benchmark against the 26,004-record retained inventory loaded and prepared 12,260 eligible spans, including 3,420 covered spans, without errors. Initial preparation and nearby geometry construction took approximately 245 ms; sampled district replans took 0–40 ms. These are local CPU observations before browser integration, not browser frame-rate guarantees. The root task performs the integrated city-browser checks and records current source counts separately.
