# Landmark progress (HKS-199)

Run `python source-scripts/city/landmark-progress/report.py` from the Astra worktree after updating the inventory and bulk report. This only reads the current SQLite inventory and writes documentation. It verifies inventory input hashes before counting installed source IDs.

`reviews.json` is explicit whole-landmark acceptance, keyed by the existing registry ID. Empty records do not mean the city has no detailed buildings: they mean whole-landmark completion has not yet been certified here. Existing component-level acceptance is retained in its original reports.

A review record needs `identityReviewed`, `componentMembershipComplete`, exact `sourceUids`, `checks` (appearance, placement, picking, collision, viewerLoading), `evidence` mapping repository-relative files to SHA256, and no `blockingGaps`. All source components must be installed. Changed membership, missing assets, incomplete checks or changed evidence fail closed. This ledger reports readiness for user review; it does not grant publication or alter geometry.

The 213-entry membership is preserved. Historical interior venues retain their host/scope work. Cached candidates, components and complete landmarks remain separate counters. Proposed identity overlays stay separate until integrated into an updated, source-accounted bulk report.

Tests: `python -m unittest discover -s source-scripts/city/landmark-progress -p 'test_*.py'`.

Source preparation also reads the original acquisition report and subsequent pinned batch reports. It reports checked source absences and acquired matching holds separately from pending downloads. Installed and prepared source parts override older acquisition outcomes. These statuses do not certify whole landmarks or prove territory-wide source absence.
