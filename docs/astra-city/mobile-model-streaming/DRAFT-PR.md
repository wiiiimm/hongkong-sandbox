Title: perf(city): bound canvas-aware model streaming (HKS-229)
Base: codex/astra-hong-kong-city
Head: codex/hks-229-canvas-streaming
Draft: true

Camera and canvas changes previously rescanned all model metadata, used a startup width-based budget and could repeatedly abort or retire detail. This adds bounded spatial planning, two-axis CSS projection, finite hardware budgets, warm/source caches, safe fallback transitions, support/collision pins and coalesced container/DPR updates. Substantial fallback geometry runs in bounded workers; small measured-cheap swaps stay inline. Demo downloads and quality controls retain finite limits.

Original government assets, 1× HKPD transforms, import decisions and source terrain are unchanged. This is stacked on draft #298 and implements the viewer slice of [HKS-229](https://linear.app/stealth-company/issue/HKS-229), under HKS-199.

Validation: 303/303 city unit tests; syntax/diff checks; real Ocean Pride tower/podium browser fixture across eight viewports, high/fractional DPR, embedded/hidden canvases, exact worker-buffer parity, source picking/collision/support and two source transfers through all resizes. CPU catalogue replay performs 95% fewer settled planner executions. Exact results and commands: `docs/astra-city/mobile-model-streaming/IMPLEMENTATION-20261004.md` and `evidence/`.

This is not physical-device performance acceptance. Full Central routes time out under cloud SwiftShader; corrected serial AB/BA isolated fixture timings change sign and do not establish a reliable speedup. Performance acceptance is not passed/unverified. Phone/integrated-laptop/desktop frame targets, full-scene routes and adaptive budget/render-scale tuning remain acceptance gates. Keep draft; do not merge, auto-merge or deploy.

Publication is currently local only because the existing Git integration can automatically deploy a Vercel preview.
