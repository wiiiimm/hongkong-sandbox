# Hong Kong Island and Kowloon: first regional pass

Implemented by GPT-6 Astra for HKS-124 / HKS-125 on the isolated comparison branch. This pass adds source geometry for the city renderer and a visit point for each of the 56 proposed sections in districts 01–09. **Every section remains partial.** A source import and a checked arrival do not complete a neighbourhood's model, coast, walking network or gameplay review.

The payload is `3d-viewer/city/data/regional/urban.json`. It has 56 visits with supplied dry, building-clear public-path arrivals, 1,710 mapped surface polygons, and no building-height overrides. The new surface shapes comprise 1,491 sports pitches/courts, 102 piers, 77 pedestrian plazas and 40 beach polygons. The surface layer has about 10,800 vertices and the complete payload is under 600 KB. Exact counts, bounds, hashes, source timestamps and arrival evidence are in [verification.json](verification.json).

## What is grounded in sources

All surface outlines come from retained OpenStreetMap geometry. Closed rings, holes and multipolygon parts are retained; a 0.25 m simplification and 0.1 m coordinate rounding keep the render payload small. Open line piers are omitted rather than given an invented width. Features tagged as buildings, roof/underground locations or elevated ground surfaces are omitted. Plazas and pitches with more than 10% overlap against committed building footprints are omitted to reduce false rooftop overlays. These filters do not prove that every remaining polygon is at ground level.

The nine OSM district polygons determine which surfaces belong to this urban payload. They are mapped administrative boundaries, not an independent verification of the official boundary dataset. A surface's `sectionId` is the nearest visit within its district; proposed section boundaries have not been drawn. Sports shapes can include school or other restricted compounds. They describe visible geography and do not imply public entry. Likewise, a beach polygon does not establish a managed swimming beach.

Retained regional roads/buildings and the new surface query have OSM timestamps on 6 September 2026. The additional named-place response is dated 1 June 2026 and the district-boundary response 6 May 2026. Duplicate features use the newer response. This mixed source set is explicit in the verification metadata; it is not a live map feed. Original retained snapshots and `references/` were left untouched. No Lantau reference imagery was used for this urban pass.

Primary references were used to check names and the type of public place, while OSM supplies the exported coordinates:

- [LCSD public bathing-beach list](https://www.lcsd.gov.hk/en/swimhandbook/pbb/pbb4.html) identifies the Southern District beaches, including Deep Water Bay, Repulse Bay and Shek O. Their mapped sand polygons are retained without inventing a new coastline.
- [LCSD Victoria Park](https://www.lcsd.gov.hk/tc/parks/vp/) identifies the park and its courts. The layer uses separately mapped pitches; it does not colour the entire park as a sports field.
- [LCSD Kowloon Walled City Park](https://www.lcsd.gov.hk/en/parks/kwcp/) supports a present-day park visit. No historic dense-city reconstruction is implied.
- [LCSD Nan Lian Garden](https://www.lcsd.gov.hk/sc/parks/nlg/) confirms the public garden at Diamond Hill. The retained OSM English tag contains `Nam Lian Garden`; the visit uses the correct `Nan Lian` name and retains the feature ID.
- [Harbourfront Commission: HarbourChill](https://www.hfc.org.hk/en/hss/harbourchill-wan-chai) identifies the public waterfront setting beside Wan Chai Ferry Pier. [Its harbourfront history](https://www.hfc.org.hk/en/20th-anniversary) distinguishes promenades and the elevated Kai Tak Sky Garden. The Kai Tak runway visit uses the mapped ground-level promenade, not the terminal's roof garden.

## Arrival verification and limits

The builder finds the nearest usable point on a retained `footway`, `pedestrian`, `path` or `living_street`. It excludes restrictive access/foot tags, indoor and underground routes, bridges, non-zero layers and pedestrian-area polygons. The point is rounded before testing so the emitted coordinates themselves pass. Each successful arrival has:

- A triangle whose three terrain samples are above water, plus terrain height over 0.8 m.
- A 1.2 m clearance disc clear of overlapping building geometry for a 1.8 m actor.
- Dry terrain at four points 2 m away, with under 1.5 m height difference.
- A recorded OSM path ID and centre-to-arrival distance, never over 1 km.

These are model checks against the existing 70 m sampled terrain and committed building meshes. They do not establish surveyed terrain precision, accessibility, real-time opening hours or a complete traversable route. No arrival in this pass needs the aerial-only fallback. Upper Eagle's Nest trails are still a future review: section 06.6 uses a public garden in the Beacon Hill foothill approach within Sham Shui Po. Section 08.2 uses Lok Fu Recreation Ground on the Wong Tai Sin side of the district edge.

Piers remain a visual layer until elevated walking surfaces, supports and collision are implemented. Beach/harbour edges still depend on the coarse terrain. Landmark detailing, old-street façades, sports markings, building-height verification and complete day/night/browser section review remain outstanding. No section is marked complete.

## Reproduce and validate

From the feature-worktree root:

```sh
/private/tmp/astra-city-venv/bin/python source-scripts/city/regional/urban/fetch.py
/private/tmp/astra-city-venv/bin/python source-scripts/city/regional/urban/build.py
/private/tmp/astra-city-venv/bin/python source-scripts/city/regional/urban/test_urban.py
```

`fetch.py` keeps existing snapshots and only fetches missing ones. Queries are retained beside each compressed response; no network is used by the builder or tests. The runtime needs pyproj and Shapely from the existing importer environment. The five artefact tests check all 56 section IDs, each arrival against mapped paths/terrain/buildings and its assigned district, every exported polygon against source geometry, closed valid rings, and the render budget. Root integrates and verifies the shared renderer and browser behaviour separately.

Source geometry is © OpenStreetMap contributors, under [ODbL 1.0](https://www.openstreetmap.org/copyright). Coordinate conversion follows the existing EPSG:4326 → EPSG:2326 pipeline, with city origin E834500/N816500 and positive Z pointing south.
