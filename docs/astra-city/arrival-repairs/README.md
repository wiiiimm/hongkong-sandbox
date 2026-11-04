# Arrival repairs after official building coverage

GPT-6 Astra, 6 September 2026. The full official footprint import invalidated five existing arrivals through building clearance; a sixth failed the stricter neighbouring-terrain check. Only those six arrival positions were moved. All destination IDs, camera centres and existing aerial-only choices were retained.

| Destination ID | Move | Retained public path |
| --- | ---: | --- |
| `mongkok` | 20.016 m | [way/970658225 — Portland Street pavement](https://www.openstreetmap.org/way/970658225) |
| `kowlooncity` | 4.973 m | [way/1348776549](https://www.openstreetmap.org/way/1348776549) |
| `lamma` | 4.973 m | [way/530132789](https://www.openstreetmap.org/way/530132789) |
| `section-01-2` | 74.444 m | [way/142227306](https://www.openstreetmap.org/way/142227306) |
| `section-05-1` | 4.965 m | [way/699026408](https://www.openstreetmap.org/way/699026408) |
| `section-05-2` | 11.442 m | [way/557643422](https://www.openstreetmap.org/way/557643422) |

Of **196 destinations**, all **190 walking arrivals** now pass. **184 walking arrivals remain unchanged**, and all **six existing aerial-only destinations remain unchanged**. Each repair is within 75 m of the old arrival, well inside the 1 km search limit. Rounded points lie within 0.049 m of their retained source path.

The candidate search is extracted from the existing `build_places.py` algorithm: footways, pedestrian ways, paths and living streets, with restricted, indoor, underground and elevated routes excluded. `arrival-validator.mjs` directly reuses the city's `makeTerrainSampler`, `BuildingIndex` and `collisionVolumes`; it creates no renderer or GPU context. Its checks include current terrain patches, detailed model bounds, open-sided roofs/posts and foundations. Each arrival must stand on a fully dry triangle, clear a 1.2 m disc for a 1.8 m actor, and have less than 1.5 m raw/rendered rise at four neighbouring points 2 m away. Each replacement also passes checks every 0.5 m along a 2 m section of its actual mapped path.

Tai O promenade did **not** require moving: it passes the runtime open-sided collision volumes. The previous regional validator treated the entire roof footprint as a solid building. Regional validation now calls the same runtime rules, eliminating that false conflict.

`before.json` freezes the initial generated destinations and failures. `repairs.json` records original/new coordinates, conflicting building UIDs, retained path tags/files/hashes and all short-walk samples. `verification.json` records the repeated full audit with zero remaining failures. `source-scripts/city/arrival-overrides.json` is the reproducible source configuration consumed by both destination builders; the six values are not manual-only changes to generated JavaScript.

## Rebuild and verify

From the feature worktree, with the current generated city/tile data and retained OSM snapshots:

```sh
CITY_NODE=/Users/williamli/.nvm/versions/node/v24.17.0/bin/node /tmp/astra-city-venv/bin/python source-scripts/city/repair_arrivals.py
CITY_NODE=/Users/williamli/.nvm/versions/node/v24.17.0/bin/node /tmp/astra-city-venv/bin/python source-scripts/city/build_regional.py
```

The repair command audits the currently generated destinations and moves only failures; on the repaired state it reports zero failures and leaves destination data unchanged. The regional build reapplies the recorded overrides and regenerates `regional-places.js`, independently validating all 153 regional places. `build_places.py` also reapplies those same overrides whenever the base destinations are regenerated. Source snapshots, terrain and building geometry are never rewritten by this repair.

The existing streaming/arrival suite passed **9/9**, including every walking arrival on the expanded city data. The parent subsequently reported the full city suite passing **102/102**. The tested manifest SHA256 is `d6f496ef068454dd7ca03a242ed2b58b3819b46877dda3a3ee099ce7ac900e63`, with 346,115 building forms.

A short checked path segment does not establish a complete accessible route or detailed district acceptance. Unmoved legacy arrivals retain their original approximate provenance; this pass does not relabel them as surveyed locations.
