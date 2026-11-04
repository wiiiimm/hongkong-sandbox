# HKS-214 — West Kowloon Station reclaimed-land correction

The earlier station child inherited zero-height water-mask nodes underneath actual source-confirmed land. Its low-rim checks missed the interior: the station centre had no rendered terrain triangle, although LandsD native TIN gives 7.637826 m HKPD. This correction supersedes the station terrain approval in the earlier five-part identity review. The building source geometry remains unchanged.

`station_mask.py` stages an immutable replacement at `support-native-297401-0-station-land-v2.json`. It repairs only source-positive masked nodes covered by the official station footprint plus a 1.414 m collar (one diagonal interpolation cell). The grid extends 140 m west to include the station's western wing. All 20,565 one-metre footprint census points have native source coverage; none lie outside the replacement. The 1 m spacing is a sampling interval, not a claim of survey accuracy.

10,782 nodes are corrected: 8,787 existing-child nodes and 1,995 in the new western extension. `changed-nodes.json` records each index, prior value and exact source TIN height. All unlisted existing nodes and vegetation remain unchanged. The replacement outer boundary remains equal to its previous/parent terrain. Its coarse cells are `[498,420,503,425]`; no other current manifest child overlaps that rectangle.

The normal-scene browser check intercepts only the station terrain URL and corresponding manifest entry. It verifies 104 terrain rays spanning centre/interior/western wing on desktop and emulated mobile. Every ray hits land, and rendered mesh and sampler agree within 2 mm. Four day/night screenshots show the native station active with no page errors or horizontal overflow. Desktop daytime and mobile night images were inspected: the sweeping station roof and west wing remain visible, with no fabricated window stamps on the opaque roof. This is not a physical-mobile performance certification.

The complete source model has 168,011 vertices and 58,632 triangles. After correction, 191 vertices are below local terrain by more than 0.25 m, but **zero entire triangles** and **zero upward faces** are buried. These are intersections at foundation/terrain boundaries, not wholly concealed roof geometry. Original native source elevations and 1x scale are preserved.

Neighbouring non-station water-mask gaps are still visible in the wider scene and are outside this footprint-bounded repair. This proves the native station part and its ground coverage, not completion of West Kowloon or every station component.

Reproduce from the Astra worktree:

```sh
/tmp/astra-city-venv/bin/python source-scripts/city/identity-hold-review/station_mask.py
node source-scripts/city/identity-hold-review/station_mask_surfaces.mjs
node source-scripts/city/identity-hold-review/station_mask_browser.mjs
```

The parent integrator must verify the superseded terrain SHA and changed-node allowlist, replace its manifest entry with the new URL, validate expanded coarse-cell coverage, and rerun actual installed-route checks. Historical evidence and the prior terrain asset remain immutable.
