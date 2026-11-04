# Exact paired-original uncovered-area cause analysis

This stage follows the official OP relationship and original counterpart recovery checks. It preserves exact original source SHA/poses, all current forms and all uncovered/excess areas. No mesh or GIS boundary was edited, and no identity alternative or installation was approved.

| Pair | Target area | Uncovered | Boundary-connected uncovered | Interior uncovered |
|---|---:|---:|---:|---:|
| K30/60: 147996 + 147734 | 140.532311 m² | 7.281028 m² | 7.281015 m² | 0.000013 m² |
| K300/63: 118003 + 118128 | 111.733771 m² | 6.034963 m² | 6.034314 m² | 0.000649 m² |

Nearly all the uncovered area consists of **exterior boundary strips**. The two material strips for K30/60 are 4.803861 and 2.477153 m². K300/63 has one 6.034314 m² exterior strip. These are not demonstrated internal courtyards or source-authored enclosed open voids, so a courtyard-specific alternative to the normal coverage test is unsupported.

K30/60 excess intersects retained neighbour `landsd/147250:0` by 0.536054 m², within the existing 1 m² rule. K300/63 excess intersects `landsd/118712:0` by 1.901111 m², still failing. Neither neighbour was removed, reassigned or suppressed. The exact intersection geometry is retained in the per-pair GeoJSON and cause record.

Per-pair `original-coverage-cause.png` plots show the full unchanged source projection, separate original components, current target, exact uncovered area and unrelated overlap. Their oblique diagnostic uses every original vertex. `exact-projection-difference.geojson` retains all projected shapes in viewer metres (x=easting−834500, y=816500−northing); it is a diagnostic output, not a source replacement. Every source triangle was included in the projection.

Eight raw [LandsD Imagery Map API](https://portal.csdi.gov.hk/csdi-webpage/apidoc/ImageryMapAPI) tiles provide actual-site primary aerial context. PNG files are unchanged original provider bytes with URL, SHA, size and HTTP receipt metadata. Images were visually inspected; their pixel positions do not justify sub-metre survey boundaries, courtyard ownership, exact mesh coverage or date precision. Copyright: Aerial Photograph from Lands Department, © Government of the Hong Kong SAR. No imagery was applied to models or traced.

Official site views:

- [K30/60 site, GeoInfo Map](https://www.map.gov.hk/gm/map/s/wgs84/22.323231751427436/114.16489182202304?lg=en)
- [K300/63 site, GeoInfo Map](https://www.map.gov.hk/gm/map/s/wgs84/22.30627173247838/114.16978836327654?lg=en)

The first pair requires corrected provider/source-version evidence for its missing exterior strips or a genuinely more complete original source format. The second additionally requires evidence resolving the excess intersection with its retained neighbour. Both remain revisitable source-version holds. No 95% coverage or 1 m² overlap threshold was relaxed; no permanent rejection was recorded.

`result.json` / `neon-sync.json` record the immutable completed Neon stage and exact readback. AI was used for source interpretation and coding only, with zero AI geometry modelling or script AI-service calls.
