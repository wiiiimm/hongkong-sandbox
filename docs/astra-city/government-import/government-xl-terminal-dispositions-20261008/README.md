# All XL source dispositions — 8 October 2026

Codex completed the full indexed XL source audit for HKS-199. The user replaced the earlier 100-new-installation target with accounting for every XL source as installed, fixed, rejected or filed as currently uninstallable.

| Disposition | Sources |
| --- | ---: |
| Installed and verified in the current viewer/review snapshot | 190 |
| Filed in Neon as currently uninstallable; revisit later | 331 |
| Open / in process | 0 |
| Total indexed XL government sources | 521 |

There are 453 sources with a matched viewer UID and 68 without a unique match. Counts describe source models/components, not distinct physical buildings. The older 352-source work cohort is a subset, not the full XL inventory.

## Filed reasons

| Primary reason group | Sources |
| --- | ---: |
| component support | 4 |
| other validation failure | 6 |
| source identity or component coverage | 197 |
| terrain affects neighbours | 69 |
| terrain or foundation | 55 |

Each filing records its source key, source hash, failed checks, evidence and revisit trigger. These are source-specific failures under the recorded original-source checks, not permanent rejection of the building. The current model remains in place; filing grants no enhancement or installation credit. The 68 unmatched sources are included in the identity/component group.

Hoi Tai podium `landsd/229881:0` remains deferred. Its wall clearance and the separate original tower support evidence remain unresolved after the completed authorised AI evidence review. No architectural intent or safe geometry recovery was established. See the dedicated Hoi Tai deferred-disposition record; do not repeat unchanged checks.

## Verification and provenance

- Native inventory run: `e98f84fdaeb489b229af3910d80d765bb87dbbdc565ec1794836b04909f370ec`.
- Current installed review snapshot: `0bfd3d30d478e6f8`.
- Verified Neon completion job: `45458a23d2c11f669c52d00c32c9511e91211bc246bc56e9e686244bbf2b9ff2`.
- `audit.json.gz` contains all 521 rows and their installed review or individual filing job IDs. `neon-sync.json` records fresh database readback of the completion job.
- The auditor verifies current catalogue/asset bytes and all installed review evidence-file hashes. Legacy reviews bind the source hash in the review row; newer results repeat it internally. Both formats require the same current review/source/asset agreement.
- Court of Final Appeal and Western Market were already published. Their two missing current verification records were recovered after fresh identity/contact/foundation/runtime and staged/live desktop/mobile day/night, picking/collision and failed-load/retry checks. This adds **zero new runtime model installations**.
- Cullinan West Tower 5 received a fresh check against its installed original support. Four of 652 strict contacts remain unresolved, with contact/compound-foundation failures, now filed in Neon.
- No source geometry, pose, terrain or acceptance limits were changed. Scripts made zero external AI calls. AI was used for code and non-modelling work; no AI modelling was performed in this completion pass.
- No historical Lantau map imagery was used. Government source provenance remains attached to the recorded native results and source hashes.

The completion audit is immutable evidence. Revisit an individual source only when its recorded trigger changes; do not rerun all unchanged failures or turn a deferred filing into installation credit.
