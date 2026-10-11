# HKS-213 · Remaining identity sources, batch 1

Executor: Codex acquisition agent. Source input is the pinned HKS-212 stage summary (SHA-256 `1c1f69e9c8700926b27a861421322c7bbc62695b261df92f7e182f0b270cf6be`). The original 115-target checkpoint remains unchanged. No reference-map images were used.

All **152 targets across 40 official sheets** are exhausted for this snapshot:

- **119 native models acquired/staged**, including **112 exact-CSUID matches** and **7 conservative matching holds**.
- **33 targets have no exact model** in their complete checked official sheet directories.
- **0 acquisition deferrals**. Source absence and acquired matching holds are explicit terminal acquisition outcomes, not outstanding downloads.
- **238 native members** verified, with 21 complete directories and 18 members reused from matching retained caches; 220 new members.
- **15,818,627 response bytes** including fresh official service/index metadata, within the recorded 500 MB cumulative envelope. Four sheet workers shared locked durable reservations. No monolithic tile archive was downloaded.
- Native directory counts/offsets, CRC/length, compact-cache SHA-256, staged source hashes and unchanged **1× HKPD** coordinates passed for all 40 sheets.
- A second invocation transferred **0 bytes**, with no additional requests. Eight focused tests passed, including mixed-schema target parsing, concurrent byte reservations and atomic concurrent JSON readers/writers.

The seven source-acquired matching holds are Queensway Government Offices (`landsd/142159:0`), Flagstaff House Museum of Tea Ware and the K.S. Lo Gallery (`landsd/143421:0`), The Masterpiece (`landsd/205478:0`), Island Shangri-La (`landsd/235988:0`), Hong Kong West Kowloon Station (`landsd/297401:0`), Airport Terminal 1 (`landsd/314191:0`), and Aigburth (`landsd/93890:0`). Their native models are available, but the existing decoder did not establish an exact footprint/CSUID match. Downloading them again would not resolve that hold.

`report.json` retains per-target `uid`, `outcome`, `standardMatch`, `models`, and `sheetsChecked` fields. `verification.json` records payload checks; `first-run.log` and `resume-run.log` record transfer behaviour. Local source manifests are in `source-scripts/city/landmark-acquisition/batches/identity-v1-remaining/staged/*/manifest.json`.

No geometry, terrain, registry, shared SQLite or runtime files were changed. Acquisition and native staging do not establish accepted placement, published availability, or landmark completion. Any architectural reconstruction or difficult terrain/placement correction still requires a separate higher-effort modelling pass.
