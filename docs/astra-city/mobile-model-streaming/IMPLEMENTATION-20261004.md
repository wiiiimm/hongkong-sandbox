# HKS-229 implementation and acceptance

Executor: Astra, medium reasoning. Base: PR #298, `4bf9293b2c20daffe3568e99a60cc737b29e483d`; separate branch `codex/hks-229-canvas-streaming`. Imports, model assets, provenance and placement are outside this change.

## Measurement contract (before policy changes)

Use `?streamingMetrics=1` and `window.__city.metrics.snapshot` for bounded stage distributions. Decode includes gzip/GLTF verification and collision preparation; install includes asynchronous fallback and scene attachment; render submission is CPU wall time, not GPU time. Fallback bake, planner, labels/map, frames, draw calls, triangles and long tasks are separate. Sample storage is bounded to 600 values per metric; total/count/max cover the run. No blocking GPU query.

Cloud targets: stationary planner executions drop at least 80% after settling; all viewports obey the same finite hardware budget; short camera reversals reuse decoded models and do not restart active downloads; resize does not flush caches. Repeat identical routes with the checked-in browser harness before/after. Frame distributions diagnose regressions but cannot certify physical-device speed on software-rendered cloud hardware.

Physical acceptance remains blocked on named lower-power phone, integrated-GPU laptop and capable desktop runs. Establish device-specific frame budgets and baseline-relative targets from those runs before claiming a speedup or enabling more aggressive adaptive budgets. No new offline LODs or automatic render-scale escalation without that evidence.
