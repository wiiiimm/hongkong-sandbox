---
name: hong-kong-model-optimisation
description: Plan, track and validate source-preserving Astra City model optimisation and precision/LOD variants. Use when compressing detailed models, creating quality-slider assets, preparing Meshopt/Draco variants, tracking optimisation in Neon, or resuming a per-model optimisation batch. Not permission to alter source geometry or publish unreviewed variants.
metadata:
  version: "1.1.0"
---

# Hong Kong model optimisation

## Scope and entry points

This skill complements `hong-kong-model-improvement`, which owns original model acquisition, identity, placement and installation. Never treat acquisition/install completion as optimisation acceptance. Read `source-scripts/city/model-optimisation/README.md` for the registry API and `docs/astra-city/MODEL-OPTIMISATION.md` for the quality/runtime contract. Paths are relative to this repository root; the skill requires the repository's scripts, not just a standalone copied SKILL.md.

The original registry framework has no automatic enqueue or publisher. Explicit `batch.py` adapters support full-precision Meshopt and guarded lossy high/balanced/lightweight candidates. Outputs are private processing artifacts, not approved quality presets. Do not run optimisation merely because this skill is installed. Require an explicit selected batch and authorisation to process. User instruction, 12 October 2026: ignore review flags for compression inclusion; every installed model needs variants. Use the explicit `installed-v1` policy for this authorised cohort; preserve original review records. This changes processing selection, not geometry validation or publication state.

## Non-negotiable rules

- Keep original government assets immutable. Variants are separate derived artifacts with source UID, compressed-source SHA-256, full placement/assembly metadata, source commit, recipe hash and output hash. No generated substitute geometry or invented details.
- Fixed 1x world scale and surveyed HKPD elevations. Codec dequantisation transforms must preserve world placement; never introduce vertical exaggeration.
- Precision (quantisation), detail (triangle simplification), geometry codec and transport compression are separate choices. Lossless compression after a lossy variant preserves that variant, not the original. Explicitly disable unwanted quantisation and cleanup when claiming losslessness.
- Choose a codec per variant; do not stack Draco and Meshopt on one primitive. Existing source files already use gzip. Measure whole delivered files, codec startup/worker costs and resident memory; do not double-count gzip savings or promise FPS from bytes.
- No variant inherits acceptance from another revision, recipe or output. Source/terrain/support changes require current physical and runtime preflight, even when this registry's source identity is unchanged. A registry row is evidence bookkeeping, not proof or deployment authority.

## Workflow

1. Read latest Astra feature-branch instructions and freeze explicit UIDs from committed installed catalogues. Under the user-authorised `installed-v1` processing policy, missing/negative review flags do not exclude installed assets. They remain metadata, not inherited variant approval. Retain `accepted-v1` when auditing older frozen batches. Never infer installation/quality acceptance from a filename, visibility, historical pending job or a whole landmark's label.
2. Use the pinned modelling connection, `source-scripts/city/shared-modelling/branch.json`. Never substitute an application database or change the host guard. Migrations are additive, reviewed and use the direct URL. Without credentials, prepare code and report the database step pending.
3. Dry-run `registry.py plan` for each UID and recipe. Source bytes are hashed; complete selected catalogue entry and coordinate metadata are frozen. `--apply` registers plans only. Begin with original/high/balanced/lightweight as **labels**, not universal bit counts. Base is runtime fallback, not a derived model job; Auto is runtime selection, not an asset.
4. Use `queue` or the explicit `batch.py launch` adapter only with a pinned ready recipe after implementation/code review. Reuse the shared job leases, heartbeat and stale-token fencing for `model-optimisation-v1`. Existing workers intentionally ignore that stage. Reserve `building:<full UID>` and actual shared dependencies with the existing reservations layer before overlapping source work. No parallel edits to live manifest or original assets.
5. Generate into a private staging directory, keeping negatives and failed attempts. Write immutable content-addressed artifacts. Read back hashes before reporting processing complete. Record original/output transfer bytes, accessor and resident estimates, vertices/triangles, precision/error diagnostics and environment-specific timing. Missing measurements stay null/untested, never zero or passed.
6. Validate decoder roundtrip, attributes/topology where claimed exact, finite coordinates, world placement/bounds, supported extensions, collision/support semantics and source provenance. Draco Edgebreaker can remove repeated-position zero-area faces even without quantisation: disclose this as cleanup, not strict topology preservation.
7. Review rendered close and distant views, silhouettes, roofs, undersides/openings, day/night, shadows, picking/collisions and desktop/mobile load/fallback behaviour. Quantisation bit counts are not a visual-error guarantee. Screen-space simplification budgets are hypotheses until validated. Record all six registry gates and immutable evidence references; never rubber-stamp them from pipeline success.
8. Keep processing complete, quality approved and published distinct. Approval requires an exact-output review; publication additionally rechecks current sources/context, runtime schema/decoder compatibility, budgets, source-model coexistence and the existing guarded publication protocol. Only approved compatible variants may enter a runtime catalogue. Never mark a model published merely by writing an approval row.
9. Commit focused changes on a separate branch/PR targeting Astra City, update the relevant HKS issue/parent/milestone and local notes with executor, hashes, measurements and remaining gaps. Leave original installation work untouched. Unavailable or failed variants must fall back enhanced -> base; explicit Base-only mode must not request variants/enhanced geometry.

## Evidence so far (not approved presets)

The 11 October 2026 three-model experiment (Lui Seng Chun, Saxon Tower, HSBC Main Building) found whole gzip GLBs of 12.59 MB original, 11.84 MB full-precision Meshopt, 7.87 MB unquantised Draco Edgebreaker, 5.86 MB quantised Meshopt and 1.68 MB quantised Draco. Draco had higher warm NodeIO decode/parse cost; quantisation collapsed some tiny faces. None establishes phone FPS or visual acceptance. Benchmark context: https://app.devin.ai/sessions/7a81bdca9b0844178241d6788844fec3 . Re-measure on current source hashes rather than applying these percentages city-wide.

## Explicit compression adapter

For the authorised complete installed-model batch, run `batch.py snapshot --selection-policy installed-v1`. Source asset/catalogue/manifest bytes and coordinate identity still require committed hash checks; review flags do not filter processing. `batch.py launch` performs source-bound planning, leased execution and Neon result updates with bounded ordinary workers; general modelling workers still ignore this stage. The lossless adapter preserves all bufferView bytes, indices/corner order, unused vertices, degenerate faces and metadata. The distinct lossy adapter applies measured bounded position/normal/colour rounding and conservative attribute-aware simplification, restores positions to prevent rounding-induced face collapse/reversal/degenerate expansion, and verifies exact decoding against the derived mesh. Simplifier error remains an estimate, not a visual/Hausdorff guarantee. Keep non-beneficial outputs and failed attempts. Only measured smaller whole gzip outputs earn transfer savings. See `docs/astra-city/model-optimisation/installed-enhanced-meshopt-variants-v2-20261012/` and the registry README for reproducible commands, the historical skip audit and exact batch scope. No variant approval/publication is inherited from installation or pipeline success.
