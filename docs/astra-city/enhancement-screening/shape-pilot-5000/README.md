# Scripted screening: another 5,000 forms (HKS-203)

Codex root, 10 September 2026. This deterministic sample excludes every form in
the earlier 1,000-form pilot. Kai Tak remains a separate control, outside both
sample denominators. The displayed population is 346,108 source forms; these are
not necessarily unique physical buildings.

| Outcome | New sample | Percent |
| --- | ---: | ---: |
| Existing verified skip | 3 | 0.06% |
| Keep-current candidate | 20 | 0.40% |
| Import candidate | 205 | 4.10% |
| Retain pending | 4,772 | 95.44% |

The earlier sample's one skip was already accepted before this comparison. It
produced four additional keep-current candidates. Combined, the two disjoint
samples contain 4 existing skips, 24 keep-current candidates, 243 import
candidates and 5,729 pending forms. **No new skip/acceptance credit was granted.**
Pending does not mean enhancement is necessary. Automatic acceptance remains
unvalidated, and no AI architectural review or modelling was performed.

## Complete Neon sync

Every outcome, including missing geometry and pending cases, is now stored in
`astra_modelling.shape_screening_runs` and `shape_screening_outcomes` on pinned
branch `br-icy-silence-b3wjwz0q`. Exact result JSON and membership passed a separate
post-commit read-back. The previous 1,001-row report was also backfilled. Across
the two runs: **6,000 distinct sample forms, 6,002 outcome rows** (Kai Tak is a
control in each run). No acceptance or model-review ledger writes.

New run ID: `7cece185f6637c63d6ffaf3ee26db0d48d461dfc6bd0479908a9ff7466c5b0a5`.

See `neon-sync.json`, `verification.json`, and the complete `results.json.gz`.
Metrics remain separately reusable in `city_audit_cache`; the shared replay had
3,085 exact hits and zero new metric writes. Immutable run hashes include the
routing rule, policy, complete results and sample/control membership. Local
execution time/cache-hit counts do not create duplicate diagnostic runs.

## Source and comparison evidence

- 5,000 new forms plus one control; 4,999 existing audit hits and two local audits.
- 3,086 uniquely matched exact assets recovered; one fails the viewer footprint-fit check.
- 1,905 forms lack a usable matched native source, and ten have ambiguous matches.
- 3,085 geometry pairs load, including Kai Tak: sample-only comparisons are 3,016 material, 65 negligible, three uncertain and 1,916 unavailable.
- The 65 negligible comparisons do not all pass the independent acceptance/identity/terrain gates; 20 become keep-current candidates.
- All native bytes match the pinned HKS-222 asset SHAs. City geometry, source heights, terrain and model assets are unchanged.

The larger sample exposed a compact ZIP cache bug: an older selection from the
same sheet was being treated as complete. Fix `029b6b5e` reuses verified cached
members and acquires only newly requested files. All 1,757 affected assets were
recovered on retry. Initial/retry processing took 306.515s/192.171s;
comparison took 142.257s, and the cached comparison replay took
9.994s (timings exclude full outcome sync). No AI calls were made by the
capture, recovery, comparison or persistence scripts. AI was used for coding.

The first outcome-sync attempts rolled back on JSON representation differences
(negative zero/integer floats, and in-memory tuple policies). Canonical JSON
normalisation and regression tests now cover both. Only the verified final runs
are committed in Neon; metric caches remain independent.

## Reproduce

From the repository root, use the commands in
`source-scripts/city/enhancement-screening/README.md` to capture/recover a new
sample. Frozen replay requires no government access and no database:

```sh
mkdir -p source-scripts/city/enhancement-screening/local/replay-5000/geometry
tar -xzf docs/astra-city/enhancement-screening/shape-pilot-5000/geometry.tar.gz \
  -C source-scripts/city/enhancement-screening/local/replay-5000/geometry
source-scripts/city/enhancement-screening/.venv/bin/python \
  source-scripts/city/enhancement-screening/screen.py compare \
  --evidence docs/astra-city/enhancement-screening/shape-pilot-5000/inputs.json.gz \
  --geometry source-scripts/city/enhancement-screening/local/replay-5000/geometry \
  --out source-scripts/city/enhancement-screening/local/replay-5000/report
```

`replay-manifest.json` fingerprints the frozen inputs and geometry archive; all
3,085 compressed and decoded geometry hashes were verified. Contact sheets were
not generated for this numeric batch. The 17-view/two-resolution comparison rule
is unchanged from the previous pilot; this pass does not establish real-world
architectural accuracy or validate automatic citywide acceptance.

Validation: 42 screening tests pass, one existing live acceptance test is skipped;
five native downloader tests pass. No source model was changed or published.
Sources: pinned Hong Kong Lands Department 3D source geometry and current City
rendered inputs; no `references/lantau-maps/` images were used.
