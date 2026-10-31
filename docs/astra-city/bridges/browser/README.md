# Footbridge city-browser verification

GPT-6 Astra independent integration review, 6 September 2026. Run from the worktree root:

```sh
node 3d-viewer/city/tests/bridges-browser.mjs
```

The final run passed in Chrome 152.0.7977.76 at `http://127.0.0.1:4176/city.html`. `verification.json` records the observations and assertions. All eleven PNGs were visually inspected at their captured dimensions: 1440 × 1000 desktop, 390 × 844 and 320 × 844 mobile. No blocking defect was found in the reviewed integration.

The four close views use actual streamed city geometry and UI deck picking:

| Area | OpenStreetMap span | Cover in source | Result |
| --- | --- | --- | --- |
| Central | way/32511520 | No | Solid raised deck and rails; correct source and estimated-height card |
| Wan Chai | way/40491206 | Yes | Covered raised deck, posts and rails; correct source card |
| Tsuen Wan | way/470688470 | Yes | Covered building connection, visible deck sides and rails; correct source card |
| Mui Wo | way/701768072 | No | Raised deck and rails; correct source card |

The app loaded 12,260 prepared spans, including 3,420 explicitly covered spans. The sampled close views used 15, 18, 15 and 11 bridge tiles respectively, within the 24-tile cap. Hiding Footbridges cleared selection, removed bridges from picking and reported zero visible spans. Restoring the layer restored the prior visible span count. A 3,500 m camera height hid Mui Wo's rail instances while retaining decks; the close view had visible rails.

English `Octopus Bridge` and Traditional Chinese `八爪魚` searches selected the bridge through the real results UI, moved to the relevant region and displayed its source card. Chinese search legitimately returns multiple source-name variants, so the fixture chooses the result named `Octopus Bridge`. Mobile arrival closed the settings panel; the source card and controls remained inside both narrow viewports without horizontal overflow. The fixture waits for the canvas resize event before measuring the 320-pixel layout.

A separate fresh page deliberately aborted the first `bridges.json` request. The Retry control appeared, bridge suppression IDs remained empty, and existing bridge-road meshes retained 46,590 vertices across the loaded tiles. Clicking the actual Retry control loaded all 12,260 spans, cleared the error and introduced 12,267 source/record suppression keys. The old bridge-road vertex count then fell to 21,222; road spans without replacements remained. No uncaught application or graphics errors occurred. The deliberately aborted request's expected network error is excluded from the error assertion.

For observation and repeatable close framing, only the intercepted test response for `app.js` adds a getter exposing the existing scene, camera, controls, sampler, stream and bridge layer. No production source file or geography is altered. Camera positions are test viewpoints, not proposed destinations. Search, layer toggles, deck clicks and retry all run through the actual interface.

These checks verify renderer/UI integration, not surveyed elevations, entrances, architectural construction or elevated walking. The card explicitly states those limits. Geometry provenance remains in the retained bridge inventory and adjacent bridge documentation. No historical Lantau reference image was used or changed.
