# Bridge-cluster source reuse audit · HKS-191

**Scope confirmed by the user: Tsing Ma + Ting Kau. Kap Shui Mun is not included.** This bounded audit checked the existing Tsing Ma archives, retained full ZIP directories, source index and mapped bridge inventory before requesting further model data. No original or staged Tsing Ma geometry was changed.

| Candidate | Already retained | Not established from retained bytes |
| --- | --- | --- |
| Ting Kau Bridge / 汀九橋 | Thirteen named source OSM bridge ways in the existing `bridges.json`; original terrain grid; the southern Tsing Yi interchange infrastructure in source sheet `10-NE-3B`; current iB5000 `10-NE-B` source map already cached for Tsing Ma. | No main-span or tower glTF bytes identified in the existing Tsing Ma caches. The main bridge corridor lies north of their seven-sheet source extent. Original cable completeness cannot be inferred from files that have not yet been obtained. |
| Kap Shui Mun Bridge / 汲水門大橋 | Two named OSM ways `875742669` and `875742670`; nearby original Ma Wan approach structures `I239782282707063C0`, `I240742285107063C0`, `I241162282207063C1` in `10-NE-2C`; original terrain grid. | The nearby structures are not evidence of a complete bridge model. No complete main span/tower/cable set is retained in this bounded cache. This bridge is outside the user-confirmed implementation scope. |

Ting Kau's mapped bridge ways cover approximately world X **−8468 to −7955 m**, Z **−8940 to −7940 m**. Kap Shui Mun's two mapped ways cover approximately X **−11049 to −10421 m**, Z **−6515 to −6069 m**. Coordinates are retained OSM geometry, not a surveyed structure envelope.

The existing Tsing Ma cache includes 16 original infrastructure models across `10-NE-2A/B/C/D` and `10-NE-3A/B/D`, plus four selected Tsing Ma tower components. Full remote ZIP directories were retained even when only infrastructure, terrain or selected towers were fetched; an indexed filename is distinguished from downloaded model bytes. The checked main-worktree archival/source locations and the other local model caches contain no separately named Ting Kau or Kap Shui Mun complete asset.

For Tsing Ma, the source audit already proves an inherited false-land ridge: elevated bridge samples in the archival 5 m DTM become 70 m averaged terrain, and the original `DTM > 1 m` land rule treats them as land. This is a **pipeline risk to test for Ting Kau**, not evidence that every nearby elevated cell is false land. Ting Kau implementation will compare its bridge corridor with source terrain and mapped water before any cut. Real shore, tower foundations and approach land must remain intact. No pedestrian access is inferred for either road bridge.

The new `source-scripts/city/ting-kau/` work retains a bounded official source index and will reuse the existing filtered archive downloader, immutable glTF transform/bake, terrain resampling and mapped-water helpers. Ting Kau is cable-stayed; Tsing Ma suspension cable geometry must not be reused as its cable geometry. Exact retained components, missing details, datum checks and any explicitly estimated additions belong in the separate Ting Kau evidence notes.
