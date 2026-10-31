# Exact original source opening investigation · 9 October 2026

Agent: xl_identity_search. Research only: zero source or viewer edits, no installations and no identity approval. AI interpreted evidence and wrote diagnostic code; scripts make no external AI calls and no AI modelling was used.

The all-179 spatial ranking identified two predominant interior gaps. The complete original source geometry, existing grouped forms and whole GeoRef cells were preserved. Two independently acquired government FBX originals retain exactly the same projected boundaries as the previously pinned glTF originals: symmetric difference 0 m², Hausdorff distance 0 m. Raw source double arrays and Blender 4.5.9 C++ imported arrays have identical world-triangle SHA256 values. Thus neither gap comes from lost glTF conversion geometry.

| Exact source | Raw coverage | Largest source hole | Inner vertical faces | Exact rim wall coverage | Current finding |
| --- | ---: | ---: | ---: | ---: | --- |
| 157125 / B365112054601063C0 | 86.6988% | 38.0630 m² | 10 | 84.8975% | Official map label is PH; the LandsD legend identifies a pump house. A bright octagonal aerial feature lies within a larger dark rectangle. An open courtyard or complete omitted exterior area is **not established**. |
| PopCorn 1, 295538 / B447991877202063C0 | 93.8868% | 1,997.0804 m² | 181 | 82.7918% | Exact fresh provider query identifies MTR Tseung Kwan O Station inside this gap; the owner’s railway protection plan separately depicts that structure. A companion-source route is being tested in the separate PopCorn station collection checkpoint. |

Both whole original source GeoRef cells pass target/projection containment. The opening-adjusted coverage calculations (98.8884% / 99.4721%) remain explicitly **unaccepted diagnostics**. No hole is removed from the GIS target and no surface is removed from either source. Inner wall geometry alone does not distinguish an intentional open area from a missing roof/floor, so no courtyard credit was granted.

The 157125 overlay uses untouched government aerial pixels and the fixed HK1980-to-WGS84 transform, with original source and current GIS rings drawn as scientific vectors. There is no fitted alignment, guessed placement or image retouching. Original aerial and map bytes, headers and checksums are retained. Map/Aerial Photograph from Lands Department; copyright reserved, Hong Kong SAR Government.

Primary references:

- [Government FBX package index](https://portal.csdi.gov.hk/server/rest/services/common/landsd_rcd_1742809441342_98380/FeatureServer/0): current sheets 11-NW-15C / 11-NE-25B, fresh index, ETag-bound ZIP directories, members, CRC and SHA256 in adjacent receipts.
- [Government building service](https://portal.csdi.gov.hk/server/rest/services/common/landsd_rcd_1637211194312_35158/MapServer/0): fresh exact PopCorn-gap envelope query returns source station GeoRef 4482718747, CSUID 4482718747T20130521, current OBJECTID 295360, original viewer UID 295539; 96.7707% of the largest gap intersects its current provider footprint. Stable identity is retained; current OBJECTID is not substituted into the viewer.
- [MTR/AP/210 B railway protection area plan](https://www.mtr.com.hk/archive/corporate/en/operations/protection/MTR_AP_210_B.pdf), November 2022: separately depicts Tseung Kwan O Station, PopCorn 1 / The Wings and their podium, with HK1980 grid labels. This is owner/source context, not permission to invent missing surfaces.
- [LandsD topographic API](https://hosting.csdi.gov.hk/csdi-webpage/apidoc/TopographicMapAPI), [LandsD map labels](https://portal.csdi.gov.hk/csdi-webpage/apidoc/MapLabelAPI), [LandsD official legend](https://www.landsd.gov.hk/doc/en/mapping/paper-map/lot-index-plan/LIP_A4_Legend.pdf): PH = pump house. The generic 126 Waterloo Road residential-courtyard paper was not bound to this pump house and gives no positive evidence for it.

Reproduce using `xl-source-authored-openings-20261009.py`, the `-overlay`, `-fbx`, `-blender-inspect`, `-raw-fbx`, `-fbx-measures` and `-station-search` runners beside it. Independent source bytes are local, pinned and untouched. The checkpoint binds every evidence file and runner; completed receipts must not be overwritten.

Next steps: 157125 needs exact visible-surface evidence for the rectangular hole before any source-backed alternative can be reviewed. PopCorn’s companion source is investigated separately; no opening waiver or inherited format approval is used. These are version-specific unresolved states, not permanent model rejection.
