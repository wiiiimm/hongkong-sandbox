---
name: hong-kong-model-improvement
description: Resume and run source-backed building and landmark improvements in hongkong-sandbox, including government model acquisition, batch preparation, terrain and assembly review, and cross-device recovery. Use for model-quality work, not ordinary city UI changes.
metadata:
  version: "1.8.2"
---

# Hong Kong model improvement

Use the existing Astra pipeline. Current user scope permits AI for code and non-modelling work only. Use scripts for identity joins, downloads, conversion, validation and reporting; leave AI modelling and architectural judgement pending until explicitly authorised.

## Resume cheaply

Locate the intended checkout with Git and read its `AGENTS.md`. Do not assume the main checkout, a previous machine's absolute paths, or a remembered task status is current. All project paths below are relative to that checkout.

Read `docs/astra-city/landmark-progress/progress.json`, `docs/astra-city/landmark-preflight/summary.json` and the latest entry in `docs/astra-city/LINEAR-TRACKING.md`. Inspect only relevant rows and summaries; do not dump the full government index or model manifests into context. Verify branch, input hashes and current Linear issues before reporting progress.

For a different device or missing local caches, read [references/resume.md](references/resume.md) first. A cloned repository is not proof that ignored source payloads or the SQLite job ledger are present.

## Reuse verified work and original government detail

User direction, 11 September 2026: remove full skip-screening from the import pipeline. Reuse current accepted decisions and source/model hashes to avoid repeat work. Do not run metadata or shape-comparison sampling as an enhancement prerequisite. The 6,000-form experiment found only 24 potential new skips, all already containing detailed geometry; its results remain historical diagnostics, not an import queue or acceptance proof.

Use the shared acceptance planner in `source-scripts/city/enhancement-screening/README.md` for existing ledger/hash checks. Skip unchanged `enhanced` and `good-to-go` forms; preserve explicit rework decisions and required dependency models. Recheck current inputs after obtaining source ownership. Offline plans are previews, never shared authority.

For other forms, proceed directly to cached government source lookup and scripted identity, component, placement/support and runtime validation. `unassessed` does not require a new good-enough assessment or an `enhancement-required` event before mechanical preparation. It also does not authorise AI modelling or imply that enhancement is needed. Reuse original government detail by default; integrate only subsets that pass the existing acceptance and guarded publication requirements. Source downloads or clean diagnostics alone are not publication approval.

Keep the current model when the source is missing, ambiguous or fails validation. Record the reason for scripted investigation and continue independent work. The agent owns batch routing; do not ask the user to decide individual buildings. Simplify original detail only when measured runtime costs justify local scripted reductions. High/Light describe mesh detail, not AI reasoning effort.

Keep source-form counting and the existing evidenced acceptance ledger. Public progress separates total map models, exact government-source matches and completed work within that source group; see `source-scripts/city/building-progress/README.md`. New good-to-go/rework records still require current input/evidence hashes and live source ownership. Historical pilot candidates grant no progress credit. No source form automatically completes a whole landmark or region.

## Inventory size groups and future passes

User direction, 11 September 2026: store several size brackets in Neon before
building queues. See `source-scripts/city/government-import/size-groups/README.md`.
Use the indexed, source-bound XS/Small/Medium/Large/XL/XXL groups and separate
Unmeasured group. Raw triangle counts, download/decoded geometry bytes and native
physical dimensions remain separate. Complexity does not establish visual quality,
AI effort, acceptance or whether enhancement is worthwhile. Classification must
not create a queue or change a model's work/review status.

For later authorised import batches, prefer a broad scripted first pass: install
passing original meshes, persist exact held reasons/checks/input and source hashes
in Neon, then investigate shared blocker categories during a second pass. Reuse
unchanged completed evidence. Preserve repository/R2 evidence references and
identify local-only caches honestly. Do not spend per-building AI effort chasing
exceptions during the broad pass. Current scope is classification/storage only;
queue construction is explicitly deferred.

## Local processing and AI-token constraint

User direction, 11 September 2026: government-model enhancement must run as ordinary local processes with **zero per-model AI calls**. Source lookup/restoration, decoding, conversion, validation, optional measured LOD generation and import orchestration use deterministic scripts. Government downloads and Neon/R2 cache/result syncing are ordinary data transfers, not AI processing. Reuse exact cached assets/results before repeating work; do not run an agent or visual-review loop for every building.

AI is permitted only for developing/fixing code and other non-modelling work. Do not invoke AI for geometry generation, model refinement, simplification, per-building architectural judgement or reconstruction. No automatic AI retry or fallback is allowed. If a case cannot be resolved mechanically and would require AI modelling or architectural judgement, retain its current model, leave that case pending and notify the user before that work starts. Continue independent scripted work without waiting on that case.

Use the existing source, placement, runtime, ownership and publication guards. Keeping the process local does not waive these checks or turn unresolved cases into accepted models. Runtime scripts make zero AI calls; AI-assisted code development is not a zero-token claim for the overall session.

## Scripted acceptance of original government imports

User direction, 11 September 2026: advance the clear subset through automated
acceptance; per-building AI architectural review is not a required import step.
Use the documented `source-scripts/city/government-import/DIRECT-IMPORT-POLICY.md`
contract for unchanged original meshes. Exact source/identity, current input hashes,
conservative drawn-terrain/contact checks, existing holds, runtime budgets and real
browser loading/picking/collision/fallback evidence remain required. Record the
scripted method and bounded scope through the existing fenced review/publisher.
This accepts a faithful source port, not architectural reconstruction or whole-landmark
completion. Models outside this contract keep their current fallback and explicit
pending reason; do not waive a failed check to reach a target batch count.

## Report status in the user’s six stages

User direction, 11 September 2026: retain detailed Neon/job/review statuses and
map them to a separate human report. Do not change the shared schema, acceptance
states or progress credit merely to rename a status. Follow
[references/human-status.md](references/human-status.md) for the mapping and report
contract. This applies to chat updates, final reports and cross-device handoffs.

Lead with **Installed**, **To do**, **Held for human decision**, **Held for AI
processing**, **Held for unknown state**, and **In process**. Technical terms such
as advanced, runtime-validated, awaiting acceptance, pending or held are supporting
check details, never unexplained top-level statuses. Every selected source form
has exactly one human status; report the original batch denominator.

The key distinction is who or what is needed next. More local CPU work, downloads,
script repairs, terrain/source investigation or automatic checks mean **In process**
(queued or running), not an AI/human hold. AI-assisted code development is not
per-model AI processing. A human hold requires an exact unanswered user decision;
an AI hold requires a documented need for AI modelling/architectural judgement.
A failed script or missing source does not establish either. **Held for unknown
state** is for an unclassified blocker or unreliable state, with a concrete next
investigation step. Keep those cases visible; do not silently equate unknown with AI.

**In process** means started and unfinished, including queued scripted follow-up;
state queued/running separately and never imply a live worker without evidence.
**Installed** requires current verified integration, not downloaded/prepared data.
**To do** means not started. Reclassifying reports grants no acceptance or deployment
credit and does not authorise AI work. Continue autonomous scripted work within the
user’s scope; notify before any AI modelling or necessary human decision.

## Choose the phase

- **Mechanical preparation:** follow [references/pipeline.md](references/pipeline.md). Reuse exact IDs, caches, pinned source batches and existing packers. Medium effort is generally sufficient. Parallelise independent sheet requests and processing, but coordinate a single SQLite writer and one process per acquisition batch.
- **Architectural improvement:** only begin when the user explicitly re-enables that work; it is currently paused under the token constraint above. Prefer original detailed government geometry and use AI only where identity, placement or missing architecture requires judgement. Keep geometry detail separate from reasoning effort; choose reasoning effort for the actual unresolved problem. Read the per-landmark preflight rows, native geometry and source evidence; do not reconstruct every building individually when a supported batch correction applies.
- **Acceptance and integration:** use the existing review and guarded publisher mechanisms with fresh evidence for the selected components. A previously approved sample is not approval for another batch.

The user may park modelling after a mechanical pass. Finish the agreed pass, record the hand-off, and leave the later modelling phase pending; do not silently continue it.

## Territory-wide native preparation

For HKS-222, read `source-scripts/city/citywide-native/README.md` and the latest evidence under `docs/astra-city/citywide-native/`. Use its existing shared Neon stage results before downloading or converting anything. A complete source catalogue (HKS-221) alone is not complete native acquisition. The native runner records each indexed model outcome and checksum-verified original/prepared R2 bundles. It has its own fenced stage leases and per-attempt folders; do not run a competing SQLite writer for these jobs. Medium effort is sufficient for running and diagnosing mechanical failures.

If inputs and code match, reuse the exact completed stage. If conversion code changes, reuse original source bundles through `source_cache.py`, then rerun the changed stage with new fingerprints. Do not re-fetch government files just because the local cache is absent. Never interpret candidate or diagnostic states as installed, architecturally accepted or region-complete. Investigate failed/unsupported-source outcomes before declaring that only AI-heavy modelling remains.

## Reserve concurrent work

Before parallel sessions process or edit overlapping model parts, follow `source-scripts/city/shared-modelling/RESERVATIONS.md` on the shared, pinned Neon branch. Reserve all canonical source keys for the intended group atomically, including the complete building UID and polygon suffix (for example `building:landsd/123456:0`); batch names do not isolate ownership. Use a unique session owner and receipt per group. Wrap long-running commands with `reservations.py run` so the script renews a 30-minute lease every five minutes while work is alive. For interactive modelling, heartbeat at work checkpoints; never leave an unattended keepalive daemon.

If ownership is lost, stop and reacquire before continuing. Expired work can be reclaimed normally; an explicit takeover requires the observed token snapshot and a reason. Keep separate worktrees/outputs, check ownership before shared edits, and retain the publisher's own guards: reservations do not atomically lock arbitrary files or R2 publication. Session/audit history remains after lease expiry. Do not discard expired work's evidence or imply that its models were accepted.

## Preserve these invariants

- Native **1× metres/HKPD** throughout terrain, models, water, bridges, collision and cameras. Do not port the old vertical multiplier or move surveyed elevations to hide a terrain problem.
- Comprehensive government footprints, downloaded government 3D geometry and OSM data are distinct sources. Preserve stable IDs, provenance, irregular outlines, holes and multipart geometry. Unnamed buildings and estimated heights retain their basic forms.
- Exact identity and component membership matter. Nearby or similarly named objects, unnamed podiums and historical replacements are not automatically interchangeable. Proposals remain proposals until reviewed.
- Keep download absence, incomplete source coverage, acquired matching holds, prepared candidates, installed parts and whole-landmark readiness separate. A complete job queue does not resolve an unknown identity or approve placement.
- Preserve native model bytes and node transforms. Changed source revisions/ZIP offsets require a new pinned batch, retaining the old evidence. Do not bypass matching, checksum, completeness or budget checks to reach a target count.
- Sampled ground gaps may describe a supported tower or overhang; terrain above a base may describe legitimate foundations. Inspect context before correcting either. A bounding-box support hint is not a triangle-level proof.
- Gallery capture is not visual acceptance. Check actual loaded candidate IDs, camera occupancy/occlusion, framing and the rendered artefact. Saved screenshots, CPU loading tests and a clear camera do not establish complete architecture, walking routes, rooftop landing or mobile performance.
- Approved detailed geometry replaces its corresponding fallback without duplicates; held or unavailable geometry keeps a usable fallback. Validate streaming, picking, collision and existing lighting behaviour after integration.

## Record modelling effort

For every new model review/refinement, follow `source-scripts/city/model-review-ledger/README.md` (HKS-224). Pass explicit effort metadata with the existing fenced `record` / `record_many` operation: geometry method, AI model and actual reasoning setting, run/job and output references where available. Use a stable request ID for retries and a new ID for a revision. Record measured token/time values only when attributable; omit unknown values. Never infer historic effort from appearance, agent name or the current session setting. Inspect `ledger.py history --uid CANONICAL_UID` before revising a model. Lightweight/detailed method does not itself imply acceptance.

## Deliver and track

Use the existing HKS issue/milestone mapping in local tracking and Linear. Record the executor, commit, source and rendered counts, evidence and remaining gaps in relevant leaf issues and parents. Move implemented, reviewable scope to **In Review**; leave broader identity, architecture or regional scope open when incomplete.

Use the existing Linear `model` and `Workflow` label groups. For this Astra workflow, tag agent work `gpt-6-astra` and `ai-software-factory`; switch the workflow label to `human-review-required` only for a concrete deliverable awaiting named human sign-off, with the reviewer, review link and exact checks recorded. Preserve unrelated labels and other models' attribution. Agent architectural/terrain review remains software-factory work. Human review of a completed slice does not automatically block other work. Explain required user action directly in chat; never rely on an ambiguous In Review status. Recommend Low reasoning effort for tracking, Medium for routine scripting, and heavier reasoning only for a specific unresolved architectural/terrain exception; retaining a High detail government mesh does not itself require a high-effort AI run. Do not treat an effort switch as a blocker.

Run checks appropriate to the change. For model integration, inspect real browser output as well as source/CPU checks; measure performance only when making performance claims. Commit logical units with HKS references and use the requested branch/PR workflow.

A skill invocation does not grant deployment, R2-upload or release permission. Honour the user's actual authorisation. Keep working-state snapshots separate from production runtime assets and do not describe local staging as deployed content.
