# Fly aircraft picker — HKS-177

Implemented by the Astra aircraft subagent (Kant), recovered and verified after the app restart by `resume_aircraft_picker` on 7 September 2026.

## Delivered

The Fly button in the bottom mode dock opens an anchored pull-up chooser containing all seven existing aircraft. Selecting a model enters Fly; selecting another while flying changes the aircraft without resetting the flight position or heading. Keyboard `3` retains quick entry with the current aircraft, including when focus is inside the chooser.

The chooser reuses `AIRCRAFT`, `selectAircraft` and `Navigation.setAircraft`, including source credits, calibrated dimensions, loading status, a usable fallback and Retry. No models, flight physics, audio or geography were replaced. Existing pending-arrival cancellation guards remain in place. Flight movement pauses while the chooser is open and held inputs are cleared, so menu navigation cannot steer the aircraft.

The menu has selected-state semantics, arrow/Home/End navigation, Escape and outside dismissal, and returns focus to the dock on keyboard dismissal. The city control sheet and aircraft chooser dismiss one another. The menu scrolls on short mobile screens and retains at least 44 px touch targets.

## Verification

Run from `3d-viewer/city` with the static viewer served on port 4176:

```sh
npm run test:aircraft-picker
node --test tests/aircraft.test.js
npm test
```

- Fresh Chrome 152 browser run: passed, no console/page errors; see [verification.json](browser/verification.json).
- All seven aircraft selected and loaded with expected dimensions; in-flight heading and position continuity checked.
- Held input isolation, native Space, arrows, Home/End, Tab, Escape, keyboard 3 inside/outside the menu and Stargaze transitions passed.
- Delayed model requests and cancelled arrival requests cannot override newer choices.
- Deliberate A350 network failure preserves flight fallback; Retry restores the detailed model.
- Desktop 1440 × 1000 and mobile 390/320 × 844 checked, plus both widths at 568 px height. Day and night screenshots retained in `browser/` and visually inspected.
- Eight focused aircraft unit tests and all 226 city unit tests passed.

The old browser consumers were adapted to select an aircraft after opening Fly. The comprehensive legacy aircraft-city and regional browser suites were not rerun in this bounded recovery pass; the dedicated picker suite covers the changed interaction directly.

## Remaining HKS-177 scope

This completes the aircraft-selection UI slice only. Original-game throttle, acceleration/reverse, take-off/landing, craft-specific handling, camera parity and engine/throttle audio still need their broader parity review. This is not evidence that HKS-177 as a whole is complete.

No map reference image was used: this change reuses the existing aircraft catalogue, geometry and design system.
