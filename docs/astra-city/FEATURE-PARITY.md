# Original-game feature parity is a required destination

User requirement, 6 September 2026: the expanded city must eventually restore **all
existing functions of the original game**, explicitly including **stargazing** and
**live and manually controlled weather**. The new city route is an interim view,
not a replacement with a permanently reduced feature set. Expansion of geography
does not satisfy this separate requirement.

Baseline: original `3d-viewer/main.js` and `index.html` at `5777bc9`.
They remain available at `/index.html`. Before final replacement, re-audit the
original source and UI, including later upstream changes; this inventory is a
starting point, not permission to drop an unlisted feature.

| Original capability | City status | Required integration |
| --- | --- | --- |
| Hong Kong/Lantau and DTM/SRTM source choice | One original DTM grid | All four source choices and their georeferences |
| Terrain surfaces | One styled surface | Shaded, elevation, matte, solid, wireframe, B50K, OSM and satellite |
| Terrain controls | True-scale city | Mesh density/colour, vertical exaggeration, map rotation/background, auto-spin; keep city layers aligned |
| Map overlays | Buildings, streets, trees and labels | Contours, trails, hydro, coast, boundaries, cliffs, peak/landmark labels and overlay height |
| Stargazing | Pending | Star catalogue, constellation selection/figures, true sky position, orientation tracking, GPS and sky clock |
| Sun/moon and time | Circular 24-hour clock, exact time, use-based sleep cycle and time lapse | Live HKT, custom date/time, actual sun/moon positions and rise/set/illumination |
| Shooting stars | Pending | Existing toggle and calm-to-apocalypse rate control |
| Live weather | Pending | Existing HKO station/wind/marine observations, rain radar, satellite view and AQHI; preserve live/manual distinction |
| Manual weather | Pending | Rain, cloud, fog, lightning/thunder rates, wind speed/direction, waves, snow, sky height, tide and typhoon T1–T10 |
| Weather and vehicle sound | Pending | Master volume, environmental sound, thunder, aircraft/UFO engines and game effects |
| Flight | Assisted prop-plane sightseeing | Full aircraft selection, original flight physics, throttle/reverse where applicable, take-off, landing, speed settings and input support |
| Aircraft cameras | Chase and pilot eye | Original exterior, eye and cockpit camera options, cockpit interiors and controls |
| Walking | Walking/running with collision | Original jump, auto-walk, pointer lock and complete keyboard/touch/camera behaviours |
| UFO/cattle game | Pending | UFO, hover/reverse, beam, cattle, score and targeting camera |
| Matrix and neon themes | Pending | Both themes available across their supported modes |
| GPX trails | Pending | Import/drop, styling, visibility/removal, playback, start/end, elevation profiles and statistics |
| Geolocation | Pending | Locate, follow, compass, position marker, relocate and walk-from-location |
| English/Traditional Chinese | Place names only | Full EN-HK/ZH-HK strings, locale routing and metadata |
| View sharing | District URL only | Original state URL, share/copy, embed and restoration of settings |
| Mobile/PWA | Responsive city and touch | Fullscreen, install/standalone, service-worker/offline behaviour, gestures and orientation |
| Accessibility/help/credits | City-specific subset | Complete help, all original controls, credits, source/licence notices and preferences |

## Integration boundary

City data and streaming are kept in their own modules, with one metre-based world
coordinate system, per-layer visibility, shared light uniforms and a collision
adapter. The original sky/weather/gameplay systems should be ported or extracted
behind these boundaries, retaining source provenance and existing user settings.
Do not replace the original astronomy with the illustrative city clock, or live HKO
weather with illustrative effects. Live and manual controls must remain explicit.

## Completion gate for parity

The original route can only be retired after an original-versus-city walkthrough
covers every baseline control, saved URL/state, keyboard/touch interaction and
mode combination. Add focused regression checks for imported systems; check
live integrations and offline/error handling separately. Reuse the existing
catalogues, datasets, models and licences rather than silently substituting them.
