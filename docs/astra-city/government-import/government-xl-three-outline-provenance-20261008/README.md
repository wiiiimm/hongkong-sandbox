# Original outline provenance — 8 October 2026

Codex recovered four unmodified features from the byte-verified original `Building_Outline_Public_v20260819` archive, SHA `4f25701140e090c0a58abb180b5b38a5c57f0a0f0897757032f35af4fa98d4e1`, and queried their exact stable CSUIDs from the current official service with `returnTrueCurves:true` in EPSG2326. Original archived outlines match current viewer forms within0.7mm. Current native straight-segment responses differ by7–29mm.

`../government-xl-three-outline-curve-diagnostic-v3-20261008/` tests every ordered native straight primitive, arc endpoint, interior arc vertex and ring role at the existing2mm bound. Gleneagles195849 and Imperial tower241723 follow the current circular arcs; Market In313033 and Imperial podium258470 retain radial differences over2mm. Thus the original hypothesis that all three target failures were only different chord spacing is not established. Chord sagitta remains separately reported; this never claims sub-2mm polygon Hausdorff equality between different tessellations.

The first two diagnostic versions are retained with their checker source. Version1 rejected a legitimate nearby Gleneagles anchor as ambiguous; version3 selects the unique nearest anchor while consuming the full ordered ring. Unsupported curves and unsafe straight/arc/hole changes fail closed. Eleven adversarial unit tests and a separate regression against all four actual original examples pass.

A separate fresh current GeoJSON export in `../government-xl-four-current-geojson-provenance-20261008/` still differs from the archive by8–61mm; it does not establish polygon equality. No current source polygon, original model, matching metadata or acceptance tolerance is edited. No identity acceptance or installation credit. Exact source-specific followups are saved in Neon via `../government-xl-original-hold-followthrough-20261008/`.

ArcGIS native curve format uses the previous endpoint, a `c` endpoint and an interior point: [official geometry documentation](https://developers.arcgis.com/rest/services-reference/enterprise/geometry-objects/). No historical map imagery used.
