# Government model resolution — 11 September 2026

Executor: Codex root. Source/processing implementation: `e0a21f53`. The user asked
for all 198 remaining forms to reach an actionable endpoint with zero In process.
No per-model AI calls, modelling, simplification or architectural image judgement.

## Human status for the original 200 forms

| Status | Forms |
| --- | ---: |
| Installed | **11** |
| To do | 0 |
| Held for human decision | 0 |
| Held for AI processing | 0 |
| Held for unknown state | **189** |
| In process | **0** |
| Total | **200** |

This pass installed **nine** additional models; two were installed previously.
All 198 selected forms completed the configured scripted resolution steps and
have terminal review/results in Neon. The 189 holds have measured technical
blockers whose safe resolution method is still unproven. No requirement for AI or
an unanswered user decision has been established. A hold does not authorise AI.
No active/queued worker remains in this bounded pass; reservations are released.

[Every form, its blockers and next evidence/action](human-outcomes.csv).
The primary reasons below partition the 189 holds; underlying flags may overlap.

| Primary blocker | Forms |
| --- | ---: |
| Source-part identity | 112 |
| Native below-grade geometry | 13 |
| Neighbour regression | 12 |
| Land/water contract | 2 |
| Native ground/support contact | 20 |
| Terrain coverage | 16 |
| Overlapping terrain surfaces | 13 |
| Existing source review | 1 |
| **Total held** | **189** |

These outcomes retain the source models and current fallbacks. They do not certify
that every hold can be resolved by existing scripts or that AI will be required.
New evidence is needed before further integration; no validation threshold was
relaxed merely to reduce the hold count.

## What the scripts completed

- Rechecked all 198 native models against original source triangles at every model
  vertex, triangle centre and <=1 m lower-rim edge sample. Combining the 70 cached
  source sheets improves coverage beyond the preceding per-sheet vertex audit.
- Evaluated source identity/current holds and constructed bounded native-facet
  terrain corrections with 10 m outer transitions split on parent triangles.
  The existing publisher rejects incomplete coverage, overlapping height surfaces,
  water-mask conflicts and boundary mismatches. Model geometry/elevations stay 1×.
- Eighteen staged terrain patches covered 21 models; all 21 pass actual loader,
  picking/collision and detailed drawn-terrain contact checks. A conservative check
  of 672 neighbouring forms holds ten patches that would worsen nearby geometry.
  Eight patches covering nine models pass. All 844 affected/pending source keys
  were reserved (including distinct source keys for four OSM neighbours).
- Looked up 48 possible support components in the frozen native database. Forty-three
  exact source meshes were available and loaded: one local reuse and 42 verified
  government restorations. All 198 have triangle-level support outcomes. Two hints
  have complete sampled low-rim contact, but do not establish accepted source assembly
  membership or companion placement. No support relationship was auto-approved.
- Installed the nine passing original meshes and eight source-backed terrain patches
  through the existing fenced publisher. Desktop/mobile day/night, active UID,
  camera visibility, source picking/collision, actual terrain-ray/sampler agreement,
  intentional download failure and retry all pass before and after installation.

## Installed scope and cost

Nine models: landsd/218894:0, landsd/206843:0, landsd/78415:0, landsd/158101:0,
landsd/159899:0, landsd/262504:0, landsd/299814:0, landsd/211455:0, landsd/183106:0.
Original building assets total **930 triangles / 21,166 compressed bytes**.
Eight terrain patches total **21,948 triangles / 3,531,385 JSON bytes**. Terrain
core facets retain source detail; only the documented outer transition joins the
existing parent. No building source heights, scales or geometry were changed.

Public progress now shows **292** verified enhanced forms overall; **285 / 212,669**
government-source forms complete (**0.13%**) and 212,384 remaining. Total map forms
remain 346,108. Batch installation means the Astra feature-branch viewer, not a
production release, whole-landmark completion or a dense-scene FPS guarantee.

## Verification and durable evidence

- 15 government policy/selection/native-context tests pass, including a native
  terrain spike caught by centre sampling but missed by vertex-only checks.
- 28 terrain/publication guard tests and 39 City native-terrain/streaming/support/
  progress tests pass. Skill v1.8.1 validates; whitespace/syntax checks pass.
- Staged and installed browser reports cover 36 day/night views each and nine
  mobile failure/retry cases each. All **72 PNG files** decode at the requested
  dimensions and pass nonblank checks; hashes are retained. No AI appearance score.
- The self-contained static progress build passes. Browser checks use software
  Chrome desktop/mobile viewports; physical-phone performance is unverified.
- Neon source review snapshot **65eed0edf9c80ea5** preserves prior source reviews and
  records nine installed-verified outcomes plus 189 held outcomes. Full job result
  and all 198 review states were read back and compared exactly. Source/job writes
  are fenced; the supervisor released the complete reservation afterwards.

Shared job: **fbd567f80b49bea51fc854d5ad7bc3b98127b39f5bcec1079b6520f3fbad3a71** (`government-resolution-v1`).

Key artifacts: `source-resolution.json`, `staged-metrics.json`,
`neighbour-checks.json`, `support-source-lookup.json`,
`support-triangle-checks.json`, `decision.json`, `staged-browser.json`,
`live-browser.json`, both image verification files, `installed-acceptance.json`,
`final-results.json.gz`, `neon-sync.json` and `summary.json`. Publisher rollback
hashes live in `model-integration-20260909/government-resolution-20260911/`.
Prepared accepted assets/plan are under
`source-scripts/city/government-import/accepted/government-198-resolution-20260911/`.

The acquired source/cache files remain in ignored local folders. No new R2 backup
is claimed. Frozen evidence is reproducible with the matching source caches and
script revision; do not rerun this completed pass over its published destinations.
Use a new versioned pass and fresh source ownership for future resolution work.
