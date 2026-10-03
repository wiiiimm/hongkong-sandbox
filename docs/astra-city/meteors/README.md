# Shooting stars restored — HKS-168

GPT-6 Astra, 6 September 2026. The City adapter reuses the original HKS-85 implementation from `main.js` (commit `5777bc9`, PR #214). That implementation is now extracted into `3d-viewer/meteor-trails.js`; the original viewer calls it directly too. No separate meteor renderer, astronomical catalogue or weather service was introduced.

The shared code retains 14 reusable trails of 20 vertices each; their blue-white colour gradient; random local sky azimuth and 20–65° starting altitude; tangent-biased falling arcs; 0.7–1.3 s duration plus the original tail fade; and the exact rate mapping. Rate is numeric 0–1, default 0.18, corresponding to the original 0–100 slider/default 18. The mean spawn gap is `30 * 0.004 ** rate` seconds and the concurrency cap is `max(1, round(14 * rate ** 1.3))`. Zero disables emission. Labels are Off, Calm, Romantic and Apocalypse, with boundaries 0, 0.42 and 0.82. These are illustrative activity settings, not measured meteor-shower rates.

Original `main.js` keeps its controls, translated labels, `sh`/`shr` URL state, sky-luminance gate, radius and `__meteors` debug hook. Its change is restricted to replacing the meteor maths with calls to the shared pool. A reused trail now starts at zero opacity so stale geometry cannot flash during its birth frame.

## City integration contract

```js
import {createCityMeteors, meteorRateLabel, METEOR_DEFAULTS} from './meteors.js';
const meteors = createCityMeteors({scene, camera});
meteors.setOptions({enabled: true, rate: 0.18});
// After sky.update(), using the existing environment update's elapsed seconds:
meteors.update(dt, {starFade: sky.state.starFade, paused, reducedMotion});
// On teardown:
meteors.dispose();
```

Factory and methods are synchronous. The optional factory `random` callback permits deterministic tests. `setOptions` clamps finite rates to 0–1, ignores non-finite rates, clears trails immediately on disable/zero, and reschedules when rate changes. `meteorRateLabel` is exported for the UI; thresholds need not be duplicated. `METEOR_DEFAULTS` is `{enabled: true, rate: 0.18}`.

The adapter adds no UI, media-query, visibility, clock or location listeners. The root environment passes its existing pause/visibility and reduced-motion state. It uses the already computed sky fade, preserving the original dark-sky threshold of 0.55: daylight, clouds and moon wash are handled by the existing sky, while Stargaze retains its clear planetarium presentation. These controls remain independent of live-weather locks.

The pool follows the current camera position in east/+x, up/+y, north/−z axes. It does not rotate with the camera or create a second observer. Radius is `0.98 * min(85000, camera.far * 0.82)`, immediately inside the existing catalogue sphere. Fog is disabled for the City sky while normal depth testing lets nearby buildings and terrain occlude trails.

Trail time advances from frame seconds, independent of the selected astronomical date or time lapse. Pause hides the pool and freezes its clock; resume continues without a backlog. Reduced motion clears and hides trails while preserving the user's enabled/rate choice. Late frame deltas are capped at 0.1 s. Disposal is idempotent, releases every line geometry/material once, removes the group and ignores later updates.

`state` exposes `enabled`, `rate`, `rateLabel`, `gapSeconds`, `concurrencyLimit`, `poolSize`, `active`, `visibleTrails`, cumulative `spawned`, `paused`, `reducedMotion`, `starFade`, `radius`, effect-clock `elapsed`, `running` and `disposed`. `active` can include paused retained trails; `visibleTrails` is zero when the pool is hidden. Reducing the rate allows existing trails to finish naturally, matching the original behaviour; the new cap applies to births.

## Validation

```sh
node --test 3d-viewer/city/tests/meteors.test.js
node --check 3d-viewer/main.js
```

Seven deterministic tests cover original defaults/rates/labels, north/up orientation, spherical geometry and fading, a 3,600-frame high-rate simulation with stable object/buffer identities, darkness/off gates, camera relocation and clipping radius, pause/reduced-motion behaviour, and idempotent cleanup. The tests use the real shared Three.js effect without a DOM or GPU.

The original viewer browser checks pass; see `original-browser/README.md` and `original-browser/verification.json` for the retained first-pass fixture correction, targeted final checks and visually inspected screenshot. Curie's combined actual City UI verification also passed: `docs/astra-city/environment-parity/verification.json` records defaults/rate 18→100, off/on, daylight/night suppression, Stargaze, reduced motion, About pause, and reachable panels at 390 px and 320 px, with no browser/shader errors. No historical reference maps or external imagery are used for this effect.
