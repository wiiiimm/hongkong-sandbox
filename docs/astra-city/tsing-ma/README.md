# Tsing Ma Bridge repair — HKS-191

Prepared by Astra in the existing isolated city worktree. This is a staged source/data repair; the root agent owns live integration and browser acceptance. No source building heights, original glTF vertices or archival DTM arrays were changed.

The false land is inherited from the original terrain pipeline. The retained official 5 m DTM contains the elevated bridge surface. `3d-viewer/scripts/hk_dtm.py` averages 14 × 14 samples; `hk_build.py` calls an averaged elevation above 1 m “land”; `source-scripts/city/build_city.py` carries that 70 m grid into the city. Seven independently recomputed block means reproduce the existing 28–56 m grid values exactly. B50K vegetation styling does not create the ridge. See `terrain-source-audit.json` and `native-dtm-samples.json`.

## Existing assets checked first

Filename and source-code checks of the current/original viewers, main worktree, comparison worktree and read-only prior viewers found no named Tsing Ma mesh. The previously retained government archives covered Mui Wo and Tai O. A bounded query of the official 3D model index identified seven relevant sheets: 10-NE-2A/B/C/D and 10-NE-3A/B/D. Their non-textured infrastructure inventory contains 16 objects; only the two deck halves belong in this bounded bridge package. Four tower legs are classified separately as **BUILDING**, which is why an infrastructure-only query did not find them.

The corresponding individualised 2D/3A archives were checked as well. Their deck geometry has the same bounds/triangle counts, and their GENERIC objects are low surface geometry, not the missing high suspension cables. No source image entries were extracted. Original glTF/bin entries, CRCs, hashes, index queries, revision dates and public download URLs are retained beside the preparation scripts.

## Staged payloads

All paths below are relative to `source-scripts/city/tsing-ma/`.

| File | Contents |
| --- | --- |
| `bridges-tsing-ma.json` | Six immutable source components, 37,970 triangles, original colours/normals; `kind: official-infrastructure`, `region: tsing-ma`, EPSG:2326/HKPD |
| `terrain-tsing-ma.json` | 603 × 267 samples on the existing 5 m lattice; `coarseCells: [343,340,386,359]`; seven source TINs sampled through the existing terrain pipeline |
| `hydro-tsing-ma.json` | Two mapped marine polygons, exact source land complement, 8,363 replacement fine cells, 707 bed triangles and 4,058 bank triangles |
| `cables-tsing-ma.json` | Separate illustrative main-span cable/hanger geometry: two cables, 152 hangers, 6,432 triangles; **not** government source geometry |

The Tsing Ma source components are:

| Original object | Role | Existing building extrusion identity |
| --- | --- | --- |
| I244492317107063C0 | Ma Wan deck half | — |
| I254702348107063C0 | Tsing Yi deck half | — |
| B250112338101063C0 | Ma Wan north tower leg | landsd/193003:0 |
| B250222334201063C0 | Ma Wan south tower leg | landsd/205933:0 |
| B263302377501063C0 | Tsing Yi north tower leg | landsd/194907:0 |
| B263422373701063C0 | Tsing Yi south tower leg | landsd/194906:0 |

Tower identities use exact GeoRefNo/BuildingCSUID prefixes and spatial comparison. Model hull overlap of the smaller source footprint is 78.8–100%; hull centroids differ by 0.7–12.4 m because tower saddles/crosspieces overhang the narrow footprint and the datasets differ. The original footprint base/top fields remain recorded alongside the model’s independent HKPD bounds. These are source identity matches, not a claim that the two geometric revisions are identical.

Eight mapped OSM bridge proxies fall fully inside the two source-deck projected hulls with an explicit 1.5 m map tolerance. Two lower-carriageway records continue beyond the source model. `proxyClips` retains their original approximately 90 m Tsing Yi tails, with source IDs and full retained paths. A derived clipping endpoint is not labelled as a surveyed OSM node. Suppression/clipping must happen only after the entire source package validates and loads; fallback proxies and tower records must survive failure.

## Ground, water and vertical datum

Source glTF node transforms produce `[E, HKPD, -N]`; city translation is `[-834500,0,816500]`. No terrain lift or scale correction is added. The source tower tops reach approximately 209.45 m HKPD. The Highways Department’s 206 m tower height is a structural dimension to the saddle, not a replacement absolute datum.

The newer official source terrain places the Ma Wan tower island at about 6.8 m in the chosen test location, compared with 38.1 m from the inherited coarse interpolation. The source TIN and the original DTM have different revisions. The shared 5 m mosaic retains its existing boundary blending and water-node policy; mapped hydro provides the separate land/sea semantics.

The marine cut is the bounded complement of six existing-land `ContourPoly` features from current iB5000 sheets 10-NE-A/B (index revision 30 July 2026). It removes no hand-drawn bridge-axis rectangle. It explicitly preserves the real artificial island around the Ma Wan tower foundation, corroborated by the [Highways Department factsheet](https://www.hyd.gov.hk/en/information_corner/hyd_factsheets/doc/e_Tsing_Ma_Bridge.pdf). The approximately 1.936 km² polygon scope includes existing sea; this is not a claim that all that area was false land. With the new patch, roughly 0.196 km² of positive/mixed rendered triangles require cutting.

The −4 m bed is an illustrative viewer bed, **not** measured bathymetry or Chart Datum. Five marine sample points under the span are collision-free through 55 m HKPD in the shared helper check. That is a rendering/collision regression, not a shipping clearance statement.

`terrain.hydro` already contains Tai O. Integrate this payload as another bounded region, preserving earlier water/cuts and per-region provenance. Do not replace the existing hydro object wholesale. Root also owns the corresponding minimap and terrain-patch manifest integration.

## Cable approximation and limits

The source deck and tower meshes omit the high main cables. The separately staged illustration attaches to the average of unique original saddle-cover vertices within 3 cm of each local maximum; interpreting that point as a cable centreline attachment is approximate. The two spans derived from these source points are 1,377.17 and 1,377.43 m, consistent with the documented 1,377 m main span.

A static parabolic profile uses the 0.091 sag ratio reported in the primary study [Over 25-year monitoring of the Tsing Ma suspension bridge](https://link.springer.com/article/10.1007/s13349-024-00842-5). Main cable diameter 1.1 m comes from the HyD factsheet. This is a visual approximation, not the observed present curve, an engineering model, or a simulation of temperature, load or wind deflection. Hangers are illustrated at 18 m intervals and 0.16 m diameter; neither exact hanger spacing nor diameter was verified. Their lower points sample upward original deck triangles. They are not procedural windows or ordinary building façades.

**Backstay anchorage geometry and exact hanger details remain unverified and are omitted.** No public pedestrian access is added: the mapped motorway records say `foot=no`, and all six models have `walkable:false` with no walk triangles. Source geometry is detailed enough to improve the deck, towers and foundations, but this does not certify every bridge component, current condition, structural behaviour or access route.

## Verification and reproduction

Run from the Astra worktree. Source acquisition honours ordinary TLS verification and uses the existing bounded ZIP-range helper. The system curl client is used for the mapping archive endpoint because the local Python certificate store did not validate its issuer; certificate verification was never disabled.

```sh
SSL_CERT_FILE=/etc/ssl/cert.pem /tmp/astra-city-venv/bin/python source-scripts/city/tsing-ma/fetch.py
/tmp/astra-city-venv/bin/python source-scripts/city/tsing-ma/hydro_fetch.py
/tmp/astra-city-venv/bin/python source-scripts/city/tsing-ma/inventory.py
/tmp/astra-city-venv/bin/python source-scripts/city/tsing-ma/terrain_audit.py
/tmp/astra-city-venv/bin/python source-scripts/city/tsing-ma/models.py
/tmp/astra-city-venv/bin/python source-scripts/city/tsing-ma/terrain_stage.py
/tmp/astra-city-venv/bin/python source-scripts/city/tsing-ma/hydro_stage.py
/tmp/astra-city-venv/bin/python source-scripts/city/tsing-ma/cables.py
/tmp/astra-city-venv/bin/python source-scripts/city/tsing-ma/test_tsing_ma.py
node source-scripts/city/tsing-ma/verify-runtime.mjs
/tmp/astra-city-venv/bin/python source-scripts/city/tsing-ma/plot.py
```

Eight focused Python tests pass: original source hashes/positions/normals/colours, tower identity and immutable height fields, marine/island classification, exact land preservation, source-ground correction, outward cable faces, retained approach tails and terrain boundary continuity. The Node check reuses the actual geometry, terrain and model-collision helpers: six source meshes compile to finite BufferGeometry; the channel is open below, the deck collides at its source height, and the island remains land. No browser/GPU pass has been performed by this source-data agent; root owns combined live acceptance.

Primary source datasets: [non-textured 3D models](https://portal.csdi.gov.hk/csdi-webpage/metadata/landsd_rcd_1742809441342_98380/html), [individualised models](https://data.gov.hk/en-data/dataset/hk-landsd-openmap-3d-visualisation-map-individualised-models), and [iB5000 map index](https://portal.csdi.gov.hk/server/rest/services/common/landsd_rcd_1637224243141_96556/MapServer/0). Credit Lands Department / HKSAR Government; retain the original dataset terms and attribution. OSM approach identities remain credited to OpenStreetMap contributors (ODbL).
