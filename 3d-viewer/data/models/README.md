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

## plane-747.glb — fly-mode Boeing 747-400 (HKS-110)

- **Model:** “Air France Boeing 747-400” by **zairiqzairiq**
- **Source:** https://sketchfab.com/3d-models/air-france-boeing-747-400-58113c1d27984d90bd1f49cb1ff90db4
  (Sketchfab) · author: https://sketchfab.com/zairiqzairiq
- **Licence:** **CC BY 4.0** — the bundled `license.txt` states: “license type:
  CC-BY-4.0 (http://creativecommons.org/licenses/by/4.0/) · requirements:
  Author must be credited. Commercial use is allowed.” Credited in the app’s
  Credits drawer (en + 繁中); attribution is load-bearing under CC BY.
- **Original file:** Sketchfab glTF export (`scene.gltf` + 15.9 MB `scene.bin` +
  7 textures), **80 039 tris**, 133 meshes, 22 materials — a SketchUp-style
  export: untextured white hull + silver wings, **real extended landing gear**
  (twin-wheel nose strut + the -400’s four main posts), real dark
  window/cockpit-glass geometry, and the **Air France identity on floating
  decal plates** (AIRFRANCE titles, striped tail plate, SkyTeam / AF-KLM /
  engine-seahorse logos). No winglet blades despite the -400 title — the
  wingtips top out at the tip-light housings.
- **Modifications (this repo):** via `trim_747_glb.mjs` (the 777 recipe
  adapted to decal-based livery):
  - **Gear split:** connected components inside the measured nose/main gear
    boxes move to a `CXGear` material, so `loadPlaneModel()` tags them and
    `stepFlight` hides them airborne (HKS-110 fleet rule). Wheels reach below
    the belly line, so the parked stance survives the loader’s waterline fit.
  - **Livery:** all Air France branding removed and replaced with the
    project-supplied Cathay artwork documented in
    `../../scripts/assets/README.md`: the tail plate repainted jade
    **#00655B** with the complete white brushwing SVG; the title decal band
    painted hull-white with a jade brushwing beside the cockpit and the
    supplied serif **CATHAY PACIFIC** wordmark (the band’s two sides map
    opposite-signed u↔z, so starboard prims are split onto their own cloned
    texture and each side is painted through its own least-squares
    (u,v)→(z,y) fit, u-flipped so the lettering reads nose-first from either
    view — verified in the CPU-raster previews,
    `../../scripts/previews/cx747-zairiq-*`); SkyTeam / AF-KLM / engine-logo
    decal plates deleted. Windows are geometry, so the repaint can’t eat them.
  - **Budget (light — silhouette first):** flatten+join (the 348-node export
    wastes ~0.9 MB on per-part accessor overhead), dead UVs dropped from
    untextured prims, weld + meshopt-simplify at ratio 0.80,
    dedup/prune/quantize (POSITION float32, 8-bit normals), metallic/roughness
    clamps, textures ≤1024 px JPEG →
    **63 863 tris (11 125 of them gear), ~1.33 MB raw**.
- **Rebuild:** `node ../../scripts/trim_747_glb.mjs <scene.gltf> plane-747.glb`
  (needs `@gltf-transform/*` v4 + `meshoptimizer` + `sharp` — see the script
  header; the build is byte-reproducible).
- **Used by:** `main.js` `PLANE_GLBS.cx747` — the `cx747` fly-mode skin
  (authored nose +Z → `rotY: Math.PI`; `anchorLights` snaps the nav lights to
  this hull’s real wingtips/tail).
- **Supersedes:** “Boeing 747-100” by **Marine** (rd.palaciosdeleon26,
  Sketchfab
  https://sketchfab.com/3d-models/boeing-747-100-6ef67f9995d345ddaee9ec845ac10b69,
  CC BY 4.0, 35 502 tris) — the flight-sim-grade 747-100 whose ANA livery
  atlas we repainted jade in place (shipped ~1.55 MB, nose −Z). Replaced by
  user preference: Cathay’s classic jumbo was the **-400**, and the hull read
  too low-poly next to the rest of the HKS-110 fleet. Which itself superseded
  “Boeing 747” by **Miha Lunar** (Poly Pizza https://poly.pizza/m/49CLof4tP2V,
  CC BY 3.0, 1 904 tris) — the low-poly hull shipped first for HKS-110.
- **Evaluated, not used (original HKS-110 bake-off):**
  - “boeing 747” by **hilos run** (Sketchfab
    https://sketchfab.com/3d-models/boeing-747-a285b0f308e5473d919d94cf00358e9f,
    CC BY 4.0, 1 371 771 tris) — a SketchUp-style scene export: dozens of
    duplicated 4 k-tri detail objects, stray ground/scene geometry, flat
    colours only. Needed 97 %+ decimation plus scene surgery for a worse
    starting livery than the 747-100; not worth it.
  - “Boeing 747-8i” by **outpiston** (Sketchfab
    https://sketchfab.com/3d-models/boeing-747-8i-61b531546bb242f690f87028e333aa5c,
    ⚠ CC BY-NC-SA 4.0, 9 527 tris) — lowest-poly of the three and NC-fenced;
    since the shipped hull gets our repaint anyway, the NC cost bought
    nothing over the CC BY candidates.

## plane-777.glb — fly-mode Boeing 777-300ER (HKS-110)

- **Model:** “boeing 777-300ER Saudi Arabian Airlines (Saudia)” by **Omatar**
- **Source:** https://sketchfab.com/3d-models/boeing-777-300er-saudi-arabian-airlines-saudia-410ec4a0d4b646918ac2e5f83b48c27e
  (Sketchfab) · author: https://sketchfab.com/Omatar
- **Licence:** **CC BY 4.0** — the bundled `license.txt` states: “license type:
  CC-BY-4.0 (http://creativecommons.org/licenses/by/4.0/) · requirements:
  Author must be credited. Commercial use is allowed.” Credited in the app’s
  Credits drawer (en + 繁中); attribution is load-bearing under CC BY.
- **Original file:** Sketchfab glTF export (`scene.gltf` + 26 MB `scene.bin` +
  one 2048² “Stickers” baseColor atlas), **507 667 tris**, 241 meshes, 69
  materials, no animations. Livery as authored: the **Saudia 75-years scheme**
  — “saudia” titles, green/blue cheatlines and the 75-years gold mark in the
  atlas (two fuselage side strips + the green fin plate); everything else is
  flat-coloured materials. Crucially it ships **real extended landing gear** —
  two 6-wheel main bogies (struts, open bay doors) + a twin-wheel nose gear —
  and real dark **window/cockpit-glass geometry**.
- **Modifications (this repo):** via `trim_777_glb.mjs` (the A350 recipe
  ported to this hull):
  - **Gear split:** connected components inside the measured nose/main gear
    boxes move to a `CXGear` material, so `loadPlaneModel()` tags them and
    `stepFlight` hides them airborne (HKS-110 fleet rule). Wheels reach below
    the belly line, so the parked stance survives the loader’s waterline fit.
  - **Livery:** the Saudia branding is replaced with the project-supplied
    Cathay artwork documented in `../../scripts/assets/README.md`, painted in
    world space through per-texel world coords recorded while rasterising each
    region’s actual UV triangles: clean white hull with the subtle pale-jade
    lower band, jade **#00655B** fin with the complete white brushwing SVG,
    the brushwing again in jade aft of the cockpit, and the supplied serif
    **CATHAY PACIFIC** wordmark on both upper forward sides (flipped per side
    so it reads nose-first from either view). Cabin windows are geometry, so
    the wipe can’t eat them; uncovered atlas texels under the window holes are
    dilated/flooded so mip filtering never fetches old Saudia paint. The
    -300ER’s raked wingtips carry no winglet mark; the two full-length red
    strips (`Material.103`) are recoloured hull-white.
  - **Budget:** weld + meshopt-simplify (harder second pass on the CXGear
    wheel stacks), dedup/prune/quantize (POSITION float32, 8-bit normals),
    metallic/roughness clamps, atlas ≤1024 px JPEG →
    **56 104 unique tris (9 326 of them gear), ~1.94 MB raw** (dedup shares
    wheel meshes across the bogies, so the instantiated scene draws ~84 k).
- **Rebuild:** `node ../../scripts/trim_777_glb.mjs <scene.gltf> plane-777.glb`
  (needs `@gltf-transform/*` v4 + `meshoptimizer` + `sharp` — see the script
  header; the build is byte-reproducible).
- **Used by:** `main.js` `PLANE_GLBS.cx777` — the `cx777` fly-mode skin
  (authored nose −X → `rotY: -Math.PI/2`; `anchorLights` snaps the nav lights
  to this hull’s real wingtips/tail).
- **Supersedes:** “Boeing 777-300er.” by **The F-35’s Modeling Hub**
  (777_Boeing, Sketchfab
  https://sketchfab.com/3d-models/boeing-777-300er-2ee4847b20724a308ef73f33e3823ecb,
  CC BY 4.0, 119 998 tris — textureless, one flat grey material). Shipped
  earlier for HKS-110 with a vertex-colour Cathay livery + tangent decals and
  a heuristic below-the-engine-line gear split (48 041 tris shipped); replaced
  by user preference for this higher-fidelity hull with authored gear and
  UV-mapped skin. Which itself superseded “Airplane” by **Poly by Google**
  (Poly Pizza https://poly.pizza/m/fzIXe2paBN9, CC BY 3.0, 1 100 tris — a
  generic 787-8 shape standing in for the 777, jade-tinted at load).
- **Evaluated, not used (original HKS-110 bake-off):**
  - “Air New Zealand Boeing 777 219 ER” by **A Random Modeler**
    (danielskom111, Sketchfab, CC BY 4.0, 30 051 tris) — clean and cheap, but
    a shorter 777-200-series airframe; the -300ER shape won.
  - “Boeing 777- 300ER” by **Adam.White** (Sketchfab, CC BY 4.0, 236 444
    tris / 80 MB) — highest fidelity but needed the heavy decimation
    pipeline for no visible gain at fly-mode distances over the chosen model.
  - An **outpiston Air Canada 777-200LR** (⚠ CC BY-NC-SA 4.0) — REJECTED:
    our repaint makes its livery worthless, so the NC restriction buys
    nothing over the CC BY candidates.

## plane-a350.glb — fly-mode Airbus A350-1000 (HKS-110)

- **Model:** “A350 V3 with animation” by **Newbie99999993**
- **Source:** https://sketchfab.com/3d-models/a350-v3-with-animation-965439a6041847a0b8decba253ffdf6f
  (Sketchfab) · author: https://sketchfab.com/Newbie99999993
- **Licence:** **CC BY 4.0** — the bundled `license.txt` states: “license type:
  CC-BY-4.0 (http://creativecommons.org/licenses/by/4.0/) · requirements:
  Author must be credited. Commercial use is allowed.” Credited in the app’s
  Credits drawer (en + 繁中); attribution is load-bearing under CC BY.
- **Original file:** Sketchfab glTF export (`scene.gltf` + 20.6 MB `scene.bin` +
  one 4096² baseColor atlas), **626 981 tris**, 9 objects, 20 baked animations
  (a Sketchfab-retargeted gear-retract-style timeline). Livery as authored:
  the **AIRBUS house scheme** — “AIRBUS A350-1000” titles, giant “1000”s and
  carbon-pattern tail art in the atlas. Crucially it ships **real extended
  landing gear** — 6-wheel main bogies + twin nose wheels — which is why it
  was picked (“I prefer one with wheels and landing gear”).
- **Modifications (this repo):** via `trim_a350_glb.mjs`:
  - **Gear split:** connected components inside the measured main/nose gear
    boxes (plus the bogie-wheel objects wholesale) move to a `CXGear`
    material, so `loadPlaneModel()` tags them and `stepFlight` hides them
    airborne (HKS-110 fleet rule). The baked animations are dropped — the
    fleet rule is a visibility toggle and the GLB is reparented at load.
  - **Livery:** the AIRBUS house branding is replaced with the project-supplied
    Cathay artwork documented in `../../scripts/assets/README.md`: a clean
    white hull, subtle pale-jade lower band, procedurally redrawn cabin windows,
    the supplied serif **CATHAY PACIFIC** wordmark, a jade **#005D63**
    brushwing beside the cockpit, and the complete supplied brushwing SVG in
    white on the jade fin. The white winglet mark is limited to each winglet’s
    inward face by splitting those triangles to a second marked atlas; outward
    faces stay plain jade. Regions are masked by rasterising their actual UV
    triangles because the atlas islands interleave.
  - **Budget:** weld + meshopt-simplify (harder second pass on the two
    102 k-tri fan disks and the CXGear wheels), dedup/prune/quantize
    (POSITION float32, 8-bit normals), metallic clamped, atlas ≤1024 px JPEG
    → **47 590 tris (24 733 of them gear), ~2.11 MB raw / ~1.31 MB gzip**.
- **Rebuild:** `node ../../scripts/trim_a350_glb.mjs <scene.gltf> plane-a350.glb`
  (needs `@gltf-transform/*` v4 + `meshoptimizer` + `sharp` — see the script header).
- **Used by:** `main.js` `PLANE_GLBS.a350` — the `a350` fly-mode skin
  (authored nose +X → `rotY: Math.PI/2`). The procedural builder stays as
  loading stand-in / offline fallback.
- **Supersedes:** “[FREE] Airbus A350-1000” by **hakai315** (Sketchfab
  https://sketchfab.com/3d-models/free-airbus-a350-1000-0729c1138a8f4186a549abffc1ff1721,
  CC BY 4.0, 1 973 821 tris). Shipped first for HKS-110 with a scripted
  planar-projection livery, but the ~97 % decimation it needed read visibly
  broken at chase distance, and it had **no landing gear geometry at all**.
  Its hakai315-specific trim script (livery projection included) was removed
  with it — this file’s history has both if ever needed.
- **Evaluated, not used (2026-07 bake-off, gear-first):**
  - “Airbus A350-1000” by **outpiston** (Sketchfab uid
    `97577f60b81140e995d27dbb0ca36181`, ⚠ CC BY-NC-SA 4.0, 12 568 tris) —
    the A330/DC-3 author, so the fleet style would have matched, but it is
    NC-fenced (nc/ + commercial-deploy deletion, per LICENSE-ASSETS.md) and,
    like the same author’s A330, would still have needed procedural gear.
    A CC BY model with real gear beats it on both counts.
  - “Airbus +A350-900XWB” by **CloudHub** (Sketchfab
    https://sketchfab.com/3d-models/airbus-a350-900xwb-6fa01964177646d4943143c07047b933,
    CC BY 4.0, 194 243 tris) — licence-clean and has gear meshes, but it’s
    the shorter −900 airframe (skin says A350-1000), a 246-mesh SketchUp-style
    export with 36 flat materials and no UVs/textures, so it needed the full
    scene-surgery + repaint pipeline for a worse starting point.

## nc/plane-a330.glb — fly-mode Airbus A330-300 ⚠ NC (HKS-110)

- **Model:** “Cathay Pacific Airbus A330-300” by **OUTPISTON**
- **Source:** https://sketchfab.com/3d-models/cathay-pacific-airbus-a330-300-45a62d88607145c4afb1f46b281aa277
  (Sketchfab) · author: https://sketchfab.com/outpiston
- **Licence:** **⚠ CC BY-NC-SA 4.0** — the bundled `license.txt` states:
  “license type: CC-BY-NC-SA-4.0 (http://creativecommons.org/licenses/by-nc-sa/4.0/) ·
  requirements: Author must be credited. No commercial use. Modified versions
  must have the same license.” Credited in the app’s Credits drawer (en + 繁中,
  marked non-commercial). **Our modified GLB remains CC BY-NC-SA 4.0.**
- **NC fencing (see LICENSE-ASSETS.md):** lives under `data/models/nc/` —
  commercial deployments must delete the `nc/` folder. The `a330` skin then
  falls back to its procedural widebody-twin build (`buildCX777` stand-in).
  NC models are deliberately **not** in the SW `DEFAULT_TERRAIN` precache/migration
  list, so they never persist in Cache Storage and cannot be served after `nc/` is
  removed — they load on-demand (online only) on non-commercial deploys.
- **Original file:** Sketchfab glTF export (`scene.gltf` + 2.5 MB `scene.bin` +
  7 textures), 42 770 tris / 24.3 k verts, **real Cathay Pacific livery textures
  as authored — kept, not re-tinted** (that livery is the point of this asset).
- **Modifications (this repo):** optimisation only — dedup/prune/quantize
  (POSITION float32, same r160 lesson) and livery textures resized to ≤1024 px
  JPEG q78 → **42 766 tris, ~2.6 MB raw / ~1.4 MB gzip**.
- **Landing gear:** the source model ships with **no extended landing gear**
  (its lowest geometry is the engine cowls — verified by component analysis),
  so there is no `CXGear` split for this airframe. `loadPlaneModel()` lifts it
  to a gear stance and adds simple procedural gear instead
  (`PLANE_GLBS.a330.gearProc`); an earlier heuristic split only captured
  belly-fairing fragments and left the parked plane floating on its engines.
- **Rebuild:** `node ../../scripts/trim_a330_glb.mjs <scene.gltf> nc/plane-a330.glb`
  (needs `@gltf-transform/*` v4 + `sharp` — see the script header).
- **Used by:** `main.js` `PLANE_GLBS.a330` — the `a330` fly-mode skin
  (authored nose +Z → `rotY: Math.PI`; `fit` scales the 777-reference length
  down to the A330-300’s 63.7 m).

## nc/plane-betsy.glb — fly-mode DC-3 “Betsy” ⚠ NC (HKS-110)

- **Model:** “McDonnell Douglas DC-3” by **OUTPISTON**
- **Source:** https://sketchfab.com/3d-models/mcdonnell-douglas-dc-3-7673f61636554c02bf86015f1b6a8333
  (Sketchfab) · author: https://sketchfab.com/outpiston
- **Licence:** **⚠ CC BY-NC-SA 4.0** — the bundled `license.txt` states:
  “license type: CC-BY-NC-SA-4.0 (http://creativecommons.org/licenses/by-nc-sa/4.0/) ·
  requirements: Author must be credited. No commercial use. Modified versions
  must have the same license.” Credited in the Credits drawer (en + 繁中,
  marked non-commercial). **Our modified GLB remains CC BY-NC-SA 4.0.**
  NC is justified here: no licence-clean open DC-3 exists (earlier sweep:
  Poly Pizza has none; other Sketchfab candidates NC/ND or login-gated).
- **NC fencing (see LICENSE-ASSETS.md):** lives under `data/models/nc/` —
  commercial deployments delete `nc/`; the `betsy` skin falls back to its
  procedural `buildBetsyDC3` canvas-livery build.
- **Original file:** Sketchfab glTF export, 13 574 tris, bare-metal textures,
  named prop (`prop0/1_still…`) and tire nodes.
- **Modifications (this repo):** historically-correct **1946 VR-HDB markings**
  painted onto the (already bare-metal) atlas — a Union Jack on the tail fin,
  era-style “CATHAY PACIFIC AIRWAYS” titles above the windows and the VR-HDB
  registration (studied from period photography: Swire archive, preserved
  VR-HDB) — **no modern jade/green anywhere**; then dedup/prune/quantize
  (POSITION float32), textures ≤1024 px JPEG → **13 494 tris, ~0.7 MB raw**.
- **Runtime:** nose +Z → `rotY: Math.PI`; `fixedGear` — a taildragger’s
  semi-fixed gear stays visible in flight (fleet-rule exception); its
  `prop0_still`/`prop1_still` nodes join the shared airborne prop-spin.
- **Rebuild:** `node ../../scripts/trim_betsy_glb.mjs <scene.gltf> nc/plane-betsy.glb`

## Fleet rules (HKS-110)

- Landed: **gear + wheels visible, props/fans stopped**. Airborne: **gear
  hidden, props spinning** (throttle-tied). GLB gear is tagged via `CXGear-*`
  materials (split out by the trim scripts) or gear/wheel/tire node names;
  `stepFlight` drives visibility off the landed state. Exception: betsy
  (taildragger, `fixedGear`).
- **Deploy note:** on the official deploy `data/` is served from the R2 assets
  origin — upload all `plane-*.glb` files (including `nc/…` where licensing
  permits that deployment) to the bucket under `data/models/` at merge, like
  the hiker GLB. sw.js precaches the CC0/CC-BY models via `DEFAULT_TERRAIN`
  (VERSION `hks-sandbox-v33`). The `nc/…` GLBs are **excluded** from that list:
  they load on-demand (online only) and are not expected to work offline, so
  commercial deploys that delete `nc/` never serve them from Cache Storage.
