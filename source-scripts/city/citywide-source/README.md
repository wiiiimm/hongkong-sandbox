# Government model directory discovery — HKS-221

This companion to `citywide-audit` inventories every sheet in the pinned official Lands Department non-textured 3D model index. It reuses the existing acquisition pipeline's HTTP range budget, ZIP-directory parser and exact-ETag source caches. It requests archive tails and central-directory ranges, with no native glTF or geometry-buffer member requests and no AI calls. ZIP-tail responses can include incidental trailing file bytes; all transferred bytes count towards the budget, and no such fragments are decoded as models.

## Run and resume

Run from the Astra feature checkout, using the existing modelling Python environment and the pinned `astra-modelling` Neon configuration:

```sh
python source-scripts/city/citywide-source/discover.py \
  --index source-scripts/city/landmark-acquisition/batches/identity-four-native-20260909/index.json \
  --workers 4 --max-mb 512
```

The index is an already paginated, retained source snapshot, not a claim about every building existing today. The run records its SHA and retrieval date. An unchanged rerun reuses shared Neon directory results; a new machine needs the repository/pinned index and Neon configuration, not the first machine's local SQLite. `--refresh-head` explicitly checks the government's current ETags instead of trusting the pinned snapshot cache. `--limit N` performs a partial trial; it cannot report the entire index complete.

The transfer budget is cumulative for the local index cache and reserves up to 8 MB per in-flight directory. Unsupported HTTP range responses are rejected rather than silently downloading large ZIPs. The process uses a renewable shared source-index reservation; a stale owner cannot persist results. Successful sheets are checkpointed to Neon every 100 attempts. Local directory and transfer files also allow interrupted work to resume.

## Shared results and interpretation

`astra_modelling.city_source_directories` contains per-sheet, content-keyed records: source URL/revision, exact archive ETag, directory SHA, native model names, government geographic reference numbers, member CRCs, offsets and sizes. Cache identity includes the acquisition/parser implementation; changing another sheet in the index does not invalidate an unchanged source archive. `city_source_discovery_runs` records coverage and errors.

`docs/astra-city/citywide-source/summary.json` and `directories.json.gz` retain a compact summary and full machine-readable catalogue. Local raw directories are under the ignored `cache/` folder and belong in the working-material R2 checkpoint, not the public viewer bundle.

A listed government model is **not** an exact match to a viewer footprint, downloaded geometry, a converted asset, a terrain-checked replacement or an accepted landmark. Model occurrences can repeat across sheets and must be deduplicated using provenance before downstream work. A missing name cannot be labelled source-unavailable while any relevant sheet remains unchecked. Listed native member sizes cover matched glTF/bin entries; external resource dependencies must be checked after parsing the actual glTF.

This pass does not change any installed building, terrain scale, model-review approval or publication state. Subsequent acquisition should use the retained exact source metadata and existing bounded downloader, then validate identity and geometry. The separate whole-city audit identifies technical exceptions; manual architectural and visual work remains distinct.

## Verification

```sh
python -m unittest discover -s source-scripts/city/citywide-source -p test_discover.py -v
```

The tests exercise actual ZIP-directory parsing, model/member selection, truncated-directory rejection, source/pipeline invalidation and reuse across unrelated index revisions.

## R2 working-cache checkpoint

After both scripts finish, `checkpoint.py pack --audit-run RUN_ID` creates a deterministic archive of directory caches, compressed audit plans/results and reports. Feed its `local/inventory.json` into the existing `landmark-resume/remote_checkpoint.py upload` command. That uploader writes into `astra-modelling/` in the existing bucket, downloads the objects again, checks hashes and only then exposes the immutable snapshot manifest. The standard uploader takes an explicit private environment-file path; credentials are never packaged.

```sh
python source-scripts/city/citywide-source/checkpoint.py pack --audit-run RUN_ID
python source-scripts/city/landmark-resume/remote_checkpoint.py upload \
  --root "$PWD" --cache /tmp/astra-citywide-r2 \
  --inventory source-scripts/city/citywide-source/local/inventory.json \
  --manifest /tmp/astra-citywide-manifest.json \
  --env-file /path/to/private/env-file --workers 8 \
  --report /tmp/astra-citywide-upload.json
```

On another machine, restore the recorded manifest using the existing standard restore CLI at its exact Git commit, then unpack the restored archive into a **new** temporary directory:

```sh
python source-scripts/city/citywide-source/checkpoint.py unpack \
  --archive /path/to/restored/citywide-HASH.tar.gz \
  --sha256 HASH --destination /tmp/astra-citywide-restored
```

The unpacker verifies the archive checksum before writing, rejects links/path traversal and refuses an existing destination. Reconcile the extracted caches with the checkout rather than overwriting newer work. Neon remains authoritative for shared job and review state; this archive never restores database tables or overwrites current model decisions. The earlier model-pause snapshot contains the native model inputs; this smaller checkpoint adds HKS-221 automation results and metadata.

The full compressed directory catalogue is intentionally ignored by Git and retained in R2; the small summary and verification records are versioned.

The actual two-run network reuse proof is reproducible with `python source-scripts/city/citywide-source/verify_reuse.py --index source-scripts/city/landmark-acquisition/batches/identity-four-native-20260909/index.json`. It records request and transferred-byte deltas and fails if the unchanged replay contacts the source again.
