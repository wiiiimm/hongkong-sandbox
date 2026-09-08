# Shared modelling work — HKS-217

All workers use the persistent **astra-modelling** Neon branch, not the application's production branch or individual device branches. `branch.json` pins project `soft-snow-34493321`, branch `br-icy-firefly-b3zn5ogh` and its endpoint. Changing Vercel preview branches does not change this worker configuration. Do not delete/reset this branch: it holds shared work state.

The original source SQLite remains untouched. `inventory_sync.py` stores immutable, indexed source snapshots in PostgreSQL, preserving all source tables and history. `jobs.py` is the live shared queue. Importing a snapshot does **not** enqueue historical pending jobs. Use explicit plans to create new work. Local SQLite exports are compatibility inputs for older source/geometry scripts, not the authority for new shared job status.

## Device setup

Use Python 3.11+ and an isolated virtual environment; install `requirements.txt`. Pull the Vercel environment using the correct linked project, keeping it ignored. Then, from the repository root:

```sh
python source-scripts/city/shared-modelling/configure.py --vercel-env .env.local
python source-scripts/city/shared-modelling/db.py check
```

`configure.py` creates mode-0600 `.env.modelling`, refuses to overwrite it, and selects only the pinned modelling endpoint. It does not edit Vercel's application environment. The new branch inherits its parent's role credentials; if they are later rotated independently, obtain the modelling branch URL from Neon and store it as `MODELLING_DATABASE_URL`. Never commit it. Existing environment variable `MODELLING_DATABASE_URL` takes precedence; application `DATABASE_URL` is never a fallback. `MODELLING_ENV_FILE` can select another private worker env file.

The connection guard rejects other hosts/databases, alternate host-address/service routing and session overrides. TLS verifies the server certificate using the portable certifi CA bundle. No production schema is modified.

Run `db.py migrate` once when schema changes are reviewed; it uses a transaction lock for schema setup. Normal worker sessions do not rerun migrations. See [INVENTORY.md](INVENTORY.md) for immutable import, indexed lookup and clean-device SQLite export/verification.

## Shared jobs

```sh
python source-scripts/city/shared-modelling/worker.py plan-audit \
  --snapshot SNAPSHOT_SHA256 --batch EXPLICIT_BATCH --uid SOURCE_UID
python source-scripts/city/shared-modelling/worker.py run --batch EXPLICIT_BATCH --workers 4
python source-scripts/city/shared-modelling/worker.py report --batch EXPLICIT_BATCH
```

Run the same batch on multiple devices. Each claim uses a row lock with `SKIP LOCKED`; each attempt has a new UUID token and a server-clock lease. Workers heartbeat while running. Expired claims are reclaimable; stale workers cannot renew or record a result, including when the same worker name is reused. Attempts are bounded. Stable payload-derived job IDs make repeat planning idempotent. Unsupported stages remain untouched. Adapters failing or losing their lease cause a non-zero worker exit.

**Current worker adapter:** the existing pure building metadata audit, using frozen building/model records read directly from Neon. This adapter needs no local SQLite or model cache. Geometry conversion, terrain changes, browser checks and publication are not automatically made concurrency-safe by a shared database. They remain the existing local scripts until explicitly wrapped with isolated per-job outputs and verified R2 inputs. Never run those legacy scripts concurrently in one shared checkout or import their local queue as active work. Future adapters must produce immutable object keys and publish the result only after successful token-fenced completion; arbitrary commands are not accepted from job payloads.

## Working files

R2 bucket `hk-sandbox-assets`, dedicated prefix `astra-modelling/`, is reserved for verified source/cache and prepared outputs. See `docs/astra-city/landmark-resume/R2-WORKING-STORE.md`. Neon stores records and job results; it does not replace these files. A successful local restore is not proof of a cloud upload.

## Verification

```sh
python -m unittest discover -s source-scripts/city/shared-modelling -p 'test_*.py' -v
MODELLING_INTEGRATION_TEST=1 python -m unittest discover \
  -s source-scripts/city/shared-modelling -p test_jobs.py -v
```

The live tests create uniquely named verification batches only on the pinned branch. They leave small test records for evidence. See `VERIFICATION.md` and `inventory-verification.json` for actual run results. Job completion always remains separate from architectural acceptance and runtime publication.
