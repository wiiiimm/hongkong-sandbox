# Bounded government structured-source research

Codex, 8 October 2026, HKS-203. No source geometry, terrain, poses or acceptance limits changed. No historical map references used.

The official [3D Spatial Data API](https://p1hosting.csdi.gov.hk/csdi-webpage/apidoc/3d-spatial-data-api) supplies WGS84 building/infrastructure 3D Tiles. This investigation read its building root and terminal metadata around The Apex and HSBC Centre. The API key in provenance is the published documentation example, not a local credential.

The first coarse-content traversal stopped at its 60-request cap, retaining 6,262,656 cache bytes without producing a completed report. The completed narrower traversal reads 13 files / 902,006 bytes and three terminal B3DMs. Routing uses approximate EPSG2326-to-ECEF coordinates, with conservative radial allowance; this is not an accepted HKPD vertical-datum or placement conversion.

The three exact GeoRef-prefix matches are different government model variants:

| Current detailed original | Structured tile variant | Original triangles | Structured triangles |
|---|---|---:|---:|
| Apex B333211500201063C0 | B33321150020106010 | 13,370 | 31 |
| HSBC podium B346081997602063C0 | B346081997602062C2 | 15,336 | 268 |
| HSBC Tower 3 B346242001101063C0 | B346242001101062C1 | 8,396 | 52 |

Their batch-table hierarchy names one model and RootNode. It does not establish neighbouring component ownership, solid containment, detailed-source equivalence or physical support. No replacement/import is approved. Existing source-specific contact failures remain.

Neon job `514060248bdbf2eed7e1ea0cdac573286a6ca110aa8b7787ec627b7a6aeed857` is complete and read back. `result.json` binds all files, hashes, scripts and per-source findings. Model payloads remain in the documented local cache; the committed report records their exact hashes. AI interpreted unchanged metadata; no modelling AI or external per-model AI calls occurred.
