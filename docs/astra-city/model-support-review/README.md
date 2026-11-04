# Native support streaming — HKS-214

Native towers now retain the supporting geometry used in their placement review. A tower and its transitive native supports enter the existing count, geometry-memory, resident-memory and triangle budgets together. Supports load before dependent models; a failed support keeps the tower's original form until Retry succeeds. Small or off-camera podiums remain eligible while a visible tower needs them. Existing mobile and desktop limits are unchanged.

Retirement reverses that order: a tower's fallback must finish replacing it before its native podium can retire. A failed fallback bake preserves both source models and their memory accounting. Supporting groups also remain visible across source-tile boundaries, including the interval after a retiring tower leaves the lookup map but before its fallback bake removes the old visible geometry.

Metadata is `supportDependencies:[{uid,state,csuid?,...}]`. `candidate` and `installed` mean the native source model is required. `fallback` and `surveyed-footprint-fallback` require the already loaded surveyed form and never request an unavailable native model. Early string entries, including Masterpiece's K11 dependency, are interpreted as fallback. A plan cannot simultaneously upgrade a form that an admitted model requires as surveyed fallback. Unknown states, conflicting dependencies, missing native sources and cycles keep the original forms; cycles are not partially activated. Reasons are available through `officialModels.stats.supportHolds`.

The viewer does not invent dependencies from proximity. Catalogues must carry reviewed source relationships. A source tile must already be available before admitting its model; this change does not introduce a second raw tile loader or increase city streaming radius.

## Verification

- 23 focused tests pass, including the existing official-model suite and an actual `CityStreaming` replacement-order test.
- New tests cover shared/transitive supports, off-camera support LOD, failure/Retry, cancellation, failed fallback restoration, visibility while rebaking, cycles, unavailable sources, surveyed fallback conflicts, and each mobile budget independently.
- The [catalogue audit](catalogue-audit.json) checks the current installed catalogues without downloading models. At this snapshot, 2,300 source models include 57 entries with dependencies; each declared closure fits unchanged mobile limits and resolves to existing catalogue entries. This is not a claim that every source tile is currently loaded.
- The [real browser run](browser.json) exercises Manhattan Heights `landsd/136500:0` and podium `landsd/114461:0` on 1280×900 desktop and 390×844 mobile Chromium emulation. An injected podium HTTP503 leaves both native parts inactive and the tower fallback present. Retry attaches the podium first; travelling away starts podium retirement only after the tower is inactive. Both final screenshots were inspected. No page errors or horizontal overflow occurred, and measured model counts, resident bytes and triangle counts remain within their profiles.

[Desktop after Retry](desktop-native-support-after-retry.jpg) · [Mobile after Retry](mobile-native-support-after-retry.jpg)

The browser check is a lifecycle test against unchanged installed geometry, not architectural sign-off, phone thermal testing or production publication. Surrounding buildings remain visible. The recorded runtime hashes are unchanged across the final run; future integration changes require their own installed check.

## Reproduce

```sh
node --test --test-timeout=10000 3d-viewer/city/tests/official-models.test.js 3d-viewer/city/tests/model-support.test.js
node source-scripts/city/model-support-review/audit.mjs
node source-scripts/city/model-support-review/browser.mjs
```

The browser test uses the running local viewer on port4176, private HTTP failure injection and the existing review-hook pattern. It never edits source geometry, shared databases, catalogues or production assets.
