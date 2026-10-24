# XL component recovery, 8 October 2026

Produced by Codex from the existing government native source receipts and current viewer forms. This pass does not use historical map images or edit model geometry.

The 68 previously unmatched XL sources were routed using exact government GeoRef, tower/podium type, current BuildingCSUID and official ObjectID. Routing produced 64 unique candidates and four missing matches. Routing alone grants no identity or publication approval.

- Four exact original sources already have current installed verification: Cullinan I and II, The Masterpiece and the TWO IFC podium. These are accounting corrections, not new installations.
- Harrow has a different source already published; preserve that publication and do not substitute the older indexed original.
- The other 59 originals were recovered and checked. West Wing is already published but does not have current verification for this source.

R2 restoration was unavailable because cache credentials were not configured. Public government archive ranges recovered 54 exact originals. Five archive ETags and directory hashes had changed; their model IDs remained present. Separately recorded revised-directory downloads recovered all five with the exact original packed hash and byte length. No corrupt model or download was established.

Runtime loading rejected six originals for footprint fit. The remaining 53 underwent full source projection, all-vertex/face-centre/low-rim contact, source graph, foundation and runtime checks against actual current rendered terrain. There were zero installation passes. Independent spatial/contact/foundation failures remain after correcting one metadata-only candidate-selection mismatch (Island Industrial Building). Keep the earlier receipts immutable.

## Receipts

- `routing.json`: exact component routing, 68 sources.
- `restoration.json`: initial local/R2 restoration, two local originals.
- `government-recovery.json`: public pinned-archive recovery, 54 originals.
- `revised-archive-recovery.json`: five changed archive versions with identical original model bytes.
- `current-checks.json`: first 54 runtime/physical outcomes.
- `revised-physical-checks/current-checks.json`: remaining five outcomes.

Every completed result is persisted in Neon and freshly read back. Model assets, downloaded ranges and world geometry remain in the adjacent ignored `local/government-xl-held-component-recovery-20261008` cache. The per-source held audit links all completed work.

## Resume

Use the persisted selection and exact hashes. Do not rerun completed immutable failures until their source/terrain/component evidence or a relevant code correction changes. There is no geometry-edit or architectural AI approval in this pass.

The initial routing runner is retained verbatim because its hash is bound to the receipt. Its old `restore` entry point uses an invalid lease duration and was never executed successfully; use the separately recorded `xl-held-component-source-restore.py` instead. The physical-check runners also remain immutable. Final held records correct the first runner's metadata-only ambiguity without waiving any geometric gate.
