# Landmark identity and source preparation — HKS-212

The final scripted pass accounts for all **213 registry entries**: **92 retain prior identities**, **102 have unapproved identity proposals**, and **19 remain explicit identity exceptions**. The overlay contains 183 source records, including 164 newly proposed unique UIDs relative to the original bulk selection. It resolves 98 of the original 115 unidentified entries and geographically separates the three ambiguous same-name groups.

This is source preparation for review. Component completeness, architecture, foundations and publication remain separate decisions. No master registry, source geometry, terrain or live viewer assets were changed.

| Identity state | Entries |
| --- | ---: |
| Prior identities retained | 92 |
| Proposed overlay | 102 |
| No supported identity | 13 |
| Independent location still needed | 2 |
| Historical interior host unresolved | 3 |
| Historical building conflict | 1 |

[Identity report](report.json) · [Validation](validation.json) · [Staging summary](stage-summary.json) · [CPU checks](prepared-validation.json)

## Evidence

The read-only resolver joins exact canonical government names, stable UID/CSUID/object IDs and unchanged footprint positions to sourced geographic hints. EPSG:4326 hints use the existing EPSG:2326 projection and origin 834500/816500. The majority of hints come from the retained discovery table; The Beacon uses its operator’s own map hyperlink. One explicit exception joins 133 Wai Yip Street to the unique government name The Grid using government and architect address evidence. No coordinates are invented or substituted into the building data.

The second pass adds documented aliases from Lands Department inventory, Rating and Valuation Department building-name/address lists, MTR, property owners, architects and first-party occupier addresses. Exact references, findings, provisional numbering relationships and unresolved reasons are retained in [aliases-v2.json](../../../source-scripts/city/landmark-identity/aliases-v2.json). Historical RVD lists are used as name/address evidence, not current geometry or completion dates. Cached reference hashes are in [reference-cache-manifest.json](../../../source-scripts/city/landmark-identity/reference-cache-manifest.json).

All geographic proposals require a name relationship and a distance of at most 250 m from a sourced hint. This is identity discovery, not a footprint matching tolerance for geometry. Named A/B parts remain separate; unnamed podiums and annexes are not assigned by proximity. Literal source ranges retain missing-number questions. Bel-Air’s discovery “8–9” remains unresolved because the official index names 8A/8B, not Tower 9. May House stays held because Police historical evidence records demolition in 1999; the replacement is not silently substituted.

Other remaining exceptions include Chu Hai campus component identities, the Nina and Cullinan tower/compound relationships, historical NatWest and Westpoint naming, source locations absent or conflicting, and three interior venues with unverified host buildings. Each has an explicit reason in the report. All groups retain `componentMembershipComplete: false` and all proposed identities remain unapproved for publication.

## Completed combined preparation

The separate SQLite selection `landmark-identity-hks212-preparation-v2` contains **459 unique source parts across 194 identified groups**:

| Source preparation state | Unique parts |
| --- | ---: |
| Already detailed in inventory | 133 |
| Candidate geometry staged | 273 |
| No usable retained model match | 45 |
| No government source identity | 8 |

The 45 unmatched source parts comprise **36 complete-sheet checked absences and nine acquired matching holds**. There are no unattempted exact-ID acquisitions in this selected set. All 326 processing jobs completed. The adapter consumed the original acquisition checkpoint plus all three verified incremental batches; 25 prior compact assets were reused. New staged assets contain **26,744,210 compressed bytes**; the complete prepared directory is **28,494,834 bytes**, under the 128 MiB ceiling. It used two workers, no AI calls and no network calls. The final cached rerun took 8.4 seconds, including 6.29 seconds of CPU validation.

All 273 candidates passed CPU loading, source-triangle picking/collision and sampled terrain checks. These checks do not establish browser quality or acceptable placement. Diagnostics include 208 sampled ground gaps, 43 terrain-above-bottom flags and two highest-roof-below-terrain cases, with overlap between categories. The last two concern `landsd/186982:0` and `landsd/226248:0`.

All **17 historical placement holds** remain in the ledger; seven held parts were packed for review without approval. The merged acquisition ledger retains **nine source-matching holds**, and none of those nine was staged. HKS-214 handles contextual preflight and HKS-209 retains physical reconstruction decisions. Native geometry remains at 1× scale and its original HKPD elevations. No candidates were published.

## Reproduce

```sh
/tmp/astra-city-venv/bin/python source-scripts/city/landmark-identity/resolve.py
/tmp/astra-city-venv/bin/python source-scripts/city/landmark-identity/validate.py
/tmp/astra-city-venv/bin/python source-scripts/city/landmark-identity/verify_determinism.py
/tmp/astra-city-venv/bin/python source-scripts/city/landmark-identity/stage_proposals.py check
```

After acquisition stability and exclusive SQLite-writer coordination:

```sh
/tmp/astra-city-venv/bin/python source-scripts/city/landmark-identity/stage_proposals.py run --sources-stable
```

The adapter verifies overlay input hashes, exact active database metadata, retained tile bytes, completed acquisition reports and verifier results. Reproducible ignored relative symlinks expose nested acquisition manifests to the unchanged existing cache scanner. Staged model provenance resolves to actual pinned source paths, and native source hashes remain unchanged. Generated geometry stays in ignored `prepared/` and is not a deployment asset.

[Determinism evidence](../../../source-scripts/city/landmark-identity/determinism.json) recomputes in memory, proving byte-identical overlay output without disturbing pinned staging reports. The prior identity and 109-candidate preparation evidence is preserved in [snapshots/pass-1](../../../source-scripts/city/landmark-identity/snapshots/pass-1/). The original bulk reports also remain untouched.
