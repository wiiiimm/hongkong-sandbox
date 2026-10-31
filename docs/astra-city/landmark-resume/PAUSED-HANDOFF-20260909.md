# Astra modelling pause and cross-device hand-off — 9 September 2026

The user requested a pause after the current model work. Manual modelling remains paused. The user subsequently resumed deterministic scripting under HKS-221; that does not authorise starting another manual modelling batch. This is a user-directed pause, not a user-review blocker or a finished-landmarks claim.

## Delivered

The latest installed checkpoint has **269 verified source components:209 new native parts plus60 existing parts reviewed**. Source review snapshot `7d47a5f3c7362e9b` contains539 components. Grand Promenade/Marine Police native integration is `2802a451`; civic support corrections `4ebbc93f`; Lantau24 review `d76b9d89`. Native geometry stays at1×source metres/HKPD. All269 belong to the feature-branch viewer, not a production release.

## Resume state

- Foundation package: `source-scripts/city/residual-support-review/foundation/publication-plan.json`. Two native components255200/255386 are approved in Neon; integration/live acceptance remains.230686 is held because a native upward face remains buried against exact terrain. See adjacent source approval and `docs/astra-city/residual-support-review/foundation/README.md`.
- Cullinan/Elements/China Resources/Oakhill: source, terrain and dependency work is under `source-scripts/city/identity-four-native/`; inspect its final package/README and current Neon states. Do not mistake staged views for installed models.
- Three existing Mui Wo embedded models: `docs/astra-city/landmark-completion-audit/muiwo3-handoff.md`. All12 browser captures are saved. Architectural/source acceptance remains; do not count them as newly installed.
- HKS-220 public progress meter: see `docs/astra-city/building-progress/` and Linear for its final UI status. Its deployed statistics count source forms honestly, not whole landmarks.
- Broader queue still contains identity, source and terrain holds. The original213-landmark objective is not complete. Do not infer regional completion from model-part counts.

## Authoritative records and files

Git branch `codex/astra-hong-kong-city`, draft PR298. Neon branch `astra-modelling` is pinned by `source-scripts/city/shared-modelling/branch.json`. Read `docs/astra-city/model-integration-20260909/current-source-review.json`, then `python source-scripts/city/model-review-ledger/ledger.py status`. Never reimport the historical SQLite checkpoint to overwrite current shared review/job state.

The final R2 manifest and verified restore results will be recorded in `R2-PAUSE-CHECKPOINT-20260909.json` alongside this hand-off. If that file is absent, the final upload is not yet verified: use the older documented checkpoint only with its exact matching Git revision. The source/cache files are separate from production runtime asset delivery.

On another device, read the final checkpoint metadata before switching revisions; install Python dependencies from `source-scripts/city/landmark-resume/requirements.txt` and `source-scripts/city/shared-modelling/requirements.txt`. Obtain private R2/Neon environment values through the authorised Vercel project, keep them out of Git, and validate the pinned Neon branch before any writes. Check out the checkpoint’s `sourceGitCommit`, then run the existing `remote_checkpoint.py restore` with its recorded manifest SHA and a fresh cache as documented in `R2-WORKING-STORE.md`. Restore does not accept a different Git revision.

Read source-specific resume notes, reclaim a fresh canonical source reservation, and dry-run the existing guarded publisher before integration. Old local reservation receipts are invalid after pause. Existing source approval remains reusable only while source/model/terrain dependency hashes still match. Recheck the current viewer after integration; do not repeat source acquisition unless inputs are absent or a deliberate source revision update is needed.

Recommended effort: Medium for restore/scripts; High for architectural, terrain and source-identity judgement. No model work is currently waiting on a user approval.

## Proposed next automated phase (not launched)

The user wants deterministic checks to cover all Hong Kong source forms, then persist their results in Neon so other agents do not repeat the work. Extend the existing inventory/worker/reservation scripts; do not rebuild them or ask AI to inspect each building. Cache checks by canonical UID, source SHA, pipeline version and all relevant terrain/input hashes. Store compact results, failure categories, evidence object hashes and code version in Neon; source and prepared payloads remain in R2. Claim atomically, heartbeat, checkpoint and resume interrupted jobs. Reuse successful checks only while inputs/version match. Produce aggregate reports and route bounded exceptions to later architectural review. Do not promote automated checks to visual acceptance or whole-landmark completion. Respect the user-directed pause: no citywide batch has been launched.
