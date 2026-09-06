# Astra city explorer

A first playable district for Hong Kong Sandbox, created by **GPT-6 Astra** on
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

- 9,743 OSM building forms across Central, Sheung Wan, Admiralty, Wan Chai and
  the Kowloon waterfront. Irregular footprints, courtyards, building parts,
  tagged heights, minimum heights and floor counts are retained.
- 20,443 street/path segments, 135 park polygons and 6,181 illustrative trees
  distributed within existing mapped vegetation or parks, avoiding buildings.
- True-scale terrain across Hong Kong and Lantau. The full terrain is retained;
  detailed building coverage is limited to the first district.
- Independent building, street, vegetation and label toggles; named-building
  search; clickable buildings showing source and height confidence; four
  neighbourhood views; orbit, overhead and north-facing views.
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
or street-level survey. Heights: **688 tagged**, **5,151 inferred from levels**,
**3,904 fallback estimates**. Building counts include constituent parts. Every
building's inspector identifies its height source. Roof shapes, building interiors,
façade details, road widths, bridge clearances and ferry motion are simplified.
A few named structures share several separately mapped parts.

The terrain is the project's existing **70 m sampled mesh**, derived from the
Lands Department source. It is not a newly downloaded 5 m street surface.
Shorelines, slopes and very small pedestrian routes inherit this resolution.
Trees and façade windows are an illustrative presentation layer. Lantau has
terrain and navigation but no new building import in this first district.

Walking is constrained to land and clear building space; raised footbridges are
visual geometry and are not a complete multi-level walkable navigation network.
Flight is assisted sightseeing: it maintains terrain clearance and lifts clear of
buildings on contact. There is no take-off/landing or damage simulation. Building
collision remains active when the visual building layer is hidden.

The project data and raw snapshots are deliberately bundled for reproducibility.
The current scene is roughly 2.4 million triangles and about 30 main-pass draw calls
in the default desktop view (shadows add GPU work). Buildings are merged by
material and trees are instanced. Future expansion should introduce spatial tiles
and distance-based detail rather than loading every new district at once.

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

- Six JavaScript tests: courtyard holes and wall radius; vertical clearance;
  spatial hash boundaries; triangle-matched terrain sampling; full-dataset
  geometry/height validation; IFC height and retained Bank of China identity.
- Three Python tests: height units; coordinate conversion control; multipolygon
  courtyard import.
- Browser suite: city load, all layer switches, search and empty results, actor
  dimensions, walking motion/clearance, camera changes, flight climb/boost,
  paused help, lighting, district navigation, mobile layout/panel, and real PNG
  export dimensions. It fails on page errors or local asset HTTP errors.
- `verification.json` records the result. PNGs alongside this file are rendered
  browser evidence at the dimensions in their filenames. The postcard is verified
  from its PNG header at 1440 × 1000, not by looking only at a preview canvas.

## Provenance and licences

See `source-scripts/city/README.md` and
`3d-viewer/city/data/provenance.json` for the source snapshot, reproducible import
and ODbL data licence. No archival reference-map image was used or modified.

Existing bundled models are reused with their original attribution:
[Adventurer by Quaternius](https://poly.pizza/m/5EGWBMpuXq), CC0;
[Small Airplane by Vojtěch Balák](https://poly.pizza/m/7cvx6ex-xfL), CC BY 3.0.
Models are scaled/oriented at runtime; their source files remain unchanged.
Code follows the repository licence; the OSM database remains under ODbL.
