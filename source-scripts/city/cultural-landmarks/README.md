# HKS-207 — Space Museum and Cultural Centre candidate run

Prepared by Astra using the existing government cache, matcher and lossless packer. The acquisition script stages candidates only. Root subsequently validated and installed the reviewed ten-model catalogue; see [delivery report](../../../docs/astra-city/cultural-landmarks/README.md).

Run from the Astra worktree:

```sh
/tmp/astra-city-venv/bin/python source-scripts/city/cultural-landmarks/acquire.py
/tmp/astra-city-venv/bin/python source-scripts/city/cultural-landmarks/canopy_audit.py
```

The run reads the local SQLite inventory in read-only mode, retains neighbouring footprint identities, reuses the complete geometry cache for government sheet **11-SW-4D (2025-12-22)**, verifies its SHA-256, calls the existing `prepare_model_sample.stage`, then the existing `central-completion/pack_models.py`. No government model bytes were downloaded, and no AI inference was used by the scripts. Geometry, materials, node matrices, original float values and HKPD elevations are unchanged; **vertical scale is exactly 1×**.

## Scope and results

- **16 source building parts**: 3 Space Museum, 12 named/identified Cultural Centre parts, plus one unnamed structure spatially inside the Cultural Centre podium.
- **10 packed models**, 29,699 triangles and 825,208 compressed bytes, from already retained source geometry.
- Before this run, none of those 16 source parts had embedded or progressive detailed models in the current viewer.
- The Cultural Centre's distinctive main roof is `landsd/211702:0`, named **Auditoria Building**. It is explicitly included rather than lost by an exact landmark-name search.
- Space Museum east/dome `landsd/252061:0`, west wing `landsd/252854:0`, and small named ancillary part `landsd/211468:0` are all staged. Their native roofs reach 26.488 m, 21.067 m and 5.214 m HKPD respectively. The first two block survey tops are 13 m; flattening native geometry to those values would erase the roof detail.
- Six Cultural Centre **open-sided structures** have no individual GeoRefNo BUILDING entries in the complete cache. The main Auditoria mesh roof triangles project over 84–94% of these six footprints, so part of their geometry may already be bundled with the main building. This is geometric evidence, **not a verified identity mapping**. Keep their fallback identity until visual/collision review settles overlap. The nearby infrastructure meshes do not provide roof coverage for these six parts.
- Museum of Art, its unnamed podium, Clock Tower, Star Ferry Pier and 1881 Heritage are separate neighbours and were not reassigned to the requested two landmarks.

## Explicit review requirements

Nine candidates pass the shared exact GeoRefNo, >=50% overlap and <=10 m centroid matcher. Cultural Centre podium `landsd/72491:0` matches the exact GeoRefNo and overlaps, but the source model's centroid is 29.506 m from the source polygon centroid. This likely reflects partial/multipart podium geometry and needs explicit review; the global matcher was not relaxed.

The Space Museum roof heights, restaurant roof (+5.03 m over block top), podium extents, low unnamed structure, foundations, duplicate canopy geometry and pedestrian/plane surfaces require browser review. Keep source heights separate from native roof geometry; never introduce a vertical multiplier or terrain-height second addition. This run alone is not an architectural or regional sign-off.

## Artifacts

- `compact/catalogue-index.json` and `compact/catalogue.json`: 10 individual gzip GLBs, ready for the existing candidate validator.
- `report.json`: full source identity, source cache/hash, geometry match and height evidence, six held identities, scope rules and references.
- `canopy-audit.json`: projected native triangle coverage, not convex-hull overlap.
- `official-selection.json.gz`: retained neighbouring source footprint records for matching.
- `staged/11-SW-4D/manifest.json`: fresh matcher result using current local neighbourhood footprints.

Official context: [Cultural Centre Auditoria identity](https://www.lcsd.gov.hk/en/hkcc/contactus.html), [Cultural Centre facilities](https://www.gov.hk/en/residents/culture/performart/venues/performancevenues.htm), [Space Museum east/west wings and dome](https://hk.space.museum/en/web/spm/about-us.html). Model source: Lands Department 3D Visualisation Map (non-textured), dataset `landsd_rcd_1742809441342_98380`; footprints retain `Building_Outline_Public_v20260819` provenance.

## Foundation follow-up

`support_context.py` and `studio_terrain_context.py` reuse native indexed triangle evidence to inspect the four CPU concerns. The active terrain here is already **5 m**, not 70 m.

- The restaurant block has actual source podium surfaces under 718/860 sampled interior points, including 639 within 0.5 m of its native bottom and 677 within 1 m. Its elevated base is expected.
- The podium has 53/4,152 unique vertices more than 0.5 m below terrain; the exhibition gallery has 3/2,507. Their source substructures extend to 2.341 m HKPD below roughly 4 m ground. These are local intersections, not proof that entire buildings are buried.
- Studio Theatre has three low-edge vertices near x=1104.3, z=-778.5 to -775.5 with a terrain gap. The native TIN also descends at two of these points (-0.264 m and 0.695 m), so below-grade circulation/steps must be considered before any terrain change. Most foundation vertices align well: median clearance 0.078 m. The exact points are in `studio-terrain-exception.json` for browser inspection.

No corrective terrain changes were made by this staging task. The parent task decides whether visual evidence supports publication or a local terrain follow-up.
