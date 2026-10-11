# Model optimisation registry — HKS-229

Executor: Devin, 11 October 2026. Framework only; no model processing or historical-map sources. See [the skill](../../../.agents/skills/hong-kong-model-optimisation/SKILL.md) and [runtime contract](../../../docs/astra-city/MODEL-OPTIMISATION.md).

## Setup and migration

Reuse the Python 3.11+ environment and requirements from `../shared-modelling/requirements.txt`. Credentials are read only through the existing pinned `db.connect()`: `MODELLING_DATABASE_URL` or ignored `.env.modelling`. No fallback to application `DATABASE_URL`. No new ORM: this extends the repository's established psycopg/SQL migration conventions rather than introducing a second migration framework.

```sh
python source-scripts/city/model-optimisation/registry.py migrate
python source-scripts/city/model-optimisation/registry.py report
```

Test the SQL on an isolated database before applying to shared Neon. The migration requires the shared jobs table to exist, uses a direct connection, transaction/advisory lock and bounded timeouts. It creates only `optimisation_sources`, `optimisation_variants`, `optimisation_reviews`, indexes and the `optimisation_status` view in `astra_modelling`. Re-running is idempotent; no existing modelling rows are changed. Future migrations must be additive/versioned, not edits that assume CREATE IF NOT EXISTS alters an existing table.

## Explicit plans

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

## Processing adapter contract

```sh
python source-scripts/city/model-optimisation/registry.py queue --variant SHA256 --batch explicit-batch
```

Queueing is opt-in and rejects draft recipes. Variant identity is global to source + recipe, not batch, so requeueing the same variant cannot run duplicate cross-batch work. A row lock creates/links exactly one shared job atomically. The general modelling worker deliberately ignores `model-optimisation-v1`. The explicit `batch.py` adapter implements this stage only for its pinned ready lossless recipe. Queueing alone does not start that adapter.

Processing workers must use the existing `jobs.claim/heartbeat/finish` lease API, verify revision and source hashes before processing, and finish with a JSON result:

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

## Explicit accepted-model compression (12 October 2026)

`batch.py snapshot` freezes every installed UID and selects only sources with `publicationApproved=true` or `placementReviewed=true`, while any explicit negative publication/identity field takes precedence. Missing acceptance is held, including historically visible/screened models. Full source/coordinate/assembly metadata, catalogue membership and source bytes are verified against a single commit with no staged source changes.

`codec.mjs` encodes bufferViews using Meshopt 0.24.0 ATTRIBUTES / INDICES, filter NONE, and gzip level 9. It performs no quantisation, simplification, cleanup, welding, triangle rotation or reordering. The independent viewer decoder must reproduce every bufferView byte and unchanged accessors, materials, nodes/scenes and transforms, including unused vertices and degenerate faces. Unsupported/textured/nonfinite sources fail explicitly. Entire GLB.gzip sizes are compared with the existing gzip source. Larger outputs are retained and marked non-beneficial, rather than reported as savings.

```sh
cd source-scripts/city/model-optimisation
npm ci --ignore-scripts
npm test
cd ../../..
python source-scripts/city/model-optimisation/batch.py snapshot --output docs/astra-city/model-optimisation/BATCH/sources.json
# Use the exact selected/pinned recipe, not recipe.example.json.
python source-scripts/city/model-optimisation/batch.py launch \
  --snapshot docs/astra-city/model-optimisation/BATCH/sources.json \
  --recipe docs/astra-city/model-optimisation/BATCH/recipe.json \
  --output source-scripts/city/model-optimisation/staging/BATCH \
  --batch BATCH --workers 4
```

The launcher validates the full source snapshot once and hash-binds its preflight to the committed worker and selected inventory. Each worker verifies that receipt, current catalogues, recipe/tools and each source/output hash. Up to 16 ordinary processes partition groups of at most 100 UIDs, keeping each connected support family together; no source manifest edits occur. Each group reserves selected buildings, source hashes and named support dependencies. Conflicting reservations wait without takeover. Registrations use the existing globally revision/recipe-unique identities and one linked shared job per variant. Jobs claim only IDs in the currently reserved group, including jobs from an earlier invocation/batch, and use the shared heartbeat/finish stale-token fencing. Connections stay pinned and transactions end before encoding. Completed results are reused; interrupted receipts remain immutable. Unknown failures are retained and not automatically retried under new batches.

Neon results are processing-complete/unreviewed, with source/output hashes and exact measurements. Only sourceIdentity and geometry gates pass these offline checks; current physical placement, visual, collision and devicePerformance gates remain untested. Device frame time and peak memory are null. Accessor bytes are a resident estimate, not measured peak or total GPU/JS memory. Compression savings imply no FPS or resident-memory reduction. No variant catalogue is published.

Current batch evidence: `docs/astra-city/model-optimisation/accepted-enhanced-meshopt-lossless-v1-20261012/`. Original model acceptance and installation ledgers are preserved. No historical-map imagery is used.

After processing, independently read back Neon, receipt hashes and all source/output bufferViews:

```sh
python source-scripts/city/model-optimisation/audit.py \
  --snapshot docs/astra-city/model-optimisation/BATCH/sources.json \
  --recipe docs/astra-city/model-optimisation/BATCH/recipe.json \
  --output docs/astra-city/model-optimisation/BATCH/readback-UNIQUE-RUN.json \
  --batch BATCH-audit --apply
```

Use a fresh audit filename on later runs: reports include measured audit duration and are immutable. `--apply` adds a fenced batch checkpoint, including held-source reasons by immutable inventory reference; it does not approve variants or alter original model installation records. The audit refuses incomplete batches or mismatched source/recipe/result/output hashes.
