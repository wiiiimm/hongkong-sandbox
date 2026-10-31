# Atomic originals with a suppressed BASIC feature

Codex, HKS-203, 28 October 2026. No source geometry or historical map imagery used.

The private Elegant sixteen-source browser decoded originals but rejected activation: `Atomic replacement requires every suppressed source in the group: landsd/99061:0`. Negative Neon browser receipts are `bbd78b599ff22dde431fedc39bd2bb1561adef0c958c36b022e55d0c339b6b66` and `3423c88183909109a922c13f31f5120aae02456db3f36a8cfab4eba59e300182`. The latter records exact wanted/cache/errors/support availability and confirms the actual rejection. No model installation or approval followed.

A BASIC suppression target is an affected fallback record, not another native asset. `AtomicModelGroups` now includes an explicit `[basicUid, null]` in the stream transaction when an old or new group owner suppresses that source. This includes activation, Base-only/eviction, visibility switching and rollback. `CityStreaming.setDetailedModels` is unchanged: it still requires every suppression target in the transaction and stages fallback meshes, collision maps and native groups before one synchronous commit.

The helper refuses to silently remove another managed detailed source. Such a source requires an explicit group replacement. New suppression requires a loaded BASIC source and rejects embedded geometry. Retiring an old suppression can include an unloaded BASIC target, since no visible tile then needs restoration. Native group membership, physical support dependencies, count/memory/triangle limits and publisher guards remain unchanged.

Validation: all 19 activation/group lifecycle tests pass, including BASIC suppression activation/Base-only, preservation of another active detailed source and rejection of missing/embedded targets. All 12 streaming tests pass. Actual private desktop/mobile failure/retry/Base-only/suppression restoration checks run separately; these unit results do not approve the sixteen-model installation or claim performance gains.
