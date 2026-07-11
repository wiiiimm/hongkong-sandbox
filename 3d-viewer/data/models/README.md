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
