---
name: hong-kong-model-improvement
description: Resume and run source-backed building and landmark improvements in hongkong-sandbox, including government model acquisition, batch preparation, terrain and assembly review, and cross-device recovery. Use for model-quality work, not ordinary city UI changes.
metadata:
  version: "1.1.0"
---

# Hong Kong model improvement

Use the existing Astra pipeline. Spend model reasoning on architectural decisions and exceptions; use scripts for identity joins, downloads, conversion, validation and reporting.

## Resume cheaply

Locate the intended checkout with Git and read its `AGENTS.md`. Do not assume the main checkout, a previous machine's absolute paths, or a remembered task status is current. All project paths below are relative to that checkout.

Read `docs/astra-city/landmark-progress/progress.json`, `docs/astra-city/landmark-preflight/summary.json` and the latest entry in `docs/astra-city/LINEAR-TRACKING.md`. Inspect only relevant rows and summaries; do not dump the full government index or model manifests into context. Verify branch, input hashes and current Linear issues before reporting progress.

For a different device or missing local caches, read [references/resume.md](references/resume.md) first. A cloned repository is not proof that ignored source payloads or the SQLite job ledger are present.

## Choose the phase

- **Mechanical preparation:** follow [references/pipeline.md](references/pipeline.md). Reuse exact IDs, caches, pinned source batches and existing packers. Medium effort is generally sufficient. Parallelise independent sheet requests and processing, but coordinate a single SQLite writer and one process per acquisition batch.
- **Architectural improvement:** only begin when requested. Prefer High effort for tower/podium membership, foundations, terrain or source conflicts. Read the per-landmark preflight rows, native geometry and source evidence; do not reconstruct every building individually when a supported batch correction applies.
- **Acceptance and integration:** use the existing review and guarded publisher mechanisms with fresh evidence for the selected components. A previously approved sample is not approval for another batch.

The user may park modelling after a mechanical pass. Finish the agreed pass, record the hand-off, and leave the later modelling phase pending; do not silently continue it.

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

## Deliver and track

Use the existing HKS issue/milestone mapping in local tracking and Linear. Record the executor, commit, source and rendered counts, evidence and remaining gaps in relevant leaf issues and parents. Move implemented, reviewable scope to **In Review**; leave broader identity, architecture or regional scope open when incomplete.

Use the existing Linear `model` and `Workflow` label groups. For this Astra workflow, tag agent work `gpt-6-astra` and `ai-software-factory`; switch the workflow label to `human-review-required` only for a concrete deliverable awaiting named human sign-off, with the reviewer, review link and exact checks recorded. Preserve unrelated labels and other models' attribution. Agent architectural/terrain review remains software-factory work. Human review of a completed slice does not automatically block other work. Explain required user action directly in chat; never rely on an ambiguous In Review status. Recommend Low effort for tracking, Medium for routine scripting and High for architectural/terrain decisions without treating an effort switch as a blocker.

Run checks appropriate to the change. For model integration, inspect real browser output as well as source/CPU checks; measure performance only when making performance claims. Commit logical units with HKS references and use the requested branch/PR workflow.

A skill invocation does not grant deployment, R2-upload or release permission. Honour the user's actual authorisation. Keep working-state snapshots separate from production runtime assets and do not describe local staging as deployed content.
