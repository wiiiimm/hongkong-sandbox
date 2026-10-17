# City sky and Hong Kong civil time

Implemented by GPT-6 Astra in the isolated `codex/astra-hong-kong-city` worktree. The original viewer and its shared catalogue/astronomy source files remain unchanged. No Lantau reference maps were used for this sky layer.

The city renderer now has an independent sky module with the existing project's 1,573 Yale Bright Star Catalogue stars, 24 constellation figures, the Sun and a phase-shaded Moon. The date and time are absolute instants interpreted in Hong Kong civil time (UTC+08:00), independently of the device timezone. Solar altitude drives seasonal daylight/twilight; office, residential and retail occupancy schedules still follow local civil time.

## Integration API

```js
import {createSky} from './sky.js';
import {getSkyState,hktParts,dateFromHKT} from './sky-time.js';

const sky=await createSky({scene,camera});
const instant=dateFromHKT('2026-09-06',21.5); // 21:30 HKT
const celestial=getSkyState(instant,22.3,114.17);

// Every frame, AFTER positioning the camera. Star/ephemeris coordinates cache
// for five simulated seconds; the celestial sphere follows the camera every frame.
sky.update({date:instant,lat:22.3,lon:114.17,stargazing:false,cloudCover:.2});
sky.setConstellations(true);
const picked=sky.pick({x:0,y:0}); // normalised device coordinates (-1..1)
sky.setSelectedConstellation('Lyr');
// sky.dispose() removes its group and disposes its GPU resources.
```

`hktParts(Date)` returns `{date:'YYYY-MM-DD', time:'HH:MM', hour, hours, minutes, seconds}`. `hour` includes fractional minutes/seconds/milliseconds. Invalid instants throw `RangeError`.

`dateFromHKT(dateString, hour=12)` returns a `Date`, or `null` for invalid civil dates or non-finite hours. It rejects dates such as 30 February. Finite hours outside 0–24 deliberately carry the civil date backwards/forwards, so a time lapse can cross midnight and New Year without repeating the previous day's sky.

`getSkyState(Date, lat=22.3, lon=114.17)` returns:

- `date` (ISO instant), `hkt`, `lat`, `lon`.
- `sun` and `moon`: `direction:{x,y,z}` unit vectors, `altitude` and `azimuth` in radians, `altitudeDeg`, and `bearing` in compass degrees.
- `moon` also has `fraction` (0 new to 1 full), `phase` (0 new, .25 first quarter, .5 full, .75 last quarter), `angle`, and `distance` in kilometres.
- `sunrise`, `sunset`, `solarNoon`, `moonrise`, `moonset`: absolute `Date` instances for the selected **HKT civil day**. A missing rise/set is `null`.
- `night`, `golden`, `starVisibility`: bounded presentation coefficients, derived from solar altitude, plus a `phase` string distinguishing daylight and civil/nautical/astronomical twilight.

City coordinates are east **+x**, up **+y**, south **+z**. The inherited astronomy library's south/west azimuth convention is converted explicitly. Sunrise/sunset calculations use the selected day's local noon; lunar rise/set uses its local midnight. This prevents the midnight-in-Hong-Kong / previous-date-in-UTC error.

`sky.state` exposes `astronomy`, `catalogueStars`, `constellationCount`, `visibleStars`, `starFade`, `coordinateUpdates`, `stargazing`, `cloudCover`, `limitingMagnitude`, `constellations` (toggle), and `selected` (`{iau,en,zh}` or `null`). `pick()` returns `{hr,magnitude,altitudeDeg,constellations:[{iau,en,zh}]}`, and traces the nearest visible star's first constellation. It returns `null` on an empty-sky pick. The caller owns its label/card UI and should prefer a foreground world-object hit over a sky pick where applicable.

## Presentation and performance

- Sky geometry remains centred on the camera, at 82% of its far clipping distance (capped at 85 km). Observer translation produces no false celestial parallax.
- The custom shaders support the city's logarithmic depth buffer. They ignore scene fog but retain depth tests, so opaque terrain/buildings occlude stars correctly. Horizon fades reject stars below ground level.
- The Sun's core is approximately its real 0.53° angular diameter, surrounded by a soft display halo. The Moon's angular diameter follows the inherited distance estimate and a 1,737.4 km lunar radius. Its terminator faces the calculated Sun direction in the local sky; phase and limb orientation update when the date changes.
- Default city presentation limits stars around magnitude 2.8; `stargazing:true` raises this to 5.3 and presents a clear planetarium sky regardless of daytime/cloud settings. It does not mutate live/manual weather state. The optional `limitingMagnitude` parameter accepts 1–6 for future controls.
- In normal exploration, stars fade through astronomical twilight, with extra attenuation from cloud cover and a bright Moon. The city light-pollution level and cloud attenuation are illustrative presentation curves, not measured visibility predictions.
- Only catalogue stars are rendered: no invented geographic sky positions or random replacement figures. The catalogue and figure buffers rebuild at most once per five simulated seconds/location change; camera anchoring and phase orientation remain responsive each frame.

## Sources and precision

Reused local sources:

1. `3d-viewer/vendor/astro.js`: the project's compact Meeus/SunCalc-family solar/lunar ephemeris, and J2000 fixed-star horizontal coordinate reduction.
2. `3d-viewer/data/hk-sky.json`: the existing BSC5 catalogue and 24 curated constellation figures. Original generator, source notes and upstream links are in `source-scripts/hk-sky/build_hk_sky.mjs`; upstream data are [CDS V/50 (Yale BSC5)](https://cdsarc.cds.unistra.fr/ftp/V/50/), [CDS I/239 (Hipparcos)](https://cdsarc.cds.unistra.fr/ftp/I/239/), and the pinned [Stellarium v0.20.4 western figures](https://github.com/Stellarium/stellarium/tree/v0.20.4/skycultures/western). The existing catalogue's provenance/licence notes remain intact.

Independent event references checked on 6 September 2026:

| HKT date | HKO sunrise / sunset | HKO moonrise / moonset |
| --- | --- | --- |
| 21 June 2026 | 05:40 / 19:10 | 11:46 / no moonset |
| 6 September 2026 | 06:07 / 18:36 | 00:40 / 14:53 |
| 21 December 2026 | 06:58 / 17:44 | 14:51 / 03:39 |

References: Hong Kong Observatory Almanac 2026 [June page](https://www.hko.gov.hk/en/gts/astron2026/files/2026cal06.pdf), [September page](https://www.hko.gov.hk/en/gts/astron2026/files/2026cal09.pdf), [December page](https://www.hko.gov.hk/en/gts/astron2026/files/2026cal12.pdf), and [index](https://www.hko.gov.hk/en/gts/astron2026/almanac2026_index.htm). June/December source pages were visually inspected; September values were extracted from HKO's indexed almanac table. No HKO tables are fetched at runtime.

The automated reference checks allow **3 minutes for solar** events and **15 minutes for lunar** events. The lunar model is deliberately compact and is not accurate enough for eclipse prediction or precise observation planning. Event times assume an unobstructed horizon; Hong Kong's hills/buildings and varying refraction alter observed rise/set. Fixed J2000 stars omit precession/proper motion, retaining the existing catalogue's roughly sub-degree present-day positional limitation. Moon surface markings are an illustrative procedural texture, not a surveyed lunar map. Hong Kong's historical daylight-saving rules are not modelled: the date controls use current UTC+08:00 civil time throughout.

## Verification

```sh
node --test 3d-viewer/city/tests/sky.test.js
node 3d-viewer/city/tests/sky-browser.mjs
```

Five pure tests cover HKT/date rollover and validation, cardinal axes, seasonal rise/set against HKO, seasonal daylight and lunar phases, catalogue integrity and Polaris above north.

The Chrome/WebGL fixture verifies visible stars under dense scene fog, logarithmic-depth occlusion by foreground geometry, zero camera-translation parallax, catalogue star/constellation picking, coordinate caching, faint-star suppression in city mode, daylight/cloud fading, constellation arcs, full/new/quarter lunar brightness, and resource removal. Results are saved in `sky-verification.json`.

This milestone restores the core catalogue/constellation sky rendering. Original meteor controls, procedural deep field/Milky Way, phone orientation, GPS tracking, constellation walk automation, and the rest of the original game's feature set remain separate parity work. The original viewer remains available while those are migrated.
