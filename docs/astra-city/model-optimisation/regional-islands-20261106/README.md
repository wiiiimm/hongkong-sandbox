# Island enhancement and compression checkpoint — HKS-199 / HKS-229

Executor: Codex, 6 November 2026. Branch: `feature/islands-model-enhancement-and-compression`.

This branch starts from original-model commit `85ed796896c4db3ce45b5ed0fbcad07aec937e05`, preserving all current 7,109 progressive detailed actors. It brings across the existing compression branch's **code and recipes only**, with the additive regional renderer-export adapter. It does not import the compression branch's large staging/history changes or overwrite its worktree. No historical-map reference imagery was used.

## Agreed order and current delivery

1. Enhance Peng Chau and Cheung Chau with available unchanged government sources, using the original acquisition, physical/identity, browser and guarded installation workflow.
2. Prepare Tung Chung as the next requested test area. Keep town/waterfront and rural/valley scopes explicit.
3. Freeze the resulting installed originals and generate independent original/lossless, high, balanced and lightweight compression candidates across Lantau, Peng Chau and Cheung Chau.
4. Review and publish compatible variants separately; processing completion never grants runtime approval.

The user intends to port this checkpoint to another project now, and port again when the three new test areas are ready. This checkpoint contains the audit and processing tools; **the requested new island installations and bulk compression have not run**. The older fixed-521 XL campaign remains paused. No Neon optimisation plans/jobs/reviews or model-installation records were written in this checkpoint.

## Coverage audit

`audit-summary.json` binds source manifest SHA, source commit, pinned Neon target and the immutable native-model size-inventory run. Every one of the viewer's 346,115 building forms was considered. Regional membership uses footprint centroids in internal project review polygons; this is not an official geographic survey.

The requested regions contain **20,379 building forms**. The previously completed Discovery Bay–Mui Wo–south/west Lantau scope remains 6,775/6,775 government-matched forms installed. The broader Lantau scope still includes unfinished Tung Chung, airport and northeast areas.

| Next area | All forms | Government source matched | Installed matched detail | Remaining matched detail |
|---|---:|---:|---:|---:|
| Peng Chau | 1,809 | 1,426 | 1 | 1,425 |
| Cheung Chau | 3,990 | 3,420 | 0 | 3,420 |
| Tung Chung town/waterfront | 2,042 | 1,551 | 3 | 1,548 |
| Tung Chung valley/rural coast | 383 | 223 | 0 | 223 |

Peng Chau is separated from Hei Ling Chau using retained OSM relation 9279538, with the existing regional-package 25 m feature-assignment tolerance. The old section 10.12 combines both islands, so its totals must not be reported as Peng Chau alone. Missing government inventory matches do not prove that the government has no source anywhere; they remain lookup gaps. Catalogue/embedded membership establishes installation, not fresh architectural or physical review.

## Compression implementation

`regional_batch.py` uses immutable source/recipe identities, shared reservation/job leases and the established Meshopt codecs. Existing identical completed variants are reusable only after source/output/receipt and decoder readback. Missing private artifacts must be restored with their exact recorded hashes before reuse; a database row alone is insufficient. Failed attempts remain failed and are not silently requeued.

Unlike the older catalogue-only adapter, the regional adapter also exports existing embedded `modelGeometry` through the **actual committed renderer**. It pins tile/record/module/exporter hashes and retains Float32 positions, normalized renderer normals, UVs, corner order and window masks, including existing illustrative foundations. The export has identity pose in the viewer's existing local-world metre/HKPD coordinates. Government source bytes and live viewer data remain unchanged. A generated render export is a distinct processing source, never a claim that its gzip byte count was the original network tile size.

The initial freeze found 4,929 progressive sources and 1,859 embedded detailed meshes across these regions. It also counted 13,591 basic shapes. A twelve-output offline pilot exercised one progressive, one embedded and one basic mesh through all four recipes. The user then clarified that government enhancement must precede compression, so `scope.json` now explicitly excludes basic-only shapes from the compression cohort. These earlier private exports/pilot files are not installed or published and are excluded from Git.

Small meshes can become larger with Meshopt/container overhead. Keep those measured negatives; use original bytes when a candidate offers no saving. Four tier labels do not guarantee four different triangle counts or improved phone FPS.

## Reproduction after enhancement

Install the existing Python shared-modelling requirements in an isolated environment, and run `npm ci --ignore-scripts --prefix source-scripts/city/model-optimisation`. Use only the repository-pinned modelling connection; do not run migrations or substitute application credentials.

```sh
python source-scripts/city/model-optimisation/regional_batch.py freeze \
  --source-root /absolute/path/to/the/committed/source/checkout \
  --scope docs/astra-city/model-optimisation/regional-islands-20261106/scope.json \
  --output source-scripts/city/model-optimisation/staging/regional-islands-AFTER-INSTALL

# Only after acquisition/installation and fresh snapshot verification:
python source-scripts/city/model-optimisation/regional_batch.py launch \
  --snapshot source-scripts/city/model-optimisation/staging/regional-islands-AFTER-INSTALL/sources.json \
  --recipes docs/astra-city/model-optimisation/regional-islands-20261106/recipes \
  --output source-scripts/city/model-optimisation/staging/regional-islands-AFTER-INSTALL \
  --batch regional-islands-AFTER-INSTALL --workers 4
```

Use a fresh ignored `regional-*` staging directory for changed sources. Keep large generated candidates out of Git/Vercel. Durable object-storage delivery/versioning remains separate work; no R2 migration is implemented here.

## Validation and remaining gates

Validation: **63 tests passed; 15 dedicated-database fixture tests skipped; zero failures after integration**. Python optimisation/shared-worker tests and Node codec/export tests check committed/staged input guards, import closure, private-output containment, borrowed pinned sessions, support-family partitioning, exact render export and codec roundtrips, plus unsafe inputs and lossy error guards. Isolated database fixture tests remain skipped without their dedicated test database. No bulk Neon processing, desktop/mobile visual/physical review or variant publication is claimed by this checkpoint. New government installs must retain all existing identity, complete affected-scope, placement/support, terrain, collision, browser and publication guards.
