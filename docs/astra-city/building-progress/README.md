# HKS-220 — public building-form progress

Historical implementation notes. The current source-scoped counter and refresh
commands are documented in [government progress](../building-progress-government/README.md).

The header opens a compact native dialog with346,108 mapped source forms and269 verified enhanced forms (0.0777214%, displayed0.08%) in this review snapshot. Seven building proxies replaced by bridge models are excluded. These are source-component UIDs, not physical buildings: a tower, wing and podium may count separately. No whole-building/landmark completion metric is inferred. Models still awaiting review, held models, downloaded candidates and hash-mismatched replacements are excluded from the numerator.

`countCoverage` deduplicates deployed UIDs across tiles and replacement catalogues. Reviewed native geometry must match the frozen installed-verified source SHA. Catalogue asset bytes are hashed during generation. Embedded geometry uses a separately verified canonical ledger SHA and an exact runtime JSON digest, avoiding Python/JavaScript number-serialisation differences. Bridge-suppressed building UIDs leave both numerator and denominator. Counts do not read camera, LOD, streaming or zoom state.

## Refresh after integration

From the repository root on a configured modelling machine:

```sh
python3 source-scripts/city/building-progress/export.py --refresh
node 3d-viewer/scripts/build_progress.mjs
```

The Python environment requires the existing shared-modelling PostgreSQL dependencies and selected Neon branch configuration. On this machine use `/tmp/astra-city-venv/bin/python`. Export reads Neon in a read-only transaction, using `current-source-review.json`; it never changes that pointer. Commit the resulting `3d-viewer/scripts/building-progress/review-proof.json` and `3d-viewer/city/data/building-progress.json` with the reviewed publication. Export without `--refresh` reuses the frozen audit capture. Newly installed assets without updated verified source proof remain excluded.

The static Vercel build runs `node scripts/build_progress.mjs` inside `3d-viewer`. It requires no database/network credentials, Python or files outside the deployable viewer. It recalculates against that checkout’s actual tiles, catalogues and asset bytes. Run this build before any future packaging step removes local model files in favour of R2. The tiny public statistics JSON stays with the app. No government source downloads or working-cache/R2 uploads are required for this feature.

Runtime checks the statistics’ manifest digest and labels mismatches as updating rather than showing counts from another map. Missing/invalid data has an explicit unavailable state. The review date is labelled in Hong Kong time; frozen review evidence is intentionally conservative until refreshed. The statistics artefact’s input digest accounts for all tile/catalogue and frozen review inputs.

## Validation

`node --test 3d-viewer/city/tests/building-progress.test.js` covers multipart/partial upgrades, duplicate replacements, held/pending/downloaded-only and changed sources, proxy removal, empty totals and conflicting installed IDs. `node 3d-viewer/city/tests/building-progress-browser.mjs` passed real city desktop1280×900, mobile390×844 and narrow320×740, accessible native dialog/meter labels, camera-stable totals, no page/dialog horizontal overflow, and stale/unavailable/empty fixtures. The screenshots were visually inspected. Emulated Chrome is not a real-device Safari performance certification.

9 September label refinement: header and dialog now say “Model Enhancement Progress”. The header includes percentage and enhanced/total form counts, including narrow screens. Existing counting rules are unchanged. Four counting tests and desktop/mobile/narrow browser checks passed, including unavailable, stale and empty statistics.
