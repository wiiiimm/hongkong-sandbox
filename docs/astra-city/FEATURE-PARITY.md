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
| Stargazing | Catalogue stars, 24 constellation figures, picking, dated positions, compass/drag/keyboard sky camera | Phone orientation, GPS follow, wider original selection/presentation behaviours |
| Sun/moon and time | Live HKT, custom date/time, circular clock, seasonal dawn/dusk, sun/moon positions, phase and rise/set | Remaining original studio-light and sky presentation options; preserve ephemeris precision limits |
| Shooting stars | Shared original toggle and Calm/Romantic/Apocalypse rate control; daytime, pause and reduced-motion gates verified (HKS-168) | Saved city settings/URL parity tracked with HKS-187 |
| Live weather | HKO condition, temperature/humidity and district rain; timestamped station wind; live/manual separation and stale/error state | Marine observations, radar, satellite, AQHI and remaining regional fields |
| Manual weather | Rain, cloud cover, fog, wind strength/direction, waves, snow and simulated lightning/thunder (HKS-169) | Sky height, tides, typhoon T1–T10, snow accumulation and remaining original controls (HKS-180) |
| Weather and vehicle sound | Original environmental sound and thunder with master volume, gesture unlock, mute and pause lifecycle (HKS-169) | Aircraft/UFO engines and movement/game effects (HKS-177–179) |
| Flight | All seven original models, corrected proportions/materials, propellers and navigation lights; assisted sightseeing | Original flight physics, throttle/reverse where applicable, take-off, landing, speed settings and input support |
| Aircraft cameras | Chase and pilot eye | Original exterior, eye and cockpit camera options, cockpit interiors and controls |
| Walking | Walking/running with collision | Original jump, auto-walk, pointer lock and complete keyboard/touch/camera behaviours |
| UFO/cattle game | UFO model selectable for sightseeing | Hover/reverse, beam, cattle, score and targeting camera |
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
The circular clock now drives the original compact ephemeris. Building occupancy
and weather appearance remain visual simulations, with separate sources and
confidence. Live and manual controls remain explicit.

## Completion gate for parity

The original route can only be retired after an original-versus-city walkthrough
covers every baseline control, saved URL/state, keyboard/touch interaction and
mode combination. Add focused regression checks for imported systems; check
live integrations and offline/error handling separately. Reuse the existing
catalogues, datasets, models and licences rather than silently substituting them.

## Verified environment restoration — 6 September 2026

HKS-168 and HKS-169 reuse the original meteor renderer and audio synthesiser. The original viewer meteor controls, translated labels and URL state pass their compatibility checks. The combined City browser checks cover Sky/Weather controls, live/manual restoration, Stargaze, About pause, reduced motion, trusted sound activation, volume/mute and 390 px/320 px layouts with no browser or shader errors. See [environment evidence](environment-parity/README.md), [meteor provenance](meteors/README.md) and [storm/audio evidence](weather-effects/README.md). The live HKO transition uses explicit deterministic fixtures; it does not prove an observed lightning feed. Other inventory rows remain open.
