# HKS-209: cache-only bulk processing of all 16 flagged parts

All **16 requested source parts** are accounted for: **3 staged and validated candidates, 11 held, 2 missing from the reviewed retained sources**. No live building, terrain, source coordinates or shared inventory records were changed. All native geometry remains at 1× HKPD.

“Ready” means ready for the next browser review, not published or architecturally accepted. The three candidates total **5,507 compressed bytes**. Shared loader, source-surface picking/collision and terrain checks pass for all three with zero exceptions and zero sampled terrain concerns. Actual browser review remains with the root task.

The three resolved match failures were stale cached footprint-selection matches: current source footprints match the original geometry at the existing ≥50% smaller-footprint overlap and ≤10 m centroid thresholds. The thresholds were not relaxed; source geometry was not shifted. Original source hashes and refreshed matching evidence are retained.

## Per-building disposition

| Source UID | Building / part | Processing state | Evidence and next action |
|---|---|---|---|
| landsd/3089:0 | ASIA SOCIETY HONG KONG CENTER | ready | Fresh current-footprint match passes unchanged thresholds; shared loader/terrain checks pass. |
| landsd/3090:0 | ASIA SOCIETY HONG KONG CENTER | ready | Fresh current-footprint match passes unchanged thresholds; shared loader/terrain checks pass. |
| landsd/4314:0 | The Asia Society Hong Kong Center Miller Theater | ready | Miller Theater: refreshed exact source match and loader/terrain checks pass. |
| landsd/70574:0 | ASIA SOCIETY HONG KONG CENTER | held | Nearby native building covers 99.4% horizontally, but none of 131 rays reaches the estimated canopy band; insufficient canopy proof. |
| landsd/91009:0 | FLAGSTAFF HOUSE MUSEUM OF TEA WARE AND THE K.S. LO GALLERY | held | Related native roof covers 88.7%;40/47rays hit, only 31 reach the estimated height band. Keep unmatched remainder/fallback. |
| landsd/114964:0 | E Hall | held | Current retaining-edge burial remains. Prior high-cost 0.25 m grid is not accepted; retain source heights. |
| landsd/143421:0 | FLAGSTAFF HOUSE MUSEUM OF TEA WARE AND THE K.S. LO GALLERY | held | Exact GeoRef but zero actual footprint overlap; 6.37 m centroid gap. No coordinate shift or threshold relaxation. |
| landsd/223348:0 | ASIA SOCIETY HONG KONG CENTER | held | Native upper component remains about 7 m above ground with no identified support; retain full-height fallback. |
| landsd/223783:0 | ASIA SOCIETY HONG KONG CENTER | held | Adjacent native model covers only 7.8% (one of 11 rays); downhill support remains unresolved. |
| landsd/242698:0 | Married Inspectors' Quarters | missing | No standalone exact member in the checked complete 11-SW-8D directory (2,428 entries). |
| landsd/246271:0 | THE PEAK TOWER | held | Main Peak model covers 99.96%; 19/22 rays reach estimated band. Needs main-model placement and architectural confirmation. |
| landsd/246272:0 | THE PEAK TOWER | held | Main Peak model covers 100%; only 6/28 rays reach estimated band. Height/component correspondence remains unresolved. |
| landsd/248218:0 | The Peak Tower | held | Cached 5 m DTM trial worsens lowest-vertex burial to 16.67–20.05 m and introduces neighbour flags; rejected. |
| landsd/322573:0 | Opus Hong Kong | held | Cached 5 m/native-TIN trial improves median contact to −0.12 m, but residual corner gaps and full-patch/browser review remain; held. |
| landsd/324948:0 | The Henderson | missing | No exact source member in prior bounded complete-directory review; retain surveyed-height baseline. |
| landsd/330467:0 | JC Cube | held | Current retaining edge leaves 3–4 m gap; prior 58,081-vertex trial still about 1 m gap. Lower-cost edge solution remains pending. |

## Cost and reusable tooling

The final bulk pass took **2.274 seconds**, inspected **87 cached manifests**, and verified/read **32 native payload files totalling 5,093,095 bytes**. That byte count excludes metadata reads and the separate terrain experiment. Network requests, downloaded bytes and AI calls inside the scripts were all **zero**.

The pass reuses the existing `cached_models.Processor`, original model decoder/packer, indexed-triangle evidence helper and read-only SQLite inventory. Individual failures become explicit retry entries rather than abandoning the remaining records. Candidate assets are checksum-addressed and reruns reuse identical output bytes.

The separate cached terrain experiment reuses the established 5 m DTM builder and native-TIN mosaic. **Both terrain outputs remain held.** Opus still needs broader neighbour and browser checks; Peak's DTM proposal increases burial and is unsuitable. The earlier high-cost Tai Kwun terrain candidate is also excluded. No source was moved to conceal a terrain problem.

## Reproduce

From the Astra worktree, using the existing local runtimes:

```sh
/tmp/astra-city-venv/bin/python source-scripts/city/architecture-followup/bulk_pass.py
/Users/williamli/.nvm/versions/node/v24.17.0/bin/node source-scripts/city/building-batch/validate_candidates.mjs --candidates source-scripts/city/architecture-followup/compact --out source-scripts/city/architecture-followup/compact/validation.json
/tmp/astra-city-venv/bin/python source-scripts/city/architecture-followup/terrain_pass.py
/tmp/astra-city-venv/bin/python source-scripts/city/architecture-followup/write_review.py
```

- `bulk-report.json`: per-UID source identity, exact geometry/support evidence and input hashes.
- `queue.json`: one next action for each of the 16 parts.
- `candidate-validation.json` and `verification.json`: source identity, checksum, loader and complete-scope checks.
- `terrain-report.json`: held Opus and rejected Peak terrain experiments with explicit limitations.
- Staged model assets remain in `source-scripts/city/architecture-followup/compact/`.

Cache/directory absence is limited to the listed source revisions; it does not establish dataset-wide unavailability. No fresh downloads were made. Further source acquisition, retaining-edge work or source-component correspondence review should be bounded follow-ups. HKS-209 remains In Progress; only the three validated candidates can proceed to visual review now.
