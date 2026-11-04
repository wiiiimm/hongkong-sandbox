# Central detailed models — staged hand-off

Produced by Astra/Kant for HKS-193. These files are staged, not integrated into the live city. The three sections remain under review.

The original non-textured Lands Department glTF/bin entries are retained under `source-scripts/city/central-completion/sources/` and extracted unchanged in `staged/`. Their hashes, sheet revision and source download are recorded in each source manifest. The existing importer matches the exact GeoRefNo, footprint overlap and centroid, then requires one model and one building component for the matched BuildingCSUID. This yields 2,977 matches inside the buffered Central review selection. It does not make all those buildings architecturally reviewed.

The compact batch contains 12 landmarks: HSBC, Bank of China Tower, One and Two IFC, Jardine House, Cheung Kong Center with its two associated forms, two City Hall forms, Legislative Council Complex and Central Market. Four additional exact matches at candidate-route contacts are packed: the older Bank of China Building, City Hall High Block, Hollywood House and one unnamed Chater Garden form. Three waterfront contact records were initially unmatched. The separate [contact follow-up](contacts-README.md) now matches the curved podium; the two canopy models remain unavailable. The ordinary city building records remain untouched. Source outline heights and model bounds are distinct facts; for example, Bank of China Tower's source mesh includes its spire above the recorded outline top.

## Files and reproduction

- `source-scripts/city/central-completion/compact/catalogue.json`: the small packed-only catalogue for a future runtime adapter.
- `compact/catalogue-all.json`: all 2,977 matched inventory entries; unbuilt assets are null. Keep this out of initial browser loading.
- `compact/models/*.glb.gz`: individually compressed standard GLB assets. Apply native `DecompressionStream('gzip')`, then the app's existing `GLTFLoader.parseAsync`.
- `compact-assets.json`: source hashes, expanded-attribute hashes and per-model packing evidence.
- `compact-verification.json`: actual vendored-loader validation, without WebGL.
- The 892 MB expanded JSON model collection is an offline staging artefact only. It must not enter ordinary 2 km city tiles.

From the Astra worktree:

```sh
/private/tmp/astra-city-venv/bin/python -B source-scripts/city/central-completion/pack_models.py
node source-scripts/city/central-completion/compact-test.mjs
```

Packing indexes only bit-identical complete vertex tuples, including normals and colours, in first-use order. Triangle order, float bits, hard edges, materials and original node matrices are preserved. There is no quantisation, simplification, height correction or terrain draping. Apply the catalogue root translation `[-834500, 0, 816500]` once to obtain city coordinates. Model coordinates are EPSG:2326 with heights above Hong Kong Principal Datum.

All 16 GLBs parse with the app's loader. Re-expanded position, normal and colour attributes reproduce the original bytes, and world bounds agree within 0.0000001 m. Catalogue UID/OBJECTID/CSUID and raw base/top heights are checked against the retained footprint selection. The batch contains 304,336 triangles, 7,669,121 compressed bytes, and 33,689,130 decoded geometry bytes. HSBC accounts for 4,678,280 compressed bytes and 20,093,640 decoded geometry bytes. These are file/buffer measurements, not GPU performance claims.

## Proposed runtime loading contract

This is a starting budget to measure in the actual mobile and desktop app, not a tested performance guarantee.

| Limit | Mobile | Desktop |
| --- | ---: | ---: |
| Concurrent source-model requests | 1 | 2 |
| Resident detailed geometry budget | 48 MiB | 96 MiB |
| Resident model count | 24 | 48 |
| Detailed triangle budget | 450,000 | 900,000 |
| Landmark distance from camera | 1,800 m | 2,500 m |
| Ordinary street detail distance | 300 m | 500 m |
| Minimum projected model height | 24 px | 18 px |

Use source bounds for frustum/distance planning and prioritise selected landmarks and nearby walking surfaces. Debounce planning during camera motion. Retain the existing extrusion until an individual model successfully loads; replace only its exact UID. An abort, decompression/parse error or missing asset must retain the fallback and use the existing retry state. Evict unused models by distance/recency within the byte and triangle budgets, dispose geometries/materials, and guard late completion after disposal. Do not keep both compressed bytes and expanded offline arrays in a resident cache. Loading the entire catalogue's assets is not a startup action.

Source picking should resolve to the existing building UID and show recorded outline heights alongside source-model geometry attribution. Reuse the existing activity/night material settings; preserve the original source materials and vertex colours in provenance. Flight avoidance must include the source mesh top rather than the lower outline roof. Walking collision and public access must be checked separately, including any actual undercroft/overhang; a successful visual import is not an access approval.

## Terrain and route status

`terrain-central.json` is a staged 5 m patch produced by the existing DTM/source-TIN mosaic importer. The complete retained sheet union is included so the importer never clips or silently drops an original grid. The review boundary is unchanged. `terrain-crop.json` documents the larger source extent and the existing outer transition.

The bounded official 3D pedestrian source has 13,026 segments with original XYZ and attributes retained. The linked opening-time tables and escalator operation reference are retained. The official data dictionary confirms HKPD heights and states ±1 m horizontal / ±2 m vertical accuracy. Three outdoor source-connected route candidates have passed source/topology tests, but still require actual navigation replay. Neither this terrain patch nor the pedestrian source has been published as a walkable surface. Landmark terrain intersections, waterfront shoreline and full continuous walking remain acceptance work.

Primary source: [Lands Department 3D Mapping](https://www.landsd.gov.hk/en/survey-mapping/mapping/3d-mapping.html), [3D Pedestrian Network metadata](https://portal.csdi.gov.hk/csdi-webpage/dataset/landsd_rcd_1637222018065_52265). Full per-file URLs and revisions are retained in the adjacent source/evidence JSON.
