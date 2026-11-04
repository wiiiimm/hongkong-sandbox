# Cheung Sha, Tong Fuk and Shui Hau · HKS-171 availability

This is a small source-availability audit for project review section **10.8**. Pui O is being handled separately and was not edited. No model archive, texture or live dataset was downloaded or changed for this audit; only three small official index responses were retained.

The current source-model caches were checked first. None of the 24 relevant official sheets is retained under the existing Astra city source folders. A targeted filename search of the main repository’s read-only references, source scripts and comparison worktrees also found no matching 13-NE archive. The existing government footprint layer and archival DTM are already reusable; they must not be fetched or rebuilt wholesale again.

| Preliminary village/coast study | Advertised original model sheets | Current forms | Government forms | Recorded-height forms | Existing detailed model forms |
| --- | ---: | ---: | ---: | ---: | ---: |
| Cheung Sha | 12 | 687 | 684 | 592 | 0 |
| Tong Fuk | 5 | 339 | 337 | 309 | 0 |
| Shui Hau | 9 | 215 | 215 | 178 | 0 |

There are **24 unique sheets**, because two are shared between the Cheung Sha and Tong Fuk index queries. The current building counts are footprint intersections with explicit preliminary study rectangles, not official village boundaries or a section-completeness claim. All source forms are counted, including open-sided, temporary and podium structures. Government `Tower` is a source classification and does not mean a skyscraper.

The retained [availability report](availability.json) contains the exact HK1980 bounds, sheet lists, revision dates, original glTF download URLs, current form types and source-height counts. Original query bytes, request URLs, retrieval time and hashes are under `source-scripts/city/south-lantau-audit/`. The primary [Lands Department non-textured model index](https://portal.csdi.gov.hk/server/rest/services/common/landsd_rcd_1742809441342_98380/FeatureServer/0) advertises these sheets with revisions from September 2025 through July 2026. An indexed URL establishes advertised availability; the contents and geometric completeness of an unacquired archive remain unverified.

A suitable next implementation is one village at a time: retain only its relevant original BUILDING/INFRASTRUCTURE/TERRAIN glTF/bin entries through the existing filtered ZIP-range downloader, compare exact source IDs with the already loaded government forms, and stage geometry through the existing model/terrain pipeline. Shared sheets should be acquired once. Shorelines, beach surfaces and public walking arrivals then need area-specific verification; Shui Hau’s tidal flats particularly require mapped coastal semantics and an honest distinction between simulated tide and surveyed elevations. No exact water depth, surveyed private access or complete infrastructure inventory is inferred here.

Reproduce the bounded audit from the Astra worktree; retained index responses are reused:

```sh
SSL_CERT_FILE=/etc/ssl/cert.pem /tmp/astra-city-venv/bin/python source-scripts/city/south-lantau-audit/audit.py
```

Source credit: Lands Department / HKSAR Government. Existing OSM forms and arrival references retain OpenStreetMap attribution. No `references/` files were modified.
