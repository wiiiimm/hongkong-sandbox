# Foundation review pause checkpoint — HKS-214

Two components are approved for integration: **255200 Dynasty Club / Convention Plaza podium** and **255386 Convention Plaza Office Tower**. The plan passes the existing publisher dry-run: two native models, no terrain changes, no estimated-base changes. Both source assets retain their original checksums and elevations. The Office Tower requires the native podium.

Normal and isolated views were inspected. The podium's wider normal view has 16/21 source rays; ten unrelated model groups retain their fallbacks under the existing rendering budget. The reviewed parts remain active without errors. The podium has 755 upward faces and 483 sampled roofs, with no fully buried upward face or roof. The tower has 721 upward faces and 371 sampled roofs, also clear; all nine low-rim points contact its native podium. Some podium foundation vertices are below both the native terrain and existing terrain; this was not corrected by moving geometry.

**230686 is held separately.** Its exact source name is B337351515902063C0; it must not be labelled The Merton. The original and exact-terrain browser views are retained. Exact TIN improves rim contact from 4/26 to 21/26, and all eight neighbouring footprint checks show no new flags. Five source rim points remain below grade and one upward source triangle remains buried, requiring explicit retaining-bank/source-face judgement. No terrain candidate is approved for publication.

## Resume on another machine

Restore the parent Git/R2 checkpoint and use the pinned Neon branch. Read checkpoint.json, approval.json and hillside/decision.json first. Claim the two approved source keys before running any integration. The exact next validation command for their existing plan is:

```sh
python source-scripts/city/island-detail-integration/publish.py source-scripts/city/residual-support-review/foundation/publication-plan.json
```

This is a dry-run. Publication and installed browser checks remain a separate, reserved operation. Do not run foundation.py to resume: it is the original claim/staging command. The shared snapshot may have advanced; resolve the current pointer before writing the ledger.

For the held source, claim building:landsd/230686:0 first. Existing diagnostic commands (no acquisition, no publication):

```sh
node source-scripts/city/residual-support-review/foundation-hillside-check.mjs
node source-scripts/city/residual-support-review/foundation-hillside-browser.generated.mjs
```

The native exact patch is under foundation/hillside/exact-tin/. Its parent was terrain-central.json SHA2207e6d0e933daf100ea5240b974d7346da96ec169d5c199346fdee1a3a276d7 when generated. Reconcile any changed parent before publication; preserve other reviewed child patches. The Python terrain generator uses cached official TIN sources; no new downloads are necessary for this checkpoint. Native geometry, native elevations and vertical scale1 remain unchanged.

A source component approval is not a complete landmark or region. No source was published by this review pass. The parent task records the final cloud checkpoint and issue status.
