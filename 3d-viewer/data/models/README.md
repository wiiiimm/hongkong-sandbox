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

## plane-prop.glb — fly-mode prop plane (HKS-110)

- **Model:** “Small Airplane” by **Vojtěch Balák**
- **Source:** https://poly.pizza/m/7cvx6ex-xfL (Poly Pizza)
- **Licence:** **CC BY 3.0** — “Creative Commons Attribution” on the model page;
  credited in the app’s Credits drawer.
- **Original file:** `https://static.poly.pizza/077afae1-24b7-4bac-a31d-53d367002a04.glb`
  (36 KB, 584 tris, flat material colours — white hull with red trim, no branding).
- **Modifications (this repo):** dedup/prune/quantize with glTF-Transform
  (POSITION stays float32, same r160 lesson as the hiker) → **~31 KB raw / ~12 KB gzip**.
  Normalised at runtime by `loadPlaneModel()` (nose −Z as authored; fitted to the
  procedural prop plane’s length/waterline). Its `Propeller_Cone` node is wired
  into the shared prop-spin.
- **Rebuild:** `node ../../scripts/trim_plane_glb.mjs <original.glb> plane-prop.glb`
- **Used by:** `main.js` `PLANE_GLBS.prop` — the `prop` fly-mode skin. The
  procedural builder stays as loading stand-in / offline fallback.

## plane-747.glb — fly-mode Boeing 747 (HKS-110)

- **Model:** “Boeing 747” by **Miha Lunar**
- **Source:** https://poly.pizza/m/49CLof4tP2V (Poly Pizza)
- **Licence:** **CC BY 3.0** — “Creative Commons Attribution 3.0” on the model
  page; credited in the app’s Credits drawer.
- **Original file:** `https://static.poly.pizza/f9afa9f0-92a5-41c1-afa4-c0b7d3444f35.glb`
  (117 KB, 1 904 tris, flat material colours — clean white/grey airframe, no
  airline branding).
- **Modifications (this repo):** dedup/prune/quantize (POSITION float32) →
  **~99 KB raw / ~39 KB gzip**. Normalised at runtime (nose −Z as authored,
  fitted to the procedural CX 747’s length/waterline).
- **Rebuild:** `node ../../scripts/trim_plane_glb.mjs <original.glb> plane-747.glb`
- **Used by:** `main.js` `PLANE_GLBS.cx747` — the `cx747` fly-mode skin.

## plane-777.glb — fly-mode widebody twin-jet (HKS-110)

- **Model:** “Airplane” by **Poly by Google**
- **Source:** https://poly.pizza/m/fzIXe2paBN9 (Poly Pizza, archived Google Poly)
- **Licence:** **CC BY 3.0** — “Creative Commons Attribution” on the model page
  (Google Poly assets were published CC BY 3.0); credited in the Credits drawer.
- **Original file:** `https://static.poly.pizza/d2e42bad-4a68-40b8-abee-f8744cf8d2db.glb`
  (15 KB, 1 100 tris, flat material colours — teal-blue hull, grey engines; the
  internal node is named `Boeing_787_8.obj`, i.e. a generic Boeing widebody
  twin-jet shape standing in for the 777).
- **Modifications (this repo):** dedup/prune/quantize (POSITION float32) →
  **~15 KB raw / ~11 KB gzip**. Normalised at runtime (authored tail at −Z →
  yawed 180° so the nose faces −Z; fitted to the procedural CX 777’s
  length/waterline). The hull material is re-tinted **Cathay brushwing jade
  (#00655B)** at load — our own colour choice over the author’s geometry.
- **Rebuild:** `node ../../scripts/trim_plane_glb.mjs <original.glb> plane-777.glb`
- **Used by:** `main.js` `PLANE_GLBS.cx777` — the `cx777` fly-mode skin.

## plane-a350.glb — fly-mode Airbus A350-1000 (HKS-110)

- **Model:** “[FREE] Airbus A350-1000” by **hakai315**
- **Source:** https://sketchfab.com/3d-models/free-airbus-a350-1000-0729c1138a8f4186a549abffc1ff1721
  (Sketchfab) · author: https://sketchfab.com/hakai315
- **Licence:** **CC BY 4.0** — the bundled `license.txt` states: “license type:
  CC-BY-4.0 (http://creativecommons.org/licenses/by/4.0/) · requirements:
  Author must be credited. Commercial use is allowed.” Credited in the app’s
  Credits drawer (en + 繁中); attribution is load-bearing under CC BY.
- **Original file:** Sketchfab glTF export (`scene.gltf` + 70 MB `scene.bin` +
  2 textures), **1 973 821 tris / 1 061 377 verts**, flat material colours with
  a branding-clean “No_human_logo” engine texture set.
- **Rejected candidate (do not re-litigate):** Sketchfab uid
  `97577f60b81140e995d27dbb0ca36181` — an alternative A350 that is
  **CC BY-NC-SA** (non-commercial, share-alike): incompatible with this
  project’s commercial licensing. hakai315’s CC BY 4.0 model was chosen instead.
- **Modifications (this repo):** heavy decimation + our own livery, via
  `trim_a350_glb.mjs` (a350-specific — does far more than `trim_plane_glb.mjs`):
  interior/outlier groups dropped (engine fan blades, cargo-bay interiors,
  cabin floors, a stray mesh floating ~140 m off the nose that would have
  broken the loader’s bounding-box fit), textures stripped to flat colours,
  then flatten/join/weld + meshopt-simplify with a connected-component prune
  (sub-2.6-unit hardware invisible at fly-mode distances), dedup/prune/quantize
  (POSITION float32, 8-bit normals) → **52 144 tris, ~1.7 MB raw / ~630 KB gzip**.
  The livery is **our own Cathay-style repaint baked in-file**: fuselage, nose,
  doors and tail fin re-materialed to brushwing jade **#00655B** (`CXHull`),
  wings/belly/engines left grey — original colour work, no third-party airline
  branding shipped.
- **Rebuild:** `node ../../scripts/trim_a350_glb.mjs <scene.gltf> plane-a350.glb`
  (needs `@gltf-transform/*` v4 + `meshoptimizer` — see the script header).
- **Used by:** `main.js` `PLANE_GLBS.a350` — the `a350` fly-mode skin
  (authored nose −X → `rotY: -Math.PI/2`). The procedural builder stays as
  loading stand-in / offline fallback.

## Not upgraded (HKS-110)

- **betsy (Cathay DC-3 “Betsy” VR-HDB)** keeps its procedural canvas-livery
  build: no clean, licence-verified open-source DC-3 model was found (Poly
  Pizza has none; Sketchfab candidates were NC/ND, login-gated, or carried
  unverifiable real-airline branding).
- **Deploy note:** on the official deploy `data/` is served from the R2 assets
  origin — upload the four `plane-*.glb` files to the bucket under
  `data/models/` at merge, like the hiker GLB. sw.js precaches them
  (`DEFAULT_TERRAIN`, VERSION v26).
