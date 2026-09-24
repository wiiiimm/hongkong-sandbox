# Stonecutters Bridge browser evidence — HKS-196

The baseline was captured in the actual Astra viewer before source reconstruction. Run `node source-scripts/city/stonecutters/browser.mjs before` from the worktree. The script uses the existing bridge verification hooks and a valid Tsing Yi destination, then frames Stonecutters using retained OSM corridor coordinates. Those camera/sample coordinates are contextual, not surveyed foundation geometry.

Seven exported views cover daytime, night, both landings, the space below the span and 390/320 px layouts. Inspection of the daytime, under-span and 320 px images confirms a continuous raised terrain causeway beneath cylindrical tower proxies. Eleven centreline terrain rays measure approximately 50–77 m HKPD and agree with the navigation sampler; all currently report land. No page, shader or data errors occurred.

Measured baseline: desktop 111 draw calls / 1,370,070 triangles; narrow mobile view 80 calls / 1,060,415 triangles. Median and p95 frames were 16.7 ms in desktop Chrome. These are not physical-handset measurements.

`before/verification.json` records the commit, hashes, camera states and measured rays. The prepared `after` mode requires the source packet to be integrated and will check original source identity, exact proxy replacement, picking, foundations, submerged terrain and actual flight. **After-mode acceptance has not yet run; reconstruction is not declared complete.**
