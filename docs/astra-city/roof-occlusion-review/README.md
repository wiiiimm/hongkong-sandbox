# Two roof-occlusion corrections — HKS-214

Executor: Astra `roof-occlusion-review` agent. **Two source-backed terrain candidates are prepared and visually checked; neither is published.** Existing government building geometry and elevations remain unchanged at native 1× HKPD.

Both preflight warnings are real burial by the existing 70 m terrain mesh. The retained government terrain TIN places the ground below the roofs and agrees with the native foundations. Raising the models would have hidden the actual terrain problem.

| Source component | Existing ground at sampled roof | Native TIN at sampled roof | Native roof | Candidate roof clearance |
| --- | ---: | ---: | ---: | ---: |
| `landsd/186982:0` — Lai Tak Tsuen Block 8 Substation | 72.361 m | 62.592 m | 66.774 m | 4.180 m |
| `landsd/226248:0` — Creative Media Centre named ancillary part | 86.308 m | 81.820 m | 84.070 m | 2.214 m |

The second source component is only approximately **4.09 × 3.52 × 2.30 m**. Its official name refers to the Creative Media Centre, but this component is **not the main angular landmark building**. Correcting it does not complete the centre's architecture or assembly.

## Evidence and verification

- `audit.json`: original model/TIN hashes, exact source footprint intersection, sampled highest-roof point and all highest-roof vertex clearances. Native terrain covers the complete footprint for each case; no native terrain lies above its highest roof.
- `patch-review.json`: two 140 × 140 m candidates, each with 19,881 grid vertices. Uses the existing native-TIN decoder, barycentric sampler, rendered DEM sampler and neighbour-extrema audit.
- `verification.json`: all 11 intersecting source building footprints checked in each candidate extent; no newly introduced roof/basement envelope flags. Each patch has 560 boundary samples joining the existing rendered parent within 0.00000043 m numerical error.
- `browser/report.json`: four successful before/after diagnostics, both candidates active, identical paired camera positions and no page errors. The files below were visually inspected: the substation changes from a small exposed corner to its complete roof and walls; the Creative Media Centre ancillary part changes from buried to visible at its native level.

| Component | Existing terrain | Candidate terrain |
| --- | --- | --- |
| Lai Tak substation | [Before](browser/landsd-186982-0-before.jpg) | [Candidate](browser/landsd-186982-0-candidate.jpg) |
| Creative Media ancillary part | [Before](browser/landsd-226248-0-before.jpg) | [Candidate](browser/landsd-226248-0-candidate.jpg) |

The diagnostic hides unrelated buildings to expose the foundations. It does not establish ordinary-scene visibility, complete-landmark acceptance, walking/road alignment, rooftop landing or mobile performance. Street strips remain in these views; their alignment needs normal-scene review before publication.

## Prepared correction and remaining gate

Candidate files are under `source-scripts/city/roof-occlusion-review/roof-review-186982-0.json` and `roof-review-226248-0.json`. Each is a disjoint top-level patch of `city/data/terrain.json`, aligned to that parent's 70 m cell boundaries. One-metre spacing is a resampling interval, **not a claim of one-metre survey accuracy**. A 10 m outer display transition joins the existing rendered terrain. Absent native source coverage and the existing water mask retain the previous terrain; 282 nodes at the substation patch's far eastern edge have no source coverage, outside the fully covered target footprint.

**Decision:** accept the source diagnosis and prepared correction for guarded integration review. Hold runtime publication until the parent workflow checks the combined manifest, normal-scene roads/paths and neighbouring detailed components, and records fresh integration evidence. Do not treat a candidate terrain file as an installed model upgrade. No SQLite, shared manifest, runtime source file, R2 object or model-review ledger was changed here.

## Reproduce

Reserve the exact two source UIDs through the shared Neon session-reservation workflow first. Run from the Astra worktree with the existing NumPy/Shapely/pyproj environment, browser dependency and local viewer on port 4176:

```sh
python source-scripts/city/roof-occlusion-review/audit.py
python source-scripts/city/roof-occlusion-review/prepare.py
python source-scripts/city/roof-occlusion-review/verify.py
node source-scripts/city/roof-occlusion-review/browser.mjs
```

The source model and terrain caches are required. Scripts make no downloads. Browser routes inject a correctly counted two-part catalogue and the staged patches for that isolated session. The original government geometry is loaded through the existing checksum-validating loader.
