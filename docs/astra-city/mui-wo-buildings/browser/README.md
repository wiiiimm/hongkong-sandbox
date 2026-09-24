# Integrated Mui Wo shelter and building checks

The live city at `http://127.0.0.1:4176/city.html?district=muiwo` was checked in Chromium, at 1440×1000 and 390×844. The source-building renderer is still the shared `extrudeBuilding` → `makeBuildings` palette-batch path; no second building renderer or per-building draw-call layer was introduced.

## What changed

`city/building-geometry.js` supplies cached visual/collision descriptions. Open-sided records render a roof slab following the full source rings and courtyard holes. With footprint extrusion the slab's upper face is exactly `base + height`; its thickness is a visual approximation of at most 0.28 m. At most eight 0.22 m square support posts are distributed along the perimeter, inset and verified inside the actual footprint. Their positions/dimensions are illustrative, not surveyed columns. The 227 loaded Mui Wo open-sided forms produce 965 posts.

Roof slabs, posts and explicit foundation skirts have `cityWindows = 0`. They receive scene lighting but do not acquire procedural windows or window emission. Ordinary façades retain their existing night occupancy and distant shimmer. Every vertex retains the shared `feature` index for source picking.

An explicitly supplied `foundationBase` adds an unlit skirt below an enclosed building's source base, or extends shelter posts downward. It does not move recorded source fields or the roof. A negative/invalid foundation gap is ignored. Foundation geometry is an integration aid, not a new survey.

`BuildingIndex` caches the same roof/post/foundation volumes. Open air below a shelter is passable; posts and the roof slab remain blocked. Collision is conservative at the supplied character/aircraft radius. Foundations also collide. Source geometry remains the fallback if an optional detailed model is invalid.

Optional `modelGeometry` positions, normals and indices are validated before use. Valid world-coordinate triangles replace the extrusion in the same palette batch; indexed meshes become non-indexed to match existing geometry. Invalid/non-finite arrays, bad indices or implausible placements retain the source-footprint fallback. Detailed enclosed-model collision conservatively uses the source footprint and model bounds, including a bounding rectangle when an overhang exceeds the footprint envelope. This is not exact mesh collision. Detailed open shelters retain analytical roof/post collision approximations; precise native-model column collision remains a limitation.

## Evidence

- `before-verification.json`: live baseline before renderer changes.
- `after-verification.json`: final live run after shelter rendering and the root's subsequent 275 detailed-model/source-TIN integration.
- `before-market-day-1440x1000.png`, `after-market-day-1440x1000.png`: same cooked-food-market camera. Neighbouring enclosed source forms partly obscure its open walkways; this is not a clean isolated-canopy comparison.
- `after-open-sided-316300-day-1440x1000.png` and `after-open-sided-316300-night-1440x1000.png`: clearly visible isolated source canopy and its supports. Recorded base is 4.3 m HKPD, recorded roof top 12.5 m HKPD; the roof stays at 12.5 m. The unnamed source record is not assigned an invented building identity.
- `after-market-source-card-1440x1000.png`: real source selection/card.
- `after-market-mobile-390x844.png`: final mobile layout, showing the isolated canopy view; the historic filename is retained for the test's output slot.

The final run passed real canvas selection, source-card display, under-roof clearance, blocked posts, blocked roof, all 227 source roofs present, 13 loaded tiles with no load errors, and no mobile horizontal overflow. Screenshots were opened and visually inspected. No page or console errors occurred.

## Local performance observations

At the same cooked-food-market camera, the initial shelter-only comparison kept 65 draw calls and changed 1,730,915 triangles to 1,740,947 (+0.58%). Across 90 frames, median frame time stayed 16.6 ms; p95 was 17.1 ms before and 17.3 ms afterwards.

The final rerun also includes the root's separate 275 detailed models and source-TIN work: 65 draw calls, 1,764,903 triangles, median 16.7 ms, p95 18.3 ms. This later total cannot isolate the cost of shelter rendering. These are short local headless observations, not a cross-device benchmark or a guarantee of frame rate. Both timings include the scene's existing terrain and tree workload.

## Reproduce

```sh
node --test 3d-viewer/city/tests/building-geometry.test.js
node 3d-viewer/city/tests/mui-wo-buildings-browser.mjs after
```

Eleven focused JS tests cover exact source roof position, open air, courtyard holes, source-field immutability, foundation/window masks, collision agreement, exact terrain-grid edge sampling, valid detailed geometry, malformed fallback and indexed model compatibility. The complete JS suite passed 89 tests at this change. Ten Python source-conversion tests also passed, including the territory OBJECTID 4795 regression where millimetre packing damaged a valid polygon; the converter now keeps finer/full precision when necessary.

The test uses an in-memory response getter to inspect existing scene objects; it does not add production debug UI or alter source geometry. Root integration owns source profile classification, final publication and the territory-wide data merge.
