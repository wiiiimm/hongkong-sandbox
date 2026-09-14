# Government XL batch of 50 — 13 September 2026

This bounded batch selected the 50 largest uninstalled XL government source models (10,000–49,999 triangles) that had a unique exact viewer match. All source recovery, conversion, identity, projection, foundation, terrain, runtime, neighbour and browser work was performed with deterministic local scripts. No per-model AI call, AI modelling, simplification or model-geometry edit was used.

| Final user status | Source models |
| --- | ---: |
| Installed | 18 |
| To do | 0 |
| Held for human decision | 0 |
| Held for AI processing | 0 |
| Held for unknown state / later local scripted processing | 32 |
| In process | 0 |

WEST9ZONE (`landsd/229310:0`) is installed from the byte-identical 30,359-triangle government mesh. A bounded source-terrain patch resolves the coastal terrain seam. The adjacent Florient Rise Tower 2 fallback remains visible and is supported by the unchanged source podium across 99.998% of its footprint.

1881 Heritage (`landsd/264745:0`) is installed from the unchanged government podium. Its separate basic tower remains visible; the source roof supports 100% of the tower footprint with a 4.7 cm overlap.

Seaside Sonata Tower 3 (`landsd/274763:0`) and Ocean Pride Towers 3 and 5 (`landsd/162512:0`, `landsd/219311:0`) are installed from their unchanged government meshes. Deterministic low-rim checks prove that their existing basic podiums support them, so no terrain or geometry edit was needed. All five installations passed staged and live desktop/mobile load, picking, collision, framing, fallback, retry, and retained-support visibility checks.

A second supported-tower pass installed the unchanged government mesh for `landsd/236065:0` and The Grandiose Blocks 1, 2 and 3 (`landsd/81678:0`, `landsd/81008:0`, `landsd/81151:0`). Their separate native podium sources were installed with them. Deterministic support-contact and staged/live browser gates passed without model-geometry changes.

The Spectra Tower 3 (`landsd/265311:0`) is installed from its unchanged 26,440-triangle government mesh. A bounded native terrain patch resolves its source contact while preserving the original overlapping source facets. Independent highest-surface checks, neighbour checks, and staged/live desktop and mobile browser gates passed with zero AI calls.

Chung Kin Building (`landsd/147024:0`) is installed from its unchanged 46,310-triangle government mesh. Its government object ID and Building CSUID match exactly, it is the sole viewer match, and it covers 99.999995% of the footprint. A complete native terrain patch passes contact, neighbour, runtime, and staged/live browser gates with zero AI calls.

HARBOURFRONT HORIZON ALL-SUITE HOTEL (`landsd/31275:0`) is installed from its unchanged 44,871-triangle government mesh. A hashed detailed projection proves the exact source component, and its native terrain patch preserves every parent shoreline water/land classification. The wide complex uses the existing long-range model priority and passes staged/live desktop and mobile gates with zero AI calls.

V City (`landsd/230643:0`) is installed as an atomic 11-model government assembly with Tuen Mun Station, two V City support components and Century Gateway Towers 1, 2, 3, 5, 6, 7 and 8. All 152,487 unchanged source triangles pass exact identity, podium contact, same-sheet station foundation, neighbour, mobile budget, and staged/live browser checks. The ten supporting components increase the site-wide ready count but are outside the original XL-50 sample.

Government tower `landsd/147505:0` (`B350402046901063C0`) is installed from its unchanged 41,344-triangle mesh. Exact object ID and Building CSUID checks, 99.9986% target coverage, a bounded same-parent overhang, and a deterministic native-terrain repair passed. The terrain repair preserves the current ground under Cheung Fung Mansion with a 1 cm numerical boundary fringe; staged/live desktop and mobile checks prove the adjacent basic form remains loaded and visible.

The Goldmark (`landsd/177244:0`) is installed from its unchanged 26,122-triangle government mesh. Exact object ID and Building CSUID checks prove 99.5089% footprint coverage; its only unrelated intersection is a 6.25 m2 boundary sliver against the adjacent Hysan Place assembly. Full runtime-mesh checks prove that the native terrain adds no buried Hysan triangles and that the Hysan tower remains supported by its installed podium. Staged/live desktop and mobile gates passed with zero AI calls.

Chung Mei Building (`landsd/160193:0`) is installed from its unchanged 29,576-triangle government mesh. Its exact identifiers, 99.0311% footprint coverage, isolated source projection and source terrain pass deterministic identity and contact checks. Because its terrain rectangle overlapped the installed Chung Kin patch, one hash-pinned combined native patch replaces that manifest entry while retaining both target UIDs. The full 46,310-triangle Chung Kin mesh gains no newly buried triangles and stays visible through staged/live desktop and mobile checks.

Mei Choi House (`landsd/264691:0`) is installed from its unchanged 33,397-triangle government mesh. Its exact identifiers, complete target coverage, 0.58 m projection-centroid offset and bounded 3.47 m overhang pass a source-complex identity rule. Four non-overlapping neighbouring fallbacks retain their current parent terrain, including boundary-stitched vertices and numerical hole fill. Staged/live desktop and mobile checks passed with zero AI calls.

Mong Kok Stadium (`landsd/240527:0`) is installed from its unchanged 24,595-triangle government mesh. Exact identifiers, 99.46% target coverage, a 0.95 m detailed-projection centroid offset, and bounded adjacent-form intersections pass the complex identity rule. Complete triangle-surface contact resolves the coarse bounds warning, one non-overlapping neighbour retains its current parent terrain, and original overlapping source-terrain facets remain hash-bound. Staged/live desktop and mobile checks passed with zero AI calls.

The other 32 models retain their current viewer fallbacks. Their blockers overlap:

- 18 still need a deterministic source-assembly suppression or support map.
- 9 include below-grade source surfaces that need a source-preserving exception or terrain resolution.
- 4 need the stricter viewer identity/component policy resolved.
- 10 retain native terrain coverage, ground-contact, or below-grade diagnostics.
- 1 has an existing review that must be resolved before a new publication decision.

These are local pipeline/processing holds. None is classified as requiring AI modelling or a user decision. The exact per-model reason combinations and next steps are in `second-pass/final-script-pass/final-results.json.gz`.

The original 50-result checkpoint remains in pinned Neon job `9963d69f1a4c5c150cb119ba7409204fc9beca9c0ddb49ba2b4e85d9d7334585`. Third-pass snapshot `04d8813ba3dacd9e` records the earlier 5-installed/45-held checkpoint. Current review snapshot `0f6948ee7ca03b60` records 18 installed and 32 held rows. Third-pass job `8a8785c85c67137ff82059ea857f957cfa3546393a463b4c48aabf8be0fe324c` preserves the earlier four-blocker checkpoint; Spectra's overlap-evidence blocker, Chung Kin's numerical terrain/identity blockers, Harbourfront's shoreline/component blockers, Goldmark's boundary-touch/native-neighbour blocker, Chung Mei's overlapping native-terrain blocker, Mei Choi's source-complex and neighbour-terrain blockers, and Mong Kok Stadium's complex-boundary/contact blockers were subsequently resolved by deterministic rules. The resulting public count is 427 ready government-source forms and 441 enhanced source forms overall.

Use `xl-final-sync.py` for the original checkpoint and `xl-third-pass-sync.py` for the refined terrain/support checkpoint. Resume held models by blocker group from the frozen final results and third-pass evidence; do not repeat source acquisition or completed diagnostics when their hashes still match.
