# 1883 Building — original government model installed

Codex root, 5 October 2026; HKS-203 / HKS-215 / HKS-199. Source form
`landsd/118475:0` is installed with unchanged government geometry and native
coordinates: 15,486 triangles, source SHA256
`8a90520bddbfa439e3479e578d422dcad8f6bf0f88f6207b8ce8bb04d0f54b44`.
No reference-map image, AI architectural review or geometry generation was used.

The initial terrain sheet ends at x=1499.5m and leaves a source-covered region
outside the available TIN. The original adjoining 11-NW-25C terrain extends
11-NW-24D without manufactured elevations or relaxed coverage tolerances.
Provenance and exact source/archive/file hashes are in `source-recovery.json`
and `adjacent-source-11-NW-25C.json`. Original acquisition files remain local-only;
committed runtime terrain and accepted compressed model are self-contained.

Minimum drawn-terrain clearance is -0.117116m; maximum low-rim gap 0.288933m,
sampler error zero and no missing samples. Whole-source foundation checks complete
with zero buried/upward area; all 51 neighbours pass. CPU loading, exact picking,
collision, staged/live desktop/mobile day/night and mobile 503 fallback/retry pass.
The Annex of 1883 Building and HK Observatory B Substation remain visible.
Exported browser images are retained under `installation/`; no phone FPS claim.

Installed snapshot `b8d42e765476890d`; fenced Neon installation job
`d7216ff7f8ac3b51d45789cddaa24fe6ddfd182d4e144813dbf0640629ffe1d3`
has exact job/review readback, and ownership is released. The earlier source-stage
job `dc5730af1093e3ff15abf18dfce861edcde5ce4c94f2882e39a7455588566119`
and top-level `result.json` describe a historical script-ready checkpoint,
not current installed state. Use `installation/neon-sync.json` and the current
review snapshot for resumption. Do not repeat the completed dated installer.

XL352: 42 Installed / 310 Held. Map: 346,108 source forms, 4,390 enhanced;
4,376 / 212,669 matched government forms installed (2.05766%). Counts refer to
source forms, not whole physical buildings. No per-model external AI calls.

Reproducible commands, from the Astra checkout, with Python dependencies and
original local caches available (historical completed runs):

```sh
python source-scripts/city/government-import/xl-terrain-source-case-20261005.py 1883-building
python source-scripts/city/government-import/xl-1883-building-install-20261005.py
```
