# Original golden-hour sky and celestial shadows · HKS-119 / HKS-129

The city used a weak beige tint instead of the original renderer's amber sunset curve. Astra/root extracted the existing `main.js` skyColour function into shared `3d-viewer/sky-colour.js` and both viewers now use it. Twenty-eight sampled original RGB outputs across both palettes are retained and match exactly. The original service-worker shell includes the new dependency.

The city uses the original pale-blue/soft-amber palette. The sun's computed altitude controls the transition rather than a fixed Hong Kong clock hour. Manual Haze0 cannot erase golden/civil twilight: clarity darkens the background only as the sun descends from−6° to−14°. Stargaze retains its separate planetarium presentation. Live/manual weather still modulates the scene through the existing system.

Sky sprites already used the original ephemeris with the selected HKT date/time and the projected observer location. That path is preserved. The directional shadow light previously raised its vertical component to at least0.08, causing long shadows to diverge from the visible low sun. It now uses the actual unit celestial direction. When the sun is below the horizon, the key light follows an above-horizon moon; it switches off if neither body is above the horizon. Ambient city lighting remains. Existing finite shadow-map coverage and resolution still limit distant and very long shadows.

Verification:

```sh
node --test 3d-viewer/city/tests/sky-colour.test.js 3d-viewer/city/tests/sky.test.js 3d-viewer/city/tests/observer.test.js
node 3d-viewer/city/tests/golden-hour-browser.mjs
```

Eleven focused tests pass, including the original colour references, HKT midnight/seasonal event tests and observer-coordinate references. Five actual-city browser groups pass at1440×1000 plus a390px export, zero page errors. Real sun and moon objects match the ephemeris; actual directional-light vectors match the sun or moon; morning/evening shadow matrices and visible cast shadows change; low sun remains below the old clamp; timelapse advances the same shared astronomical state. Exported golden-hour and morning/afternoon images were inspected.

This verifies mapping and reuse, not a replacement high-precision ephemeris. The existing compact solar/lunar algorithm retains its documented approximation limits: checked HKO solar rise/set references within3minutes and lunar references within15minutes. Source references and observer limits remain in [SKY-INTEGRATION.md](../SKY-INTEGRATION.md) and [OBSERVER-PROJECTION.md](../OBSERVER-PROJECTION.md). No surveyed shadow-edge precision is claimed.

[Browser verification](browser/verification.json) · [Golden hour18:06](browser/central-golden-hour.png) · [Low sun18:25](browser/central-low-sun.png) · [Morning shadows](browser/central-morning-shadows.png) · [Afternoon shadows](browser/central-afternoon-shadows.png) · [Mobile](browser/golden-hour-mobile-390.png)
