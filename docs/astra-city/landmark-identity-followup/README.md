# HKS-214 · Exact identity follow-up

Four previously unmapped landmark names now have supported main-tower identity proposals in `alias-decisions.json` and the source folder's `proposed-overlay.json`:

- Cullinan North → LandsD 203728, The Cullinan I. The structural council explicitly records the North Tower alias.
- Cullinan South → LandsD 203724, The Cullinan II. Its corresponding council record explicitly records South Tower.
- China Resources Center → LandsD 37369, China Resources Building. The council records the alternate name and 26 Harbour Road address.
- OAK 28 → LandsD 323059, The Oakhill. The council records the alternate name and 28 Wood Road address.

Each proposal retains exact government UID/CSUID, source tile hash and source naming plus the cached primary reference's hash. These select only the named main towers. Elements, lower podiums and unnamed components are not inferred from proximity. Identity review does not authorise placement or whole-landmark completion. Existing discovery positions corroborate the Cullinan pair; their main towers have separate government labels. The China Resources and Oakhill aliases each resolve to the uniquely named main government tower, separate from their named lower podium.

The retained Nina Hotel operator factsheet confirms two towers at 8 Yeung Uk Road, but matching its tower diagram to all source components still needs review. In particular, the taller named source footprint tops at253.1m while the architectural landmark is substantially taller; do not declare the full building model complete from name matching alone.

Two support exceptions requested by the residual review were separately acquired and packed exactly:179500 (CSUID4384214085T20181127),272501 (CSUID4620017075T20141126). The existing pipeline reused caches and fetched3,102 bytes. `packing.json` records model hashes/native bounds. They remain staged for physical review, and reservations were released after acquisition.

All work is isolated here. No shared registry, runtime manifest, model position or SQLite write. New local source/reference caches postdate checkpoint d6f25b3b and need a later incremental checkpoint.
