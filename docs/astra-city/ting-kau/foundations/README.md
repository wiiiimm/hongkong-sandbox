# Foundation terrain correction · HKS-191

The first integrated bridge image review found real foundation islands with jagged heights. The bridge source meshes and mapped island outlines were correctly placed; the existing terrain mosaic was the problem. Its `valid &= fine > 0` rule retained an archival DTM water mask, excluding newer original TIN samples on parts of the mapped foundation islands. The surrounding 15 m blend retained elevated bridge artefacts. The issue was not missing source coverage.

The separate candidate restores original source-grid elevations across the complete Ma Wan tower island, the complete Ting Kau central tower island, and connected contaminated strips beside Ting Kau’s southern footing. The source grids derive from the same retained official terrain models already used for the common patch. Their native HKPD values remain unchanged. Five of the thirteen retained source sheets contribute to the repair; hashes are in [staging.json](staging.json).

The southern footing’s 45 m search radius selects a contaminated connected component, rather than defining a fabricated shore boundary. The repair follows connected bad grid cells and includes further contaminated components met by its 8 m guard. This extends along the adjoining mapped coast until the existing terrain already agrees with the source. The guard is wider than a 5 m triangle diagonal so all vertices contributing to the repaired shoreline are corrected. It changes intermediate terrain samples in some mapped water; the exact marine cut still removes that terrain. No land is added beyond the original `ContourPoly` boundaries.

Only 1,435 of 346,725 grid heights change. All 344,569 vertices outside the 2,156-vertex correction/guard mask remain identical. The original `renderedElev` coarse transition array is unchanged. No source model, original source grid, source building height, cable packet, mapped water polygon or bed triangle is modified. The original common patch remains intact beside the corrected candidate.

| Whole mapped area | Old rendered range, m HKPD | Corrected rendered range, m HKPD | Triangles checked |
| --- | --- | --- | --- |
| Ma Wan tower island, 22,175 m² | −4–46.06 | 1.30–11.29 | 1,898 |
| Ting Kau central tower island, 7,993 m² | −4–41.21 | 1.92–10.62 | 716 |
| Southern footing repair strips, 2,751 m² | −4–34.30 | 2.52–19.58 | 415 |

The −4 values are former render-water holes, not surveyed ground. Every clipped 5 m terrain triangle across these complete areas is compared with the original source grid: 3,029 triangles, 9,850 clipped vertices, maximum difference below 0.005 m from the existing 0.01 m rounding policy. Another 3,255 hydro replacement vertices match that terrain. The 139 dry transition neighbours match the source within 0.005 m; both former patch seams and the complete outer boundary are unchanged. The real northern shore slope reaches 27.93 m inside the 40 m audit neighbourhood and remains untouched, as does the eastern Tsing Ma footing. See [verification.json](verification.json) and the inspected [2,400 × 2,000 comparison](foundation-terrain-comparison-2400x2000.png).

The shared JavaScript terrain sampler verifies all 1,206 grid nodes inside both islands. Nine under-span samples remain open water with −4 m illustrative bed; original source-deck collision is retained and no public walking surface is inferred. See [runtime-helper-verification.json](runtime-helper-verification.json). These checks validate the 5 m resampling and software collision behaviour, not unsampled engineering detail, bathymetry or navigational clearance.

Reproduce from the Astra worktree after the original combined package exists:

```sh
/tmp/astra-city-venv/bin/python source-scripts/city/ting-kau/foundation_stage.py
/tmp/astra-city-venv/bin/python source-scripts/city/ting-kau/verify_foundations.py
node source-scripts/city/ting-kau/verify-runtime.mjs --foundations
/tmp/astra-city-venv/bin/python source-scripts/city/ting-kau/plot_foundations.py
```

The candidate is `source-scripts/city/ting-kau/foundation-candidate/terrain-tsing-ma-ting-kau.json` plus adjacent `hydro-tsing-ma-ting-kau.json`. Publication replaces only the existing live bridge-cluster patch and its two regional entries in the current hydro composite, preserving Tai O, Mui Wo, Pui O and every unrelated patch. Update the patch bytes/hash metadata. Do not load both original and corrected bridge patches. Root published the corrected patch and preserved the other hydro regions. The [final actual-city browser pass](../browser/README.md) verifies the original high-spike locations against actual mesh rays and includes inspected images of both complete islands. Source and browser evidence remain distinct.
