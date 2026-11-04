# Lee Kong original podium and tower

Installed two unchanged government originals at native placement and fixed 1x scale. Original geometry is immutable; no AI geometry modelling.

- Podium landsd/72296:0: 21,662 faces; tower landsd/253697:0: 372 faces.
- Exact source identity reviewed; raw neighbouring-footprint overlap flags retained. No adjacent-source suppression.
- Complete foundations in four coordinate representations pass. All 72 strict tower-to-podium contacts pass without wall intersections.
- Full changed terrain domain: 80 basic forms and two retained native models checked, no remaining regression flags.
- Staged/live desktop and mobile day/night checks pass, with explicit podium dependency and tower failed-download fallback/retry. ROOT inspected all eight live exports.
- Native terrain replacement passed the existing validator.

Neon installed job: 5b4671074435228867c4635171d205635ada4826c63ffcada5a2fa79570aad36; snapshot: 94f2abd4f135efce.

XL coverage: **278 installed / 243 unfinished of 521**. Two models installed; only the podium is an XL source.

Limitations: neighbouring buildings obscure parts of lower facades; captures do not certify physical-phone performance or full-map loading. Mobile v2 intentionally failed both dependency downloads and timed out; corrected v3 isolates tower retry while support is available. The failed diagnostic is retained.
