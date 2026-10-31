# Mui Wo regional completion · HKS-192

This bounded regional pass is integrated into the local Astra viewer and ready for review. It does not claim that every architectural detail or all of section **10.6** is finished.

Root published the source-derived5m terrain, separate estuary/water boundaries, ten original infrastructure models and four estimated public approaches through the existing pipelines. All346,115 territory forms and1,859 detailed models remain. All195 walking arrivals pass (190 retained plus five new village/ferry arrivals). The actual browser replay covers4,136.85m in both directions, each with63,975 frames, one initialisation and zero route resets. Source picking shows reviewed deck heights and public-access provenance; flight advances124m with no collision. Nine fixed-camera day/night/village views and a390px mobile view pass with no page/data errors. Desktop53 calls/1,952,424triangles and mobile66 calls/1,864,271triangles; both16.7ms median/16.8ms p95 on this local Chrome machine. Images inspected. [Integrated browser evidence](browser/after/verification.json).

Remaining limits:13 partial roof/terrain diagnostic conflicts,1,081 footprint-based building fallbacks, historical/overlapping Wang Tong source components and explicitly estimated approaches/river bed. These are documented below; source heights are not altered to manufacture perfect agreement. The pass enters In Review, while whole-section readiness remains Under review.

The work reuses the **2,408 official forms and 1,327 detailed building models** already imported for Mui Wo. No building or roof model is re-imported or matched by appearance. The territory must retain all **346,115 forms and 1,859 detailed models**, including Tai O.

## Terrain and source accounting

The original audit found **114 wholly buried roofs and 214 partial roof/terrain conflicts**. All 114 whole conflicts, and 205 partial conflicts, were outside the seven previously imported source terrain sheets. Twenty bounded **terrain-only** official sheets add 1,612,745 source terrain triangles to the existing 5 m resampling/mosaic pipeline. Validated HTTP byte ranges transfer **41,248,822 bytes**, avoiding the 470,016,498-byte full source archives and their photographs. Original glTF hierarchy, HK1980 coordinates and HKPD elevations remain unchanged; raw samples and hashes are retained.

The staged 869 × 869 patch uses 27 source sheets and covers 2,359 of the 2,408 footprint centres with source TIN samples. It reduces conflicts to **0 whole / 13 partial**. Only **164 forms whose original base and top are both null** receive refreshed terrain-based base estimates through the existing policy. Holding all previous display tops fixed instead gives **1 whole / 15 partial**; both comparisons are retained in [terrain-audit.json](terrain-audit.json).

The 13 remaining partial conflicts comprise seven estimated roofs, five recorded outline roofs and one detailed roof model (0.208 m below the terrain maximum across its outline). These are conservative highest-roof-versus-footprint-terrain diagnostics, not a measurement of every roof face. Source heights are not raised to force them to disappear. [existing-audit.json](existing-audit.json) also retains all 13 previously unmatched model IDs, candidate footprints and reasons; spatial overlap is not substituted for source identity.

All old non-positive water nodes and patch-edge elevations are preserved. One newly sampled offshore node at world **[−15812.5, 2972.5]** changes from +2.00 to −0.03 m HKPD; the current iB5000 land polygon places it 3.61 m offshore. Original source grids remain untouched. Adjacent TIN samples are joined before a 15 m blend around the source union; [terrain-mosaic.json](terrain-mosaic.json) reports seams as neighbouring 5 m height differences, not same-position errors.

## Shoreline, bridges and public connections

Current Lands Department iB5000 closed land polygons and iB1000 river polygons define the bounded waterfront, lower River Silver estuary and the seaward Wang Tong reach. The separate [hydro source audit](hydro-source-audit.json) retains upstream polygons, source revisions and exclusions. Wang Tong's display starts at the northern bound of the existing bridge model; this is an explicit display extent, **not a surveyed tidal limit**. The −4 m submerged display bed is illustrative, not bathymetry. No proposed drainage works are represented as built.

Ten exact infrastructure meshes already retained during HKS-167 supply **8,450 triangles**, including the promenade and river bridges. Six have reviewed original public floor faces. The source depicts overlapping old/new Wang Tong components: only the upper western pedestrian floor is walkable; the cycleway is not substituted for a footpath. Nine complete generic bridge proxies and only the overlapping portions of 16 others are replaced after the complete source package loads. Positive exact source projection overlap is required before applying the explicit 1.5 m map-alignment tolerance. Unmatched approach portions remain. See [infrastructure-package.json](infrastructure-package.json).

Four short visible approach profiles connect unchanged source floors to ground. Widths and intermediate heights are labelled estimated; source railings, benches, columns and deck geometry remain collidable and unchanged. The promenade route uses a collision-checked existing railing opening, with a **3.37 m** connector to retained public street node 6598342309. Its 149.92 m floor route passes through the original source floor rather than the conflicting mapped centreline.

The connected ferry waterfront → town → Silvermine Bay beach → Wang Tong → Pak Ngan Heung → Tai Tei Tong → Luk Tei Tong route passes the actual `Navigation.update` in both directions: **4,136.85 m**, **63,975 frames** each way, one initialisation and zero position resets. Negative controls block without source floors or the estimated approaches, and at excessive water level. [Route evidence](route-navigation.json) and [source map](source-geometry.png) retain the source-node paths, explicit floor detour and access caveats; government village lanes can be shared with vehicles.

Of 190 current walking arrivals, only `muiwo` becomes wet under the mapped estuary. A **41.739 m** repair onto public footway **way/243658484** passes the existing 1.2 m collision clearance and 2 m path checks; all 190 then pass. A further **508.56 m** unchanged source-node route connects that arrival to the ferry route start and passes in both directions. Five additional village/ferry arrivals pass the same checks. Existing place IDs and six aerial-only choices remain. See [arrival evidence](arrivals-staged.json) and [continuous arrival connection](arrival-connection.json).

## References and verification

- [Lands Department current Mui Wo GeoPDF](https://www.landsd.gov.hk/doc/en/mapping/ehkg/MapPages/GeoPDF/IS12_MuiWo.pdf): contemporary settlement, coast and public-map context; not image-traced geometry.
- [Lands Department 3D mapping](https://www.landsd.gov.hk/en/survey-mapping/mapping/3d-mapping.html): original government terrain and infrastructure model provenance.
- [Highways Department Wang Tong twin bridges](https://www.hyd.gov.hk/en/our_projects/walkability_projects/district_facilities/6850th/index.html): separated pedestrian/cycle bridges and current project context.
- [Hong Kong Tourism Board Mui Wo guide](https://www.discoverhongkong.com/eng/place-to-go/travel.guide-mui-wo.html) and [Islands District visitor route](https://www.islands.gov.hk/en/routes-mui-wo.php): public waterfront, beach and village visitor context.
- [Drainage Services Department Mui Wo drainage project](https://www.dsd.gov.hk/EN/Our_Projects/All_Projects/4189CD.html): proposed works remain excluded. Indexed EPD EIA238/2016 section7.6.4 describes a non-tidal upper Wang Tong reach; its direct PDF returned404, so this is historical ecology context only and supplies no current geometry or tidal boundary.

**18 focused Python tests pass**, including the five composite-hydro preservation cases. The original13 source checks are retained. Shared GML multipart-ring decoding rejects disconnected/open rings. The unchanged Tai O source-water output remains byte-identical at 51,830 bytes, and the extracted shared terrain builder's default Tai O result remains byte-identical at 4,804,872 bytes; [decoder proof](gml-decoder-regression.json), [builder proof](hydro-builder-regression.json). Existing helper defaults remain unchanged.

Seven fixed-camera [before views](browser/before/verification.json) were captured from the unchanged live viewer, with zero page/data errors and a measured 16.7 ms median /16.8 ms p95 at the last village view. Integrated day/night, continuous walking, flight, picking and390×844 mobile acceptance now pass; see the current delivery summary and after evidence above.

[Before overview](browser/before/overview-1440x1000.png) · [Before waterfront](browser/before/waterfront-day-1440x1000.png)

No historical reference image was used to trace current geometry or modified. © OpenStreetMap contributors, ODbL1.0; Lands Department/HKSAR Government/CSDI source attribution and original URLs/hashes are retained next to each output.
