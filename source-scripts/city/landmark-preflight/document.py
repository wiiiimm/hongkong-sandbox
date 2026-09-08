"""Summarise current immutable preflight evidence without changing review decisions."""
import json,pathlib
R=pathlib.Path(__file__).resolve().parents[3];D=R/'docs/astra-city/landmark-preflight'
def read(p):return json.loads(p.read_bytes())
p=read(D/'report.json');t=read(D/'terrain-inputs.json');assert p['snapshotId']==t['snapshotId'];g=read(D/'gallery-summary.json')if(D/'gallery-summary.json').exists()else{};complete=g.get('snapshotId')==p['snapshotId']and 'counts'in g
text=f'''# HKS-214: mechanical preparation before bulk modelling

**Preparation only: no new modelling, terrain changes, acceptance or publication.** Executor: `terrain_publication_guard`; root coordinates Linear, acquisition and integration.

Snapshot `{p['snapshotId']}` accounts for all **{p['registryEntries']} landmark entries and {p['sourceParts']} selected source parts**. The **{p['stagedModels']} staged models** passed the existing shared CPU loader, source-surface picking/collision and terrain checks; {p['validation']['compressedBytes']:,} compressed model bytes, about {p['validation']['seconds']:.2f} seconds of validation. Preflight reuses hash-verified CPU evidence rather than repeating unchanged checks.

| Source state | Parts |
|---|---:|
'''
for state,count in p['sourceProgressCounts'].items():text+=f'| {state} | {count} |\n'
text+=f'''
Zero routine model acquisitions remain pending in this snapshot. Checked-sheet absence is not a dataset-wide absence claim. Identity, historical-source conflicts and incomplete component membership remain explicit; no landmark is marked complete.

CPU diagnostics include **{p['classificationCounts'].get('elevated-component-support-context',0)} elevated-component support checks**, **{p['classificationCounts'].get('foundation-burial-context',0)} foundation checks** and **{p['classificationCounts'].get('sampled-roof-occlusion',0)} sampled roof-occlusion cases**. These categories overlap. **{p['classificationCounts'].get('cpu-clear-awaiting-visual-review',0)} candidates** have no current CPU terrain flags/prior hold; they still need appearance, identity and whole-assembly review. Known source/placement holds are never cleared by a clean CPU result. Native bounding-box neighbour hints are not proof of supporting triangles.

The two sampled roof-occlusion cases are `landsd/186982:0` Lai Tak Tsuen Block 8 Substation and `landsd/226248:0` Run Run Shaw Creative Media Centre. Difficult source/terrain/assembly decisions are flagged for higher effort rather than mechanically corrected.

## Terrain prerequisites

**{t['nativeTerrainAvailableModels']}/{t['flaggedModels']} terrain-flagged parts have retained native terrain inputs; {t['missingNativeSheets']} sheets remain missing.** The acquisition agent downloaded missing geometry-only native terrain through separate pinned batches; preflight verifies the retained manifests/payload hashes and source availability. The archival whole-HK 5 m DTM is already local. No imagery was requested and no terrain was generated or applied here.

`terrain-inputs.json` separates verified staged native payloads from retained raw ZIP members. Raw archive CRC/read checks occur at extraction. Source bounding-box coverage is not exhaustive triangle support proof. Cached inputs may still differ in date or omit retaining edges; availability does not itself fix placement.

## Scripted gallery

'''
if complete:
 c=g['counts'];text+=f'''All **{c['attemptedAssemblies']}/{c['plannedAssemblies']} eligible assemblies were attempted**, producing **{c['images']} JPEG views**. **{c['cameraClearViews']} views pass the bounded camera ray/occupancy check; {c['cameraUnresolvedViews']} remain explicitly unresolved.** {c['reframedViews']} views used automatic higher-angle reframing. There are {c['failedAssemblies']} capture failures and {c['assembliesWithInactiveParts']} assemblies with at least one candidate inactive in both captured views.

The self-contained [thumbnail contact gallery](contact.html) is committed for review. Full 1280 × 900 JPEGs stay local/ignored under `gallery/{p['snapshotId']}/`; checksums are in `gallery-images.json`. `gallery-summary.json` records camera rays, active candidate IDs, loading flags and all unresolved outcomes. Model activity and a clear camera ray do not establish architectural fidelity or complete component coverage.
'''
else:text+='The final automated assembly gallery is pending. Saved screenshots alone do not establish a clear view or acceptance.\n'
text+='''
The capture adapter reuses existing staged browser routes/navigation and the current Three.js scene. It checks camera occupancy plus nine source-feature rays, tries at most three higher-angle reframes, then records an unresolved view instead of hand-tuning architecture. Normal buildings/terrain remain visible. Four disjoint workers can run concurrently; this is not an FPS benchmark. The Pedder camera regression and ordinary Airside framing were checked before the bulk run. Detailed façade/entrance review remains later modelling work.

## Evidence and reproduction

- `report.json`: every part's identity, acquisition evidence, native bounds, CPU findings, assembly hints and every landmark checklist.
- `queue.json`: per-part/per-landmark next actions and effort flags; publication disabled throughout.
- `summary.json`: current counts and resource metrics.
- `snapshot.json`: frozen input/source filenames, sizes and SHA256 hashes. Local copies are ignored under `source-scripts/city/landmark-preflight/snapshots/`.

From the Astra worktree, with Python 3 and Node 20+ on PATH and the viewer's Playwright dependency installed:

```sh
# Reuse the pinned snapshot, no network/database/GPU work.
python3 source-scripts/city/landmark-preflight/preflight.py

# Capture a later stable expanded set. Refuses stale CPU/progress evidence
# or incomplete acquisition batches; all source ledgers must be refreshed first.
python3 source-scripts/city/landmark-preflight/preflight.py --capture
python3 source-scripts/city/landmark-preflight/terrain_inputs.py

# Run each disjoint worker (N=1,2,3,4) in a separate process.
GALLERY_WORKER=N/4 node source-scripts/city/landmark-preflight/gallery.mjs
python3 source-scripts/city/landmark-preflight/merge_gallery.py --workers 4
node source-scripts/city/landmark-preflight/contact.mjs
python3 source-scripts/city/landmark-preflight/document.py

python3 -m unittest discover -s source-scripts/city/landmark-preflight -p 'test_*.py'
node --test source-scripts/city/landmark-preflight/browser-runtime.test.mjs
```

Browser portability (HKS-215): set `CHROME_PATH` or `CHROMIUM_EXECUTABLE_PATH` to an installed executable when needed. Otherwise the adapter checks existing macOS Chrome, the project Playwright Chromium installation, and common Linux/Windows paths. An invalid explicit path fails clearly. The same lookup is used for captures and thumbnail generation; no source snapshot changes are required. Two focused JavaScript tests cover override precedence, missing executables and Playwright fallback.

Successful camera-checked captures are resumable; `GALLERY_IDS=id1,id2` permits bounded retries. Eight tests cover duplicate/missing accounting, immutable snapshots, preserved holds, runtime failures, distinct pending/absent/mismatched sources and non-authoritative support hints. No tests infer appearance acceptance.

No source coordinates/elevations, shared inventory, live runtime or published assets were changed. All geometry remains 1× HKPD. No reference maps were used or modified. Further work is the actual source/assembly/terrain modelling and visual review—not repeating the now-completed routine acquisition.
'''
(D/'README.md').write_text(text)
