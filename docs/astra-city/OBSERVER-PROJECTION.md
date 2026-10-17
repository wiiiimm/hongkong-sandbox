# Simulated observer coordinates

The city sky can follow the current free-flight, walking or orbit focus instead of staying fixed to the selected neighbourhood. `city/observer.js` converts the terrain's local metre coordinates to WGS 84 without a runtime projection library or network request. These are coordinates of the **simulated observer**, not live device GPS.

```js
import {worldToWgs84,OBSERVER_BOUNDS} from './observer.js';
const observer=worldToWgs84(focus.x,focus.z); // {lat,lon}, or null
```

Finite numeric coordinates inside the inclusive terrain rectangle return `{lat,lon}` in degrees. The function returns `null` for non-finite/non-numeric inputs or points outside that measured extent. The caller can retain its last valid observer or fall back to an explicitly approximate neighbourhood preset when an orbit pan leaves the terrain. It must not silently describe extrapolated positions as accurate.

The world origin is EPSG:2326 easting **834500 m**, northing **816500 m**. Thus `E=x+834500` and `N=816500-z`. Positive world x is east; negative world z is north. The current terrain rectangle is:

- x: **−34467.5 to 29162.5 m**
- z: **−31467.5 to 16412.5 m**

A reproducible **14 × 11** grid samples the same `pyproj.Transformer.from_crs(2326,4326,always_xy=True)` operation used by the existing map importer. Runtime bilinear interpolation uses this committed 5,620-byte table. No guessed metres-per-degree conversion is used.

Generation and validation:

```sh
/private/tmp/astra-city-venv/bin/python source-scripts/city/build_observer.py
node --test 3d-viewer/city/tests/observer.test.js 3d-viewer/city/tests/stargaze-controls.test.js
```

The generator reads the current terrain's dimensions, origin and georeference; it then checks a 5 × 5 lattice within every grid cell and 20,000 additional deterministic random points against direct PROJ transformations. A maximum interpolation error above 0.25 m fails generation. The recorded run tested **23,250 points**, with **0.1981 m maximum** and **0.1262 m mean** error. Those figures measure interpolation error **relative to PROJ**, not physical survey accuracy. The selected `Hong Kong 1980 to WGS 84 (1)` datum operation itself reports **1 m accuracy**. Runtime precision does not improve the underlying terrain, building footprints or datum accuracy.

The recorded toolchain was pyproj 3.8.0 / PROJ 9.8.1. Full CRS operation metadata, terrain bounds, validation statistics and the grid SHA-256 are in `observer-projection-verification.json`. The grid is generated into `city/observer-grid.js`, and independent direct-transform samples into `city/tests/observer-reference.json`. Tests also detect a stale grid after a terrain extent/origin change and cross-check current neighbourhood presets.

For efficient integration, update the astronomical observer at a modest spatial or time interval (for example, after roughly 100 m of movement or once per second). Passing a newly changed floating-point coordinate every animation frame needlessly invalidates rise/set and star-position caches. The interpolation itself is inexpensive and does not allocate large buffers.

The accompanying stargazing control fix retains the first active pointer and ignores unrelated pointer-up, capture-loss and cancellation events. It prevents a second touch from replacing or cancelling a drag. It does not add pinch zoom or the original game's two-finger geographic panning; those remain separate interaction work.
