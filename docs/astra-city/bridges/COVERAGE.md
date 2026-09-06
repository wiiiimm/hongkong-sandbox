# Mapped bridge inventory coverage

15,608 tagged bridge segments, 1,864 elevated links and 8,532 source-node-connected access segments. These are OSM way segments, not distinct bridge structures.

| District (OSM midpoint containment) | Tagged bridge segments | Elevated links | Connected access ways |
| --- | ---: | ---: | ---: |
| Boundary waters / unassigned | 15 | 0 | 4 |
| Central and Western District | 803 | 281 | 420 |
| Eastern District | 659 | 126 | 364 |
| Islands District | 1133 | 169 | 505 |
| Kowloon City District | 496 | 38 | 254 |
| Kwai Tsing District | 1218 | 89 | 476 |
| Kwun Tong District | 1149 | 131 | 477 |
| Lok Ma Chau Loop | 1 | 0 | 0 |
| North District | 800 | 34 | 634 |
| Sai Kung District | 680 | 182 | 459 |
| Sha Tin District | 1332 | 179 | 727 |
| Sham Shui Po District | 595 | 53 | 256 |
| Southern District | 596 | 65 | 471 |
| Tai Po District | 908 | 93 | 905 |
| Tsuen Wan District | 1022 | 92 | 517 |
| Tuen Mun District | 992 | 26 | 514 |
| Wan Chai District | 533 | 60 | 271 |
| Wong Tai Sin District | 423 | 26 | 289 |
| Yau Tsim Mong District | 1224 | 205 | 285 |
| Yuen Long District | 1029 | 15 | 704 |

The export has 159,655 centre-line vertices and 527 source-linked deck outlines. 1,587 records retain an indoor flag. Explicit numeric source evidence is sparse: 115 widths, 162 total feature heights, 0 minimum heights and 3 elevation tags. None of these counts imply surveyed deck elevations.

Source-node reconciliation resolved 4 node IDs across 4 retained ways to their newest source coordinates. Raw snapshots were preserved. Seven automated tests cover parsing, role distinctions, source geometry, boundary clipping, original-node alignment, connected access and all eighteen districts.
