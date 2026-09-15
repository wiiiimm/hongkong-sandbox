# Original viewer browser verification

The combined `verification.json` records a passing check of the shared shooting-star extraction in the actual original viewer (`index.html?debug=1`), Chrome 152, at 1440 × 1000 and device scale 1. It uses the existing original controls and debug hooks; no new production test hook was added.

`first-pass.json` preserves the first run verbatim. Defaults, all four rate labels, the single 14-trail pool, visible Stargaze emission, immediate toggle-off, re-enabling and `sh`/`shr` URL state all passed. The run then stopped because the fixture tried to change the sky-mode selector while Stargaze deliberately disabled it. This was a test-sequence correction, with no production change.

`remaining-verification.json` runs only the remaining checks: sky-off clears trails and disables the controls; fixed midday clears trails while retaining usable controls; the original Traditional Chinese rate label remains 末日. The fixture now leaves Stargaze before attempting sky-mode changes and explicitly supplies `lv=0` to avoid the original curated default's unrelated live-weather network activity.

The retained PNG was visually inspected: a sharp, thin, fading meteor is visible to the right of the panel among the original stars and constellation lines; the shooting-star checkbox and Apocalypse rate label are legible. The snapshot is the actual browser render at its recorded dimensions, without post-processing.

Both runs contain no page exceptions or WebGL/shader errors. Diagnostic logs retain one local 404 each; the first run also contains unrelated satellite-image CORS failures from inherited live weather. These did not affect meteor validation.

Reproduce all assertions after the corrected sequencing:

```sh
cd 3d-viewer/city
node tests/meteors-original-browser.mjs
# To repeat only the final three controls:
node tests/meteors-original-browser.mjs --remaining
```

Set `ORIGINAL_URL` or `CHROME_PATH` for a different local server or browser. Coordinate GPU use with other browser tests; this evidence does not provide performance benchmarks.
