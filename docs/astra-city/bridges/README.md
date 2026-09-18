# Hong Kong mapped bridges and building links

Produced by the Codex Astra bridge-data subagent for HKS-153. The package supplies sourced centre-lines and connected access geometry to the city's bridge renderer. It is a mapped inventory, not a claim that every real Hong Kong footbridge has been captured.

## Reproduction

```sh
/tmp/astra-city-venv/bin/python source-scripts/city/bridges/build.py
/tmp/astra-city-venv/bin/python source-scripts/city/bridges/test_bridges.py
```

The generator uses the existing pinned pyproj/Shapely dependencies. It writes `3d-viewer/city/data/bridges.json` and `verification.json` here. Rebuilds use retained source files without network requests. `fetch.py` retrieves missing supplementary bridge/district snapshots; each response and exact query are retained locally. Existing snapshots and original game sources remain untouched.

The fresh bridge snapshot contains 18,969 source elements at 6 September 2026 07:06:48 UTC. Complete retained highway snapshots supply directly connected access ways; the narrower supplementary query supplies current bridge/elevated-link tags and bridge outlines. Every source has its timestamp, SHA-256 hash, filename and ODbL attribution in the output.

## Contract and geometry

`bridges` records retain `id`, `source`, unsimplified `path`, aligned original `nodes`, original highway `kind`, `role`, source `bridge` value, `layer`, raw `tags` and any unambiguous numeric dimensions. `name`, `zh`, `covered`, `interior`, `level`, `levels`, `height`, `minHeight`, `width` and `ele` are optional. `elevationEvidence` names the tags actually present.

- `role: bridge` means an existing highway way carries a recognised non-`no` bridge tag. Unsupported/typo values, proposed/construction ways and degenerate geometry are reported rather than invented into structures.
- `role: elevated-link` means a pedestrian-type way has a positive floor, relative layer or minimum-height tag. These include podium and inter-building networks. `interior: true` distinguishes indoor routes; a floor tag alone does not prove an outdoor bridge. Ordinary ground-floor interior routes are not promoted to elevated links.
- `role: access` means an actual source endpoint shares an original OSM node with an exported bridge/link. `connections` supplies that node, the exported vertex index, coordinates and connected bridge IDs; `connectsTo` is a convenient unique ID list. No proximity snapping or guessed stair routes are used.
- A long ground path touching a bridge is still an access record. It must not be raised along its whole length. The renderer should separately decide whether a short stair/ramp has enough endpoint evidence for a raised profile. These data do not yet supply a pedestrian routing/collision network.
- All lines are clipped to retained Hong Kong boundary relation 913110. Original junction vertices are not simplified. Newly created boundary vertices have `null` node IDs. Coordinates are projected through the existing HK1980 transform and rounded to 0.01 m; this storage precision is not a claim of centimetre mapping accuracy.
- Different snapshots can contain different coordinates for the same OSM node. The generator resolves each node ID to its newest retained source coordinate, preserving that evidence in each affected record's `coordinateUpdates`. This corrects real mismatches in shared junctions without moving unrelated crossings together. Raw snapshots are never rewritten.
- The optional, separate `decks` collection contains actual `man_made=bridge` polygons. A route is linked only when its explicit layer matches the outline and at least 90% of its centre-line lies within the polygon. No-conflict-but-unknown-layer matches are deliberately omitted. Shared outlines are separate so two carriageways do not duplicate one deck. Invalid rounded outlines are excluded; holes are preserved.

## Elevation honesty

[OSM's bridge documentation](https://wiki.openstreetmap.org/wiki/Key:bridge) describes the bridge tag as a property of the carried way. Physical bridge outlines can be mapped separately with [man_made=bridge](https://wiki.openstreetmap.org/wiki/Tag:man_made%3Dbridge).

[Layer](https://wiki.openstreetmap.org/wiki/Key:layer) expresses relative stacking order; it is not metres. [Level](https://wiki.openstreetmap.org/wiki/Key:level) describes a building floor. [Height](https://wiki.openstreetmap.org/wiki/Key:height) normally describes total object height and cannot automatically be used as road-deck elevation or clearance. The dataset keeps these concepts separate and does not assign a surveyed deck elevation where none is provided. `ele` is retained as source elevation evidence without asserting a Hong Kong Principal Datum conversion.

Only simple numeric metre values are parsed. Ranges, lists, imperial values and uncertain text remain intact in raw tags. No widths, heights, clearance values, spans or supports are fabricated by this generator. Renderer fallback dimensions must remain labelled estimates.

## Coverage and remaining gaps

`verification.json` provides counts by role, highway kind, explicit dimension evidence and all eighteen Hong Kong district boundaries. District counts use line-midpoint containment in the retained OSM polygons; the Lok Ma Chau Loop is kept separately, and unmatched boundary/water records are reported rather than forced into a district. Cross-district bridge segments are counted once. These are source-geometry statistics, not an official bridge census or a count of distinct structures.

The inventory includes road viaducts, footways, elevated building links and source-connected stairs. It does not recover untagged/unmapped links, resolve missing or inconsistent real deck levels, reconstruct suspension cables/towers from geometry that does not contain them, verify openings or private access, or restore footbridge walking collision/routing. The existing coarse terrain can still require renderer-side estimated deck clearance; this package does not change terrain.

Source geometry: [OpenStreetMap contributors](https://www.openstreetmap.org/copyright), ODbL 1.0, with direct element URLs and retained snapshots. No third-party bridge imagery or archival Lantau maps were used. Source tags may describe restricted routes; rendering them is not a statement of public access.
