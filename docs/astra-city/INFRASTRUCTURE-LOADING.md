# Official infrastructure runtime adapter — HKS-191 / HKS-192

Implemented by the Astra infrastructure agent in the isolated comparison worktree. This hand-off changes runtime modules and tests only. Package publication, app wiring and WebGL acceptance remain with the integrating agent.

`BridgeLayer.load(url)` accepts both `official-infrastructure` and the original `tai-o-official-infrastructure` schema. Original meshes, source IDs, HKPD heights, colours and normals remain unchanged. All source geometry, declared model/triangle counts, public-floor evidence and replacement metadata validate before a complete package can activate suppression. A failed package leaves proxy geometry and tower outlines available through the existing Retry path.

Integration uses the existing bridge change callback:

```js
stream.suppressBridgeRoads(bridgeLayer.loadedIds, bridgeLayer.proxyClips.values());
await stream.suppressInfrastructureBuildings(bridgeLayer.suppressedBuildingUids);
```

`proxyClips` is a Map of **active, source-path-validated** clips. A package arriving before the mapped source inventory retains pending clips internally; it cannot prematurely hide road tails. `suppressedBuildingUids` is available only after the full source package validates. Calling building suppression with an empty set restores the stored source outlines. The caller must keep accepted infrastructure surfaces connected to Navigation; suppression does not itself create floors or grant pedestrian access.

For partial replacements, the adapter checks retained paths against original source vertices and direction, then interpolates proxy deck heights only at derived cut endpoints. It retains intervening original corners and source picking IDs. Curated public approaches are independent of their parent way's clipping. Road-only Tsing Ma lower-deck proxies remain in the street renderer: verified retained paths are clipped to existing street tile boundaries, preserving road metadata and the `foot=no` access constraint.

Tower suppression rebakes only affected cached building groups. Rendering and collision indices swap together after the bake; original source records, heights, UID lookup and picking indices are retained. Pending loads use the latest replacement set. Eviction/disposal rejects late results, including unused facade materials from a fully suppressed tile. The existing 24-tile bridge cache remains in force. Stats expose `clippedProxies`, `pendingProxyClips`, `suppressedBuildings` and streaming `infrastructureErrors`.

Validation on 7 September 2026 (Hong Kong time):

- 51 focused unit checks pass across infrastructure loading, original Tai O source/walking surfaces, bridge rendering/data and streamed activity.
- Actual staged Tsing Ma and Mui Wo packages pass CPU integration in both source-first and mapped-first order: 16 unchanged source meshes, six reviewed public source decks, four explicit estimated approaches, 17 full proxy replacements, 18 validated partial clips and four matched tower outlines.
- Source package parsed-content hashes are unchanged after load/disposal. Region views built finite buffers in six and seven cached bridge tiles, below the 24-tile limit.
- No GPU/browser test, geographic access expansion, live manifest edit or source publication is claimed by this adapter hand-off.

Reproduce from the repository root:

```sh
node --test 3d-viewer/city/tests/infrastructure-loading.test.js 3d-viewer/city/tests/infrastructure.test.js 3d-viewer/city/tests/bridges-render.test.js 3d-viewer/city/tests/bridge-data.test.js 3d-viewer/city/tests/activity-streaming.test.js
node 3d-viewer/city/tests/infrastructure-staged.mjs
```

The second command accepts explicit package filenames, enabling the same check after staged files are published. The contracts and geographic source evidence remain in `source-scripts/city/tsing-ma/` and `source-scripts/city/mui-wo-completion/`; no new source data was fetched for this adapter.
