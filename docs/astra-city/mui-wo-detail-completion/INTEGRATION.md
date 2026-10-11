# Mui Wo terrain-screened publication · HKS-192

**Publish291of312 acquired source matches**, using `source-scripts/city/mui-wo-detail-completion/publication/catalogue.json`. This adds475,630 compressed model bytes and24,313 source triangles. Together with1,327 existing embedded models, the accepted total becomes1,618/2,408forms (67.2%) after root publication. The original312-model catalogue remains intact as the acquisition inventory.

The21heldUIDs and individual evidence are in [publication-screen.json](publication-screen.json). Seven have material roof conflicts that also exist in original native terrain;14have unsupported native elevated bases. Do not lift, scale, stretch or drape those models to force a match. Their unchanged government footprint forms remain available.

## Terrain and dependent updates

Apply these owned payloads together against the verified parent `city/data/terrain-mui-wo.json`:

- `terrain-refinements.json`: three disjoint1m child grids. One is the unchanged `mui-wo-refinement-5` from the earlier `b90c15f5` package; two new small grids address source-grid interpolation near202951and208041. The parent elevations and source model geometry remain unchanged. Parent SHA256: `95e288a0ad14f8389ed4daaad0a7af8657251b2bc0af9f282233448fbcf06648`.
- `building-estimate-updates.json`: exactly the two earlier guarded estimates173217and173237. Both recorded source heights remain null, both original3.5m fallback heights remain unchanged, and no detailed model is involved. This local payload points to the actual new three-patch bundle hash and retains the original payload/hash as provenance.
- `diagnostic-updates.json`: only two derived terrain flags within these three patch neighbourhoods. Do not apply all six diagnostics from the earlier five-patch package.

Root must omit the corresponding5m parent cells and render each nested child once. The existing terrain sampler already supports nested patches. If the full old five-patch bundle is integrated later, deduplicate `mui-wo-refinement-5` by ID; never draw or sample it twice.

The two new patches have1,116and1,476vertices, complete native-TIN coverage and zero changed water nodes. The three-patch bundle includes6,618vertices. One-metre spacing is a sampling interval, not surveyed accuracy. Every new sample uses retained native LandsD TIN triangles with a5m transition to the unchanged parent, through the existing `source_samples` helper. Original glTF/bin files and source hashes remain in the acquisition package.

The corrected roof-contact measurements are:

| UID | Before: maximum terrain minus roofing surface | After |
|---|---:|---:|
|202951|+0.389m|−0.760m|
|206970|+5.360m|−1.052m|
|208041|+0.625m|+0.301m, a0.350m²native roof-edge discrepancy retained explicitly|

201705shares the reused child patch, but its native source roof still conflicts with native terrain. It remains held even though the correction removes the much larger derived-grid error.

## Full placement checks and acceptance

Every one of312source meshes was decoded with the existing original-geometry baker. The audit measures all unique vertices, lowest base vertices, the whole unchanged footprint and the exact upper projected mesh surface. Lower faces occluded by higher surfaces are removed before comparing roofs. Thin sloping wall skins are measured separately rather than mistaken for buried roofs; roofing planes have a vertical normal component≥0.25, covering slopes up to75.5degrees.

The final screen intersects those actual roof planes with every parent/child terrain triangle, retaining projected contact area and maximum depth. Small source/5m roof-edge discrepancies are accepted only when all three bounds hold:≤0.5m depth,≤1m²area and≤1%of roofing area. They remain individually labelled in the evidence. Seven larger native conflicts stay out of the publication catalogue. The source identity/footprint matching rules are unchanged.

Foundation screening uses the actual existing `foundationBase` support contract. Existing illustrative foundations are retained as such; they are not counted as new government geometry. Four raised towers are valid stacks over separately mapped podiums:76963→87027,95569→272725,257187→259108and261085→253898. The original podium roof/deck geometry beneath each tower covers>99.94%of its footprint within0.75mof the native tower base. All four podium models are accepted. Their retained basic podium forms also join the tower within0.5m, so progressive loading can continue to show the fallback until the detailed podium arrives. Parapet maxima are not mistaken for deck height.

The final neighbour audit covers20forms intersecting the three patches. There are **zero new wholly buried roofs, partially buried roofs or floating-base flags** after the two guarded estimate updates. All1,072half-metre perimeter samples match the unchanged parent, maximum error1.57×10⁻¹³m. These are CPU geometry checks; root still owns actual browser/mobile/LOD acceptance and live Linear updates.

## Reproduction and checks

Before applying the live parent changes:

```sh
/tmp/astra-city-venv/bin/python source-scripts/city/mui-wo-detail-completion/placement.py
/tmp/astra-city-venv/bin/python source-scripts/city/mui-wo-detail-completion/refine_placement.py
/tmp/astra-city-venv/bin/python source-scripts/city/mui-wo-detail-completion/verify_placement.py
/tmp/astra-city-venv/bin/python source-scripts/city/mui-wo-detail-completion/test_placement.py
/tmp/astra-city-venv/bin/python source-scripts/city/mui-wo-detail-completion/test_completion.py
```

Seven new tests pass: occluded lower-floor exclusion, coplanar deduplication, exact sloping-terrain contact area, accepted/held UID and byte integrity, terrain/estimate guards and disjointness, seams/neighbours, and corrected representatives/podium support. The five original source-accounting tests still pass. All312unchanged source assets had already passed the actual shared loader, source picking and triangle collision checks; the publication subset copies291of those exact hashed assets. No source or live renderer changes are part of this owned hand-off.
