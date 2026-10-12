# Every installed enhanced model — four Meshopt candidates

Codex, 12 October 2026. User-authorised processing scope: every installed asset, ignoring review flags as inclusion criteria. The committed `installed-v1` snapshot has 6,649 unique UIDs, zero review-based exclusions and full original entry/coordinate/source SHA metadata. Original model bytes, installation records, source acceptance reviews and runtime catalogues remain unchanged. No historical-map references were used.

| Candidate | Position-rounding budget | Simplification target / estimated absolute cap | Other precision |
| --- | ---: | --- | --- |
| Original / lossless | Exact original attributes | Original topology/corner order | Exact bytes |
| High | 0.005 m | Original topology, all unused vertices retained | Float32 normal/colour components rounded at 1/4096 |
| Balanced | 0.020 m | Target 65% of triangles, estimated error at most 0.05 m | Components rounded at 1/1024 |
| Lightweight | 0.080 m | Target 35% of triangles, estimated error at most 0.20 m | Components rounded at 1/256 |

These are three distinct lossy candidate recipes, not universal visually approved presets. Position extrema are pinned. Simplification locks topological borders, preserves primitive/material boundaries and accounts for normal/colour attributes. It may stop well above the requested triangle count because of seams and error caps. Actual geometry counts/errors are recorded per primitive. Positions are restored when rounding would collapse/reverse faces or create area from original zero-area faces. Every stream is compacted consistently in LOD candidates. Meshopt encoding is then lossless against that derived mesh, with the exact viewer decoder independently checking every derived bufferView.

Position-rounding diagnostics are conservative maxima in metres over all original vertices through every source node matrix using Float64 arithmetic; restorations only lower actual error. GPU/literal Float32 placement remains untested. Simplifier error is a weighted absolute quadric estimate, not a Hausdorff distance or a visual bound. Source transforms/materials remain exact, while geometry/normal/colour precision is explicitly lossy. Collision/support assets are not replaced; accessor bytes exclude originals retained for collision and all JS/GPU/decoder/temporary overhead.

Whole gzip files are compared with the existing gzip source. Keep larger results, failed attempts and originals; choose originals wherever a generated candidate does not save transfer bytes. No frame-time, peak-memory, rendering, collision, current terrain/support or runtime publication improvement is inferred from offline compression. SourceIdentity and geometry reflect offline identity/format/derived-decoder/error checks; other gates remain untested.

The lossless recipe is unchanged from the earlier batch, allowing Neon to reuse its 4,272 completed global variants and process the additional 2,377. All three lossy recipes apply to every installed UID. Each tier has an independent full result/receipt/decoder audit and a verified Neon checkpoint in its corresponding report directory. Processing results remain unreviewed and unpublished.

Reproduce using the pinned modelling credential through `MODELLING_ENV_FILE`, never the application database:

```sh
python source-scripts/city/model-optimisation/batch.py snapshot \
  --selection-policy installed-v1 --output docs/astra-city/model-optimisation/NEW-BATCH/sources.json
python source-scripts/city/model-optimisation/run_installed_batch.py \
  --folder docs/astra-city/model-optimisation/installed-enhanced-meshopt-variants-v2-20261012 \
  --staging source-scripts/city/model-optimisation/staging/installed-enhanced-meshopt-variants-v2-20261012 \
  --workers 16
```

Only reuse this frozen batch while input and tool hashes still match. Later changes require a new snapshot/recipe rather than rewriting immutable evidence. Sequential tiers avoid reserving the same source simultaneously; ordinary workers keep connected supports together, scope claims to reserved jobs, heartbeat/fence stale tokens and release only their own leases. The independent audit rereads every source/output byte and derived bufferView and verifies Neon against immutable receipt bytes.

The [historical skip audit](../accepted-enhanced-held-audit-v1-20261012/README.md) explains all original exclusions. The [superseded first pilot](../accepted-enhanced-meshopt-lossy-v1-20261012/README.md) preserves discovered tiny-face failures; the [guarded 39-output pilot](../accepted-enhanced-meshopt-lossy-v2-20261012/README.md) passed before whole-cohort processing.
