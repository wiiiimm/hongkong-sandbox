# 1,000-form screening pilot — 10 September 2026

> Historical experiment: full skip-screening was retired from the import pipeline
> on 11 September 2026. Results remain diagnostics, not acceptance or a work queue.
> See `source-scripts/city/enhancement-screening/README.md` for the active route.

Codex root ran `pilot.py --capture` on `codex/astra-hong-kong-city`. This is a
script-only triage experiment, not a completed visual acceptance pass.

| Random-sample result | Forms | Share |
| --- | ---: | ---: |
| Already accepted; confirmed skip | 1 | 0.1% |
| Likely skip; validate the rule visually | 59 | 5.9% |
| Enhancement review candidate | 4 | 0.4% |
| Inconclusive; further inexpensive assessment needed | 936 | 93.6% |
| Total | 1,000 | 100% |

The sample uses seed `hks-screening-pilot-v1`, drawn uniformly from 346,108 displayed
source forms across 220 tiles. It contains 992 footprint forms, five embedded meshes
and three native catalogue meshes. Small sheds, roofs and individual building parts
are included. These counts do not estimate the fraction of visible city architecture
that looks wrong. Kai Tak Stadium is an additional control, excluded from this table.

The full fresh input capture took **133.751 seconds**; classification took
**0.0281 seconds**. All 1,001 current audit keys hit the existing Neon cache.
There were **zero modelling AI API calls, geometry downloads, database writes or
new acceptance decisions**. Agent time spent writing/interpreting the script is
not included in a claim of zero AI use for the overall task.

## What the skip number means

The 59 likely skips satisfy every conservative gate documented in the
[script README](../../../../source-scripts/city/enhancement-screening/README.md):
ordinary use, surveyed height, clean source/terrain checks, modest size, one ring,
exact native identity, nearly identical overall bounds/heights and a simple source
mesh. Those gates reduce review volume; they do not establish visual adequacy.
MANHATTAN HEIGHTS (`landsd/99033:0`) is the one already verified sample form.

Allowing 128 native triangles produces 90 likely skips; allowing 256 produces 103.
All other gates remain identical. This sensitivity check does not validate either
looser rule, and no threshold was promoted to public acceptance. The actual safe
skip rate remains unknown until labelled visual checks measure false skips.

Among inconclusive forms, overlapping reasons include 424 native-envelope
differences, 406 missing/ambiguous native matches, 389 nonordinary/support forms,
382 meshes above the strict complexity ceiling, 330 estimated heights and 179
source/terrain diagnostics. These reason counts overlap and must not be summed.
A difference, missing source or elevated base is not by itself proof of poor quality.

The four enhancement-review candidates are a transportation form, a pavilion,
KAI MING TEMPLE and The Church of Jesus Christ of Latter-Day Saints. The script
prioritises distinctive building uses represented only by extrusions; it has not
visually confirmed a worthwhile change for every one of those four.

## Kai Tak Stadium: separate positive control

- Current UID: `landsd/318723:0`; CSUID: `3837920357T20241029`.
- Current representation: a 555-point footprint extrusion, with no native or
  embedded detailed mesh. Its top is **59.9 m HKPD**.
- The generic `grandstand`/stadium rule flags **enhancement-candidate**. No
  hard-coded stadium UID or name is used by the classifier; the name only locates
  the separately requested control. A test checks detection without any name/UID.
- Existing cached Lands Department model: `B383792035701063C1`, sheet `11-NE-16B`,
  **5,178 triangles**, **89,005 compressed bytes**. Its identity and recorded heights
  match; cached hull overlap is 100%, centroid distance about 6.5 cm, and current
  footprint/native bounding-box edges differ by at most 0.71 m.
- Native top: **67.101 m HKPD**, about **7.201 m above** the current extrusion.
  This is concrete geometric evidence that the fallback misses vertical structure;
  it is not proof that the cached source captures every finished architectural detail.
- The current audit flags its base above sampled terrain. The frozen native-stage
  diagnostic reports lower-rim gaps about 8.3–10.3 m on 70 m terrain. Review podium,
  support and terrain context before integration; do not lower the source geometry
  to hide those gaps. The candidate has no placement or publication approval.

The stadium operator describes its pearlescent exterior and retractable roof on
its [official venue page](https://www.kaitaksportspark.com.hk/venues-spaces/4).
Those defining features are appropriate visual checks for the next source review.
No photographs or native model bytes were inspected in this metadata-only pilot,
so source recency, roof shape and finished facade fidelity remain unverified.

## Reproduce and inspect

- [summary.json](summary.json): counts, thresholds, timings, reasons and control.
- [sample.csv](sample.csv): all 1,000 UIDs, fingerprints, classifications and reasons.
- [kai-tak-stadium.json](kai-tak-stadium.json): separate control and native metrics.
- `evidence.json.gz`: frozen source records, screening fingerprints, exact audit keys
  and results, native-stage outcomes and landmark candidate inventory IDs.

From the worktree root:

```sh
python source-scripts/city/enhancement-screening/pilot.py
python source-scripts/city/enhancement-screening/pilot.py --capture
python -m unittest discover -s source-scripts/city/enhancement-screening -v
```

The first command reproduces classifications offline; capture refreshes current
inputs using the existing pinned Neon configuration. Threshold or interpretation
changes require a new policy version and labelled validation before any automatic
acceptance. A small varied visual check of likely skips and uncertain cases is the
next calibration step; the pilot creates no modelling queue or good-to-go credit.

Source provenance: current city Lands Department/retained OSM forms, HKS-221 audit
cache, HKS-222 native run `e98f84fdaeb489b229af3910d80d765bb87dbbdc565ec1794836b04909f370ec`,
and the committed landmark candidate inventory. No `references/lantau-maps/` images
were used or modified.
