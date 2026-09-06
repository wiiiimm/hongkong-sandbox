# Stonecutters Bridge source checkpoint · HKS-196

**Staged only. The live city is unchanged. HKS-196 remains unfinished.** This checkpoint supplies three original government components, exact tower/proxy matches, retained source terrain and a mapped channel cut. The terrain is **not ready to publish**: the full port-land audit identifies 1,211 remaining shoreline mask/blend discrepancies. Cables and actual-city AFTER acceptance are also pending. Root’s [baseline browser evidence](browser/before/verification.json) remains the current live reference.

The reuse audit examined 82 existing Astra cache metadata records and searched relevant main/reference archive names before acquisition. None contained the target sheets or a named Stonecutters asset. One current iB5000 archive, `10-NE-B`, was reused from the Tsing Ma source cache. No other model’s implementation or reference source file was changed. All acquired compact original-entry ZIPs, original map archives, index responses, request URLs, hashes and selected extracted components are retained in git under `source-scripts/city/stonecutters/`.

## Original bridge components

| Source component | Sheet | Source triangles | Original Y bounds, m HKPD |
| --- | --- | ---: | --- |
| I296272022407063C0 · deck and supports | 11-NW-11C | 23,168 | 5.213–98.825 |
| B298652107401063C0 · Tsing Yi tower | 10-NE-15B | 306 | 4.470–305.097 |
| B306502042501063C0 · Stonecutters Island tower | 11-NW-11C | 160 | 5.102–299.353 |

The staged `bridges-stonecutters.json` uses the existing `official-infrastructure` contract and totals **23,634 original triangles**. The only coordinate transform is the existing original hierarchy followed by city translation `[-834500,0,816500]`. No vertices are scaled, lifted or moved. The full deck bounds are `[-4872.90625,5.213,-4778.66016]` to `[-3614.46875,98.825,-3723.58984]` in city metres/HKPD. See the inspected [original-component figure](original-components-2520x1260.png) and [model-build evidence](model-build.json).

Exact GeoRefNo/BuildingCSUID prefixes and source footprint intersections identify `landsd/75319:0` and `landsd/75938:0`. Their original building-record tops are both 298 m HKPD; the model upper extents are higher. Both values remain visible in provenance, and the discrepancy is not silently attributed to a particular antenna or structural element. The model-bounds tower centres are 1,018.684 m apart. Twelve named OSM bridge ways are fully covered by the source deck hull plus the explicit 1.5 m map tolerance; two original approach tails, **5.965 m and 5.699 m**, remain unchanged. Neighbouring interchanges and port structures are not added to the live layer.

The corresponding individualised infrastructure `I296272022407063A0` has the same bounds and 23,168 triangles. Its separate `GENERIC/G300002040001062A0` has 374,502 triangles but reaches only 133.773 m HKPD; it cannot supply complete stays to the towers. Neither inspected bridge version contains the complete high cable system. The original sources are retained, and **no illustrative cable packet has yet been generated**.

The official [Highways Department factsheet](https://www.hyd.gov.hk/en/information_corner/hyd_factsheets/doc/e_Stonecutters_Bridge.pdf), retained and visually inspected, supplies independent checks: 1,018 m main span, two 289 m back spans, approximately 53 m split deck, 298 mPD design tower level and 224 stays. These references can guide a separately labelled future cable illustration; they do not provide surveyed individual cable-anchor coordinates. All three components have `walkable:false` and no walk triangles. Motorway pedestrian access is not inferred.

## Terrain and port land

Eight original terrain models are resampled through the existing common bridge pipeline into a **393 × 365 grid at 5 m**, covering E829292.5–831252.5/N819827.5–821647.5. Four official iB5000 source sheets (`10-NE-B/D`, `11-NW-A/C`) supply closed `ContourPoly` land boundaries. GML axis order is handled by the existing source parser; source HKPD elevations remain distinct from the illustrative −4 m render bed.

The bounded source-water complement covers 1,866,062 m² and preserves 526,438 m² of mapped port land. The candidate removes 176,101 m² of elevated/mixed terrain triangles from that water, using 7,451 unique cut cells. Eleven source-axis samples currently have coarse rendered heights of about 52–80 m HKPD; after the staged mapped-water cut they reach the illustrative bed. This fixes the false channel surface in the candidate without erasing real port land in plan.

Both complete 40 m tower-foundation neighbourhoods agree with retained source-grid heights within 0.005 m, but the **full 21,055-node mapped-land audit** finds **1,211** nodes retaining archival mask/blend differences. All those nodes have original source coverage. The largest example, city `[-3912.5,-3897.5]`, is 18.83 m in the candidate versus 1.00 m in the source grid. There are also old zero-mask holes where newer source land is present. This must be repaired and checked across the full relevant shore extent before publication; source values close to 1 m also require explicit treatment of the existing renderer’s 1.2 m dry-ground clamp. See [terrain-source-audit.json](terrain-source-audit.json). A plausible tower-centre result is not accepted as whole-area terrain validation.

## Checks and integration handoff

Seven focused Python tests pass: exact original rebake, tower identity/height preservation, full/partial proxy coverage, mapped water/foundation protection, cut-triangle topology, explicit unfinished terrain flags, and the existing outer terrain transition. The shared JavaScript infrastructure/geometry/terrain/collision adapters also pass: all three original models retain their vertices, five under-span points are clear through 60 m HKPD, and source-deck collision appears at roughly 81–87.4 m at those samples. These are software regression checks, not navigational clearances. No source-task GPU/browser run was used. See [runtime-helper-verification.json](runtime-helper-verification.json) and [checkpoint.json](checkpoint.json).

After the remaining terrain/cable work is accepted, root can use the existing `BridgeLayer` to load the bridge packet, conditionally suppress the two matched building extrusions while retaining source records, and apply the two exact proxy clips. The source IDs are stable `landsd-infrastructure/<original-id>` values. A future cable layer must require these original parents and remain separately labelled. Add the terrain as a single patch and merge only this region into the existing hydro composite, preserving Tai O, Mui Wo, Pui O and the Tsing Ma/Ting Kau region. **Do not publish the current terrain candidate.** Root owns runtime/manifest integration, Linear updates and browser acceptance.

Reproduce from the Astra worktree:

```sh
SSL_CERT_FILE=/etc/ssl/cert.pem /tmp/astra-city-venv/bin/python source-scripts/city/stonecutters/fetch.py --index-only
SSL_CERT_FILE=/etc/ssl/cert.pem /tmp/astra-city-venv/bin/python source-scripts/city/stonecutters/fetch.py
SSL_CERT_FILE=/etc/ssl/cert.pem /tmp/astra-city-venv/bin/python source-scripts/city/stonecutters/fetch.py --folder towers --prefix BUILDING/B2986521074 --prefix BUILDING/B3065020425 --tile 10-NE-15B --tile 11-NW-11C
SSL_CERT_FILE=/etc/ssl/cert.pem /tmp/astra-city-venv/bin/python source-scripts/city/stonecutters/fetch.py --folder individual --individual --prefix INFRASTRUCTURE/ --prefix GENERIC/ --tile 11-NW-11C
SSL_CERT_FILE=/etc/ssl/cert.pem /tmp/astra-city-venv/bin/python source-scripts/city/stonecutters/fetch.py --folder terrain --prefix TERRAIN
SSL_CERT_FILE=/etc/ssl/cert.pem /tmp/astra-city-venv/bin/python source-scripts/city/stonecutters/hydro_fetch.py
/tmp/astra-city-venv/bin/python source-scripts/city/stonecutters/inventory.py
/tmp/astra-city-venv/bin/python source-scripts/city/stonecutters/models.py
/tmp/astra-city-venv/bin/python source-scripts/city/stonecutters/terrain_stage.py
/tmp/astra-city-venv/bin/python source-scripts/city/stonecutters/hydro_stage.py
/tmp/astra-city-venv/bin/python source-scripts/city/stonecutters/terrain_audit.py
/tmp/astra-city-venv/bin/python source-scripts/city/stonecutters/test_stonecutters.py
node source-scripts/city/stonecutters/verify-runtime.mjs
/tmp/astra-city-venv/bin/python source-scripts/city/stonecutters/plot.py
```

Sources: Lands Department / HKSAR Government, [non-textured 3D dataset](https://portal.csdi.gov.hk/csdi-webpage/metadata/landsd_rcd_1742809441342_98380/html), [individualised 3D dataset](https://portal.csdi.gov.hk/csdi-webpage/metadata/landsd_rcd_1671676915450_88604/html), [iB5000 official index](https://portal.csdi.gov.hk/server/rest/services/common/landsd_rcd_1637224243141_96556/MapServer/0). Original index revisions and entry hashes are in the retained metadata; source-sheet revisions differ. Compact ZIP hashes describe selected original-entry caches, not complete remote ZIPs. OSM identifiers/paths remain credited to OpenStreetMap contributors (ODbL). No bathymetric survey, complete engineering reconstruction or public-access permission is claimed.
