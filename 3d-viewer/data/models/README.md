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

---

## Fly-mode airframes (HKS-110)

All five selectable aircraft load a real open-source mesh over the procedural
stand-in (same pattern as the hiker). Cathay-style **painted** liveries stay on
the procedural builders; downloaded models are clean airframes (no airline
trademark textures from the source files). Attribution is also in the Credits drawer.

Rebuild any plane with:

```bash
node ../../scripts/trim_plane_glb.mjs <input.glb> <output.glb>
```

### plane-prop.glb — light single-prop (`pl=prop`)

- **Model:** “Airplane” by **Poly by Google**
- **Source:** https://poly.pizza/m/8VysVKMXN2J
- **Licence:** **CC-BY** (Poly by Google catalogue)
- **Original:** `https://static.poly.pizza/13293400-c90f-4cc0-966a-7e07d38f7565.glb` (~378 KB)
- **Modifications:** animations dropped (none useful), resample/dedup/prune/quantize → ~351 KB
- **Notes:** low-poly GA silhouette; procedural red-trim Cessna-style builder remains fallback

### plane-twin.glb — twin / DC-3 stand-in (`pl=betsy`)

- **Model:** “plane 2” by **Jake Blakeley**
- **Source:** https://poly.pizza/m/amIu9ua-L0A
- **Licence:** **CC-BY**
- **Original:** `https://static.poly.pizza/5cfb30a6-25ab-4f27-94f4-dec75879eac4.glb` (~55 KB)
- **Modifications:** optimised → ~47 KB
- **Notes:** **partial upgrade** — no clean CC0/CC-BY Douglas DC-3 was available at ship
  time; this is a light twin-style airframe for Betsy until a better match is found.
  Procedural VR-HDB “Betsy” builder remains the detailed livery fallback.

### plane-747.glb — Boeing 747 (`pl=cx747`)

- **Model:** “Boeing 747” by **Miha Lunar**
- **Source:** https://poly.pizza/m/49CLof4tP2V
- **Licence:** **CC-BY**
- **Original:** `https://static.poly.pizza/f9afa9f0-92a5-41c1-afa4-c0b7d3444f35.glb` (~117 KB)
- **Modifications:** optimised → ~99 KB
- **Notes:** real 747 silhouette; no airline livery textures from the source — painted
  Cathay brushwing stays on the procedural stand-in

### plane-jet.glb — widebody jet (`pl=cx777`)

- **Model:** “Jet” by **Poly by Google**
- **Source:** https://poly.pizza/m/3B3Pa6BHXn1
- **Licence:** **CC-BY** (Poly by Google catalogue)
- **Original:** `https://static.poly.pizza/fd29b917-dada-4982-92e0-f812d71f0afe.glb` (~22 KB)
- **Modifications:** optimised → ~19 KB
- **Notes:** generic airliner jet; used for 777 skin (no clean CC0 777 found)

### plane-airliner.glb — long-haul jet (`pl=a350`)

- **Model:** “Jet” by **jeremy**
- **Source:** https://poly.pizza/m/6fyLMORhgGK
- **Licence:** **CC-BY**
- **Original:** `https://static.poly.pizza/19d58465-dafb-4df0-a3b8-b0500bd9ed4b.glb` (~78 KB)
- **Modifications:** optimised → ~66 KB
- **Notes:** **partial upgrade** — generic jet for A350 until a better airframe is licensed

### Deploy note (all plane GLBs)

On production, upload every `data/models/plane-*.glb` to the R2 assets bucket under
the same path (with the terrain JSON and hiker). The service worker precaches them
in `DEFAULT_TERRAIN`. Until then, fly mode keeps the procedural builders (by design).
