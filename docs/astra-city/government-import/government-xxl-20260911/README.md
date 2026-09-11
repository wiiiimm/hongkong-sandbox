# Government XXL first pass — 11 September 2026

Codex/Astra processed the frozen 22 XXL government source parts after the user authorised this bounded batch. Original government detail, coordinates and elevations are preserved. No AI modelling, architectural scoring, simplification or geometry/terrain changes were used.

| Final user status | Source parts |
| --- | ---: |
| Installed | 4 |
| To do | 0 |
| Held for human decision | 0 |
| Held for AI processing | 0 |
| Held for unknown state / grouped second pass | 18 |
| In process | 0 |

**Newly installed:** Hong Kong Central Library (`landsd/227428:0`), 145,359 triangles, 4,065,809 compressed bytes. The other three installations reuse verified current government hashes: HSBC, Two IFC and the M+ podium. These are source-part counts, not whole-landmark completion.

The 18 holds comprise 10 strict footprint/centroid fit failures, five sources without a unique current viewer match, and three terrain/support contact failures. No AI or human-decision dependency has been established. See [the grouped second-pass handoff](SECOND-PASS.md) and [all 22 final statuses](human-status.csv). Retain current models while these exceptions remain unresolved.

## Verification and provenance

The original Lands Department assets are bound to native run `e98f84fdaeb489b229af3910d80d765bb87dbbdc565ec1794836b04909f370ec`, frozen source IDs, cache keys and SHA-256 hashes in `selection.json.gz`. Four eligible candidates were restored from verified government downloads; R2 credentials were unavailable, so these recovery caches are local only. The accepted Central Library source asset is also committed in the portable stage and runtime catalogue.

Four candidates passed loader, picking/collision and per-model mobile budgets. Detailed terrain checks sampled 1,893,766 points and 3,467 low-rim points; only Central Library passed all existing gates. No thresholds were relaxed. Staged and installed desktop/mobile day/night browser checks passed, including full model framing, terrain ray/sampler agreement and mobile asset-failure fallback/retry. Eight PNGs were decoded and checked for dimensions, nonblank output and hashes by script. This is not a physical-device or dense-city FPS benchmark.

An initial staged mobile test camera fell outside the 300 m detail-load range. `staged-attempt-01/` preserves the diagnosis. Correcting test framing and asserting the existing range resolved it without changing the model or runtime profile.

## Durable checkpoint

`final-results.json.gz`, `final-summary.json` and `final-neon-sync.json` are authoritative. All 22 final outcomes were written and read back exactly from completed Neon job `06ab160dd479d9ba6efe82ee7177e50e1b98480343daf54d078b4c23792acd74` (`government-xxl-first-pass-v1`). Source/job ownership was fenced, all reservations were released, and snapshot `fc07e72cc1a9e88e` records the new installed review. Earlier `results.json.gz` / `summary.json` describe a historical pre-publication checkpoint, not current unfinished work.

The viewer now counts 293 enhanced forms overall and 286 ready government forms out of 212,669 matched sources (0.13%); total mapped forms remain 346,108. The earlier 200-form batch remains 11 installed / 189 held.

Reproduction commands and input/version guards are in [the import runbook](../../../../source-scripts/city/government-import/README.md). Commit every newly verified installed group promptly; preserve each batch's source provenance, review receipts and held reasons for resumption.

## Commit and deployment status

The new model, runtime statistics and all 22 outcomes are committed locally as `887b6f4c` on `codex/astra-hong-kong-city`. Automatic approval review rejected the push to `git@github.com:wiiiimm/hongkong-sandbox.git` because destination/push authorisation was not established. No push or new hosted preview is claimed. Resume by pushing the existing branch only after approval, then verify the READY preview, progress JSON, catalogue and original asset hash. Do not rerun the completed import or rewrite its Neon outcomes.
