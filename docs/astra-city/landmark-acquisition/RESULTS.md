# HKS-213 verified first acquisition checkpoint

Produced by the Codex acquisition subagent on 8 September 2026. This pass uses retained government source geometry and official tile metadata; no reference maps, registry rows, shared SQLite state, terrain or viewer runtime were changed. No new geometry was modelled.

| Result | Count |
|---|---:|
| Exact-ID missing-cache source parts planned | 115 |
| Official source sheets fully checked | 45 |
| Unique native models acquired and staged | 88 |
| Targets passing the decoder’s exact-CSUID match | 82 |
| Acquired models held for match review | 6 |
| Parts with no exact model in complete checked sheets | 27 |
| Deferred source parts | 0 |
| Complete retained directories reused | 10 |
| Retained native members reused | 18 |
| New native members downloaded | 158 |
| Native members verified | 176 |

The pass received **14,302,166 bytes (14.3 MB)** against its 100,000,000-byte cumulative cap. This includes 1,450,345 bytes of live official service/index metadata and 12,851,821 bytes during model acquisition. It used one sequential network worker. A completed restart made zero new requests and transferred **0 additional bytes**; the cumulative ledger remains unchanged.

Verification passed all 45 complete directories, compact-cache SHA-256 values, native member CRC/length/SHA-256 values, staged source-file hashes and the unchanged native 1× HKPD/root-translation policy. Five focused tests passed for directory completeness, exact member decoding, ignored-Range refusal, persistent transfer reservations and provenance-header filtering. Retained HTTP headers are restricted to provenance; no cookie/session headers remain.

## Match-review holds

These exact-reference source models were acquired, but none passed the existing conservative footprint/CSUID matching screen. They must remain separate from the 82 matched targets. Resolving them needs identity/geometry/placement review; it does not authorise moving native geometry or automatically replacing the fallback.

| Target | UID | Native model |
|---|---|---|
| Hong Kong West Kowloon Station | landsd/297401:0 | B350631826101063C0 |
| Hong Kong International Airport Terminal 1 | landsd/314191:0 | B113491963101063C0 |
| The Masterpiece | landsd/205478:0 | B359541762701063C0 |
| ISLAND SHANGRI-LA | landsd/235988:0 | B349791533602063C0 |
| Queensway Government Offices | landsd/142159:0 | B349391545601063C0 |
| Aigburth | landsd/93890:0 | B338111495801063C0 |

The other 27 outcomes mean no exact-reference model was present in all complete current official sheet directories checked for that retained footprint. This is not a blanket claim that the government has no model elsewhere. Acquisition, identity matching, placement acceptance and whole-landmark completion remain separate. Any reconstructive modelling or source/terrain placement repair should be a separate, higher-effort task; this pass was entirely mechanical.

## Evidence and hand-off

- `report.json`: target-by-target outcomes, exact-CSUID distinctions, source IDs, checksums, native bounds and source-sheet checks.
- `verification.json`: all 45 sheet/cache/member/staged checks passed, with zero errors.
- `first-run.log`: actual sequential acquisition output.
- `resume-run.log`: completed restart with zero additional transfer.
- `source-scripts/city/landmark-acquisition/README.md`: runnable commands and the reuse/cap/restart policy.
- `source-scripts/city/landmark-acquisition/staged/*/manifest.json`: stable inputs for the existing cached-model processing adapter.

All staged manifests are stable and the identity-integration agent has been notified that it may scan them. Source/model staging does not approve placement or publication. The root agent owns HKS-213 tracking and any subsequent shared processing.
