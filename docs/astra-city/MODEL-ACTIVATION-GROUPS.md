# Coordinated original-model activation

Some neighbouring original sources cannot safely coexist with each other’s basic outlines. An optional `activationGroup` array on each catalogue entry names the complete family of source UIDs. Every member must declare the same array, including itself. This is an availability relationship; physical `supportDependencies` remain separate and mandatory.

The planner admits the complete dependency closure within the existing device limits. It rejects missing peers, inconsistent declarations, physical cycles, cycles introduced by grouping, and conflicts with surveyed basic supports. Old catalogues without this field retain their existing loading path. No installed catalogue is changed by this implementation.

One cache flight decodes the entire family sequentially, so mobile concurrency of one does not deadlock while waiting for a peer. Estimated and decoded costs reserve the entire family. External physical supports still activate first. Internal physical supports activate in the same transaction as the rest of the family.

`CityStream.setDetailedModels` prepares every affected basic rendering and collision map before changing the visible state. A failed bake, cancellation, changed tile, changed infrastructure exclusion, or changed detail map discards the preparation. A synchronous commit then changes every affected map and group together. Single-model replacement cannot bypass an explicit group declaration. Complete fallback uses the same transaction.

Travel, Base-only, retry, visibility changes and retirement operate on the family. Failed fallback retains the complete original family and accounts for its resident cost until retry; it does not dispose geometry still used by the scene. Activation peers remain visible across source-tile boundaries with a visible peer.

## Verification and scope

The city Node suite passes 440 tests, including 25 new tests for group metadata/planning, transactional rendering/collision replacement, and loader lifecycle. Real-browser evidence is recorded separately under `government-xl-ocean-four-atomic-lifecycle-browser-v1-20261027`.

The private browser harness serves byte-identical original assets with test-only activation metadata and previously recorded private terrain. It observes state at render calls, exercises complete switching, Base-only, retry after each intentionally failed download, and eviction. Its render observer suppresses continuous GPU rendering and explicitly renders the captured frame. It establishes no frame-rate or mobile performance acceptance.

This software capability does not approve source identity, placement, terrain, collision interfaces, appearance, installation, or publication. Those source-specific decisions and publisher checks remain necessary. No source geometry or production asset compression is changed.
