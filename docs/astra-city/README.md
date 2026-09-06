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

- 42,892 OSM building forms across Hong Kong Island, urban Kowloon and Lantau.
  Irregular footprints, courtyards, building parts, tagged heights, minimum
  heights and floor counts are retained. Coverage is approximate regional import
  coverage, not a claim that every building or district is complete.
- 90,912 street/path fragments and 668 park fragments in 167 spatial tiles.
  Buildings have one owner tile and retain their complete geometry; roads and
  parks are clipped at tile boundaries. Tree counts depend on the active tiles.
- Existing true-scale terrain across Hong Kong and Lantau, with wholly submerged
  zero-height cells omitted to reduce unnecessary geometry.
- Nearby city sections load on demand, with two concurrent requests, at most 24
  wanted tiles and a 30-tile cache. Distant vegetation, roads and building shadows
  are hidden. Failed downloads expose Retry; walking/flight waits for nearby
  collision data. Superseded loads are cancelled and discarded safely.
- Independent building, street, vegetation and label toggles; global named-building
  search that can fetch an unvisited area; clickable buildings with source and
  height confidence; 15 destinations across three regional navigation tabs.
- An animated character with walking/running, ground-following, building collision,
  courtyard access, chase-camera wall avoidance and first-person view.
- A controllable propeller aircraft with climb/descent, banked turns, boost,
  chase and pilot-eye cameras, terrain clearance and assisted building avoidance.
- Day/golden-hour/night lighting, lit façades, harbour ripples, illustrative
  ferries, a position-tracking minimap and native-resolution PNG postcards.
- Responsive mobile layout, touch movement controls, keyboard controls, visible
  focus states, reduced-motion handling and a recoverable loading error screen.

## Accuracy and scope

This is a geographically grounded **LoD1 city prototype**, not an architectural
or street-level survey. Heights: **1,836 tagged**, **18,742 inferred from levels**,
**22,314 fallback estimates**. Building counts include constituent parts. Every
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
review task. The New Territories and other islands are not yet deliberately
covered by complete regional imports.

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
All geometry tiles together are about 34.4 MB; clients fetch nearby tiles only.
The search catalogue and minimap overview are separate background downloads.

## Section reviews and original-game parity

[SECTION-CHECKLIST.md](SECTION-CHECKLIST.md) breaks all 18 districts into 132
practical review sections, with stable IDs and honest import status. None is
marked fully reviewed solely because an import or browser test passed.

[FEATURE-PARITY.md](FEATURE-PARITY.md) records the user's requirement to restore
**all existing original-game functions**, explicitly including stargazing and
live/manual weather. Those systems are still available in the original game at
`/index.html`; they have not yet been ported into `/city.html`. The city lighting
slider is illustrative and is not a replacement for astronomy or live weather.

## Controls

| Mode | Controls |
| --- | --- |
| Explore | Drag to orbit; scroll to zoom; right-drag to pan; click a building |
| Walk | W/S forward/back; A/D strafe; arrows move/turn; drag to look; Shift run |
| Fly | W/S climb/descend; A/D turn; Shift boost; drag to look |
| General | 1/2/3 choose mode; C changes walk/flight camera; Esc returns to Explore; / searches |

Touch devices have on-screen directional and boost controls. Mode switches and
window focus changes clear held input. Opening the help dialog pauses movement.
District links preserve the selected district in the URL.

## Verification

```sh
npm --prefix 3d-viewer/city ci
npm --prefix 3d-viewer/city test
# Start the static server above before the browser test.
npm --prefix 3d-viewer/city run test:browser
```

The browser suite uses Chrome at its standard macOS path. Set `CHROME_PATH` for
another executable, or run `npx playwright install chromium` inside `3d-viewer/city`
on another platform. `CITY_URL` can point the suite at another local/preview URL.

- Thirteen JavaScript tests: courtyard holes and wall radius; vertical clearance;
  spatial hash boundaries; triangle-matched terrain sampling; full-dataset
  geometry/height validation; IFC height and retained Bank of China identity;
  stale-load disposal, cancellation, cache/concurrency bounds, retry recovery,
  boundary-spanning buildings, complete tile ownership/counts and destination coverage.
- Three Python tests: height units; coordinate conversion control; multipolygon
  courtyard import.
- Browser suite: city load, all layer switches, search and empty results, actor
  dimensions, walking motion/clearance, camera changes, flight climb/boost,
  paused help, lighting, global search into an unvisited region, walking in Tung
  Chung, travel across distant areas, cache bounds, rapid destination changes,
  forced HTTP 503 failure with explicit retry, mobile regional navigation, and
  real PNG export dimensions. It fails on page errors or unexpected local asset
  HTTP errors. Nineteen check groups passed in `verification.json`.
- `verification.json` records the result. PNGs alongside this file are rendered
  browser evidence at the dimensions in their filenames. The postcard is verified
  from its PNG header at 1440 × 1000, not by looking only at a preview canvas.

## Provenance and licences

See `source-scripts/city/README.md` and
`3d-viewer/city/data/manifest.json` for source snapshots, reproducible imports
and ODbL data licence. No archival reference-map image was used or modified.

Existing bundled models are reused with their original attribution:
[Adventurer by Quaternius](https://poly.pizza/m/5EGWBMpuXq), CC0;
[Small Airplane by Vojtěch Balák](https://poly.pizza/m/7cvx6ex-xfL), CC BY 3.0.
Models are scaled/oriented at runtime; their source files remain unchanged.
Code follows the repository licence; the OSM database remains under ODbL.
