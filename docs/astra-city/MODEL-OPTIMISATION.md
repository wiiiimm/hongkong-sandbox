# Model variants and quality selection — HKS-229

Devin, 11 October 2026. No reference-map imagery used. Framework and future runtime contract; no optimised assets or quality presets are approved by this document.

## Product decisions

- Offline source -> validated precision/LOD variants -> lossless geometry encoding where beneficial -> transport compression. Runtime selects already-built assets; no simplification on the phone.
- User slider's first position is **Base only**: keep the existing first-loaded basic models and do not download detailed geometry. Other positions select lightweight/balanced/high/original preferences. Auto chooses a device-appropriate preference. Auto and Base are not processing jobs.
- Projected screen size, frustum/distance visibility and device triangle/memory budgets remain authoritative. A maximum-quality preference does not request every original city model simultaneously.
- No optimised variant available, invalid metadata, unsupported codec or failed decode: try the existing enhanced source; if that fails, retain base. Abort/camera movement is not a reason to begin another download.
- Upgrades should keep the current visual until the replacement is ready. Apply hysteresis/debounce, cancel obsolete requests, respect shared memory budgets/cache eviction and avoid downgrade/upgrade thrashing.
- Visual LOD and exact collision/support requirements are distinct. Until separately validated, do not substitute simplified surfaces into collision or physical-support logic or claim full resident-memory savings while retaining originals for collisions.

## Asset and database identities

One UID can have multiple immutable source revisions; one revision can have multiple recipes at the same named quality level. A recipe identifies exact tools, precision, simplification/error policy, codec, transport and acceptance policy. Each recipe/output must be independently tested. No universal bit count/triangle ratio is safe for all buildings.

The registry lives under `source-scripts/city/model-optimisation`. It adds only source/variant/review state to the pinned Neon modelling schema and reuses shared job leases. Plans do not enqueue; queueing does not implement a processor; processing does not approve; approval does not publish. Existing native model acceptance and optimisation acceptance must not overwrite each other.

The static viewer must not query Neon. A later guarded publisher will export only source-matching, output-hash-bound approved variants to a deployable catalogue. Include source SHA/context, variant/recipe ID, output SHA, tier, bounds, placement/collision policy, required codec/extensions, compressed/GLB/decoded sizes, vertex/triangle counts and validated screen-space range. Preserve original enhanced entries so fallback remains available. Loader contract/version and supported decoders must be explicit, never inferred from a filename.

### Runtime loading contract

Optional descriptors are read only from the catalogue's top-level `optimisedVariants` array. They bind to the catalogue source bytes and to `sourceMetadataSha256`, computed as SHA-256 over UTF-8 JSON after recursively sorting object keys (array order is retained) for `{entry, rootTranslation, crs, verticalDatum, coordinatePolicy, datasetId}`. This is a JavaScript canonical JSON serialization; it is distinct from the optimisation registry's immutable revision SHA. Invalid or stale optional descriptors are ignored without invalidating the native catalogue. Variant metadata cannot replace source pose, support, or suppression relationships.

The viewer uses the approved selected variant first, then the existing enhanced/native source, and finally leaves the basic form visible if both fail. Base-only mode starts no detail geometry requests while keeping the shared compressed-byte cache alive. Variant decode/fetch failures are remembered by variant ID until explicit Retry. Native-to-variant and variant-to-native changes are same-UID atomic replacements: the current model remains installed until the replacement is fetched, decoded, validated and admitted. Peak admission counts the candidate together with held geometry, including the old resident; a replacement that cannot fit is deferred and the old model is retained. Budget deferral is not classified as a corrupt variant.

Native GLBs remain decoder-free. Selected variants may declare only `none`, Meshopt, or Draco; external buffers, all images (including embedded images), and undeclared extensions are rejected. Variants are geometry-only until texture memory has a separately validated budget. Draco assets are vendored from Three.js r160, Meshopt from meshoptimizer 0.24.0, and codec modules are initialized lazily with a single worker where supported. Decode failure falls back to the source model. Tests exercise synthetic lifecycle/validation cases; browser Draco decoding and actual quantised-asset rendering remain unverified coverage gaps.

No approved presets or optimised assets currently exist in the repository. Publishing remains a future, separately authorised operation; this runtime integration does not generate or process model assets.

## Delivery sequence

1. Skill + additive Neon registry, tested in isolation. Shared migration requires the pinned direct credential. No bulk plans or source jobs are seeded automatically.
2. Loader and quality UI on a separate follow-up change; feature works without any generated variants, using enhanced/base fallbacks.
3. Explicitly authorised offline pilot on current accepted sources. Verify output and render evidence on desktop/mobile, then publish selected variants in an isolated PR targeting Astra City. Coordinate with ongoing original-model work via existing reservations and current-source preflight.

## Acceptance before publishing assets

Hash/roundtrip and full-precision equality where promised; finite geometry; surveyed placement and fixed 1x scale; current support/terrain/source dependencies; no incorrect base suppression; shadows and day/night appearance; close-up and distant silhouettes; picking/collision; failed fetch/hash/decode fallback; slider changes during loading; actual mobile frame-time/loading stalls/peak memory. Record environment and untested gaps. Finite visibility sampling and quantisation bits alone are not acceptance.

Related runtime optimisation PR: https://github.com/wiiiimm/hongkong-sandbox/pull/333 . Benchmark context: https://app.devin.ai/sessions/7a81bdca9b0844178241d6788844fec3 . Originals remain the source of truth.

## Offline compression adapter — 12 October 2026

Codex added the explicit lossless Meshopt adapter on `feature/astra-hong-kong-city-compressed`, stacked on `codex/astra-hong-kong-city`. The accepted installed-source batch is frozen at `113625f3fe156b04453814d2cbcb33b78feaeafe`: 6,649 installed UIDs inventoried, 4,272 explicitly accepted sources selected, 2,377 missing/negative acceptance entries held. This is an offline processing slice, with separate content-addressed staging artifacts and Neon optimisation results. It does not provide approved quality presets or change the runtime catalogue. See the batch report in `model-optimisation/accepted-enhanced-meshopt-lossless-v1-20261012/README.md` for final measurements, complete UID lists and remaining gates.

## Complete installed-source variants — 12 October 2026

The user subsequently authorised processing every installed asset while ignoring review flags as inclusion criteria. The explicit `installed-v1` policy now includes all 6,649 UIDs with zero exclusions. Originals, source reviews and runtime catalogues remain unchanged. The historical 2,377-UID audit diagnoses the catalogue/Neon discrepancies without altering review history.

Each UID has one lossless and three distinct lossy high/balanced/lightweight candidates: 26,596 complete variants, zero failures, all source/output/derived-decoder/receipt/Neon audits verified and zero active batch reservations. Effective potential transfer savings, retaining originals wherever candidates are larger, are 7.28% / 36.89% / 43.23% / 49.72%. Only the lossless candidate is exact against original geometry; other candidates are exact against their measured derived mesh. Position rounding preserves tiny-face validity and fixed scene poses. Actual LOD triangle reductions are only 2.82% / 3.93%, and UInt32 index repacking leaves estimated accessor bytes slightly higher than the original corpus. This is transfer-size improvement, not measured resident-memory or frame-time improvement.

See `model-optimisation/installed-enhanced-meshopt-variants-v2-20261012/README.md` and its immutable summary/checkpoints for exact recipes, counts, bytes, geometry/error diagnostics, tests and gaps. Candidates are staged and unreviewed; current rendered Float32 placement/terrain/support, visual/collision, device performance and runtime publication remain distinct from processing inclusion.
