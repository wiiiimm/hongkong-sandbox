# HKS-214: mechanical preflight before bulk modelling

This is supporting preparation, **not completed modelling, visual acceptance or publication**. The executor is the `terrain_publication_guard` subagent. Root coordinates acquisition, final integration and Linear updates.

The immutable initial snapshot accounts for all **213 landmark entries and 401 selected source parts**, including 50 entries with no selected source identity. Its 109 staged models total 8,880,859 compressed bytes. See `summary.json` for the current snapshot/counts after subsequent recaptures.

The source states are kept separate: 132 installed parts, 109 prepared candidates, 119 acquisition-pending parts, 27 exact sources absent from the checked complete sheets, 6 acquired exact-reference match holds, and 8 parts requiring government identity. A checked-sheet absence is not a claim that no government source exists anywhere.

The existing shared CPU validator passed all 109 staged models in about 2.51 seconds. It exercised native source-surface picking/collision as well as geometry loading and terrain samples. Preflight reuses that hash-verified evidence instead of repeating unchanged checks. It found 65 elevated-component support diagnostics, 31 foundation diagnostics and 2 sampled roof-occlusion diagnostics; these categories overlap. Nineteen candidates have no current CPU terrain flags and no prior hold, but remain unapproved for visual appearance, identity membership and full component coverage.

The two roof-occlusion cases are `landsd/186982:0` Lai Tak Tsuen Block 8 Substation and `landsd/226248:0` Run Run Shaw Creative Media Centre. They are higher-effort modelling review items, not mechanically corrected here. Seventeen previously recorded source/placement holds are retained. Native bounding-box support hints are provided for seven models; those hints **do not prove triangle support** and never clear a hold.

## Outputs

- `report.json`: every source part, exact IDs, source/acquisition evidence, candidate checksum/native bounds, CPU findings, possible assembly neighbours and every landmark checklist.
- `queue.json`: compact per-part/per-landmark actions, with difficult terrain/identity/assembly decisions flagged for higher effort. Publication remains disabled for every item.
- `summary.json`: current counts, source-state split, runtime/resource metrics and limitations.
- `snapshot.json`: source filenames, lengths and SHA256 hashes for the frozen inputs and assets.

The snapshot assets and full input copies are ignored under `source-scripts/city/landmark-preflight/snapshots/<id>/`. These local reproducibility copies are not deployable assets. The script only writes its own directories; it makes no network, database, GPU, runtime or live-catalogue changes. It preserves fixed 1× source coordinates/elevations. No reference maps were used or modified.

## Reproduce or extend

From the Astra worktree:

```sh
# Reprocess the pinned snapshot without reading a changing acquisition batch.
/tmp/astra-city-venv/bin/python source-scripts/city/landmark-preflight/preflight.py

# Pin the final expanded batch after acquisition, identity, progress and CPU
# validation reports have all been refreshed and the source agent confirms stability.
/tmp/astra-city-venv/bin/python source-scripts/city/landmark-preflight/preflight.py --capture

# Safety/accounting regression checks.
/tmp/astra-city-venv/bin/python -m unittest discover -s source-scripts/city/landmark-preflight -p 'test_*.py'
```

`--candidates`, `--validation`, `--stage-summary`, `--identity`, `--progress` and `--acquisition` can target a subsequent expanded batch. Capture checks source hashes, unchanged inputs during copying, unique/exhaustive model coverage and asset hashes/sizes. Processing checks snapshot integrity, exact model identity against the part ledger and complete landmark membership accounting. An expanded source catalogue therefore needs its matching refreshed validation and identity ledgers; it cannot silently reuse stale results.

Seven tests cover stale snapshot rejection, duplicate UID rejection, clean-CPU preservation of known holds, runtime exceptions, distinct pending/absent/mismatched source states, non-authoritative support hints and avoiding an unsupported-foundation claim from a simple base gap.

After preparation, resolve exact-source/identity exceptions, then review coupled model assemblies and source terrain in batches. Existing component-membership gaps remain explicit; no landmark is promoted to complete merely because all currently selected parts were packed.

## Source prerequisites and automated gallery

`terrain_inputs.py` inventories existing geometry-only native TIN payloads and retained ZIP members before requesting more inputs. `terrain-inputs.json` gives exact checked directory members/offsets/CRC and affected part IDs for missing sheets. The initial 109-model snapshot had 90 terrain-flagged parts: 30 had retained native inputs, while 60 required native inputs across 26 sheets (about 140.5 MB of compressed geometry). The whole-HK archival 5 m DTM is already local. These initial counts will shrink as acquisition completes; rerun against the final expanded snapshot before reporting final prerequisites.

```sh
/tmp/astra-city-venv/bin/python source-scripts/city/landmark-preflight/terrain_inputs.py
```

The root assigned missing native terrain acquisition separately. No terrain is generated or applied here. The report separates verified staged geometry from retained archive members whose CRC/read checks occur during extraction.

`gallery.mjs` is a small adapter of the existing browser review staging/navigation routes. After final source stability, it captures a normal-scene day overview and closeup per landmark assembly. It logs actual active candidate IDs, absent native components, capture failures and overly broad geographic groups; it does not approve models. It reuses the current Three.js renderer and leaves all ordinary scene buildings and terrain visible.

```sh
/Users/williamli/.nvm/versions/node/v24.17.0/bin/node source-scripts/city/landmark-preflight/gallery.mjs
```

Optional `GALLERY_IDS=id1,id2` selects a bounded retry. Captures and the local contact-page `index.html` are ignored under `gallery/<snapshot-id>/`; `gallery-summary.json` is tracked evidence with per-landmark results. The gallery refuses changed reviewed terrain/source inputs. It has not been run on the initial 109 batch to avoid duplicate work before final expansion.
