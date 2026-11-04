# Mui Wo bounded height recovery · 15 September 2026

This batch resolves the final three models held by the earlier 16-model Mui Wo pass. Each record has an exact Lands Department object ID and Building CSUID match, strong footprint overlap, and unchanged source asset bytes. The source meshes disagreed vertically with their current Lands Department building records.

The deterministic recovery applies one vertical translation per model so the highest source roof equals the current recorded `TopHeight`. The original GLB bytes, nodes, vertices, indices, materials, shape, and horizontal placement remain unchanged. The corrected mesh bottoms land within 1.1 metres of the current recorded `BaseHeight`.

| UID | Source model | Vertical correction | Result |
| --- | --- | ---: | --- |
| `landsd/172460:0` | `B178611539001062G0` | −8.4067 m | Installed |
| `landsd/201705:0` | `B179951563401062G0` | +4.1313 m | Installed |
| `landsd/208036:0` | `B171281503901062G0` | +4.5487 m | Installed |

All three passed source hash, catalogue schema, terrain sampling, runtime budget, source picking, collision, staged browser, live browser, mobile failure/retry, and desktop/mobile framing checks. Two foundations enter sloped terrain by about 2.4 metres while their source roofs remain above terrain and aligned to the official height. No terrain or source geometry was edited.

Yuen's Mansion (`YU TAK LEE YUEN`) was separately verified during this work. Its six government components were already installed through the older embedded `modelGeometry` tile path, so no duplicate catalogue was published for them.

Neon terminal job: `9a3a105548e14a12c977de0fa970680407b4062d784db5f5f6342a789d956ad`. Review snapshot: `53e94dc0e2aee182`. AI calls: 0. Remodelling: 0.
