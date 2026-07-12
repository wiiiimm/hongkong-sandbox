# 3D models — provenance

## hiker-adventurer.glb — the walk-mode hiker

- **Model:** “Adventurer” by **Quaternius**
- **Source:** https://poly.pizza/m/5EGWBMpuXq (Poly Pizza) · author: https://quaternius.com
  (from the Ultimate Animated Character Pack)
- **Licence:** **CC0 / public domain** — Poly Pizza model page states
  “Creative Commons public domain zero 1.0”; Quaternius publishes all packs as
  CC0 (“free for everyone to use in any project, even commercially”).
  No attribution required — credited anyway in the app’s Credits drawer.
- **Original file:** `https://static.poly.pizza/bbe369ee-a686-42c7-adad-14356f5f2f15.glb`
  (1.94 MB, FBX2glTF v0.9.7 export, 24 animation clips, 10 198 tris, no textures —
  flat material colours).
- **Modifications (this repo):** trimmed to the 4 clips the viewer uses
  (`Idle`, `Walk`, `Run`, `Wave`), resampled/deduped/pruned and quantized
  (adds `KHR_mesh_quantization`) with glTF-Transform → **~743 KB raw / ~234 KB gzip**.
  POSITION attributes stay float32 — three r160's `computeBoundingBox` reads
  quantized attributes raw, which broke the viewer's height normalisation.
  Geometry, rig and materials otherwise untouched.
- **Rebuild:** `node ../../scripts/trim_hiker_glb.mjs <original.glb> hiker-adventurer.glb`
  (needs `@gltf-transform/core|extensions|functions` v4 — see the script header).
- **Used by:** `main.js` `loadHikerModel()` — walk-mode chase-view body, driven by
  its own Idle/Walk/Run clips via `THREE.AnimationMixer`. The procedural box hiker
  in `buildHiker()` remains the loading stand-in / offline fallback.
- **Deploy note:** on the official deploy `data/` is served from the R2 assets
  origin — upload this file to the bucket under `data/models/` (same path), like
  the terrain JSON. The service worker precaches it (sw.js `DEFAULT_TERRAIN`).

## Fly-mode aircraft (HKS-110)

Four lightweight, licence-verified airframes progressively replace the procedural
exteriors in Fly mode. The procedural models remain the immediate loading state and
permanent offline/error fallback; they also continue to own the cockpit interiors,
camera offsets, retractable-gear contract, animated propellers and navigation lights.

All four source pages state **“Creative Commons Attribution”** and link to
[CC BY 3.0](https://creativecommons.org/licenses/by/3.0/). Attribution is retained
here and in the bilingual in-app Credits drawer.

| File / selection | Source model | Author | Original GLB | Raw size |
|---|---|---|---|---:|
| `aircraft-prop-small-airplane.glb` (`prop`) | [Small Airplane](https://poly.pizza/m/7cvx6ex-xfL) | Vojtěch Balák | [Poly Pizza CDN](https://static.poly.pizza/077afae1-24b7-4bac-a31d-53d367002a04.glb) | 36,200 B |
| `aircraft-cx747-boeing-747.glb` (`cx747`) | [Boeing 747](https://poly.pizza/m/49CLof4tP2V) | Miha Lunar | [Poly Pizza CDN](https://static.poly.pizza/f9afa9f0-92a5-41c1-afa4-c0b7d3444f35.glb) | 116,644 B |
| `aircraft-cx777-generic-airliner.glb` (`cx777`) | [Airplane](https://poly.pizza/m/a3XrQkLNna9) | Poly by Google | [Poly Pizza CDN](https://static.poly.pizza/e6ac358e-e5a4-4a1b-8ffe-71d6d7ffa52f.glb) | 193,456 B |
| `aircraft-a350-generic-airliner.glb` (`a350`) | [Airplane](https://poly.pizza/m/8ciDd9k8wha) | Poly by Google | [Poly Pizza CDN](https://static.poly.pizza/4754ce4b-40ec-4089-8be4-98ce7230bfe4.glb) | 236,520 B |

### Modifications and runtime treatment

- The GLBs are stored byte-for-byte as downloaded. At **582,820 bytes total**, they
  are already far below HKS-110's 8 MB aggregate mobile budget, so lossy geometry or
  texture processing would add risk without a useful payload saving.
- `main.js` normalises each model to the viewer's forward = `-Z`, centred-fuselage,
  gear/waterline contract and the corresponding procedural airframe length.
- Generic blue texture pixels on the two passenger airliners are translated at
  runtime to the project's sampled Cathay jade palette. Titles and brushwing-tail
  panels are original runtime canvas art from the existing photo-referenced livery,
  not downloaded airline textures.
- Source materials are cloned before grading, so Matrix / Neon look filters and
  disposal during hot-swaps do not mutate or leak loader-owned resources.
- The A350 candidate exposes wheel nodes separately; those baked wheels are hidden
  so the procedural retractable gear remains authoritative. The other candidates
  keep their baked low-poly gear where it is inseparable from the airframe mesh.
- **Betsy / DC-3 remains procedural.** No candidate found during this pass combined
  an unambiguous permissive licence, credible DC-3 silhouette and mobile-suitable
  downloadable geometry. HKS-110 explicitly permits a partial upgrade rather than
  substituting a misleading or legally unclear model.

### Deploy note

Upload all four GLBs to the official R2 bucket under `data/models/` at merge. They
are listed in `sw.js`'s best-effort precache so an aircraft used online remains
available offline; a cold/offline miss simply keeps the procedural aircraft.
