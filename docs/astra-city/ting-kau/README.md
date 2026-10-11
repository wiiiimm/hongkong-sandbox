# Ting Kau and combined bridge-cluster staging · HKS-191

Prepared by Astra in the existing isolated city worktree. The user confirmed **Tsing Ma + Ting Kau**; Kap Shui Mun remains outside this implementation. The source assets and corrected terrain are now integrated in the Astra preview and passed [actual-city browser acceptance](browser/README.md). Root owns the generic infrastructure loader and shared hydro/minimap integration. No public walking access is added.

## Original assets and identity

The reuse audit is [cluster-scope.md](../tsing-ma/cluster-scope.md). Existing Tsing Ma caches contained nearby southern interchange structures, but no complete Ting Kau bridge. A bounded official index query identified six non-textured sheets: **6-SE-18C/D and 6-SE-23A/B/C/D**. Only their infrastructure and terrain entries, three selected tower identity entries, and the individualised infrastructure/generic entries from 23B were fetched through the existing filtered ZIP-range downloader. The index revision for the six non-textured sheets is 28 September 2025 UTC; retrieval was 6 September 2026 UTC. Original model bytes, full remote ZIP directories, public URLs, entry hashes and revision metadata are retained. Compact cache hashes describe derived ZIPs of selected original entries, not complete remote archives.

The 23 infrastructure objects were inspected. **I259872443407063C0**, in sheet 6-SE-23B, already contains the complete bridge deck and all three towers: **16,995 source triangles**. The corresponding individualised object I259872443407063A0 has exactly the same bounds and triangle count; it also omits the inclined stay cables. The individualised GENERIC object is low coastal geometry, not a cable model. See [source-inventory.json](source-inventory.json) and the inspected [original geometry figure](source-infrastructure-inspection.png).

Three separate BUILDING entries establish identity, but are **not rendered again**:

| Original identity entry | Existing footprint UID | Recorded base / top (m HKPD) |
| --- | --- | --- |
| B260722538701063C0 | landsd/219323:0 | 7.5 / 172 |
| B262702498501063C0 | landsd/219830:0 | 5.3 / 200 |
| B264802455801063C0 | landsd/221079:0 | 4.7 / 165 |

Exact BuildingCSUID/GeoRefNo prefixes, footprint overlap and tall faces in the full infrastructure establish the matches. The separate northern BUILDING asset models only a lower portion of its tower; its mesh bounds are not mistaken for the complete tower height. All source footprint heights and original mesh coordinates remain immutable. Suppress the three ordinary building extrusions only after the complete valid infrastructure package loads, retaining their original source identities for picking/provenance and failure fallback.

All **13** named Ting Kau OSM bridge ways lie within the projected original bridge hull plus an explicitly declared **1.5 m map tolerance**. The payload maps these exact IDs for conditional proxy suppression; it has no partially clipped Ting Kau tails. Neighbouring roads and interchanges are untouched. Tsing Ma’s two partly covered lower-carriageway proxies still retain their approximately 90 m original Tsing Yi tails.

## Terrain, water and datum

Original glTF transforms produce `[E, HKPD, -N]`; the only city translation is `[-834500,0,816500]`. The full source bridge bounds are approximately Y **2.805–202.286 m HKPD**. HyD’s tower heights above the footings are structural dimensions and must not replace absolute model elevations.

The inherited false-land mechanism is verified independently at Ting Kau. Elevated bridge samples occur in the retained original LandsD 5 m DTM. Seven recomputed **14 × 14** block means reproduce the existing 70 m source elevations exactly; the old `DTM > 1 m` land rule renders those averaged bridge heights as land. For example, a mapped marine point at city `[-8340,-8710]` had rendered ground **44.179 m**, and its source block contains values up to bridge height. See [terrain-source-audit.json](terrain-source-audit.json). This is not caused by a new decorative road layer.

Six newer original terrain TINs are sampled through the existing 5 m patch builder. Closed existing-land `ContourPoly` features from official **iB5000 6-SE-C/D** provide bounded marine semantics, preserving all three tower foundation sites and the real central protection island. The maps’ index revision is 30 July 2026; individual source feature dates remain in the metadata. Original GML positions are read as `[N,E,Z]`, without treating placeholder zero Z as a surveyed level. Eleven selected land features produce two water polygons with 370 vertices, covering **957,900 m²**, including already-existing sea. Roughly **87,244 m²** of positive/mixed fine-grid triangles require removal; the total water area is not the area of the former artefact.

The **−4 m viewer bed is explicitly illustrative**, not bathymetry or Chart Datum. Shared collision checks at four points find open water beneath the source span through 55 m HKPD, with source deck collisions around 68.5–76.9 m depending on location. These are software regression samples, not navigational clearances. Source foundation samples remain land at 4.27, 7.38 and 3.67 m HKPD.

## Use the combined terrain package

The independently prepared Tsing Ma and Ting Kau patches overlapped by 140 m. Their separate transition bands differed by up to **16.526 m** at E826745/N824140, so publishing them together by load priority would leave an avoidable seam. The common package resolves this with **one 603 × 575 grid at 5 m**, using all **13 original terrain sheets** and the existing mosaic/transition tools.

For live integration, use these staged files:

| File relative to `source-scripts/city/` | Role |
| --- | --- |
| `tsing-ma/bridges-tsing-ma.json` | Six immutable original components; 37,970 triangles |
| `ting-kau/bridges-ting-kau.json` | One immutable original deck/tower mesh; 16,995 triangles |
| `tsing-ma/cables-tsing-ma.json` | Separate illustrative suspension cables/hangers; 6,432 triangles |
| `ting-kau/cables-ting-kau.json` | Separate illustrative inclined stays; 4,104 triangles |
| `ting-kau/foundation-candidate/terrain-tsing-ma-ting-kau.json` | **Single common terrain grid with source foundation repair**, replacing both isolated bridge patches |
| `ting-kau/foundation-candidate/hydro-tsing-ma-ting-kau.json` | Both source marine regions, with cuts/banks derived against that same corrected common grid |

Keep the older isolated terrain/hydro files as source-audit evidence; do not load them alongside the common patch. Existing Tai O and Mui Wo hydro must remain present. The combined hydro preserves each region’s individual bounds/source metadata; a minimap should fill those individual regions, not paint the union bounding rectangle as a single land/water area.

The first combined patch is retained as intermediate seam evidence. Its browser review exposed archival-mask spikes across real foundation islands; the [whole-foundation correction](foundations/README.md) restores the retained source terrain. Use the corrected candidate paths above for final publication. Both former seams and the complete outer transition remain identical.

The original regional water polygons and bed triangles are **byte-equivalent as JSON values**. Only terrain cut cell indices and bank heights are regenerated against the common grid. The first combined package’s 12,187 unique cut cells contain 5,670 replacement land triangles, plus 1,073 bed and 6,380 bank triangles. Tsing Ma’s foundation island and all Ting Kau foundation sites remain land. The original bridge and cable packets are untouched.

The seam audit checks 1,862 old-overlap samples, 532 samples across former boundaries, 6,505 unchanged core samples and 2,356 outer coarse-boundary samples. The maximum height change across a 2 mm traversal of a former boundary is 2.43 mm, consistent with local terrain slope; there is now only one surface there. Outer coarse-boundary mismatch is below 0.000001 m. The old source-union blend at N824000 becomes interior source terrain; 24 sampled points on that line change by up to 14.165 m as the previous blend into the archival DTM is removed. No original source TIN or bridge was moved. See [combined verification](combined/verification.json), [shared collision checks](combined/runtime-helper-verification.json) and the inspected [2400 × 1920 source plan](combined/source-plan-2400x1920.png).

## Clearly separate cable estimates

The official [Highways Department factsheet](https://www.hyd.gov.hk/en/information_corner/hyd_factsheets/doc/e_Ting_Kau_Bridge.pdf), retained with hash, describes three single-legged towers, four fan planes, 13.5 m deck anchorage spacing and longitudinal/transverse stabilisation. Ting Kau is **cable-stayed**, and uses no Tsing Ma suspension curve. The shared tube tessellator alone is reused.

The optional illustration contains **334 fan stays and eight longitudinal stays**. Upper anchors derive from original tower-top vertices and lower points sample actual upward source deck faces. Exact cross-deck placement, upper anchorage distribution and cable diameters remain visual estimates. Two proposed anchors with no supporting original deck face are omitted. The illustration does **not** claim to reconstruct the published cable inventory exactly. Transverse stabilisation cables, precise hardware, dampers and dynamic sag are still omitted. The [comparison figure](source-with-illustrative-stays.png) and [cable notes](cable-approximation.json) distinguish original geometry from this separate estimated layer.

## Reproduction and checks

Run from the Astra worktree, with the existing Python runtime. Index responses/request URLs are retained; reruns can use those exact versions. No broad model set or model textures are downloaded.

```sh
# Bounded source acquisition; existing caches are reused.
SSL_CERT_FILE=/etc/ssl/cert.pem /tmp/astra-city-venv/bin/python source-scripts/city/ting-kau/fetch.py
SSL_CERT_FILE=/etc/ssl/cert.pem /tmp/astra-city-venv/bin/python source-scripts/city/ting-kau/fetch.py --folder towers --prefix BUILDING/B2607225387 --prefix BUILDING/B2627024985 --prefix BUILDING/B2648024558 --tile 6-SE-18C --tile 6-SE-23B --tile 6-SE-23D
SSL_CERT_FILE=/etc/ssl/cert.pem /tmp/astra-city-venv/bin/python source-scripts/city/ting-kau/fetch.py --folder terrain --prefix TERRAIN
SSL_CERT_FILE=/etc/ssl/cert.pem /tmp/astra-city-venv/bin/python source-scripts/city/ting-kau/fetch.py --folder individual --individual --prefix GENERIC/ --prefix INFRASTRUCTURE/ --tile 6-SE-23B
/tmp/astra-city-venv/bin/python source-scripts/city/ting-kau/hydro_fetch.py

/tmp/astra-city-venv/bin/python source-scripts/city/ting-kau/inventory.py
/tmp/astra-city-venv/bin/python source-scripts/city/ting-kau/models.py
/tmp/astra-city-venv/bin/python source-scripts/city/ting-kau/terrain_stage.py
/tmp/astra-city-venv/bin/python source-scripts/city/ting-kau/hydro_stage.py
/tmp/astra-city-venv/bin/python source-scripts/city/ting-kau/terrain_audit.py
/tmp/astra-city-venv/bin/python source-scripts/city/ting-kau/cables.py
/tmp/astra-city-venv/bin/python source-scripts/city/ting-kau/combined_stage.py
/tmp/astra-city-venv/bin/python source-scripts/city/ting-kau/test_ting_kau.py
/tmp/astra-city-venv/bin/python source-scripts/city/tsing-ma/test_tsing_ma.py
/tmp/astra-city-venv/bin/python source-scripts/city/ting-kau/verify_combined.py
node source-scripts/city/ting-kau/verify-runtime.mjs --combined
/tmp/astra-city-venv/bin/python source-scripts/city/ting-kau/foundation_stage.py
/tmp/astra-city-venv/bin/python source-scripts/city/ting-kau/verify_foundations.py
node source-scripts/city/ting-kau/verify-runtime.mjs --foundations
/tmp/astra-city-venv/bin/python source-scripts/city/ting-kau/plot_foundations.py
/tmp/astra-city-venv/bin/python source-scripts/city/ting-kau/plot.py
/tmp/astra-city-venv/bin/python source-scripts/city/ting-kau/plot_combined.py
```

Eight Ting Kau tests and eight existing Tsing Ma tests pass, as do source-entry hashes, the combined seam/hydro audit and both bridges’ shared collision checks. The approved parameterisation of `tsing-ma/terrain_stage.py` and `hydro_stage.py` keeps their default outputs byte-identical; hashes are recorded in the combined audit. The subsequent actual-city browser pass verifies loading, conditional proxy suppression, retained approach tails, source and cable picking, the repaired foundation meshes, under-span flight and day/night/mobile rendering. Its source-island review prompted the bounded original-TIN correction described above; no original bridge mesh was moved.

Credit Lands Department / HKSAR Government. Primary datasets: [non-textured 3D models](https://portal.csdi.gov.hk/csdi-webpage/metadata/landsd_rcd_1742809441342_98380/html), [individualised 3D models](https://portal.csdi.gov.hk/csdi-webpage/metadata/landsd_rcd_1671676915450_88604/html), [iB5000](https://portal.csdi.gov.hk/server/rest/services/common/landsd_rcd_1637224243141_96556/MapServer/0). Retain original attribution and terms. Existing OSM bridge identities remain credited to OpenStreetMap contributors (ODbL). No `references/` source file was modified.
