# HKS-222: mechanical native converter

`convert_sheet(archive: Path, download: dict, official_path: Path, out: Path)` processes a sheet independently and returns its compact `summary.json`. It writes no Neon state, model reviews, shared catalogue or viewer assets. The orchestrator owns reservations, cache bundles, R2 upload verification and retries.

The input ZIP is a checksum-pinned compact archive of original building/terrain glTF and binary members. `download` carries `sheet`, `revisionDate`, `source`, `sha256` and preferably `expectedModels`. `official_path` is the existing gzip official selection format, augmented with `viewerUids: [{uid,rings,base,height}]` on each feature. Rings in those explicit viewer parts are city metres. Original feature rings remain EPSG:2326. The converter never invents `objectId:0` or assigns unnamed models to nearby buildings.

## Outputs

- `models/<outcome-id>.json` and `outcomes.jsonl`: every BUILDING glTF, including failures, unsupported layouts and matching holds.
- `assets/<sha256>.glb.gz`: unchanged native source attributes/nodes/materials packed by the existing bit-preserving GLB packer. Unmatched but packable geometry is retained too.
- `catalogue.json`: only unique conservative source/viewer matches satisfying current attribute/bounds/size contracts. These are **unreviewed candidates**, with placement/publication flags false.
- `native-terrain/<id>/`: existing `prepare_model_sample.stage` output for each terrain entry, isolated from failures in other entries. Derived glTF omits texture references, and original glTF/bin remains in the retained source archive. No photograph is fetched or invented.
- `terrain-outcomes.json`: separate terrain preparation counts and source provenance, never mixed into building counts.
- `terrain-check.json`: actual current viewer sampler diagnostics against capped source vertices. Below-grade samples and elevated towers are observations, not placement decisions. Out-of-map samples are labelled explicitly instead of using clamped boundary terrain as proof.
- `summary.json`: expected/source count agreement, all model outcome counts, packed bytes, source/code fingerprints and output hashes. A caller must inspect `modelCountMatchesExpected`, failures, terrain failures and held counts rather than interpreting return alone as architectural completion.

Matching reuses the existing exact GeoRefNo + at least 50% smaller-footprint overlap + at most 10 m centroid screen, repeated against explicit viewer polygon parts. Multiple parts/models targeting the same UID are held. The converter does not resolve those architectural identities automatically.

Every source model is validated independently for finite attributes, native affine node transforms, scene cycles, triangle/index ranges and buffer bounds. Unsupported TRS, animation, skinning, normalised/sparse attributes and new source extensions remain explicit. Source geometry is never lifted, draped, simplified or multiplied vertically. No native model is accepted because it merely parses.

The module keeps one Node terrain sampler process across sequential sheets in each Python worker. Terrain and its manifest patches are pinned on worker startup, and their hashes are recorded. Restart workers to use changed terrain. Set `CITYWIDE_NODE` when Node is not on PATH. There is no Node process per building.

`converter_dependencies()` exposes the decoder/packer/helper source paths for orchestration versioning. Per-model checkpoints are reusable only with the same input/code key and verified packed asset hashes. A changed source input/code reruns conversion. Malformed source records remain explicit on restart rather than disappearing from counts.

## Verification

```sh
python source-scripts/city/citywide-native/test_convert.py
python source-scripts/city/citywide-native/convert.py archive.zip download.json official.json.gz output-directory
```

Five tests cover malformed/cyclic/out-of-range/non-finite/external-dependency isolation; held identity; nonzero multipart UID preservation; asset corruption repair; restart reuse; duplicate UID holds; no UID invention; source hash rejection; geometry-only terrain preparation and isolated malformed terrain.

The complete Mui Wo pilot covered sheets 10-SW-17A and 10-SW-17B: **672/672 buildings packed**, **668 unique candidate matches**, **four explicit source matching holds**, **two native terrain geometries prepared**, and actual terrain diagnostics for all 672 models. First conversion took about 3.77 seconds combined; a restart reused all 672 models. See `docs/astra-city/citywide-native/converter-pilot.json` for source/code hashes and per-sheet evidence. These timings are a local mechanical pilot, not browser performance or whole-territory completion.

The remaining gate is source/placement/architecture and installed-browser verification. No manual modelling or viewer publication is part of this converter.
