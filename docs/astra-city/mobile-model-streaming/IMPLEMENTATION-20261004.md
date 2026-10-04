# HKS-229 implementation and acceptance

Executor: Astra, medium reasoning. Base: PR #298, `4bf9293b2c20daffe3568e99a60cc737b29e483d`; separate branch `codex/hks-229-canvas-streaming`. Imports, model assets, provenance and placement are outside this change.

## Measurement contract (before policy changes)

Use `?streamingMetrics=1` and `window.__city.metrics.snapshot` for bounded stage distributions. Decode includes gzip/GLTF verification and collision preparation; install includes asynchronous fallback and scene attachment; render submission is CPU wall time, not GPU time. Fallback bake, planner, labels/map, frames, draw calls, triangles and long tasks are separate. Sample storage is bounded to 600 values per metric; total/count/max cover the run. No blocking GPU query.

Cloud targets: stationary planner executions drop at least 80% after settling; all viewports obey the same finite hardware budget; short camera reversals reuse decoded models and do not restart active downloads; resize does not flush caches. Repeat identical routes with the checked-in browser harness before/after. Frame distributions diagnose regressions but cannot certify physical-device speed on software-rendered cloud hardware.

Physical acceptance remains blocked on named lower-power phone, integrated-GPU laptop and capable desktop runs. Establish device-specific frame budgets and baseline-relative targets from those runs before claiming a speedup or enabling more aggressive adaptive budgets. No new offline LODs or automatic render-scale escalation without that evidence.

## Implemented policy

- CSS width/height and camera matrices determine clipped projected bounds. A catalogue-time BVH visits at most 1,024 nodes and returns at most 256 candidates, plus the bounded resident/running/selected set. Large projected nodes rank ahead of small distant nodes. Camera checks are throttled to 180 ms; unchanged state does no planning until a lifecycle revision or grace deadline.
- Auto starts with the same conservative model budget on every display: 24 models, one source/decode load, 48 MiB geometry, 128 MiB estimated residency (160 MiB isolated selection allowance), 450k triangles and 128 model draw calls. Fixed Higher retains the previous finite desktop model limits (48 models, 256 MiB, 900k triangles, 256 model draw calls). These are estimates, not measured VRAM.
- Selected models, nearby resident collision geometry and dependency closures precede ordinary visual ranking. Warm decoded geometry survives ten seconds within the same residency cap; in-flight requests have a short reversal grace. Tiny in-view detail has a two-second demotion grace and a lower demotion threshold. Fallback commits before the source shell leaves. Native supports remain until their active dependents retire. Offscreen active meshes use Three.js frustum culling rather than a stale planner visibility flag, preventing holes between planner ticks.
- Compressed source bytes have an independent 32 MiB / 96-entry LRU, one transfer and eight pending slots. This matches the existing maximum admitted source file size. In-flight source data is bounded separately by that maximum; this is not a claim about the browser's HTTP cache. Catalogue hashes still verify every decode. Pauses retain the transfer and gate the next decode instead of re-downloading it.
- Scene swaps serialize and yield between operations; large native collision-copy loops yield every 8,192 vertices. A single source validation, GLTF parse or GPU upload is not preemptible, so a strict millisecond GPU/upload deadline is **not** claimed.
- Substantial fallback bakes use at most two module workers with a 32-job queue and transferred output buffers. Source records are cloned, never detached from collision/picking owners. Small bakes remain inline: the matched two-record fixture showed worker overhead around 150–178 ms versus 1–2 ms for the original inline swap. The conservative worker threshold is 128 forms or a native position array over 60,000 elements; it is a tuning hypothesis requiring physical validation. Worker and inline geometry/material buffers match exactly in the browser fixture. Construction, structured-clone and runtime failure tests verify slot cleanup.
- Container resize, rotation, fractional/high DPR, fullscreen, zoom, visibility and DPR media changes coalesce without replacing caches. Picking and label projection use canvas coordinates. Hidden/zero-size canvases pause model, base-tile and demo admission. Auto has a static 1.5 DPR / 4-million-pixel ceiling; Fixed Higher restores 1.75 DPR through 4K, with a 32-million-pixel ceiling. This is an explicit quality tradeoff, **not measured adaptive resolution**; DOM UI remains at CSS resolution.
- Demo prefetch downloads at most 32 MiB or 96 models per user-started session, nearest-first with a forward bias in Fly. Its progress distinguishes downloads from decoded ready detail. It shares source bytes with foreground loading and does not decode the full catalogue.

Original government files, catalogue hashes, source transforms, HKPD placement, terrain assets, import ledgers and publication decisions are unchanged. The existing basic-form coverage and collision/picking path are retained, not replaced with new approximate geometry. No offline LODs were generated.

## Reproduction

From the repository root, with the city package's Playwright dependency available and a local Chromium:

```sh
node tools/dev-server.mjs
node --test 3d-viewer/city/tests/*.test.js
node 3d-viewer/city/tests/streaming-planner-benchmark.mjs after
node 3d-viewer/city/tests/streaming-correctness-browser.mjs --baseline
node 3d-viewer/city/tests/streaming-correctness-browser.mjs
node 3d-viewer/city/tests/streaming-performance-browser.mjs after
```

The isolated browser baseline serves unchanged instrumented runtime files from commit `55a5fe97` using Playwright routes. Both sides use the same source tower/podium and viewport route. The last command is the full Central attempt and is expected to remain difficult on this software-rendered cloud host. Failed full-scene runs are preserved rather than silently replaced by fixture success.

## Evidence and remaining acceptance

`evidence/planner-before.json` and `planner-after.json` replay 6,522 catalogue rows (deduplicated by UID inside the layer) across six sizes. Settled planning drops from 40 executions to two in each run: 95% fewer. Moving p95 timings vary by viewport and run, including regressions on this host; see the exact JSON. No general FPS improvement is inferred.

`evidence/browser-fixture-baseline.json` and `browser-correctness.json` contain cold stage distributions and 40-frame stable samples for phone and 4K viewport emulation. These are a small isolated real-asset fixture, not whole-city pan/zoom/fly acceptance. Scheduling adds wall time while yielding; worker and render timing are particularly noisy under SwiftShader. The reports retain median/p95, long tasks, stage costs and request counts. `ocean-pride-*.png` are the actually rendered embedded-canvas exports.

The correctness matrix covers 390×844, 844×390, 600×800, 1024×768, 1366×768, 1920×1080, 3440×1440 and 3840×2160; requested DPR 1, 1.25, 1.5, 2 and 3; plus 480×320 embedded and hidden/revealed containers. Native Ocean Pride Tower 2 and its exact installed podium retain source picking, collision, placement and support visibility. Only two source transfers occur through all resizes. Higher quality additionally verifies a 6720×3780 drawing buffer for 3840×2160 at device DPR 2.

`evidence/before-diagnostic.json` and `after.json` preserve full Central readiness timeouts at 90 seconds. Before, no base tiles had completed; after, four tiles / 7,999 forms had completed, but software-rendered triangles grew to about three million and frames stalled for seconds. Neither completed the route, so their frames are **not a matched before/after performance claim**. An earlier 180-second baseline attempt also timed out before this diagnostic capture.

Remaining gates: named physical low-power phone, integrated-GPU laptop and capable desktop cold/warm pan/zoom/fly routes; real monitor/DPR transitions; full-scene long-task, draw and resident-memory envelopes; thermal behavior; and baseline-relative frame targets with no material desktop regression. Automatic budget escalation/de-escalation and adaptive render scale remain deferred until those measurements justify thresholds. The static conservative and fixed-quality controls are available now. Full-territory visual acceptance is not established by two representative native components.

## Publication

The live PR #298 base was rechecked after implementation and remains `4bf9293b2c20daffe3568e99a60cc737b29e483d`. Changes are committed on `codex/hks-229-canvas-streaming`, stacked on `codex/astra-hong-kong-city`, never main. No ongoing import work was modified.

No push or PR creation was performed: the repository's existing Vercel Git integration publishes previews, and a no-deployment publication path could not be established. This honors the user's explicit no-deploy instruction. `DRAFT-PR.md` is ready for a later authorized draft publication with the correct stacked base. Nothing was merged or configured for auto-merge.

### Final regression investigation

The first isolated frame sample regressed, so it was not accepted as a speedup or dismissed as noise. Review confirmed identical rendered geometry (38,659 triangles, two draws) and matching phone/4K drawing buffers; measured planner CPU p95 was at most 0.7 ms before and no planner ran in the settled after sample. This does not account for the software-renderer's much larger frame stalls. Old Chromium process entries were defunct with zero resident memory, not active competing renderers. A stale earlier Node test process was terminated before serial repeats.

A separate test-harness defect was found: setting Playwright's viewport after the CDP DPR override reset DPR to the context default. The initial reports are retained as `*-initial.json` with that limitation and do **not** establish high-DPR correctness. Corrected `*-ab.json` / `*-ba.json` runs set viewport first, apply DPR last, assert actual `devicePixelRatio`, and assert actual drawing-buffer dimensions. They run serially in AB/BA order, with 30 warmup frames and 40 measured frames at phone and 4K sizes. The isolated baseline intentionally uses the same canvas adapter as the after run to hold buffer cost constant; it compares model streaming code, not the old startup window-sizing behavior.

Corrected serial results (milliseconds, median / p95):

| Order | Viewport / verified effective DPR | Before | After |
| --- | --- | --- | --- |
| AB | 390×844 / 1.5 (device DPR 3) | 81.9 / 91.3 | 85.6 / 103.1 |
| AB | 3840×2160 / 0.6944 (device DPR 2, 4M pixel cap) | 149.5 / 175.4 | 142.1 / 159.8 |
| BA | 390×844 / 1.5 (device DPR 3) | 84.4 / 93.6 | 81.3 / 90.1 |
| BA | 3840×2160 / 0.6944 (device DPR 2, 4M pixel cap) | 142.5 / 161.1 | 150.7 / 184.6 |

The difference changes sign with repeat order. All four corrected runs assert actual DPR/buffer dimensions, two draws, 38,659 source triangles and two source transfers. No concurrent active Chromium or test run was used for these repeats. This establishes fixture correctness, not a reliable frame-time improvement. The performance acceptance gate remains **not passed / unverified**; full-scene and physical testing is still required. The canonical `browser-*.json` reports are explicitly labelled copies of the BA run, not extra independent samples. The initial AB attempt's fixed 150 ms settling wait was also replaced with an asserted viewport/DPR-state wait before the completed AB pair.

Final automated checks: **303/303 unit tests pass**, no failures/cancellations/skips, 37.86 seconds; all **23 changed JS/MJS files** pass `node --check`; `git diff --check 4bf9293b` passes. The static city package has no configured lint or TypeScript check, so no such pass is claimed. Final embedded-label clipping is a coordinate-only correction additionally syntax-checked. `evidence/verification.json` records commands, runtime head and remaining gates.

## Review publication follow-up

The user subsequently requested creation as a draft followed by marking ready to start the review bot. A branch-specific `git.deploymentEnabled` exclusion in `3d-viewer/vercel.json` prevents automatic Vercel Git deployments from `codex/hks-229-canvas-streaming`; other branches are unaffected. Review readiness does not resolve the performance acceptance gates above and does not authorize merge, auto-merge or deployment.
