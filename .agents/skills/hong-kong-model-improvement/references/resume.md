# Resume on another device

Read `docs/astra-city/landmark-resume/PAUSED-HANDOFF-20260909.md` first. Its final `R2-PAUSE-CHECKPOINT-20260909.json` records the newest verified checkpoint when present; earlier checkpoint files below are historical. The current model-review pointer is `docs/astra-city/model-integration-20260909/current-source-review.json`.

The skill is versioned with the project under `.agents/skills/`. Fetch the relevant branch/commit on the new device before invoking it. A copied standalone skill still requires the project and its working material.

The 8 September 2026 checkpoint uses `codex/astra-hong-kong-city` and draft PR #298. Treat that as a historical routing hint: verify current tracking and remote state. Further modelling was intentionally parked after mechanical preparation. HKS-215 tracks this hand-off; HKS-212 retains identity/component questions, HKS-213 source acquisition, and HKS-214 architectural review/integration.

## Concurrent workers (HKS-217)

Use the persistent `astra-modelling` Neon branch, with the explicit configuration and commands in `source-scripts/city/shared-modelling/README.md`. Every device must use that same branch. The shared queue supports atomic claims, expiring leases and stale-worker fencing. Immutable inventory snapshots preserve SQLite history and can recreate a compatibility SQLite on a clean device. The metadata audit and source-preserving cached-model adapter support shared workers; terrain/browser/publication scripts are not automatically migrated. Do not run their local queue as a second authority.

R2 implementation and cloud verification are tracked separately in HKS-216. Read `docs/astra-city/landmark-resume/R2-VERIFICATION.md` for actual remote status before assuming a working snapshot is available.

## Session ownership and recovery (HKS-218)

Read `source-scripts/city/shared-modelling/RESERVATIONS.md` before starting overlapping batches. The job queue protects individual job IDs; resource reservations add cross-batch ownership of canonical building source keys. Use atomic group claims, the supervised `run` command for automatic five-minute heartbeats, explicit manual checkpoints for interactive work, and release when finished. The 30-minute work lease is independent of retained session/audit history. After a disconnect, check ownership rather than trusting a local receipt. Expired claims can be reclaimed; live takeover needs a fresh ownership snapshot and a recorded reason.

Keep using isolated outputs and existing publication guards. The wrapper supervises the selected command, not every process or arbitrary future AI action. Migration, commands and recovery examples live in the reservation runbook rather than being duplicated here.

## What travels where

| Material | Portable home | Recovery |
| --- | --- | --- |
| Code, skills, committed viewer inputs, source plans/ledgers, reports, acceptance records | Git at an exact commit | Fetch/check out the intended commit |
| `building-batch/local/buildings.sqlite` | Consistent SQLite backup in a versioned working snapshot | Restore the backup, or rebuild the inventory and recreate selections/jobs from verified inputs |
| Native model/terrain members, compact source ZIPs, ignored selection files and source reference material | Verified file/object-store snapshot, such as R2 | Restore relative paths and verify hashes/source revisions |
| Prepared GLBs/catalogues and pinned local preflight snapshots | Working snapshot, or regenerate from restored sources | Verify against reports before reuse |
| Generated symlinks, virtual environments, node_modules, browser binaries | Rebuild locally | Use current scripts/dependencies; do not transfer absolute symlinks blindly |
| Production runtime assets | Existing production asset workflow (HKS-206) | Separate release manifest; working-cache storage is not production deployment |

See `docs/astra-city/landmark-resume/CACHE-PLAN.md` and its inventory for the measured working-state closure and current recovery gaps. Do not assume those assets are in R2 until an upload manifest and remote checks prove it.

The chosen persistent Neon branch is now authoritative for current shared reviews, reservations and job results. The restored SQLite is historical compatibility/source inventory only. Do not overwrite Neon state from that historical database, and do not infer current acceptance from its old jobs. Files remain in the separately verified Git/R2 checkpoint.

## Cold-clone gate

Before running `status.py` or `stage_proposals.py check`, check whether `source-scripts/city/building-batch/local/buildings.sqlite` and the required prepared/source files exist. Both commands require local prerequisites; the latter also imports geometry dependencies. With no database, start with a Git/file/hash audit of tracked evidence. During a read-only request, report missing material without creating a database or fetching data.

The cache inventory describes the originating machine. Its recorded existence values and stored hashes are not proof of files on this device or of an uploaded snapshot. The collector is an originating-machine inventory tool that writes its report and needs local inputs; it is not a cold-clone doctor. Its overlapping profiles must not be added together as a minimum download estimate.

## Restore procedure

1. Read current Linear/local hand-off and identify the exact code revision and working snapshot. Ensure no other machine is actively publishing or writing the shared logical job state.
2. Restore tracked inputs and ignored working files to repository-relative paths. Verify the snapshot manifest, file sizes and hashes. Keep the original source revision/provenance; an unavailable historical download is not interchangeable with today's source.
3. Restore the recorded **historical, consistent** SQLite backup only for compatible source tools; current shared review/job status comes from Neon. Use SQLite's backup API while quiescent, or a properly checkpointed closed database when creating the snapshot; do not copy only the main file from an active WAL database. Never overwrite a newer job ledger blindly.
4. If rebuilding instead, run the inventory script against the complete intended viewer inputs. It reconstructs the source inventory, not every historical selection/job lease or uncommitted review decision. Recreate the selected preparation from its tracked config and restored sources; use the explicit Node path flag documented in `pipeline.md`.
5. Set up local Python/Node/browser dependencies and regenerate convenience symlinks. Some older example commands contain personal paths; resolve executables on this device rather than copying those paths.
6. Run read-only current-status checks and source/native verification before scheduling work. Refresh inventory when viewer hashes changed. Existing pinned plans with absent ignored payloads need restoration or a deliberate rebuild, not a claim that their work is complete.
7. Resume only the requested phase. After the next accepted checkpoint, update Git/Linear and create a new versioned working snapshot if transfer is authorised.

## R2 working snapshots

A useful snapshot records Git revision, schema/runtime notes, source revisions, file paths/sizes/hashes, a consistent SQLite backup and the relationship to earlier snapshots. Keep engineering caches in a working-state namespace separate from runtime release assets. Transfer verified bytes without moving models or modifying source geometry.

Creating this skill does not upload material. The current hand-off must state whether a snapshot is merely planned, prepared locally, uploaded, or verified remotely. Credentials, `.env` files and unrelated personal files do not belong in the snapshot. Stop source and database writers at the snapshot boundary so the manifest and files describe one consistent state.

## Verified cloud checkpoint

The 8 September R2 upload and fresh-cache clean-checkout restore passed. Resolve the exact sourceGitCommit and manifestSHA256 from docs/astra-city/landmark-resume/R2-CLOUD-CHECKPOINT.json, then use remote_checkpoint.py restore as documented in R2-WORKING-STORE.md. Do not restore against a different Git revision. This checkpoint restores working files/history; live shared jobs remain on the pinned astra-modelling Neon branch. Full source and selection checks passed after restoration. Different-OS runtime setup is still untested.
