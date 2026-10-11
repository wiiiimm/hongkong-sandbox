# Original viewer water compatibility

`verification.json` is the final passing run of `3d-viewer/city/tests/tides-original-browser.mjs`. Both PNGs were inspected at their saved 1440×1000 dimensions. The original tide and weather controls are legible, the manual wave surface is visible, and the live HUD displays the Cheung Chau prediction and 24-hour curve.

The test uses the original `?debug=1` diagnostics, retained HKO HHOT values, and a fixed 6 September 2026 12:30 HKT clock. It covers:

- Original 0–100 manual tide endpoints, the existing low-water floor, and matching shoreline uniforms.
- Animated sea normals after initial loading and a terrain-only mesh-density change.
- Original Waves, Wind and Rain controls, sun glitter, and valid WebGL shader programs.
- Three daily CCH HHOT responses, current-time interpolation and the original tide graph.
- Original Live/Manual control locking and its legacy adopted-live-level policy.

The early failed runs exposed an existing original-viewer defect: boot restores the terrain-density control, whose terrain rebuild cleared `tidalMats` without retaining the sea. The wave uniforms consequently stayed at their initial zero values. The bounded production correction re-registers the sea in `rebuildTerrain()`, and the final browser run explicitly verifies animation after another density change. This was not a Playwright-clock problem. No failed screenshots are retained.

The live screenshot includes the original debug mode's blue temperature-field canopy, produced by the existing `WxField.debugShowField('demo-temp')` callback; that overlay is unrelated to the tidal water restoration. The headless run recorded one non-shader HTTP 404 console diagnostic. Its URL was not captured, so no cause is asserted; page exceptions and WebGL/shader errors were both absent.

After the deterministic UI checks, the HHOT interception was removed for one actual browser request through the city tide controller. It succeeded at **2026-09-06 17:03:47 HKT**: CCH, status `live`, no error, **1.21885 m Chart Datum → 1.07285 m HKPD**. The record includes all three official query URLs. This checks actual browser CORS/service access separately from the retained fixtures; it is a point-in-time connectivity result rather than an availability guarantee.
