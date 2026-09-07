## Architecture batch 1 — 7 September 2026

HKS-208 is **In Review** at `d288106a`, pushed to draft PR #298. Installed **25** new government components: Tai Kwun13, Lippo3, Asia Society6, Court of Final Appeal1, Hysan Place2. Payload: **1,269,800 bytes /58,108 triangles**. Native coordinates, surveyed heights, terrain and fixed1× scale are unchanged.

The14 selected groups account for58 source parts:17 already detailed,25 new,6 placement holds,10 source/match follow-ups. HKS-209 is Backlog for E Hall, JC Cube, two Asia Society components, Opus and Peak Tower plus source exceptions and local terrain refinements. No region is closed. Territory inventory:346,115 forms;1,859 embedded+2,192 progressive=4,051 detailed references.

All31 staged candidates passed normal browser checks; all25 installed assets pass shared loader, terrain-sampler, source picking/collision checks. Five installed representative visits pass day/night/mobile/walk/Fly/fallback/Retry;229 city tests pass. Desktop frame samples are16.7ms median/≤16.8ms p95; physical-phone performance remains unverified. An optional wide Hysan mobile capture timed out and was rejected, explicitly recorded alongside passing normal views.18 labelled isolated foundation diagnostics informed the holds.

Reuse: existing cached matcher/decoder/packer,15,356,700 bounded source-transfer bytes, zero AI calls inside the scripts. Executors: root, landmark_gap_audit, terrain_publication_guard, kowloon_cultural_models. HKS-208/209, parent199, regional193, coverage116, registry201, acquisition202 and milestone overview synchronised successfully. No R2 upload or production merge; latest Vercel preview SHA not reverified. [Review evidence](architecture-batch/README.md).

## Cultural landmarks and expanded selection — 7 September 2026

HKS-207 is In Review at `aa34ac1e`, pushed to draft PR #298: ten installed detailed government parts for Space Museum (3) and Cultural Centre/podium (7), 825,208 compressed bytes. Native geometry, surveyed fields and existing5m terrain remain unchanged at fixed1× scale. The two main opaque shells opt out of invented procedural windows. All229 city tests and all10 installed-model loader/terrain/picking/collision checks pass; browser day/night/mobile/walk/Fly/fallback/Retry checks pass. Gallery:20 images/10 comparisons. Six canopy identities and the small Studio Theatre edge depression remain explicit. Territory totals:346,115 forms,1,859 embedded+2,167 progressive=4,026 detailed model references. No whole-Kowloon completion or new R2 delivery.

HKS-201 remains In Review at `52b965d0`: expanded landmark registry from the user-supplied architecture guides and skyscraper table.213 deduplicated entries (210 building/complex entries,3 interior venues), plus2 infrastructure/landscape targets. The180-row skyscraper source has179 names; explicit aliases merge existing landmarks and163 entries are added from the table. Duplicate/conflicting measurements, historical Kai Tak and excluded proposed/demolished/vision tables are retained as warnings. The original trial list remains unchanged. Single-pass audit4.658s, zero AI/network calls;94 entries have name/UID hints and119 need spatial/identity resolution. This is discovery, not new model publication. Two parser tests and byte-identical registry rebuild pass.

Linear leaves HKS-207/201, parents HKS-125/199/116 and milestone overview successfully synced with commits, evidence, executor and remaining gaps. Cultural sources: kowloon_cultural_models; integration/registry: Root. Reports: `cultural-landmarks/README.md` and `landmark-registry/README.md`. Current preview-deployment SHA has not been reverified for these commits; branch push is confirmed.

## Named landmark pass and fixed vertical scale — 7 September 2026

`c8a5fddb` adds59 reviewed source parts:2 IFC podiums,4 Tai O Heritage Hotel parts,36 Po Lin parts (including Grand Hall) and17 Ngong Ping village parts. Corrected87-part selection:67 detailed,19 without standalone source geometry,1 unsupported pagoda held. New5m Ngong Ping terrain and guarded Tai O hotel refinement; one explicitly estimated null-source canopy base corrected. All59 installed assets,17 browser viewpoints,228 city tests,20 batch tests and14 publisher tests passed. Evidence: `landmark-pass/README.md`.

HKS-203/204 remain In Review; HKS-174 is In Progress with routes and remaining source detail open. HKS-202/199/116/122/193 and milestone were updated with this evidence. No whole-region readiness promotion.

`62ff8233` records the user's explicit ban on vertical exaggeration. HKS-131/182 conflicting requirements were removed; HKS-117/187 and the milestone exclude the old multiplier. Terrain, buildings, water, bridges, collision and navigation use fixed1× metres/HKPD. Legacy original-game route remains outside this removal request. AGENTS.md and FEATURE-PARITY.md carry the rule.

## Visible tourist trial — In Review, 7 September 2026

Root committed and pushed `63a707c672f22677674c0b4dbe50bb598be41ae3` to draft PR #298. Its Vercel preview is confirmed: three trial catalogues/1,078 models and six sampled remote compressed asset hashes match. The deployable viewer now contains 1,078 additional exact-source government models: 1,075 Central and three Mui Wo, 6.5 MB compressed. Central trial detail is 1,102/3,265 (33.8%); Mui Wo section 10.6 is 1,575/2,371 (66.4%). In the older full Mui Wo boundary, the three additions raise detail to 1,621/2,408 (67.3%) and reduce its earlier 21-model hold to 18. Territory-wide 346,115 forms and 3,957 detailed models; no source elevations, footprints or terrain changed.

All 228 city tests, 20 batch tests and three publisher tests pass. Thirteen browser locations pass day/night, desktop/mobile, source picking/collision, walk/Fly and failed-load fallback/Retry. The 13-comparison gallery loads all 26 images and supports mobile sliders. Frame samples are approximately 16.7 ms on desktop Chrome; physical-phone performance is not certified. No whole region is complete.

HKS-203/204 are In Review. All 1,797 held candidates remain basic fallbacks; 1,786 are in Central and 11 in Mui Wo. HKS-202 acquisition and HKS-205 rollout remain open/gated; HKS-206 production R2 delivery remains separate. Linear leaves, HKS-199/116/122 parents, HKS-192/193 regional issues and milestone overview successfully synced with commit, evidence, executor and limitations. Review: `docs/astra-city/building-batch/visual-trial/README.md` and `comparison.html`.

## Production asset offload — 7 September 2026

Created HKS-206 in the Astra milestone: offload all heavy runtime assets to R2 in production deployments. Backlog, High priority, 8 points, assigned to William; Performance/DevOps. Covers both viewers, asset inventory, reproducible approved-output uploads, versioned release manifests and rollback, browser-origin verification, CORS/compression and offline checks. Reuses HKS-50/46/52 infrastructure and relates to HKS-199/203. Milestone overview synced. Implementation has not started; no assets uploaded or deployed.

## Cached-source conversion and validation — 7 September 2026

Root committed and pushed `a308b86131e756bdc25c2ae839c962e0b3bbac33` to draft PR #298. Reused 77 retained staged manifests and the original decoder/packer: 5,404 jobs, 2,875 candidates (2,861 Central and 14 Mui Wo), 34.8 MB compressed, 66.60 s wall time, no AI/network calls. Repeat reuses all completed jobs in 2.24 s including source/output hashes. Seventeen focused tests pass.

All 2,875 assets pass the actual current-tile/shared loader; 2,874 pass combined source-roof picking/collision and drawn-terrain checks. One missing terrain surface remains at the Central–Wan Chai Bypass Middle Ventilation Building. Fresh overlapping terrain diagnostics include 4 sampled highest roofs buried, 1,008 terrain-above-bottom and 687 ground-gap cases; contextual placement/browser review is still required. No source elevations or live models changed. 2,440 records lack a match in retained staged manifests, 16 are ambiguous, 73 lack government identities; these are not government-unavailability claims.

HKS-202 remains In Progress for bounded source acquisition; HKS-203 is In Progress for placement review, browser acceptance and guarded publication. HKS-204/205 remain gated. HKS-200/201 stay In Review. Linear leaves HKS-202/203, parent HKS-199, coverage roll-up HKS-116 and the Astra milestone successfully synchronised with commit, evidence, executor and remaining gaps. No region status changed. Evidence: `docs/astra-city/building-batch/cached-models/README.md`.

## Tourist selection review and runner checkpoint — 7 September 2026

HKS-201 is In Review at `962b54a8482b951fcef97698b222eaad19fcfbc1`, pushed to draft PR #298. HKS-202 is In Progress; HKS-199 remains open. Root selected 7,542 forms across Central (3,265), Mui Wo section 10.6 (2,371), Tai O crop (1,430) and Ngong Ping crop (476), with 86 verified source identities in eight landmark groups. Bounds/UID lists and hashes are in `tourist-trial.json` and `docs/astra-city/building-batch/trial/selection.json`. The HTML map and exported PNG are reviewable; Chrome rendered four panels/7,542 footprints without page errors.

Initial metadata preflight: 7,542 completed diagnostic jobs in 34.77 s, 2,138 existing detailed references, 5,404 basic forms, zero AI/network calls and zero geometry changes. Repeat skips all completed checks (0.06 s). Twelve focused tests pass for inventory/selection/jobs including concurrency, interruption, stale input and identity safeguards. Existing terrain flags are not fresh validation. Acquisition/conversion/packing adapters remain open under HKS-202; fresh validation/publication HKS-203 and actual model-improvement trial HKS-204 remain pending. Trial counts use different boundaries from earlier region detail percentages.

Linear HKS-201, HKS-202, HKS-199, HKS-116 and the Astra milestone successfully synced with commit, evidence and remaining work. No whole-region status changed. Review map: `docs/astra-city/building-batch/trial/selection-review.png`; commands: `source-scripts/city/building-batch/README.md`.

## Local batch automation — HKS-199, 7 September 2026

Created six linked subissues in the Astra milestone: HKS-200 inventory (In Review, 4 points), HKS-201 tourist selection (Backlog, 4), HKS-202 resumable processing (Backlog, 8), HKS-203 validation/publication (Backlog, 8), HKS-204 measured trial (Backlog, 4), HKS-205 section rollout (Backlog, 4). Dependencies gate rollout on the trial. HKS-199 and active inventory were added to Cycle 5; future children remain backlog.

Root implemented and pushed `1cc2cf0ff849388135174f44e4f40a69fe2fd0e3` to draft PR #298: local SQLite inventory of 346,115 forms, 342,223 government IDs, 1,859 embedded plus 1,020 progressive detailed references and all 132 section definitions. Initial14.56s; unchanged repeat1.17s,452tiles skipped,zero building updates. Six focused tests pass. Commands use no AI/network calls. SQLite stays ignored/local; no viewer geometry changed. Source and evidence: `source-scripts/city/building-batch/README.md`, `docs/astra-city/building-batch/`. Trial membership and processing adapters remain open.

Linear HKS-200, HKS-199, HKS-116 and milestone overview successfully synchronised with commit/evidence. These are six additional automation leaves, separate from the earlier 30 regional/parity execution leaves. No existing region status was promoted.

# Astra execution subissues

## Integrated island detail — 7 September 2026

Commit `78464134` integrates **302 additional government models**: Mui Wo +291 to **1,618/2,408 (67.2%)**, Tai O +7 to **539/1,030 (52.3%)**, Pui O +4 to **685/919 (74.5%)**. Seven source-derived terrain children and six guarded null-source base estimates are published together. All 346,115 forms and recorded government elevations remain intact. All 228 city tests, publisher rollback tests, 35 complete-terrain rays and 18 actual-browser model visits pass, including day/night/mobile, picking, walking arrivals, Fly-menu flight and failure/Retry. Source packages and root integration are committed for draft PR #298. [Evidence](island-detail-integration/README.md).

Mui Wo holds 21 acquired models for genuine native roof/foundation conflicts; remaining absent and mismatched source IDs stay explicit. Regular/temporary/open-sided structures are not interchangeable denominators. No whole section is signed off. Three source/terrain agents completed their bounded work; root completed shared publication and browser review. HKS-192/171 remain In Progress for remaining regional scope; user-set HKS-170 Ready to Merge is preserved.

## Detailed-model source hand-off — 7 September 2026

Three agents finished locally committed source packages; none is integrated or pushed. Live coverage remains Mui Wo 1,327/2,408 (55.1%), Tai O 532/1,030 (51.7%), Pui O 681/919 (74.1%). After acceptance, staged additions would yield Mui Wo 1,639 (68.1%; 287b81b1), Tai O 539 (52.3%; 4070e46b), Pui O 685 (74.5%; c43f948c). Mui Wo regular Tower-category coverage would reach 98.8%; remaining gaps largely concern temporary/open-sided structures lacking exact source models. Two Tai O and two Pui O additions need terrain correction; Mui Wo needs placement/browser screening. Agents report 17 focused tests plus actual shared-loader/picking/collision checks passing. Root verified hand-off files and commits and synchronised HKS-192/170/171, HKS-122/116 and milestone; independent browser review and publication remain pending. See each area's detail-completion README.

## Aircraft picker published — 7 September 2026

[6e8242e4](https://github.com/wiiiimm/hongkong-sandbox/commit/6e8242e4698308c98f0d99d0059352e1be632497) is published in draft PR #298. Fly now opens a pull-up chooser for all seven aircraft. All 226 city tests and fresh desktop/mobile browser checks pass, including keyboard/input isolation, in-flight continuity, races and failure/Retry. HKS-177 stays In Progress for remaining flight physics, landing, cameras and audio parity. [Evidence](aircraft-picker/README.md). Linear leaf, parent, parity roll-up and milestone updated.

## Draft checkpoint — 7 September 2026

[PR #298](https://github.com/wiiiimm/hongkong-sandbox/pull/298) is open as a draft. All 51 milestone issues have the PR attachment, with direct commit links on the relevant issues. Original commit hashes are retained. Source checkpoints b90c15f5 (HKS-192) and 7d3e3ff5 (HKS-196) are staged only; see their source notes for remaining acceptance. The 226 city tests and 13 focused source tests pass. No whole section is newly signed off.


## Milestone draft PR

[Draft PR #298](https://github.com/wiiiimm/hongkong-sandbox/pull/298) collects this milestone on the existing Astra branch. [Commit-to-issue index](MILESTONE-COMMITS.md). Older Git hashes remain unchanged; references do not imply issue completion. Tai O, Tsing Ma/Ting Kau and timelapse retain their user-set Ready to Merge statuses; the overall milestone remains unfinished.

## Current execution — 7 September 2026

Linear read-back confirms **30 execution leaves: 3 Ready to Merge, 6 In Review, 6 In Progress and 15 queued**. William owns the issues; named agents identify execution ownership. All belong to the authorised Astra milestone in the HKS team's Hong Kong Sandbox project.

| Issue | State | Current executor and scope |
| --- | --- | --- |
| HKS-192 · Mui Wo | In Progress | Heisenberg completed staged checkpoint b90c15f5: six terrain corrections and two dependent estimated bases; six tests pass. Nested rendering, live integration and seven source cases remain pending. Earlier verified baseline: `9a33045`: 5 m terrain, ten original infrastructure meshes, mapped hydro, 4.137 km public walk verified in both directions, actual desktop/mobile/picking/flight checks. Thirteen partial terrain conflicts remain; wider section still under review. |
| HKS-195 · Haze and sky clarity | In Review | `8e8a181`: live HKO visibility, separate EPD AQHI, manual haze/sky-glow override; 37 tests and five browser groups pass. |
| HKS-119 · Golden sky and celestial shadows | In Review | `367cc1b`: original golden-hour palette reused, date/time/location-driven sun/moon and exact shadow direction; 11 focused tests and five browser groups pass. This older issue is outside the 30 execution-leaf count. |
| HKS-171 · South Lantau | In Progress | `7281071`: Pui O 681 compact models, 5 m terrain, 555 m continuous route and desktop/mobile/night/picking/flight/Retry checks pass. Heisenberg complete; shoreline, wetlands, inland connections and broader south Lantau remain open. |
| HKS-196 · Stonecutters Bridge | In Progress | Curie completed staged source checkpoint7d3e3ff5: three original components,23,634triangles; seven source tests and shared adapters pass. Port terrain repair, cables, live integration and browser acceptance remain pending. |
| HKS-191 · Tsing Ma + Ting Kau | Ready to Merge | `059f3b4d` source/assets + `ea9e96b0` integration: source models, corrected island foundations, actual picking, underwater rays, under-span flight, day/night and mobile checks pass. Curie complete; cables remain illustrative. |
| HKS-193 · Wan Chai–Central–Sheung Wan | In Progress | `80c42db` assets/evidence and `455761f` runtime: all 37 models passed desktop/mobile, picking/collision, night, Retry and card upgrade. Kant complete; placement and continuous public routes remain open. Six sections: 01.1–01.4 and 02.1–02.2. |
| HKS-180 · Remaining weather controls | In Progress | Tide/wave slice verified; remaining controls have no active executor. |
| HKS-194 · Numbered review grid | In Review | `13e3574`: optional 132-section layer and evidence-based readiness. |
| HKS-170 · Tai O | Ready to Merge | `5494ad6`: source channels, bridges and 607 m public walk. Private stilts/decks and wider north-west Lantau remain open. |

Root completed shared integration in `ea9e96b0`, browser review and Linear synchronisation. Heisenberg, Kant and Curie finished the previous bounded batch. Heisenberg completed staged Mui Wo checkpoint b90c15f5 and Curie completed staged Stonecutters checkpoint 7d3e3ff5. Both are committed in draft PR #298; live integration and final browser acceptance remain pending. Neither agent is still running on that checkpoint. Latest combined city suite: **226 tests pass** after compact model integration. GPU measurements use desktop Chrome, including mobile-sized viewports, and are serialised; physical-phone performance is unverified. New staged models and local route acceptance do not complete whole sections. Feature branch published for draft PR #298; no merge or production deployment.

Whole-section readiness remains **0 Ready, 0 Close, 12 Under review, 120 Base mapped**. [Review evidence and policy](review-sections/README.md). Latest evidence: [Mui Wo](mui-wo-completion/README.md), [haze](atmosphere/README.md), [golden sky and shadows](golden-hour/README.md).

## Execution issue index

### HKS-116

- [HKS-194 — Show numbered review-section borders and evidence-based readiness on the city map](https://linear.app/stealth-company/issue/HKS-194/show-numbered-review-section-borders-and-evidence-based-readiness-on) — In Review; 4 points.

### HKS-122

- [HKS-167 — Extend Mui Wo detailed government models beyond Pak Ngan Heung](https://linear.app/stealth-company/issue/HKS-167/extend-mui-wo-detailed-government-models-beyond-pak-ngan-heung) — In Review; 8 points.
- [HKS-170 — Complete Tai O channels, stilt-building placement and village routes](https://linear.app/stealth-company/issue/HKS-170/complete-tai-o-channels-stilt-building-placement-and-village-routes) — Ready to Merge; 8 points.
- [HKS-171 — Complete south Lantau village terrain, shores and local routes](https://linear.app/stealth-company/issue/HKS-171/complete-south-lantau-village-terrain-shores-and-local-routes) — In Progress; 8 points.
- [HKS-172 — Complete Tung Chung, Discovery Bay and northern Lantau village detail](https://linear.app/stealth-company/issue/HKS-172/complete-tung-chung-discovery-bay-and-northern-lantau-village-detail) — Backlog; 8 points.
- [HKS-173 — Complete airport buildings, reclamation and runway geography](https://linear.app/stealth-company/issue/HKS-173/complete-airport-buildings-reclamation-and-runway-geography) — Backlog; 8 points.
- [HKS-174 — Complete Ngong Ping and the Lantau mountain approach routes](https://linear.app/stealth-company/issue/HKS-174/complete-ngong-ping-and-the-lantau-mountain-approach-routes) — Backlog; 8 points.
- [HKS-192 — Complete Mui Wo terrain, village models and public walking review](https://linear.app/stealth-company/issue/HKS-192/complete-mui-wo-terrain-village-models-and-public-walking-review) — In Progress; 8 points.

### HKS-123

- [HKS-175 — Complete Peng Chau village, waterfront and walking detail](https://linear.app/stealth-company/issue/HKS-175/complete-peng-chau-village-waterfront-and-walking-detail) — Backlog; 8 points.
- [HKS-176 — Complete Cheung Chau harbour, village and coastal paths](https://linear.app/stealth-company/issue/HKS-176/complete-cheung-chau-harbour-village-and-coastal-paths) — Backlog; 8 points.

### HKS-124

- [HKS-193 — Complete Wan Chai to Sheung Wan city detail, including Central](https://linear.app/stealth-company/issue/HKS-193/complete-wan-chai-to-sheung-wan-city-detail-including-central) — In Progress; 8 points.

### HKS-126

- [HKS-196 — Reconstruct Stonecutters Bridge and correct underlying terrain artefacts](https://linear.app/stealth-company/issue/HKS-196/reconstruct-stonecutters-bridge-and-correct-underlying-terrain) — In Progress; 8 points.

- [HKS-191 — Repair Tsing Ma and Ting Kau bridge models and terrain artefacts](https://linear.app/stealth-company/issue/HKS-191/repair-tsing-ma-and-ting-kau-bridge-models-and-terrain-artefacts) — Ready to Merge; 8 points.

### HKS-129

- [HKS-168 — Restore original shooting-star controls in the city sky](https://linear.app/stealth-company/issue/HKS-168/restore-original-shooting-star-controls-in-the-city-sky) — In Review; 8 points.
- [HKS-169 — Restore lightning, thunder and weather sound in the city](https://linear.app/stealth-company/issue/HKS-169/restore-lightning-thunder-and-weather-sound-in-the-city) — In Review; 8 points.
- [HKS-180 — Restore tides, typhoon and remaining manual weather controls](https://linear.app/stealth-company/issue/HKS-180/restore-tides-typhoon-and-remaining-manual-weather-controls) — In Progress; 8 points.
- [HKS-181 — Restore marine, radar, satellite and air-quality observations](https://linear.app/stealth-company/issue/HKS-181/restore-marine-radar-satellite-and-air-quality-observations) — Backlog; 8 points.
- [HKS-189 — Add adjustable city timelapse beside the 24-hour dial](https://linear.app/stealth-company/issue/HKS-189/add-adjustable-city-timelapse-beside-the-24-hour-dial) — Ready to Merge; 4 points.
- [HKS-195 — Add adjustable atmospheric haze and night-sky clarity in Weather](https://linear.app/stealth-company/issue/HKS-195/add-adjustable-atmospheric-haze-and-night-sky-clarity-in-weather) — In Review; 4 points.

### HKS-130

- [HKS-177 — Restore original aircraft flight, landing and camera behaviour](https://linear.app/stealth-company/issue/HKS-177/restore-original-aircraft-flight-landing-and-camera-behaviour) — In Progress; 8 points.
- [HKS-178 — Restore original walking, jumping and camera controls](https://linear.app/stealth-company/issue/HKS-178/restore-original-walking-jumping-and-camera-controls) — Backlog; 8 points.
- [HKS-179 — Restore UFO hover, beam, cattle and score gameplay](https://linear.app/stealth-company/issue/HKS-179/restore-ufo-hover-beam-cattle-and-score-gameplay) — Backlog; 8 points.

### HKS-131

- [HKS-182 — Restore original terrain sources, surface styles and map overlays](https://linear.app/stealth-company/issue/HKS-182/restore-original-terrain-sources-surface-styles-and-map-overlays) — Backlog; 8 points.
- [HKS-183 — Restore GPX import, playback and route statistics](https://linear.app/stealth-company/issue/HKS-183/restore-gpx-import-playback-and-route-statistics) — Backlog; 4 points.
- [HKS-184 — Restore Matrix and Neon Night themes across city modes](https://linear.app/stealth-company/issue/HKS-184/restore-matrix-and-neon-night-themes-across-city-modes) — Backlog; 4 points.

### HKS-132

- [HKS-185 — Restore geolocation, compass and device-orientation exploration](https://linear.app/stealth-company/issue/HKS-185/restore-geolocation-compass-and-device-orientation-exploration) — Backlog; 8 points.
- [HKS-186 — Restore full English and Traditional Chinese city controls](https://linear.app/stealth-company/issue/HKS-186/restore-full-english-and-traditional-chinese-city-controls) — Backlog; 4 points.
- [HKS-187 — Restore saved-view URLs, sharing, embeds and settings](https://linear.app/stealth-company/issue/HKS-187/restore-saved-view-urls-sharing-embeds-and-settings) — Backlog; 4 points.
- [HKS-188 — Restore original fullscreen, PWA, offline and help behaviours](https://linear.app/stealth-company/issue/HKS-188/restore-original-fullscreen-pwa-offline-and-help-behaviours) — Backlog; 8 points.
- [HKS-190 — Redesign city controls for mobile bottom sheets and desktop panels](https://linear.app/stealth-company/issue/HKS-190/redesign-city-controls-for-mobile-bottom-sheets-and-desktop-panels) — In Review; 4 points.

