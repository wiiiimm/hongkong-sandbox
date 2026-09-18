# New Territories regional detail pass

Produced by the Codex Astra NT subagent for HKS-126, HKS-127 and HKS-128. This package adds destinations and actual mapped surface polygons to the existing city; it does not mark entire districts finished.

The assigned scope is all 57 sections in districts 11–18 except 11.6, 11.7 and 14.8. A representative arrival is not complete coverage of every village, island, hillside or named neighbourhood within a section. Detailed landmarks, verified building heights, transport structures and section-by-section visual approval remain open.

## Data and reproduction

```sh
/tmp/astra-city-venv/bin/python source-scripts/city/regional/nt/build.py
/tmp/astra-city-venv/bin/python source-scripts/city/regional/nt/test_nt.py
```

The generator uses the pinned `pyproj` and `Shapely` versions in `source-scripts/city/requirements.txt`. It writes `3d-viewer/city/data/regional/nt.json` and the adjacent verification report. Rebuilds use retained snapshots and make no network requests. `fetch.py` retrieves the supplementary OSM geometry only if its local snapshot is missing.

- `places.tsv` contains the hand-reviewed section associations, names, descriptions and exact OSM feature references. Coordinates come from those features; none are guessed. Long sections have additional representative places, including Tai Po Kau, Hoi Ha, Long Ke and Ap Chau.
- `surfaces-osm.json.gz` retains the 6,753-element supplementary response and its OSM timestamp, 6 September 2026 06:55:36 UTC. Its query is retained alongside it. The query is bounded to Hong Kong's OSM administrative area; it includes territory-wide source data so that only the explicitly assigned NT neighbourhoods can be selected reproducibly.
- Existing source snapshots are read without alteration. SHA-256 hashes, source filenames and source timestamps are recorded in `verification.json`.
- World coordinates use the existing EPSG:4326 → EPSG:2326 transformation: `x = easting − 834500`, `z = 816500 − northing`, in metres.
- Surface selection associates a source polygon with the nearest curated destination within 750 m. These are browsing associations, not administrative district boundaries. Polygons are clipped to the retained Hong Kong boundary relation 913110, which is an OSM reference boundary rather than a legal boundary survey.
- Closed beach, sports-pitch, pier and pedestrian-area polygons are retained. Lines are never expanded into invented rectangles. Simplification is 0.45 m, coordinates are rounded to 0.1 m, and holes are preserved. Private/restricted, indoor, elevated, invalid and excessive-complexity surfaces are excluded. Ground-level pitches/plazas with substantial building overlap are omitted because no supported roof/deck elevation is available. A mapped pitch does not by itself guarantee public access.
- No building heights or footprints are changed. `buildingOverrides` is deliberately empty because this pass has no new measured height evidence.

## Arrival verification and limits

Every exported walking arrival is checked at its actual rounded coordinates, on a mapped `footway`, `pedestrian`, `path` or `living_street` with no private/permit/prohibited access tag. Bridges, underground/indoor paths and non-zero layers are excluded. The existing terrain triangle must have three dry vertices, ground height over 0.8 m, no intersecting building within a 1.2 m radius at standing height, and less than 1.5 m elevation change at four neighbours 2 m away. These are local simulation checks, not a surveyed accessibility assessment or a route planner. Buildings and terrain are hash-recorded so the check can be repeated after changes.

Four locations are intentionally aerial-only: the operational container terminals, Lung Kwu Chau, Sha Tau Kok and the Lin Ma Hang border landscape. The viewer must honour `aerialOnly` and avoid enabling walking there. The Sha Tau Kok description states the real-world permit requirement without presenting restricted streets as public routes. Piers are visual surface geometry; this pass does not provide elevated pier walking collision.

## Primary geographic and access references

The [Home Affairs Department district guide](https://www.gohk.gov.hk/en/index.php) was cross-checked on 6 September 2026. Its district pages support the broad geography and choice of public parks, coastal areas and visitor destinations:

- [Tsuen Wan](https://www.gohk.gov.hk/en/districts/tw.php): coastal town, mountain hinterland and Ma Wan. North-east Lantau remains with the island workstream.
- [Kwai Tsing](https://www.gohk.gov.hk/en/districts/ki.php): Kwai Chung/Tsing Yi, container terminals and the Lantau Link viewpoint.
- [Sha Tin](https://www.gohk.gov.hk/en/districts/st.php): town and river corridor with surrounding recreational areas.
- [Tai Po](https://www.gohk.gov.hk/en/districts/tp.php): Tai Po proper and Sai Kung North; Wong Shek and Hoi Ha are associated with Tai Po in this package.
- [Sai Kung](https://www.gohk.gov.hk/en/districts/sk.php): Tseung Kwan O, Sai Kung town, peninsula and country-park setting.
- [Tuen Mun](https://www.gohk.gov.hk/en/districts/tm.php), [Yuen Long](https://www.gohk.gov.hk/en/districts/yl.php) and [North](https://www.gohk.gov.hk/en/districts/no.php): western new towns, rural valleys and northern border/coastal geography.

[AFCD's marine-park description](https://www.afcd.gov.hk/english/country/cou_vis/cou_vis_mar/cou_vis_mar_des/cou_vis_mar_des_sha.html) locates Sha Chau and Lung Kwu Chau in western Hong Kong waters. Its [transport information](https://www.afcd.gov.hk/english/country/cou_vis/cou_vis_mar/cou_vis_mar_mpvs/cou_vis_mar_mpvs_inf.html) lists no public transport there. The [Hong Kong Tourism Board Sha Tau Kok guide](https://www.discoverhongkong.com/eng/neighbourhoods/sha-tau-kok.html) and [Hong Kong Police permit page](https://www.police.gov.hk/ppp_en/11_useful_info/licences/cap.html) support the permit note.

Coordinates and surface boundaries are from [OpenStreetMap contributors](https://www.openstreetmap.org/copyright), ODbL 1.0, with direct element URLs in every record. The HAD/AFCD/HKTB references support context and access notes, not centimetre-level coordinates. No archived Lantau reference maps or third-party imagery are used by this package.
