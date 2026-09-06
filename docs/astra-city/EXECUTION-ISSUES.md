# Astra execution subissues

## Current execution — 7 September 2026

Linear read-back confirms **30 execution leaves: 9 In Review, 5 In Progress and 16 queued**. William owns the issues; named agents identify execution ownership. All belong to the authorised Astra milestone in the HKS team's Hong Kong Sandbox project.

| Issue | State | Current executor and scope |
| --- | --- | --- |
| HKS-192 · Mui Wo | In Progress | Heisenberg resumed the 13 partial conflict checks and whole-section acceptance audit. Earlier verified baseline: `9a33045`: 5 m terrain, ten original infrastructure meshes, mapped hydro, 4.137 km public walk verified in both directions, actual desktop/mobile/picking/flight checks. Thirteen partial terrain conflicts remain; wider section still under review. |
| HKS-195 · Haze and sky clarity | In Review | `8e8a181`: live HKO visibility, separate EPD AQHI, manual haze/sky-glow override; 37 tests and five browser groups pass. |
| HKS-119 · Golden sky and celestial shadows | In Review | `367cc1b`: original golden-hour palette reused, date/time/location-driven sun/moon and exact shadow direction; 11 focused tests and five browser groups pass. This older issue is outside the 30 execution-leaf count. |
| HKS-171 · South Lantau | In Progress | `7281071`: Pui O 681 compact models, 5 m terrain, 555 m continuous route and desktop/mobile/night/picking/flight/Retry checks pass. Heisenberg complete; shoreline, wetlands, inland connections and broader south Lantau remain open. |
| HKS-196 · Stonecutters Bridge | In Progress | Curie: audit existing assets and stage source geometry/terrain using HKS-191 pipeline. Root: integration, browser acceptance and tracking. No reconstruction delivered yet. |
| HKS-191 · Tsing Ma + Ting Kau | In Review | `059f3b4d` source/assets + `ea9e96b0` integration: source models, corrected island foundations, actual picking, underwater rays, under-span flight, day/night and mobile checks pass. Curie complete; cables remain illustrative. |
| HKS-193 · Wan Chai–Central–Sheung Wan | In Progress | `80c42db` assets/evidence and `455761f` runtime: all 37 models passed desktop/mobile, picking/collision, night, Retry and card upgrade. Kant complete; placement and continuous public routes remain open. Six sections: 01.1–01.4 and 02.1–02.2. |
| HKS-180 · Remaining weather controls | In Progress | Tide/wave slice verified; remaining controls have no active executor. |
| HKS-194 · Numbered review grid | In Review | `13e3574`: optional 132-section layer and evidence-based readiness. |
| HKS-170 · Tai O | In Review | `5494ad6`: source channels, bridges and 607 m public walk. Private stilts/decks and wider north-west Lantau remain open. |

Root completed shared integration in `ea9e96b0`, browser review and Linear synchronisation. Heisenberg, Kant and Curie finished the previous bounded batch. Heisenberg has now resumed HKS-192 to examine the 13 partial conflicts using retained source geometry and terrain. Curie has now started HKS-196, a separate Stonecutters Bridge source/model/terrain pass; root owns integration and tracking. Latest combined city suite: **226 tests pass** after compact model integration. GPU measurements use desktop Chrome, including mobile-sized viewports, and are serialised; physical-phone performance is unverified. New staged models and local route acceptance do not complete whole sections. No push, merge or deployment.

Whole-section readiness remains **0 Ready, 0 Close, 12 Under review, 120 Base mapped**. [Review evidence and policy](review-sections/README.md). Latest evidence: [Mui Wo](mui-wo-completion/README.md), [haze](atmosphere/README.md), [golden sky and shadows](golden-hour/README.md).

## Execution issue index

### HKS-116

- [HKS-194 — Show numbered review-section borders and evidence-based readiness on the city map](https://linear.app/stealth-company/issue/HKS-194/show-numbered-review-section-borders-and-evidence-based-readiness-on) — In Review; 4 points.

### HKS-122

- [HKS-167 — Extend Mui Wo detailed government models beyond Pak Ngan Heung](https://linear.app/stealth-company/issue/HKS-167/extend-mui-wo-detailed-government-models-beyond-pak-ngan-heung) — In Review; 8 points.
- [HKS-170 — Complete Tai O channels, stilt-building placement and village routes](https://linear.app/stealth-company/issue/HKS-170/complete-tai-o-channels-stilt-building-placement-and-village-routes) — In Review; 8 points.
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

- [HKS-191 — Repair Tsing Ma and Ting Kau bridge models and terrain artefacts](https://linear.app/stealth-company/issue/HKS-191/repair-tsing-ma-and-ting-kau-bridge-models-and-terrain-artefacts) — In Review; 8 points.

### HKS-129

- [HKS-168 — Restore original shooting-star controls in the city sky](https://linear.app/stealth-company/issue/HKS-168/restore-original-shooting-star-controls-in-the-city-sky) — In Review; 8 points.
- [HKS-169 — Restore lightning, thunder and weather sound in the city](https://linear.app/stealth-company/issue/HKS-169/restore-lightning-thunder-and-weather-sound-in-the-city) — In Review; 8 points.
- [HKS-180 — Restore tides, typhoon and remaining manual weather controls](https://linear.app/stealth-company/issue/HKS-180/restore-tides-typhoon-and-remaining-manual-weather-controls) — In Progress; 8 points.
- [HKS-181 — Restore marine, radar, satellite and air-quality observations](https://linear.app/stealth-company/issue/HKS-181/restore-marine-radar-satellite-and-air-quality-observations) — Backlog; 8 points.
- [HKS-189 — Add adjustable city timelapse beside the 24-hour dial](https://linear.app/stealth-company/issue/HKS-189/add-adjustable-city-timelapse-beside-the-24-hour-dial) — In Review; 4 points.
- [HKS-195 — Add adjustable atmospheric haze and night-sky clarity in Weather](https://linear.app/stealth-company/issue/HKS-195/add-adjustable-atmospheric-haze-and-night-sky-clarity-in-weather) — In Review; 4 points.

### HKS-130

- [HKS-177 — Restore original aircraft flight, landing and camera behaviour](https://linear.app/stealth-company/issue/HKS-177/restore-original-aircraft-flight-landing-and-camera-behaviour) — Backlog; 8 points.
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

