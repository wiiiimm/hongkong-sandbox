# Separate illustrative cable adapter

`3d-viewer/city/bridge-cables.js` exports `BridgeCables`, `createBridgeCables(options)` and `CABLE_SOURCE_PARENTS`. Its meshes use the supplied metre/HKPD position, normal and colour arrays unchanged apart from the usual Float32 GPU upload. MeshStandardMaterial provides ordinary lighting/shadows and the existing renderer’s logarithmic depth support. There are no window attributes, floor surfaces, building replacements or source-bridge mutations.

```js
const cableLayer = createBridgeCables({scene, onChange});
await cableLayer.load(url); // boolean; validation/network errors recorded
cableLayer.plan(x, z, 3000, bridgeLayer.surfaces.models.keys());
cableLayer.group.visible = bridgeLayer.group.visible;
const hit = ray.intersectObjects(cableLayer.pickMeshes(), false)[0];
const record = cableLayer.featureAt(hit);
// Optional selection outline: cableLayer.geometryFor(record); caller disposes it.
await cableLayer.retry();
cableLayer.dispose();
```

Each region appears only after all explicit original parents exist: six original Tsing Ma components, or the one complete Ting Kau deck/tower model. One mesh/material is allocated per packet; duplicate requests reuse the pending/completed load. A conflicting duplicate region or invalid packet cannot replace a valid existing mesh. Parent loss, distance and group visibility remove it from picking. Aborting/disposal prevents a late completion from reappearing and disposes resources once.

Selection records have `kind:'illustrative-bridge-cables'`, `estimatedGeometry:true`, `walkable:false`, `sourceTriangles:0`, `illustrativeTriangles`, `name`, `zh`, `sourceUrl`, `sources`, `profile`, `limits`, `focus`, `worldBounds` and `requiredParents`. Retain the estimate wording in the inspector; never display these triangles as official infrastructure triangles. The source packets remain available independently if the cable fetch fails.

`stats` exposes `packets`, `visiblePackets`, `illustrativeTriangles`, `visibleTriangles`, `sourceTriangles:0`, `waitingForParents`, `pending` and `errors`. The two current packets total 10,536 illustrative triangles: 6,432 Tsing Ma and 4,104 Ting Kau.

Six focused tests pass with both real retained packets, all-parent activation in either load order, request deduplication, failure/retry, malformed/duplicate payload atomicity, visibility/picking isolation, metre coordinates and disposal/late completion and the browser-native fetch receiver:

```sh
node --test 3d-viewer/city/tests/bridge-cables.test.js
```

Root owns application loading, layer controls and selection-card integration. The actual-city after browser pass is tracked separately.

The first integrated browser check exposed native `window.fetch` being called with the layer instance as its receiver. The adapter now binds fetch to the global object; a regression verifies that receiver. Original source bridge loading was unaffected.
