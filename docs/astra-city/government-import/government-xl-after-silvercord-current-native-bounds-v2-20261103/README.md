# Current bounds after the Silvercord/Lippo installation

Completed on pinned Neon job `78be2c43c6e69c46268ccd03f88fd13f9b1a31b9dcaa8ae8cc66dd248d8149f3`.

The current actor census contains 7,106 originals. Exactly 7,101 prior bounds rows were reused after entry, form, asset and recorded production geometry dependency checks. Five additions were freshly loaded through the actual renderer and bounded in all four existing coordinate representations, including unused POSITION vertices. The sole prior metadata difference is the independently reviewed supportDependencies-only migration of landsd/239465:0. Any other entry or source change is rejected. The explicit authenticated five-original pair receipt pins the unchanged CPU bounds kernel; the prior all-reused census did not claim to run that kernel.

Reproduce using `refresh_fresh_native_bounds_additions_v3_20261103.py` with `--prior government-xl-after-june-current-native-bounds-reused-v1-20261103`, `--installed government-xl-silvercord-lippo-original-installed-v1-20261103`, `--readback government-xl-silvercord-lippo-installed-root-readback-v1-20261103`, `--owner-update-review government-xl-silvercord-lippo-five-original-source-review-v1-20261103`, and `--addition-kernel-evidence government-xl-silvercord-lippo-five-complete-original-pairs-v1-20261103`. Use a fresh batch name and authenticated exact paths from result.json; do not rerun completed checks merely to reproduce them.

Three adverse unittest methods pass for the real owner migration, missing review, unrelated fields, source and pose changes. This diagnostic grants no new model acceptance or publication. No geometry edits, optimisation or external AI calls.

The preserved first attempt stopped on a missing historical kernel reference before source calculations. Its log is adjacent; this was an adapter schema failure, not a corrupt government source.
