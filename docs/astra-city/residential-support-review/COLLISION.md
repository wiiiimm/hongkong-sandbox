# HKS-214: native local roof collision correction

The old closed-building collision prism filled the complete surveyed footprint to the highest vertex anywhere in a native model. At LOHAS depot B456991729402063C0 this produced a phantom volume above its lower roofs, hiding the valid collider of ancillary source B456901750901062G0.

Native interiors now retain the sourced footprint policy but stop at the highest actual triangle projected over the query position. The existing cached 4 m triangle index supplies this local ceiling; vertical walls and uncovered gaps supply no roof. Real walls, sloping roofs and overhangs still use clipped triangle/cylinder intersection, including radius contacts at courtyard edges. Ordinary surveyed extrusions and open-sided structures retain their existing rules. Source geometry, elevations, terrain and source asset bytes are unchanged.

The local ceiling bounds a collision volume; it is not a claim of surveyed room layout. The separate conservative `maximumRoof` aircraft spawn/avoidance envelope is deliberately unchanged.

## Validation

- 264 viewer unit tests passed, including 25 geometry/collision tests. New closed-prism fixtures exercise low/tall wings, clear air above the low roof, physical roof contacts, courtyards despite filled survey outlines, real courtyard wall radius contact, sloping roofs, uncovered projected corners, indexed models, negative coordinates and large faces.
- Exact source replay: 100/100 ancillary triangle-centre contacts remain solid. Depot contacts fell from 100 to five, matching the five actual source surface coincidences within 5 cm; 95 unique ancillary contacts are now reachable regardless of depot insertion order. Original evidence remains in `collision-surface-268527.json`; corrected evidence is `collision-fixed-268527.json`.
- Installed-browser replay passed at 1280×900 and 390×844: target and depot both active, no support holds or browser errors, scene collider resolves the real ancillary roof. At the regression point the depot's local roof is 18.992012 m, the target roof is 29.109997 m, and the depot's unrelated global maximum is 41.908012 m.
- Desktop cold index construction plus two queries took 22.3 ms; 2,000 warm queries took 11.9 ms desktop and 12.4 ms after the mobile viewport change. These are local Chrome measurements, not physical handset performance claims.

```sh
node --test 3d-viewer/city/tests/model-collision.test.js 3d-viewer/city/tests/building-geometry.test.js
(cd 3d-viewer/city && node --test tests/*.test.js)
node source-scripts/city/residential-support-review/collision-overlap.mjs docs/astra-city/residential-support-review/collision-fixed-268527.json
node source-scripts/city/residential-support-review/collision-browser.mjs
```

The browser script uses the running local Astra server on port 4176 and writes exact runtime hashes to `collision-browser.json`. This correction does not change model/region approval counts or publish new source assets.
