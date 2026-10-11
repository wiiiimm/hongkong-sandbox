# Original weather effects restored to the Astra city — HKS-169

The city adapter reuses `3d-viewer/audio.js` directly. Rain, wind, wave noise, fog muffling, master gain, delayed thunder rolls and the close-strike crack remain the original HKS-2 synthesiser, without samples or replacement sound assets. The forked lightning channel in `city/weather-effects.js` adapts `main.js`'s HKS-13 `spawnBolt`/`jag` algorithm to the city's HK1980 metre coordinates and terrain sampler.

## Interface

```js
const effects = createWeatherEffects({
  scene, camera, terrainHeight: (x, z) => sampler.height(x, z)
});
effects.setManual({lightning: true, thunderRate: 0.4});
// Call synchronously from the actual sound button's trusted click/key event.
const sound = await effects.setSound(true, event);
effects.setMasterVolume(0.6);
const transient = effects.update(dt, {
  settings: weather.state.settings, mode: weather.state.mode,
  paused, reducedMotion, suspended: stargazing
});
ambient.intensity = ordinaryWeatherAmbient + transient.ambientBoost;
// Optional manual test/strike control; respects the rate/mode/suspension gates.
effects.triggerStrike();
await effects.dispose();
```

Defaults: lightning off; thunder rate 0.4; sound off; master volume 0.6. Rate and volume accept finite numbers clamped to 0–1. `state` exposes the preserved manual controls, current weather mode, active flag, flash, strike count, last strike (explicitly **Manual storm simulation**) and sound state. `setSound` returns the sound-state object; its fields are `supported`, `enabled`, `unlocked`, `audible`, `masterVolume`, `status` and `error`. Status is `muted`, `gesture-required`, `starting`, `playing`, `suspended`, `unsupported`, `error` or `disposed`.

## Behaviour and reuse boundaries

- Lightning and thunder are manual simulation only. Live weather uses the existing observed/estimated rain, wind, waves and fog for ambience; it does **not** infer a lightning observation from an icon or warning. The manual lightning choice and rate return when switching back to manual. HKO regional past-hour lightning ingestion (the original HKS-68 live path) is still pending.
- The original recursive fork shape and additive line rendering are retained. The main channel ends at sampled city terrain, with a local point glow and an additive ambient contribution returned to the environment controller. There is no full-screen flash or direct mutation of the shared sun/ambient lights.
- The original quadratic rate response is converted to elapsed seconds. Strikes have a four-second minimum separation plus a random interval; a stalled frame cannot trigger a backlog. Visual decay lasts 0.28 seconds. The interval is a visual pacing approximation, not a measurement of a storm.
- A single line mesh and point light are reused; only the small channel buffer is replaced per close strike. The point light is excluded while lightning is inactive, so clear weather does not add a point-light calculation to every building. No shadow maps, territory-sized particles or extra asset downloads are introduced.
- Reduced motion suppresses the bolt, local glow and ambient flash completely. Weather sound remains the user's separate choice. Pause, Stargaze, tab hiding, mute and disposal immediately cancel queued thunder; pause/Stargaze/hidden tabs suspend the context while preserving sound preference.
- The audio adapter never creates a context on load, during a timer or for a synthetic click. The first enable requires the sound control's trusted event with active user activation. Resume errors are exposed for a gesture retry. Once unlocked, returning to a visible, unpaused city resumes the existing context.
- The original audio module gains optional status/suspend/cancel/dispose exports. Existing exports and synthesis stay intact; original callers can ignore the new return promises without unhandled resume rejections. Context disposal also closes original engine/UFO voices if present. City aircraft engine/UFO/game-event audio is outside this weather restoration.
- This adapter assumes one city environment owns the original audio module instance. It does not claim restoration of storm-signal presets, live lightning fields, terrain snow accumulation or every original game effect.

## Verification

Run from the Astra worktree:

```sh
node --test 3d-viewer/city/tests/weather-effects.test.js
node 3d-viewer/city/tests/weather-effects-browser.mjs
```

The six focused tests cover original audio compatibility and envelopes, trusted/active gesture gating, hidden-tab and pause/Stargaze behaviour, mute, failed-resume recovery, late-resume disposal races, exact terrain endpoints, bounded fork geometry, cadence, live/manual restoration and reduced-motion suppression.

The single-Chrome render fixture uses `logarithmicDepthBuffer: true` and a 100,000 m camera far plane. It measures actual original-synthesiser output through a test-only analyser; confirms queued thunder, context suspend/resume/closure; and compares rendered pixels. A close strike adds one draw call; the retained deterministic fork has 52 vertices. Reduced-motion output is pixel-identical to the baseline. Detailed metrics are in `browser-verification.json`; `storm-before-800x600.png` and `storm-strike-800x600.png` are fixture evidence, not a claim of final city UI verification. Root performs the combined city controls check after integrating weather and meteors.

Produced by the Astra weather subagent. No map imagery or external audio assets were used; provenance is the repository's original `audio.js` and `main.js` HKS-2/HKS-13 implementations.
