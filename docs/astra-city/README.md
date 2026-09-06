# Astra city explorer

A streaming city prototype for Hong Kong Sandbox, created by **GPT-6 Astra** on
`codex/astra-hong-kong-city`, based on `main` commit `5777bc9`.
The other model's checkout and the main checkout are untouched.

Open **`/city.html`**. The original application stays at `/index.html`, with a
link to the city experience. All runtime modules and map assets are local static
files, and the existing Vercel static-hosting setup supports this route.
There is no application build, map API key or live Overpass dependency.
Google Fonts is optional and has system-font fallbacks.

```sh
# Run from this worktree, using a distinct port for comparison.
python3 -m http.server 4176 --bind 127.0.0.1 --directory 3d-viewer
# http://127.0.0.1:4176/city.html
```

## What is implemented

- 117,062 OSM building forms across Hong Kong, including the New Territories and outlying islands.
  Irregular footprints, courtyards, building parts, tagged heights, minimum
  heights and floor counts are retained. Coverage is approximate regional import
  coverage, not a claim that every building or district is complete.
- 190,222 street/path fragments and 1,294 park fragments in 449 spatial tiles.
  Buildings have one owner tile and retain their complete geometry; roads and
  parks are clipped at tile boundaries. Tree counts depend on the active tiles.
- Existing true-scale terrain across Hong Kong and Lantau, with wholly submerged
  zero-height cells omitted to reduce unnecessary geometry.
- Nearby city sections load on demand, with two concurrent requests, at most 24
  wanted tiles and a 30-tile cache. Preset camera transitions keep loading their
  destination rather than replacing it with intermediate locations. Distant vegetation, roads and building shadows
  are hidden. Failed downloads expose Retry; walking/flight waits for nearby
  collision data. Superseded loads are cancelled and discarded safely.
- Independent building, street, vegetation and label toggles; global named-building
  search that can fetch an unvisited area; clickable buildings with source and
  height confidence; 43 destinations across seven regional navigation groups.
- An animated character with walking/running, ground-following, building collision,
  courtyard access, chase-camera wall avoidance and first-person view.
- Seven selectable original aircraft: light prop plane, Betsy/DC-3, Boeing 747-400,
  Boeing 777-300ER, Airbus A330-300, Airbus A350-1000 and the fictional UFO.
  Corrected orientation, calibrated dimensions, improved materials, propellers,
  navigation lights and efficient material batches support climb/descent, banked
  turns, boost, chase/pilot-eye cameras and assisted terrain/building avoidance.
  See [the aircraft review](AIRCRAFT-REVIEW.md) for model-by-model changes and limits.
- A full 24-hour lighting cycle: individual warm/cool windows on every building,
  staggered overnight sleep patterns, a 4 am minimum with some lights remaining,
  early risers and dawn. Homes peak at 10 pm, sleep from 11 pm; offices leave
  from 6 pm and shops close from 9–11 pm. Midnight now resembles the previous
  4 am occupancy, with only scattered exceptions remaining at the new 4 am minimum. Street lighting persists through the night. Evening,
  midnight and 4 am shortcuts plus optional time lapse (one hour / eight seconds).
  A circular full-day clock supports drag/touch, keyboard and exact minute entry.
  Mapped building/land uses and researched mixed-use corrections distinguish
  home, office, retail and overnight schedules. The dated Sun/Moon model controls
  seasonal dawn and dusk; live HKT and a custom date are available. Distant lights shimmer subtly;
  nearby windows stay steady, with an off switch and reduced-motion support.
- Stargazing with 1,573 catalogue stars, 24 constellation figures, star selection,
  compass directions, drag/keyboard look and the original compact ephemeris.
- Manual rain, clouds, fog, wind, waves and snow; live HKO temperature, humidity,
  conditions and district rainfall, plus timestamped station wind via DATA.GOV.HK.
  Observations and visual estimates are distinct; network failures remain visible.
- Harbour ripples, illustrative ferries, a position-tracking minimap and
  native-resolution PNG postcards.
- Responsive mobile layout, touch movement controls, keyboard controls, visible
  focus states, reduced-motion handling and a recoverable loading error screen.

## Accuracy and scope

This is a geographically grounded **LoD1 city prototype**, not an architectural
or street-level survey. Heights: **2,243 tagged**, **56,049 inferred from levels**,
**58,770 fallback estimates**, including 14,801 explicit house-like forms at an
8 m estimate, 40 bungalows at 4 m and 252 compact Tai O village forms at 8 m.
The source-based rules retain measured/tagged precedence and identify their
assumptions in the manifest. Building counts include constituent parts. Every
building's inspector identifies its height source. Roof shapes, building interiors,
façade details, road widths, bridge clearances and ferry motion are simplified.
A few named structures share several separately mapped parts.

The terrain is the project's existing **70 m sampled mesh**, derived from the
Lands Department source. It is not a newly downloaded 5 m street surface.
Shorelines, slopes and very small pedestrian routes inherit this resolution.
Trees and façade windows are an illustrative presentation layer. Lantau now has
building imports, including Tung Chung, Discovery Bay, Mui Wo and Tai O. Recent
reclamation, fine tidal creeks and small paths may disagree with the older/coarser
terrain. Correcting shorelines and building-ground alignment remains a per-section
review task. All 18 districts now have deliberate source-query coverage and settlement
destinations. This does not establish that every individual building is mapped.
See [territory coverage](GEOGRAPHY-COVERAGE.md) and the priority-island review
([islands/README.md](islands/README.md)) for known local gaps.

Walking is constrained to land and clear building space; raised footbridges are
visual geometry and are not a complete multi-level walkable navigation network.
Flight is assisted sightseeing: it maintains terrain clearance and lifts clear of
buildings on contact. There is no take-off/landing or damage simulation. Building
collision remains active when the visual building layer is hidden.

The project data and raw snapshots are deliberately bundled for reproducibility.
The default desktop Central view measured roughly 1.55 million rendered triangles
and 145 renderer calls after this expansion, with about 16,000 active building
forms. These are scene observations, not frame-rate benchmarks, and vary by camera
and loaded sections. Buildings are merged by material per tile; trees are instanced.
All geometry tiles together are about 84.0 MB; clients fetch nearby tiles only.
The shared activity metadata adds 13.7 MB before HTTP compression.
The search catalogue and minimap overview are separate background downloads.

## Section reviews and original-game parity

[SECTION-CHECKLIST.md](SECTION-CHECKLIST.md) breaks all 18 districts into 132
practical review sections, with stable IDs and honest import status. None is
marked fully reviewed solely because an import or browser test passed.

[FEATURE-PARITY.md](FEATURE-PARITY.md) records the user's requirement to restore
**all existing original-game functions**, explicitly including stargazing and
live/manual weather. Their core controls now work in `/city.html`, together
with the original aircraft collection. Remaining gameplay, sound, overlay,
mobile and other functions stay tracked in the parity inventory; the original
game remains available at `/index.html`.

## Controls

| Mode | Controls |
| --- | --- |
| Explore | Drag to orbit; scroll to zoom; right-drag to pan; click a building |
| Walk | W/S forward/back; A/D strafe; arrows move/turn; drag to look; Shift run |
| Fly | Choose an aircraft; W/S climb/descend; A/D turn; Shift boost; drag to look |
| Stargaze | Drag or arrows to look; compass buttons; scroll to zoom; tap a star |
| General | 1/2/3/4 choose mode; C changes walk/flight camera; Esc returns to Explore; / searches |

Touch devices have on-screen directional and boost controls. Mode switches and
window focus changes clear held input. Opening the help dialog pauses movement.
District links preserve the selected district in the URL.

## Verification

```sh
npm --prefix 3d-viewer/city ci
npm --prefix 3d-viewer/city test
# Start the static server above before the browser test.
npm --prefix 3d-viewer/city run test:browser
npm --prefix 3d-viewer/city run test:night
npm --prefix 3d-viewer/city run test:clock
npm --prefix 3d-viewer/city run test:lighting-render
npm --prefix 3d-viewer/city run test:integration
npm --prefix 3d-viewer/city run test:sky
npm --prefix 3d-viewer/city run test:weather
npm --prefix 3d-viewer/city run test:aircraft
npm --prefix 3d-viewer/city run test:aircraft-city
npm --prefix 3d-viewer/city run test:islands
```

The browser suite uses Chrome at its standard macOS path. Set `CHROME_PATH` for
another executable, or run `npx playwright install chromium` inside `3d-viewer/city`
on another platform. `CITY_URL` can point the suite at another local/preview URL.

- JavaScript unit/data tests: courtyard holes and wall radius; vertical clearance;
  spatial hash boundaries; triangle-matched terrain sampling; full-dataset
  geometry/height validation; IFC height and retained Bank of China identity;
  stale-load disposal, cancellation, cache/concurrency bounds, retry recovery,
  boundary-spanning buildings, complete tile ownership/counts, destination coverage;
  continuous midnight / 4 am schedules, retained overnight activity, stable profiles
  and clock formatting.
- Python import/height-rule tests: height units; coordinate conversion control; multipolygon
  courtyard import.
- Browser suite: city load, all layer switches, search and empty results, actor
  dimensions, walking motion/clearance, camera changes, flight climb/boost,
  paused help, lighting, global search into an unvisited region, walking in Tung
  Chung, travel across distant areas, cache bounds, rapid destination changes,
  forced HTTP 503 failure with explicit retry, mobile regional navigation, and
  real PNG export dimensions. It fails on page errors or unexpected local asset
  HTTP errors. Results are recorded in `verification.json`.
- The focused night browser suite checks actual scene brightness and bright pixels
  through 20:00 → 22:00 → 23:00 → midnight → 02:00 → 04:00 → dawn, new tile lighting, walking,
  time-lapse pause/rollover, mobile controls and a native-size night postcard.
  See [night-cycle/README.md](night-cycle/README.md) for the simulation policy and
  [night-cycle/verification.json](night-cycle/verification.json) for results.
- `verification.json` records the general browser result. PNGs alongside this file are rendered
  browser evidence at the dimensions in their filenames. The postcard is verified
  from its PNG header at 1440 × 1000, not by looking only at a preview canvas.

## Provenance and licences

See `source-scripts/city/README.md` and
`3d-viewer/city/data/manifest.json` for source snapshots, reproducible imports
and ODbL data licence. No archival reference-map image was used or modified.

The character reuses [Adventurer by Quaternius](https://poly.pizza/m/5EGWBMpuXq),
CC0. All seven aircraft authors, source links and licences are recorded in
[AIRCRAFT-REVIEW.md](AIRCRAFT-REVIEW.md) and the in-app credits. Betsy and A330
retain their non-commercial/share-alike asset restrictions and existing `nc/`
locations. Runtime improvements do not relicense the original models.
Source model files remain unchanged.
Code follows the repository licence; the OSM database remains under ODbL.
