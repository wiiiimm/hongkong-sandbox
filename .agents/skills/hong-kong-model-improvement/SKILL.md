---
name: hong-kong-model-improvement
description: Resume and run source-backed building and landmark improvements in hongkong-sandbox, including government model acquisition, batch preparation, terrain and assembly review, and cross-device recovery. Use for model-quality work, not ordinary city UI changes.
metadata:
  version: "1.5.0"
---

# Hong Kong model improvement

Use the existing Astra pipeline. Current user scope permits AI for code and non-modelling work only. Use scripts for identity joins, downloads, conversion, validation and reporting; leave AI modelling and architectural judgement pending until explicitly authorised.

## Resume cheaply

Locate the intended checkout with Git and read its `AGENTS.md`. Do not assume the main checkout, a previous machine's absolute paths, or a remembered task status is current. All project paths below are relative to that checkout.

Read `docs/astra-city/landmark-progress/progress.json`, `docs/astra-city/landmark-preflight/summary.json` and the latest entry in `docs/astra-city/LINEAR-TRACKING.md`. Inspect only relevant rows and summaries; do not dump the full government index or model manifests into context. Verify branch, input hashes and current Linear issues before reporting progress.

For a different device or missing local caches, read [references/resume.md](references/resume.md) first. A cloned repository is not proof that ignored source payloads or the SQLite job ledger are present.

## Screen before enhancement

User direction, 10 September 2026: reduce unnecessary work. Existing buildings that are good enough should be skipped, not remodelled to inflate enhancement counts. Follow `source-scripts/city/enhancement-screening/README.md` before scheduling enhancement work.

Run the shared screening planner against the current rendered inputs. Its three outputs are `skip`, `enhance`, and `assess`. Skip current `good-to-go` and existing verified `enhanced` forms. Only an explicit current `enhancement-required` decision enters enhancement work. `unassessed` means assess cheaply first; it does not justify launching a modelling run. Offline plans are previews, never the shared authority. Recheck after obtaining the source reservation and before expensive work; a changed model, evidence or context must not reuse stale acceptance.

Assess the actual city representation, not the deliberately unstyled comparison baseline. Name the missing recognisable feature and normal-view benefit before upgrading. User preference updated later on 10 September 2026: the original High detail comparison looks better than Light. Prefer direct reuse of suitable detailed government geometry; preserve its architectural detail by default. Simplify only for a demonstrated runtime need, with visual comparison of what is lost. High/Light in the comparison describe mesh detail, not AI reasoning effort. AI reconstruction is unnecessary where suitable government geometry exists; use reasoning for identity, placement, source gaps and acceptance. Do not equate polygon count, a source download, a clean diagnostic audit, or an ordinary-building label with visual adequacy. Uncertain cases remain unassessed. Record accepted good-to-go/rework decisions with current input hashes, evidence and live source ownership; do not replace the model acceptance ledger.

The public chart counts enhanced, good to go, enhancement required and not screened as mutually exclusive source-form categories. Good-to-go decisions earn progress without geometry changes. Skip applies to optional enhancement only: still retain dependency models and perform required source, terrain, identity and safety checks. No source form automatically completes a whole landmark or region.

## Token constraint and shape screening

User direction, 10 September 2026: processing power is acceptable, but AI tokens are only for code and other non-modelling work. Do not invoke AI for geometry generation, per-building visual/architectural judgement or reconstruction. If a case requires AI modelling, leave it pending and notify the user before proceeding. Continue independent scripted work. The user does not want a building-by-building skip/enhance approval workflow.

Extend/reuse `source-scripts/city/enhancement-screening/screen.py compare` for deterministic current-versus-government shape comparisons. Preserve original detail; use fixed multi-view silhouettes, roof/depth evidence and current fingerprints. The old triangle-ceiling pilot is a historical baseline, not the decision rule. Cache mechanical results by source, geometry, context, policy and engine hashes. Separate shape benefit from identity, support/terrain and runtime gates. Position-only changes are not extra architectural detail. No automatic per-model AI fallback.

Current shape comparison is a bounded validation/dry-run stage. Synthetic geometry tests and landmark regressions validate the implementation, not citywide perceptual acceptance. Do not grant new good-to-go credit or publish import candidates until an evidenced acceptance rule is validated and the existing fenced recording/publication checks pass. Missing/ambiguous sources and unresolved context remain pending. AI-assisted code development is not a zero-token claim for the overall session; runtime script AI calls must be zero.

## Choose the phase

- **Mechanical preparation:** follow [references/pipeline.md](references/pipeline.md). Reuse exact IDs, caches, pinned source batches and existing packers. Medium effort is generally sufficient. Parallelise independent sheet requests and processing, but coordinate a single SQLite writer and one process per acquisition batch.
- **Architectural improvement:** only begin when the user explicitly re-enables that work; it is currently paused under the token constraint below. Prefer original detailed government geometry and use AI only where identity, placement or missing architecture requires judgement. Keep geometry detail separate from reasoning effort; choose reasoning effort for the actual unresolved problem. Read the per-landmark preflight rows, native geometry and source evidence; do not reconstruct every building individually when a supported batch correction applies.
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
