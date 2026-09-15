# HKS-214 — previously inactive model parts

Executor: Astra `landmark_visibility_fix` subagent. Evidence captured 8 September 2026 against the runtime hashes and Git revision in `report.json`.

**All 10 previously never-active candidates loaded at individual close-up cameras, using the unchanged desktop profile.** There were no browser errors. This resolves the narrow loading question; it does not publish these candidates or approve their architecture, placement, or assembly membership.

The earlier preflight report and its snapshot `3887f2f23fbad306` are preserved. This is a separate inspection of the same pinned candidate model bytes in the current viewer. The harness verifies the candidate catalogue and fetched compressed asset hashes.

## Why the assembly gallery missed these parts

Prepared candidates retain `priority: unreviewed`, so the desktop detail range is 500 metres and the minimum projected extent is 18 pixels. Published landmark priority was not assigned to unapproved candidates to make the evidence pass.

| Assembly | Government part | Original view finding | Individual close-up |
| --- | --- | --- | --- |
| ICC | `landsd/201351:0` | 712 / 705 m from model bounds; outside 500 m range | Active |
| ICC | `landsd/269745:0` | 934 / 930 m; outside range | Active |
| Highcliff | `landsd/103538:0` | 15 / 11 px; close-up also 599 m away | Active |
| Highcliff | `landsd/176291:0` | Earlier overview inactivity did not reproduce after settling; close-up is 607 m away | Active |
| Island Shangri-La | `landsd/236189:0` | 515 / 610 m; outside range | Active |
| Langham Place Office Tower | `landsd/235506:0` | 567 / 586 m; outside range | Active; identity hold remains |
| Manhattan Heights | `landsd/101093:0` | 16.5 / 17.3 px; below minimum | Active |
| Queensway Government Offices | `landsd/70443:0` | 16.6 px; below minimum in both views | Active |
| The Center | `landsd/101313:0` | Overview 759 m away; closer view reaches existing 48-model count budget | Active |
| The Summit | `landsd/103209:0` | 14.2 / 15.1 px; below minimum | Active |

The Highcliff podium loaded when the old overview camera was replayed with a fresh settling period. The old gallery waits for loading before its final camera checks, then waits only 200 ms per reframe. That makes capture timing a plausible explanation, **not a proven runtime defect**. Current runtime hashes are recorded because the old evidence was captured at a different revision.

No renderer, source priority, global memory/count budget, model geometry, terrain, manifest, SQLite or publication file was changed by this investigation.

## Remaining acceptance work

- The missing Langham Place component is labelled **LANGHAM PLACE HOTEL** in its source record. Loading it does not resolve whether it belongs in the office-tower assembly. Keep the existing proposed identity unapproved.
- Most tiny parts are ancillary components, not the named main towers; count them as source parts.
- Active detailed-model membership proves that source geometry was installed in the current scene. Neighbour occlusion, foundations, source identity and architectural completeness still need review. The ICC close-up crops the tower top; this is not an accepted whole-building framing.
- No mobile performance, walking/collision, rooftop landing, night-lighting or whole-region acceptance is claimed.
- Full assembly evidence should settle again after reframing, then frame any inactive constituent separately. Do not raise all candidate priorities or increase the global cache to satisfy an assembly screenshot.

## Reproduce

Requires the pinned local preflight snapshot, its assets, the viewer data and installed `3d-viewer/city` Playwright dependency. Start the local viewer, then:

```sh
node source-scripts/city/landmark-visibility/inspect.mjs
```

Set `CITY_BASE_URL` to another running viewer (default `http://127.0.0.1:4176`). Browser selection uses the existing portable resolver (`CHROME_PATH` / `CHROMIUM_EXECUTABLE_PATH` overrides). The script writes only this evidence directory and asserts that every previously inactive candidate activates at its component camera. It changes candidate routes in its private Playwright page; it does not edit live data.

See [report.json](report.json) for exact cameras, source IDs/hashes, projected size, range, frustum, loaded-source state, detailed-model activity and cache totals. [contact.html](contact.html) links the ten close-up screenshots.

Sources: previously pinned Lands Department non-textured 3D building models and government footprint/height records. No reference map image was used or modified.
