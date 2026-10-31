# Installed-model compression handoff — 12 October 2026

Executor: Codex, using `.agents/skills/hong-kong-model-optimisation/SKILL.md`.

All 6,649 installed models have four complete staged variants: exact lossless (original), high, balanced and lightweight. There are 26,596 verified Neon results, zero skipped assets and zero failures. The user explicitly authorised ignoring review flags for processing selection; original source assets and review records remain unchanged. The historic 2,377 excluded UIDs are audited separately.

## Delivery and tracking

- Draft PR: https://github.com/wiiiimm/hongkong-sandbox/pull/337, targeting `codex/astra-hong-kong-city`.
- Implementation: `98f67761c`; exclusion audit: `0faada4d5`; full immutable evidence: `fc91d2e3b`.
- Latest parent synchronization: `7cd3c67511eb8b5a80ea131dc1e19ed303766b25`. After synchronization, all frozen source inputs still matched: 6,649 selected, zero excluded. No compression changes to `3d-viewer/`.
- HKS-229 is In Review; parent HKS-199 remains In Progress. Both issues and the Astra milestone were updated successfully and independently read back with the new 26,596-result delivery checkpoint. Older accepted-only counts are explicitly superseded.
- The existing PR description was updated successfully after verifying its destination and the invoked skill's PR delivery requirement. An initial automatic approval rejection was resolved through these checks; no delivery action remains blocked.

## Immutable evidence

See [README.md](README.md), [summary.json](summary.json), [sources.json](sources.json), four recipe files, per-tier readbacks, [neon-sync.json](neon-sync.json) and [verification.json](verification.json).

- Frozen source commit: `a5a2abd1bddec61df1735960fdda10342f5eee08`.
- Source snapshot SHA-256: `f8834523fcb11b0824eef1f5c0193239bfd3f7af6dfb0c81981daa38a5faed77`.
- Final report SHA-256: `f39ee4c1186ebb696918228e258e0b5a3d447c3f3053c981c4efd8db4ee94f96`.
- Final Neon checkpoint: `ba4295de39bf82fd5705c95863c503d8399c4e95b401c11fee4292ef0d66905f`, complete with exact readback in `billowing-surf-67227217` / `br-icy-silence-b3wjwz0q` / `astra_modelling`.
- Four full source/artifact/derived-decoder/receipt/Neon audits passed; 58 tests passed, 15 isolated-database fixture tests skipped, zero failures. Zero active batch reservations at final delivery verification.
- 4,272 earlier lossless results reused; 22,324 additional results produced. Non-beneficial outputs and unsuccessful pilot evidence retained. Original provenance remains in frozen catalogue metadata; no historical-map reference images used.

## Measurements and remaining work

| Tier | Smaller outputs | Potential gzip transfer savings |
| --- | ---: | ---: |
| Lossless/original | 504 | 12.45 MB / 7.28% |
| High | 1,794 | 63.06 MB / 36.89% |
| Balanced | 2,342 | 73.89 MB / 43.23% |
| Lightweight | 3,133 | 84.99 MB / 49.72% |

Savings retain originals wherever candidates are larger, against a 170.94 MB gzip source corpus. Actual balanced/lightweight triangle reductions are 2.82%/3.93%. UInt32 index repacking increases accessor estimates slightly; no resident-memory or FPS improvement is established. All lossy outputs have zero rounding-induced collapse/reversal/degenerate-expansion regressions.

Processing and Neon registration are complete. Variants remain unreviewed and staged; no runtime catalogue publication. Current rendered Float32 placement/terrain/support, visual/day-night inspection, picking/collision, and physical-device frame time/peak memory require separate validation before quality approval/publication.
