# Living Hong Kong delivery tracking

HKS-191 is queued under HKS-126: [replace Tsing Ma Bridge terrain artefact with a verified bridge model](https://linear.app/stealth-company/issue/HKS-191/replace-tsing-ma-bridge-terrain-artefact-with-a-verified-bridge-model). High priority, 8 points, Bug/Rendering, William assigned. Audit/reuse existing assets first; preserve real shores and water below the span. Linear parent and milestone updated. There are now **25 execution subissues: five In Review, two In Progress, 18 queued**. HKS-170 remains active.

## Current pass — 7 September 2026

HKS-190 Clock follow-up is implemented in `783cb62` and In Review: Live/Manual button, date disabled in Live, shimmer moved to Weather. Four toggle, ten timelapse and eleven circular-clock browser groups pass; night/mobile screenshots inspected. [Evidence](clock-toggle/README.md). Linear HKS-190, HKS-132 and milestone updated after verification.

HKS-170 completion continues: Heisenberg owns authoritative channels and terrain; Curie owns source infrastructure and verified public deck faces; Kant owns continuous routes and accurate model collision; root integrates runtime and reviews. Previous model counts and arrival-only checks do not close the remaining channels/route acceptance.

GPT-6 Astra · 6 September 2026. The initial planning snapshot below is retained as history. The current milestone is **Astra - Living Hong Kong — buildings, regional detail & feature parity** (same milestone ID).

## Current execution and authorisation

**Standing completion rule, confirmed by the user on 7 September 2026:** every completed implementation or subagent hand-off must update the relevant issues, parent progress and milestone overview before the completion response. Record commit, verification, executor and remaining acceptance; synchronise local trackers. If a write fails, record it as pending. This is also recorded in `AGENTS.md`.

The milestone overview has been reconciled with `72df3cf` and `46b67ed`, replacing its stale first-batch summary. Current summaries on HKS-164, HKS-170, HKS-180, HKS-189, HKS-190 and parity parents HKS-117/HKS-129/HKS-132 now reflect the delivered slices and remaining work. The 24 execution subissues remain five In Review, two In Progress and 17 queued. Existing statuses are preserved; the three satisfied identity/documentation criteria in HKS-170 are checked, while full channels and continuous routes remain unchecked.

The user explicitly authorised updates to the Astra milestone and its issues. The pending coverage report has been posted: HKS-164 is now **In Review**, and HKS-116/HKS-117 reflect the verified ff68cf1 coverage and active feature restoration. The prior automatic approval rejection is resolved.

[24 executable subissues](EXECUTION-ISSUES.md) were created and read back with correct parent, project, milestone, owner, labels and estimates. HKS-167, HKS-168, HKS-169, HKS-189 and HKS-190 are **In Review**; HKS-170 and HKS-180 are In Progress; the other 17 subissues remain queued. The first three-agent batch and subsequent timelapse/control passes are complete. Heisenberg completed the bounded central Tai O government-model pass under HKS-170, with independent review by Kant and root. No agent is still running on that completed slice. The seven existing geography parents retain the 132-section review scope.

## Current local checkpoint

`72df3cf` adds 532 verified government models on two Tai O sheets and a local 5 m terrain patch. Detailed city models total 1,859, with all 346,115 forms, 342,223 government IDs and 1,327 Mui Wo models retained. The coastal terrain join and generated promenade arrival are fixed. All 137 city tests, eight focused Python checks, 190 saved walking arrivals and final day/night plus mobile browser checks pass. Whole-roof terrain conflicts in the slice fall from 96 to 1, partial conflicts from 170 to 13. [Source and before/after evidence](tai-o-models/README.md). HKS-170 remains In Progress for full channels, stilt decks/supports and continuous routes; parent HKS-122/HKS-116 and the leaf are updated in Linear.

`46b67ed` gives the global clock its own Time tab: Places · Time · Sky · Weather. Twelve control-sheet and ten timelapse browser groups pass. The four-tab mobile layout, first-open speed controls, keyboard navigation and state retention are verified. HKS-190 is back In Review.

The HKS-189 follow-up `c9f1a79` makes the speed slider visible beside the dial on first open and displays 1×–7,200× normal speed. Six clock tests and ten browser groups pass, including scroll-zero checks at 320/390/760/1024/1440 px. The source label reads 346,115 building forms · Lands Department + OSM. HKS-189 returned to In Review; geometry counts are unchanged.

`e2c50f9` implements HKS-189 adjustable timelapse and HKS-190 mobile-first bottom sheet/desktop inspector. Both are In Review (High, 4 points each), after Curie/Kant implementation and primary-agent integration/review. All 133 city tests, nine timelapse browser groups and responsive control checks pass; exports at 320/390/1024/1440 px were inspected. [Controls](control-sheet/README.md) · [Timelapse](time-cycle/README.md). Existing services and all 118 prior control IDs are preserved. Physical handset keyboard behaviour remains unverified.

The subsequent user-requested **HKS-180 tide/wave slice** restores manual sea level, HKO predictions/24-hour graph and shared original water/shore effects. Curie owns the water/source restoration; the primary agent owns the city controls and navigation/ferry integration. **128/128 city tests** and six actual-city browser groups pass. [Tide implementation and evidence](tides/README.md). The broader HKS-180 issue stays In Progress for its remaining original controls.

### Previous three-agent batch

- `fd64435` / HKS-167: Mui Wo detailed government models **275 → 1,327**, with every territory form/source ID and recorded elevation retained. All 190 walking arrivals pass. See [source and before/after evidence](mui-wo-buildings/extension/README.md); 114 wholly-below-terrain forms and 214 partial conflicts remain documented.
- `8aa4996` / HKS-168 and HKS-169: shared original meteors, manual lightning/thunder and environmental audio/volume restored. [Actual city controls and mobile evidence](environment-parity/README.md) and original-viewer compatibility pass.
- Full combined city suite: **116/116 checks pass**. Mui Wo browser: 16.6 ms median / 17.5 ms p95, 91 draw calls at 1440×1000 locally. Linear milestone and parent progress reports are updated; full regional/parity acceptance remains open.

### Earlier verified checkpoints

- `5ae3900`: 153 added destinations covering all 132 sections (196 total), 2,923 mapped local surfaces and the separate mapped-footbridge renderer. HKS-153 is confirmed **In Review** in Linear.
- `c85ac0b`: all 2,408 official Mui Wo records, native height evidence, a reused 5 m terrain patch, 227 open-sided structures and 275 matched official 3D models. HKS-164 is now **In Review** in Linear; the approved implementation report has been posted.
- The final local territory checkpoint publishes 346,115 forms, including all 342,223 government records as 342,225 polygon components, plus 3,890 OSM forms. It reuses the existing official download, renderer and tile pipeline. See [territory provenance and verification](landsd-territory/README.md).
- HKS-116 and the seven region tasks remain **In Progress**. Full terrain/shoreline/architectural and route acceptance still needs section-by-section review. HKS-117 remains the original-game parity roll-up; no parity task is closed by this coverage pass.
- Completed verification ownership: Heisenberg — government 3D sample, references and all saved arrivals; Curie — independent full-territory source/geometry/overlap audit; Kant — per-tile lighting and independent browser/performance review; primary agent — shared publication, classification preservation and integration.

The preceding `ff68cf1` checkpoint passed 102 city checks; all 190 walking arrivals and eight representative desktop/mobile browser visits pass. Detailed implementation and validation reports remain in this worktree. The formerly pending text is retained in [LINEAR-UPDATE-PENDING.md](LINEAR-UPDATE-PENDING.md) as a historical record; the write has now succeeded. The comparison branches remain separate; no push, merge or deployment has occurred.

## Initial planning snapshot

## Milestone and scope

**Living Hong Kong — buildings, regional detail & feature parity** in the [Hong Kong Sandbox project](https://linear.app/stealth-company/project/hong-kong-sandbox-e6dde81f1f15/overview).

Milestone ID: `3a730c97-7148-4d83-bedd-c5b47b85f721`.

- [HKS-116 — Complete the Hong Kong map region by region](https://linear.app/stealth-company/issue/HKS-116/complete-the-hong-kong-map-region-by-region): finish the city region by region.
- [HKS-117 — Restore every original-game feature in the city viewer](https://linear.app/stealth-company/issue/HKS-117/restore-every-original-game-feature-in-the-city-viewer): restore every existing original-game feature before retiring the original route.

This is the continuing delivery plan, distinct from the completed local imported-base integration described in [INTEGRATION-MILESTONE.md](INTEGRATION-MILESTONE.md). The existing city implementation is on `codex/astra-hong-kong-city` at `78cc072`, with documented local checks; it is not merged or deployed. This tracking update changes documentation only.

## Regional order

All 132 section IDs from [SECTION-CHECKLIST.md](SECTION-CHECKLIST.md) are assigned exactly once. These are practical review groups, not new administrative boundaries. Every detailed section remains subject to source, terrain/building, route and browser review.

| Order | Issue | Section IDs | Count | Initial status |
| --- | --- | --- | --- | --- |
| 1 | [HKS-122 — Complete Lantau buildings, villages, airport and walking routes](https://linear.app/stealth-company/issue/HKS-122/complete-lantau-buildings-villages-airport-and-walking-routes) | 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7, 10.8, 10.9, 10.10, 10.11, 11.6, 11.7 | 13 | Todo |
| 2 | [HKS-123 — Complete Peng Chau, Cheung Chau and the outlying islands](https://linear.app/stealth-company/issue/HKS-123/complete-peng-chau-cheung-chau-and-the-outlying-islands) | 10.12, 10.13, 10.14, 10.15, 10.16, 14.8 | 6 | Todo |
| 3 | [HKS-124 — Complete Hong Kong Island from Central to the eastern and southern coasts](https://linear.app/stealth-company/issue/HKS-124/complete-hong-kong-island-from-central-to-the-eastern-and-southern) | 01.1, 01.2, 01.3, 01.4, 01.5, 01.6, 01.7, 02.1, 02.2, 02.3, 02.4, 02.5, 03.1, 03.2, 03.3, 03.4, 03.5, 03.6, 04.1, 04.2, 04.3, 04.4, 04.5, 04.6, 04.7, 04.8 | 26 | Backlog |
| 4 | [HKS-125 — Complete Kowloon neighbourhoods, waterfronts and mixed-use building detail](https://linear.app/stealth-company/issue/HKS-125/complete-kowloon-neighbourhoods-waterfronts-and-mixed-use-building) | 05.1, 05.2, 05.3, 05.4, 05.5, 05.6, 06.1, 06.2, 06.3, 06.4, 06.5, 06.6, 07.1, 07.2, 07.3, 07.4, 07.5, 07.6, 08.1, 08.2, 08.3, 08.4, 08.5, 08.6, 09.1, 09.2, 09.3, 09.4, 09.5, 09.6 | 30 | Backlog |
| 5 | [HKS-126 — Complete New Territories West, ports, new towns and Lantau connections](https://linear.app/stealth-company/issue/HKS-126/complete-new-territories-west-ports-new-towns-and-lantau-connections) | 11.1, 11.2, 11.3, 11.4, 11.5, 12.1, 12.2, 12.3, 12.4, 12.5, 12.6, 16.1, 16.2, 16.3, 16.4, 16.5, 16.6, 16.7, 17.1, 17.2, 17.3, 17.4, 17.5, 17.6, 17.7, 17.8 | 26 | Backlog |
| 6 | [HKS-127 — Complete New Territories East, river towns, Sai Kung and eastern islands](https://linear.app/stealth-company/issue/HKS-127/complete-new-territories-east-river-towns-sai-kung-and-eastern-islands) | 13.1, 13.2, 13.3, 13.4, 13.5, 13.6, 13.7, 14.1, 14.2, 14.3, 14.4, 14.5, 14.6, 14.7, 15.1, 15.2, 15.3, 15.4, 15.5, 15.6, 15.7, 15.8, 15.9 | 23 | Backlog |
| 7 | [HKS-128 — Complete northern New Territories towns, border villages and remote coast](https://linear.app/stealth-company/issue/HKS-128/complete-northern-new-territories-towns-border-villages-and-remote) | 18.1, 18.2, 18.3, 18.4, 18.5, 18.6, 18.7, 18.8 | 8 | Backlog |

Mui Wo, Tai O and the other Lantau villages come first, followed by Peng Chau and Cheung Chau. Tai O’s channels/stilt details, sparse Shui Hau coverage and the 70 m terrain are known limitations, not completed geography.

## Original-feature porting

[FEATURE-PARITY.md](FEATURE-PARITY.md) is the baseline inventory. Re-audit the original source and later upstream changes before acceptance; an unlisted old function is not permission to drop it.

- [HKS-129 — Port remaining astronomy and live/manual environment controls](https://linear.app/stealth-company/issue/HKS-129/port-remaining-astronomy-and-livemanual-environment-controls) — Backlog.
- [HKS-130 — Port original flight, walking, UFO gameplay and sound](https://linear.app/stealth-company/issue/HKS-130/port-original-flight-walking-ufo-gameplay-and-sound) — Backlog.
- [HKS-131 — Port original terrain sources, surfaces, overlays, GPX and themes](https://linear.app/stealth-company/issue/HKS-131/port-original-terrain-sources-surfaces-overlays-gpx-and-themes) — Backlog.
- [HKS-132 — Restore original mobile, bilingual, sharing and location behaviours](https://linear.app/stealth-company/issue/HKS-132/restore-original-mobile-bilingual-sharing-and-location-behaviours) — Backlog.

GPS/sky follow, time and sound cross these tasks and need shared services and explicit integration. Keep original source attribution and licences. Verify old-versus-city controls, keyboard/touch, saved URLs, mode combinations, live/offline/error paths and mobile behaviour before claiming parity.

## Subagent hand-offs

All three subagents completed their bounded local passes. No new implementation pass was running when this snapshot was written. In Review records local evidence awaiting acceptance; it does not mean the full regional or feature task is finished.

| Executor | Review issue | Follow-on tasks |
| --- | --- | --- |
| Heisenberg (`complete_geography`) | [HKS-118 — Validate the Astra building base and island-village hand-off](https://linear.app/stealth-company/issue/HKS-118/validate-the-astra-building-base-and-island-village-hand-off) | [HKS-122](https://linear.app/stealth-company/issue/HKS-122/complete-lantau-buildings-villages-airport-and-walking-routes), [HKS-123](https://linear.app/stealth-company/issue/HKS-123/complete-peng-chau-cheung-chau-and-the-outlying-islands) |
| Kant (`sky_stargazing`) | [HKS-119 — Validate the Astra sky, stargazing and independent browser review](https://linear.app/stealth-company/issue/HKS-119/validate-the-astra-sky-stargazing-and-independent-browser-review) | [HKS-129](https://linear.app/stealth-company/issue/HKS-129/port-remaining-astronomy-and-livemanual-environment-controls), [HKS-132](https://linear.app/stealth-company/issue/HKS-132/restore-original-mobile-bilingual-sharing-and-location-behaviours) |
| Curie (`weather`) | [HKS-120 — Validate the Astra weather and aircraft implementation hand-off](https://linear.app/stealth-company/issue/HKS-120/validate-the-astra-weather-and-aircraft-implementation-hand-off) | [HKS-129](https://linear.app/stealth-company/issue/HKS-129/port-remaining-astronomy-and-livemanual-environment-controls), [HKS-130](https://linear.app/stealth-company/issue/HKS-130/port-original-flight-walking-ufo-gameplay-and-sound) |
| Primary agent (`/root`) | [HKS-121 — Validate city night activity and combined exploration controls](https://linear.app/stealth-company/issue/HKS-121/validate-city-night-activity-and-combined-exploration-controls) | [HKS-130](https://linear.app/stealth-company/issue/HKS-130/port-original-flight-walking-ufo-gameplay-and-sound), [HKS-131](https://linear.app/stealth-company/issue/HKS-131/port-original-terrain-sources-surfaces-overlays-gpx-and-themes), [HKS-132](https://linear.app/stealth-company/issue/HKS-132/restore-original-mobile-bilingual-sharing-and-location-behaviours) |

William is the Linear assignee. Executor names identify who performed a pass, not separate Linear accounts. At each meaningful checkpoint, update the relevant issue with completed work, evidence/commit, remaining limitations, blocker and next action. Set In Progress only when the next pass starts; distinguish implementation, independent review and release. Do not infer progress from an agent merely being active.

## Existing issues moved

- [HKS-114 — Buildings layer — LandsD building blocks extruded on the terrain (3D city, LOD1)](https://linear.app/stealth-company/issue/HKS-114/buildings-layer-landsd-building-blocks-extruded-on-the-terrain-3d-city) — retained In Progress, owner, cycle and original implementation description.
- [HKS-115 — Sun & moon: replace the linear Time slider with a 24-hour dial](https://linear.app/stealth-company/issue/HKS-115/sun-and-moon-replace-the-linear-time-slider-with-a-24-hour-dial) — retained In Progress, owner, cycle and original implementation description.

HKS-114’s LandsD implementation is separate from Astra’s OSM comparison; this milestone must not use Astra import counts to close the LandsD work. Released legacy issues remain Released and are linked as porting references. Historical/community issues remain in HK Sandbox Community.

## Metadata and verification

- 19 milestone issues: two existing issues, two parent roll-ups, four local review issues, seven regions and four porting tasks.
- Read back all issue owners, labels, milestones, parents, statuses and estimates; read back the seven section lists and both parent indexes.
- Status snapshot: 2 In Progress, 4 In Review, 4 Todo, 9 Backlog.
- New implementation tasks: High priority and provisional 8 points; review tasks: 4–8 points. Parent roll-ups: 0 points to avoid counting their children twice. Split broad regions/features into smaller slices during execution as needed.
- No deadline or cycle was manually selected. Linear returned cycle assignments on Todo/In Review issues; preserve those workspace-managed assignments.

No map-reference images were used or modified for this planning document. Geographic provenance remains with the implementation and section review notes.
