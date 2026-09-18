# Hong Kong geographic base: all 18 districts

Produced by GPT-6 Astra on 6 September 2026 in the isolated
`codex/astra-hong-kong-city` worktree. This is the territory-wide imported base
for subsequent section-by-section modelling and gameplay review.

The dataset now contains **117,062 building forms**, **190,222 road/path
fragments**, and **1,294 park fragments** across **449 tiles**. There are **43
neighbourhood destinations**, including public-place arrivals in every one of
Hong Kong's 18 administrative districts. Building forms include constituent
parts; they are not unique addresses or a census of all Hong Kong buildings.

Detailed accuracy and gameplay review remains outstanding for all sections in
[the section checklist](SECTION-CHECKLIST.md). Deliberate query coverage does
not mean every source building is mapped, correctly classified or surveyed.

## Coverage and arrivals

The [Home Affairs Department's district map](https://www.had.gov.hk/en/18_districts/my_map.htm)
provides the 18-district framework. The following table maps those districts to
our query regions and destination shortcuts. Query rectangles overlap and are
not district polygons; the application groups places geographically for browsing.

| Administrative district | Deliberate regional sources | Example arrival |
| --- | --- | --- |
| Central and Western | Original Central, island-west | Central |
| Wan Chai | island-west, island-east | Wan Chai |
| Eastern | island-east | North Point / Chai Wan |
| Southern | island-west, island-east, outlying-south | Aberdeen / Stanley |
| Yau Tsim Mong | kowloon | Tsim Sha Tsui / Mong Kok |
| Sham Shui Po | kowloon, nt-southwest | Sham Shui Po |
| Kowloon City | kowloon | Former Yamen building, Walled City Park |
| Wong Tai Sin | kowloon, nt-central | Wong Tai Sin Cultural Garden |
| Kwun Tong | kowloon, island-east, sai-kung | Kowloon Bay |
| Islands | lantau, outlying-west, outlying-south | Tung Chung / Cheung Chau / Peng Chau / Lamma / Po Toi |
| Tsuen Wan | nt-southwest | Tsuen Wan Park amphitheatre |
| Kwai Tsing | nt-southwest, kowloon | Tsing Yi Park |
| Tuen Mun | nt-southwest, nt-northwest | Tuen Mun Park |
| Yuen Long | nt-northwest, nt-central | Yuen Long Park / Tin Shui Wai Park |
| North | nt-north, nt-central, nt-northwest | North District Town Hall / Fanling Station Playground |
| Tai Po | nt-central, nt-northeast, nt-north | Tai Po Waterfront Park / Tai Mei Tuk / Tap Mun / Tung Ping Chau |
| Sha Tin | nt-central, nt-northeast | Sha Tin Park / Ma On Shan |
| Sai Kung | sai-kung, nt-northeast, island-east | Sai Kung Waterfront Park / Tseung Kwan O Waterfront Park |

The outlying-island browsing group includes Tap Mun and Tung Ping Chau, which
belong administratively to Tai Po. The labels are geographic browsing groups,
not an alternative district boundary dataset.

New camera centres come from retained OSM features; Po Toi's centre is selected
along a retained mapped footpath near the village. Arrival points are selected
on nearby mapped footways, pedestrian streets, paths or living streets, excluding
explicit private/no-foot access, underground paths and elevated bridges. The
builder checks that each new arrival lies on fully dry triangles of the existing
terrain, including a short walking margin, avoids steep terrain artefacts and
clears building volumes. This is a starting-point check,
not a claim that complete walking routes or footbridges have been reviewed.

`source-scripts/city/destinations.json` contains the editable configuration.
`build_places.py` reproduces `city/places.js` and
`city/data/destinations-provenance.json`. The latter records source feature IDs,
arrival path IDs and WGS84 coordinates. All 43 presets expose latitude and
longitude for the sun, moon and star observer; these are approximate
neighbourhood locations, not a device location or surveyed viewpoint.

## Lantau and village priority pass

The latest priority is Lantau, Mui Wo, Tai O, Cheung Chau and Peng Chau. Six
additional Lantau shortcuts now reach Pui O, Cheung Sha, Tong Fuk, Shui Hau,
Ngong Ping and the Tung Chung valley entrance at the old fort. The existing
`muiwo`, `taio` and `lantau` IDs are preserved, with arrivals regenerated from
retained promenade, square and station geometry respectively.

| Place | Camera reference | Building forms within 800 m |
| --- | --- | ---: |
| Tung Chung | [Station](https://www.openstreetmap.org/way/45725781) | 239 |
| Mui Wo | [Waterfront promenade](https://www.openstreetmap.org/way/552532081) | 149 |
| Tai O | [Yim Tin Square](https://www.openstreetmap.org/way/680293250) | 297 |
| Cheung Chau | [Ferry pier](https://www.openstreetmap.org/way/182368836) | 554 |
| Peng Chau | [Ferry pier](https://www.openstreetmap.org/way/174414610) | 558 |
| Pui O | [Village playground](https://www.openstreetmap.org/way/1422842689) | 227 |
| Cheung Sha | [Sheung Tsuen village office](https://www.openstreetmap.org/way/1347945823) | 157 |
| Tong Fuk | [Village playground](https://www.openstreetmap.org/way/700447115) | 196 |
| Shui Hau | [Public toilet beside village paths](https://www.openstreetmap.org/way/700272388) | 22 |
| Ngong Ping | [Bus terminus public toilet](https://www.openstreetmap.org/way/700634975) | 53 |
| Tung Chung valley | [Fort park](https://www.openstreetmap.org/way/543838006) | 341 |

These are circular proximity counts around each camera reference, not village
boundaries. Every priority arrival has clear forward walking space in the runtime collision
model and fully dry terrain triangles beneath it; the browser walkthrough
verified at least 1.5 m of movement at each. New Lantau arrivals are
7–129 m from the source reference, selected on public paths. Ngong Ping starts at
approximately 449 m terrain elevation, consistent with using its upland location.

**Shui Hau needs a building-completeness review:** only 22 mapped forms lie within
800 m of its reference. The other counts also do not establish completeness.
No local form in these circles has a direct height tag except six in Peng Chau;
other heights use mapped levels or documented estimates. No rendered coastline,
beach, tidal-flat, stilt-house, pier, bridge deck, roof or façade has been certified
accurate by this pass. Those remain priority local reviews, especially at Mui Wo,
Tai O, Peng Chau and Shui Hau, where a 70 m terrain grid cannot resolve small
waterfront features.

## Source provenance and extent

The eight new cached regional responses are:

- `nt-southwest`: Tsuen Wan, Kwai Tsing, southern Tuen Mun and western islets.
- `nt-northwest`: Yuen Long and northern Tuen Mun.
- `nt-central`: Sha Tin, Ma On Shan, Tai Po and adjacent northern new towns.
- `nt-north`: Sheung Shui, Fanling, Sha Tau Kok and the northern edge.
- `nt-northeast`: northeastern country parks, rural settlements and islands.
- `sai-kung`: Sai Kung, Tseung Kwan O and the eastern islands, including Ninepin.
- `outlying-west`: western islands, Cheung Chau and Peng Chau.
- `outlying-south`: Lamma, Po Toi and southern islands.

They supplement four earlier regional responses and the original Central
snapshot. Their exact bounding boxes, base timestamps and SHA-256 hashes of the
uncompressed JSON are recorded in `city/data/manifest.json`; each gzip snapshot
has its exact `.query.txt` alongside it. Source base timestamps range from
**2026-09-06 04:30:21 to 05:52:30 UTC**. Cached rebuilds make no network requests.

New fetches combine a bounded rectangle with the mapped Hong Kong administrative
area. A separately cached [Hong Kong boundary, OSM relation 913110](https://www.openstreetmap.org/relation/913110)
is used for local clipping of roads and parks. Buildings retain their complete
footprint, but their representative point must lie within that boundary. This
avoids carrying neighbouring Shenzhen geometry into the city model and preserves
full building geometry across tile boundaries. The mapped boundary is a source
filter, not an authoritative legal survey.

Sources and the derived OSM database remain **ODbL 1.0**, attributed to
[OpenStreetMap contributors](https://www.openstreetmap.org/copyright). No archival
images under `references/lantau-maps/` were used or modified for this expansion.
No coastline or terrain changes were made.

## Height, terrain and lighting limits

Of the 117,062 forms, **2,243** have a retained tagged height, **56,049** derive
height from tagged levels, and **58,770** use the documented fallback estimate.
The source of each height remains available to the inspector. Even a tagged
height is not independently verified. Roof shapes, equipment and landmark
façades still need local modelling.

The height fallback now recognises explicitly house-like source tags:
**14,801** unmeasured house, detached, semi-detached and terrace forms use an
**8 m estimate**, and **40** explicit bungalows use **4 m**. Mapped heights and
levels always win, and raised/partial forms retain their previous fallback.
The [Lands Department's village-house information](https://www.landsd.gov.hk/en/resources/publicity-materials/purchas.html)
provides context for the scale of low-rise village housing. The 8 m value is a
rounded visual estimate, not a measured height or legal classification.

A separate, tightly scoped Tai O rule changes **252** compact forms to an **8 m
estimate**. The [official 2015 Tai O planning statement](https://www.info.gov.hk/gia/general/201508/21/P201508210487.htm)
identifies the traditional village streets, domestic structures on stilts,
low-rise character and separate modern housing/institutional areas. The
[2014 explanatory statement, section 5.2](https://www.districtcouncils.gov.hk/island/doc/2012_2015/common/dc_meetings_doc/452/IS_2014_007_A3_EN.pdf)
describes village housing as mostly three storeys.

The implemented selector requires an untyped/residential footprint no larger
than **130 m²**, at least half inside a **40 m buffer** of retained OSM geometry
for Tai O Wing On Street, Tai O Tai Ping Street, Tai O Market Street, Kat Hing
Street, Kat Hing Back Street or Shek Tsai Po Street. It also requires containment
within the documented Tai O extent. These buffers are modelling selectors, not
zoning polygons. Explicit non-residential use tags, larger forms, raised parts,
mapped height and mapped floor counts are preserved. The rule does not identify
individual stilt houses, add supports, infer roof shapes or create new footprints.

Every corrected form still has `heightSource: "estimated"`, with a `heightRule`
reference. `height-rules.json` records the exact assumptions and source URLs;
the manifest records these rules, the retained street IDs and affected counts.
**43,677** estimated forms retain the generic fallback. Four focused tests protect
source precedence, footprint size, corridor scope and excluded uses/raised parts.

The existing Lands Department terrain is a **70 m sampled mesh**, reused without
vertical exaggeration. Its land coverage supports the new destinations; the
administrative boundary also includes sea beyond the mesh. Small rocky islands,
reclaimed shoreline, tidal creeks, road decks and artificial platforms may disagree
with that grid. This expansion does not manufacture corrections to those areas.

Every form now has an activity entry. The expanded join uses **14,979 land-use
polygons**, current-use and building tags, parent tags, and the existing documented
research overrides. Classification basis: **81,211** building tags, **1,006**
parent tags, **15,082** land-use inferences, **10** research overrides and
**19,753** fallback estimates. A land-use polygon describes area character,
not a verified tenant or household. Night schedules remain simulated.

## Performance and validation

The complete tile JSON totals **84,019,192 bytes**. It is streamed as needed:
the existing cache holds at most 30 tiles, with at most 24 wanted and two
concurrent fetches. The global activity sidecar is **13,652,756 bytes**; named-form
search metadata is **7,015,699 bytes**, and the minimap overview is **2,105,041
bytes**. These are uncompressed on-disk sizes, not a measured transfer size or a
performance guarantee on mobile hardware.

Validated on 6 September 2026:

- Unique ownership for all 117,062 forms; complete footprints inside each owner's
  expanded tile bounds; finite valid height ranges and matching aggregate counts.
- Source hashes match retained raw responses; manifest extents match the queries.
- All forms have matching activity metadata and retained provenance.
- Every administrative district has a settlement destination with nearby geometry.
- All 43 preset arrivals are on fully dry terrain triangles and clear the runtime
  building collision test. The landscape-only Lantau mountains preset has no
  settlement-density requirement. Five older arrivals (Aberdeen, Stanley, Sham
  Shui Po, Kowloon Bay and Discovery Bay) were repaired along retained public paths
  while keeping their original camera centres and IDs.
- All presets expose valid Hong Kong WGS84 observer coordinates.
- The original Central importer tests continue to pass.

These automated checks establish data and arrival contracts. They do not replace
the section-by-section visual review or full-game feature parity work.

Browser verification and inspected images for the 11 prioritised Lantau/island
locations are recorded in [islands/README.md](islands/README.md). They are a
functional arrival and visual limitation review, not completed section QA.
