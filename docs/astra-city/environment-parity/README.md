# Actual city environment verification — HKS-168 / HKS-169

`tests/environment-parity-browser.mjs` drives the real city Sky and Weather controls in one Chrome instance. The completed result is `verification.json`. The original meteor smoke and weather synthesis/log-depth fixtures remain separate; they are not duplicated here.

```sh
node 3d-viewer/city/tests/environment-parity-browser.mjs
```

Reserve the shared GPU/browser slot before running. By default the test opens `http://127.0.0.1:4176/city.html?district=kowloon`; `CITY_URL` and `CHROME_PATH` can override the local server and browser.

All nine check groups passed:

- Sky shooting-star defaults at 18%, rate 100%, checkbox off/on, daylight/night suppression and Stargaze.
- Reduced Motion hides meteor trails and freezes their effect clock.
- No AudioContext on load or a synthetic click. First enabling sound while Stargaze suspends weather leaves it locked; returning to the city offers the correctly labelled enable button and a real gesture starts audio.
- Manual lightning/rate, weather mix controls, master volume and zero-volume silence.
- About dialog pauses meteor/storm progression and suspends audio; closing resumes it.
- Reduced Motion suppresses both visual effects while preserving the user's separate sound preference.
- Deterministic mocked HKO thunderstorm conditions do not create simulated live lightning. Manual storm/rain/rate settings return unchanged.
- Stargaze pauses storm/audio while keeping manual weather settings. Returning resumes previously unlocked audio; Mute suspends it.
- Both control panels remain reachable without document or panel horizontal overflow at 390×844 and 320×844. Exact control bounds are recorded in the JSON.

HKO HTTP responses are intercepted with fixed observation values and a valid timestamp generated at test start. They are test fixtures, not research evidence of conditions on that date. The test uses the public `window.__city.state.environment` diagnostics and actual controls; it does not mutate private effect controllers. There were no page, console or shader errors.

Saved, visually inspected interface evidence:

- `sky-stargaze-desktop-1440x1000.png`
- `manual-storm-desktop-1440x1000.png`
- `sky-mobile-390x844.png`
- `weather-mobile-390x844.png`

The Weather mobile screenshot shows the scrollable panel positioned around the new controls. The Sky mobile frame shows the unobstructed Stargaze view after its panel closes. The 320 px layout is checked quantitatively in `verification.json`. The successful run used the corrected test sequence that reopens Weather after Stargaze switches the selected tab to Sky; this was a harness correction, not a production defect.

Produced by the Astra weather subagent. Existing source geometry, observation handling and clock/sky calculations are unchanged by this test.
