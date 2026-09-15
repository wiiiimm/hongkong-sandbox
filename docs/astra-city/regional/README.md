# Regional browsing and local surfaces

GPT-6 Astra, 6 September 2026. HKS-116 and HKS-122–128. This pass adds 153 source-backed destinations across all 132 review sections: 147 have independently checked public-path arrivals and six are aerial-only. Together with the original 43 destinations, the viewer has 196 places. The seven regional issues remain in progress: these arrivals and surface polygons are not complete architectural or walking-route acceptance.

Three retained OSM packages supply 2,923 local surfaces: 412 in Lantau/outlying islands, 1,710 in Hong Kong Island/Kowloon and 801 in the New Territories. They include mapped beaches, piers, pitches, plazas and airport aprons, with source polygons and holes preserved. Each package has its own scripts, snapshots, hashes, validation and source notes in the matching subdirectory. All source reference imagery remains untouched. Colours, terrain-draped elevations and visual construction details are illustrative.

The renderer merges nearby surface geometry by type in 1.6 km cells, limits the cache to 24 cells, handles failed package fetches with Retry, and disposes evicted geometry. Nature instances are excluded from mapped activity surfaces. The original destination URLs remain supported; search accepts English, Chinese and section IDs. Walking is disabled for the six aerial-only destinations.

## Verification

- `python source-scripts/city/build_regional.py` validates all section assignments, shape validity, rounded arrivals, dry terrain and 1.2 m building clearance. Use the city Python requirements.
- `cd 3d-viewer/city && npm test` includes geometry, lifecycle, search, arrival and tree-mask checks.
- `npm run test:regional` exercises 21 representative sections across all 18 districts, walking, mobile, night controls and failure/Retry. Evidence: [browser/verification.json](browser/verification.json).
- An independent browser review checked urban surfaces, mobile labels, overlap exclusions, tree masking and delayed-fetch disposal. Evidence: [review/](review/).

No buildings were added by this surface pass. The original OSM base was 117,062 forms; the subsequent LandsD Mui Wo coverage work has its own source and count report. Terrain resolution and source omissions remain separate concerns.
