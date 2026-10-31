# Model optimisation registry — HKS-229

Executor: Devin, 11 October 2026. Framework only; no model processing or historical-map sources. See [the skill](../../../.agents/skills/hong-kong-model-optimisation/SKILL.md) and [runtime contract](../../../docs/astra-city/MODEL-OPTIMISATION.md).

## Setup and migration

Reuse the Python 3.11+ environment and requirements from `../shared-modelling/requirements.txt`. Credentials are read only through the existing pinned `db.connect()`: `MODELLING_DATABASE_URL` or ignored `.env.modelling`. No fallback to application `DATABASE_URL`. No new ORM: this extends the repository's established psycopg/SQL migration conventions rather than introducing a second migration framework.

```sh
python source-scripts/city/model-optimisation/registry.py migrate
python source-scripts/city/model-optimisation/registry.py report
```

Test the SQL on an isolated database before applying to shared Neon. The migration requires the shared jobs table to exist, uses a direct connection, transaction/advisory lock and bounded timeouts. It creates only `optimisation_sources`, `optimisation_variants`, `optimisation_reviews`, indexes and the `optimisation_status` view in `astra_modelling`. Re-running is idempotent; no existing modelling rows are changed. Future migrations must be additive/versioned, not edits that assume CREATE IF NOT EXISTS alters an existing table.

## Explicit plans; no processing

Copy `recipe.example.json` to your batch's documented folder. Use separate recipe files for `original`, `high`, `balanced` and `lightweight`; recipes remain draft until actual settings, exact tool versions and acceptance criteria are chosen. The example is deliberately not an approved compressor preset.

```sh
python source-scripts/city/model-optimisation/registry.py plan \
  --catalogue 3d-viewer/city/data/YOUR-CATALOGUE/catalogue.json \
  --uid landsd/12345:0 --recipe path/to/recipe.json --actor devin-session-unique-id
# Add --apply only to register that explicit source + recipe in Neon.
```

Source file hashes are verified against catalogue `sha256` (the compressed .glb.gz bytes). Source revision identity includes the complete entry, catalogue path, root translation and coordinate metadata. It excludes the git commit so unchanged model inputs can reuse work across commits. Commit remains provenance. Different sources/poses/recipes create distinct records, never overwrite older outcomes. Unrelated entries in the same catalogue do not invalidate this source's identity. Context outside the selected entry (terrain, neighbours, support assets) must still be revalidated at processing/review/publication time.

Planning requires manifest membership and exactly one UID binding across the currently installed catalogues. The viewer manifest, installed catalogues and selected source asset must be committed with no staged or working-tree changes; their bytes are read from one pinned commit. Uninstalled candidates and ambiguous duplicate UIDs are rejected. Commit source installation first, then plan; unrelated working-tree edits do not block planning. Manifest membership alone is not acceptance evidence.

`plan` is a dry run by default. `--apply` does **not** create jobs. `report --uid landsd/12345:0` shows every registered revision, not a claim about which revision is currently installed. Do not sum revisions as unique buildings; compare `revision_id` to a fresh source plan first.

## Future adapter contract

```sh
python source-scripts/city/model-optimisation/registry.py queue --variant SHA256 --batch explicit-batch
```

Queueing is opt-in and rejects draft recipes. Variant identity is global to source + recipe, not batch, so requeueing the same variant cannot run duplicate cross-batch work. A row lock creates/links exactly one shared job atomically. `model-optimisation-v1` is currently unsupported by the worker: it will not execute. Do not pretend queued jobs are running.

A future worker must use the existing `jobs.claim/heartbeat/finish` lease API, verify revision and source hashes before processing, and finish with a JSON result:

```json
{
  "variantId": "<64 hex>", "revisionId": "<64 hex>", "recipeSha256": "<64 hex>",
  "artifact": {"path": "<immutable repository path or object key>", "sha256": "<64 hex>"},
  "metrics": {"downloadBytes": 123, "triangles": 456, "deviceFrameTimeMs": null}
}
```

Numbers above illustrate structure, not accepted measurements. Retain codec name/version, transport encoding, GLB bytes, decoded accessor bytes, resident-memory methodology, normal/position/colour diagnostics and timing environment as additional metrics. The shared queue provides retries, attempt counts, errors, ownership and expiry; terminal failures remain visible. Changing source/recipe creates new work rather than resetting a completed job. Do not silently retry a known unchanged failure under a new batch.

## Review is not publication

`review --variant SHA --decision approved|rejected --actor ID --evidence evidence.json` appends a decision; it never rewrites previous reviews. Evidence must bind the same variant/revision/recipe and the processed artifact SHA. Processing must be complete. Fields:

- `variantId`, `revisionId`, `recipeSha256`, `artifactSha256`.
- `report`: durable report reference; `reportSha256`: exact report bytes; `observation`: reviewer conclusion.
- `gates`: `sourceIdentity`, `geometry`, `placement`, `visual`, `collision`, `devicePerformance`, each `passed` for approval. Rejections may contain failed/untested gates.

This API records an accountable review; it cannot prove a person actually inspected a report or images. Latest decision is displayed; all prior decisions remain. Neither a completed job nor approved review changes viewer assets/catalogues. There is intentionally no publisher in this framework. Track publication later through the existing guarded source-installation protocol and a source-bound runtime variant catalogue; do not equate this ledger to deployment state.

## Verification

```sh
python -m unittest discover -s source-scripts/city/model-optimisation -p 'test_*.py'
python -m compileall -q source-scripts/city/model-optimisation
```

Integration tests opt in with `OPTIMISATION_TEST_DATABASE_URL`, require a localhost database named `astra_optimisation_test_*`, and never use modelling credentials. Do not run fixture writes on shared Neon. No formatter/type-checker is configured for these Python scripts; compile and unittest are the repository-aligned checks.
