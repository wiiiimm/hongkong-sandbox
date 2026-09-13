# Shared modelling work — HKS-217

All workers use the shared endpoint pinned in `branch.json`: project `billowing-surf-67227217`, branch `br-icy-silence-b3wjwz0q`, database `neondb`, schema `astra_modelling`. The branch ID is used as its display label because the management API did not provide a verified branch name. Do not delete/reset it: it holds shared work state. Vercel preview branches do not automatically change this pin.

HKS-223 migrated all 21 tables and 2,161,348 rows from the previous project on 9 September 2026. Every table's sorted row hashes and every sequence matched before cutover. Existing destination Neon Auth tables were excluded from the restore. See `docs/astra-city/shared-database-migration.json`. The old endpoint and a private custom-format dump remain available for rollback; R2 objects and keys did not change. Other devices must update this checkout and replace their private worker connection with the new Vercel Development direct URL before resuming. Never run workers against the retired endpoint.

The original source SQLite remains untouched. `inventory_sync.py` stores immutable, indexed source snapshots in PostgreSQL, preserving all source tables and history. `jobs.py` is the live shared queue. Importing a snapshot does **not** enqueue historical pending jobs. Use explicit plans to create new work. Local SQLite exports are compatibility inputs for older source/geometry scripts, not the authority for new shared job status.

## Device setup

Use Python 3.11+ and an isolated virtual environment; install `requirements.txt`. Pull the Vercel environment using the correct linked project, keeping it ignored. Then, from the repository root:

```sh
python source-scripts/city/shared-modelling/configure.py --vercel-env .env.local
python source-scripts/city/shared-modelling/db.py check
```

`configure.py` creates mode-0600 `.env.modelling`, refuses to overwrite it, and selects only the pinned modelling endpoint. It does not edit Vercel's application environment. Use credentials belonging to the pinned replacement project; old-project credentials no longer apply. If credentials rotate, obtain the pinned branch URL from Neon and store it as `MODELLING_DATABASE_URL`. Never commit it. Existing environment variable `MODELLING_DATABASE_URL` takes precedence; application `DATABASE_URL` is never a fallback. `MODELLING_ENV_FILE` can select another private worker env file.

The connection guard rejects other hosts/databases, alternate host-address/service routing and session overrides. TLS verifies the server certificate using the portable certifi CA bundle. Worker operations are scoped to `astra_modelling`; unrelated application and authentication schemas are excluded.

Run `db.py migrate` once when schema changes are reviewed; it uses a transaction lock for schema setup. Normal worker sessions do not rerun migrations. See [INVENTORY.md](INVENTORY.md) for immutable import, indexed lookup and clean-device SQLite export/verification.

## Shared jobs

```sh
python source-scripts/city/shared-modelling/worker.py plan-audit \
  --snapshot SNAPSHOT_SHA256 --batch EXPLICIT_BATCH --uid SOURCE_UID
python source-scripts/city/shared-modelling/worker.py run --batch EXPLICIT_BATCH --workers 4
python source-scripts/city/shared-modelling/worker.py report --batch EXPLICIT_BATCH
```

Run the same batch on multiple devices. Each claim uses a row lock with `SKIP LOCKED`; each attempt has a new UUID token and a server-clock lease. Workers heartbeat while running. Expired claims are reclaimable; stale workers cannot renew or record a result, including when the same worker name is reused. Attempts are bounded. Stable payload-derived job IDs make repeat planning idempotent. Unsupported stages remain untouched. Adapters failing or losing their lease cause a non-zero worker exit.

**Supported adapters:** the existing pure metadata audit and the existing source-preserving cached-model processor. The model adapter requires an explicit source job ID belonging to a named current job set in the immutable snapshot. It verifies code/source hashes, uses a private temporary directory for each attempt, and returns an immutable object reference only after storage readback succeeds. A reclaimed worker may leave an unreferenced immutable object, but cannot replace the accepted job result.

```sh
python source-scripts/city/shared-modelling/worker.py plan-model \
  --snapshot SNAPSHOT_SHA256 --batch EXPLICIT_BATCH \
  --selection CURRENT_SOURCE_JOB_SET --job-id SOURCE_JOB_ID
python source-scripts/city/shared-modelling/worker.py run --batch EXPLICIT_BATCH \
  --workers 4 --enable-models --r2-env .env.local
```

Repeat `--job-id` to select multiple explicit source jobs. Historical pending jobs are never automatically scheduled. Without `--enable-models`, workers claim only metadata audits. With it, R2 configuration is required before any claim. See [MODEL-ADAPTER.md](MODEL-ADAPTER.md) and the R2 requirements for dependencies. The source caches must be restored and verified on each device first. No whole shared catalogue or SQLite is written by either worker adapter.

Terrain reconstruction, browser capture and publication are not automatically made concurrency-safe by a shared database. Those older local scripts require explicit isolated-job wrappers before simultaneous devices can execute them. Do not run legacy local queues as a second shared authority. Candidate preparation still requires terrain/browser/architectural acceptance before publication.

## Cross-session reservations and missing-agent recovery — HKS-218

See [RESERVATIONS.md](RESERVATIONS.md) for atomic source-resource group claims across batches/devices, 30-minute expiry, supervised five-minute heartbeats, release and audited takeover. A job's lease and a session's source reservation serve different scopes; the shared queue's batch-specific job IDs alone do not prevent duplicate source work in another batch. Adopt the reservation workflow for overlapping sessions and use isolated outputs. The supervised wrapper is opt-in and does not automatically intercept existing direct worker or publication commands.

## Working files

R2 bucket `hk-sandbox-assets`, dedicated prefix `astra-modelling/`, is reserved for verified source/cache and prepared outputs. See `docs/astra-city/landmark-resume/R2-WORKING-STORE.md`. Neon stores records and job results; it does not replace these files. A successful local restore is not proof of a cloud upload.

## Verification

```sh
python -m unittest discover -s source-scripts/city/shared-modelling -p 'test_*.py' -v
MODELLING_INTEGRATION_TEST=1 python -m unittest discover \
  -s source-scripts/city/shared-modelling -p test_jobs.py -v
```

The live tests create uniquely named verification batches only on the pinned branch. They leave small test records for evidence. See `VERIFICATION.md` and `inventory-verification.json` for actual run results. Job completion always remains separate from architectural acceptance and runtime publication.

## Database relocation

`migrate_database.py --private-dir PRIVATE_DIRECTORY` restores a checksummed custom-format dump into an absent destination modelling schema. It requires verified source/destination identity records and private connection files; it refuses an existing target schema. It locks source tables during restore/reconciliation, compares all row fingerprints and sequences, and retains private diagnostics. It does not switch worker credentials automatically. Quiesce all workers before taking the dump and keep them stopped through cutover. After successful verification, update the pin and private worker environment together, run `db.py check`, and confirm saved run/checkpoint records. Never rerun a successful restore against an existing schema or drop destination data to bypass the guard.
