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

## Delivery sequence

1. Skill + additive Neon registry, tested in isolation. Shared migration requires the pinned direct credential. No bulk plans or source jobs are seeded automatically.
2. Loader and quality UI on a separate follow-up change; feature works without any generated variants, using enhanced/base fallbacks.
3. Explicitly authorised offline pilot on current accepted sources. Verify output and render evidence on desktop/mobile, then publish selected variants in an isolated PR targeting Astra City. Coordinate with ongoing original-model work via existing reservations and current-source preflight.

## Acceptance before publishing assets

Hash/roundtrip and full-precision equality where promised; finite geometry; surveyed placement and fixed 1x scale; current support/terrain/source dependencies; no incorrect base suppression; shadows and day/night appearance; close-up and distant silhouettes; picking/collision; failed fetch/hash/decode fallback; slider changes during loading; actual mobile frame-time/loading stalls/peak memory. Record environment and untested gaps. Finite visibility sampling and quantisation bits alone are not acceptance.

Related runtime optimisation PR: https://github.com/wiiiimm/hongkong-sandbox/pull/333 . Benchmark context: https://app.devin.ai/sessions/7a81bdca9b0844178241d6788844fec3 . Originals remain the source of truth.
