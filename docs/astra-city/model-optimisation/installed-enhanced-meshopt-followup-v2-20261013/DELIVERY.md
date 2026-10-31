# Nam Fung Court follow-up delivery — 13 October 2026

Executor: Codex, using `.agents/skills/hong-kong-model-optimisation/SKILL.md`.

The latest installed-source check identified Nam Fung Court (`landsd/79099:0`) as the sole addition. All previous 6,649 source revisions were unchanged. Four separate candidates are generated and registered in Neon; all are smaller than its 147,127-byte original: lossless 141,960; high 98,899; balanced 91,587; lightweight 76,558 (47.96% savings). All retain 13,061 triangles. Original source assets and reviews are preserved; current review flags do not filter compression inclusion.

## Commits and stack

- Inventory check: `fa561a8e9`.
- Initial parent sync: `cec5f0485`; source freeze: `77a2703be`.
- Final parent sync: `3a39c911c`, including fetched Astra `177349187a478cd2afac66700e8b0abc52beb56b`. No additional installed-source changes were present; post-sync source validation confirmed all 6,650 revisions still matched.
- Verified artifact/audit delivery: `2a8bb52c8`, pushed to `feature/astra-hong-kong-city-compressed`.
- Updated draft [PR #337](https://github.com/wiiiimm/hongkong-sandbox/pull/337) targets `codex/astra-hong-kong-city`.

## Exact verified evidence

- Installed models: 6,650; complete variants: 26,600; variants per model: four.
- Previously complete results reused: 26,596; new variants generated: four.
- Exclusions/failures: zero; active owned reservations: zero; publication count: zero.
- Frozen source snapshot SHA-256: `176f9f6a846a8dc1e10b3a17ff84d36e98bd24c358051362457eb4b1b8f73098`.
- Final Neon job: `1ef8ffdd367ae6619facce5ab99dc38096149a7a3cfa21261fd80a9b558e5152`, complete with exact readback.
- Final summary SHA-256: `3ecefcff2229d68a42824e70da157be8a7c40947dc009eeaa11cd38fc131fe18`.
- Pinned Neon branch: `br-icy-silence-b3wjwz0q` / `astra_modelling`.
- All four full source/output/derived-decoder/immutable-receipt/Neon audits passed. All 64 finished worker logs archived with exact decompressed SHA-256 preservation.

HKS-229 was updated and independently read back as In Review; parent HKS-199 remains In Progress. Both issue descriptions and the Astra milestone overview contain the delivered 26,600-result count, commit, executor, hashes, measurements, PR and remaining gaps. All three writes/readbacks succeeded. The PR body was updated successfully.

See [README.md](README.md), [summary.json](summary.json), [neon-sync.json](neon-sync.json), [new-model-results.json](new-model-results.json), immutable per-tier readbacks and recipe/source snapshots. The previous 12 October batch and historical exclusion/pilot evidence remain unchanged. Government source provenance is preserved in the frozen catalogue metadata; no historical-map reference images used.

## Remaining validation

No codec or processing code changed for this data follow-up. Existing test baseline: 58 passed, 15 isolated-database fixture skips; every one of the 26,600 current outputs was independently audited in this run. Results remain staged/unreviewed and are not runtime-published. Rendered Float32 placement/terrain/support, visual/day-night inspection, picking/collision, physical-device frame time/peak memory and guarded runtime admission require separate validation. Transfer savings establish neither resident-memory nor FPS improvements; index repacking can increase accessor estimates.
