## Current checkpoint — Whampoa and further residential components

This pass now has **205 new native source components installed and verified**, plus **31 existing native components reviewed** in Neon snapshot `f61930a5e4dfa572` (538 tracked source components). The Whampoa is a separate user request outside the frozen213-landmark baseline; both ship/hull sources are installed. These counts do not claim whole-landmark or regional completion.

The latest root integration adds18 components: ten Island Resort/Pacifica/Wplace models, six Capitol models and two Whampoa ship/hull models. Po Lin Hall of Great Hero now retains its native podium during streaming. Actual browser checks passed with unchanged1× source geometry: source IDs, terrain agreement, collision/picking, desktop/mobile night, walk/fly, failure fallback/Retry.264 viewer tests and28 guarded-publisher tests pass.

Capitol's narrower terrain extension preserves all29,751 existing Club Galaxy grid nodes and excludes the conflicting LOHAS ancillary structure. Two null-survey canopy base estimates follow the new terrain; surveyed elevations remain unchanged. Festival City and the LOHAS ancillary conflict remain held explicitly. The Whampoa native hull/decks/masts are recognisable; exact paint, glazing, lettering and decorative night lighting are a separately recorded appearance refinement, not delivered textures.

Current evidence: `current-checkpoint.json`, `residual-ten-live/after/verification.json`, `whampoa-capitol-live/after/verification.json`, `polin-live/after/verification.json`, and `../whampoa-special/close-view/report.json`. Four new exact-name tower sources were acquired; two passed the conservative packer and two Cullinan sources retain geometric identity review. Civic, Grand Promenade and further source review continue without waiting for user approval.

## 9 September — 187 new native components verified; 12 existing reviews completed

HKS-214 remains agent-owned **In Progress** (`gpt-6-astra`, `ai-software-factory`). Neon snapshot `11a25ce297101f9e` holds529 exact source components and199 installed-verified results:187 new additions and12 reviews of existing models. No user action blocks continued work. Details, qualifications and actual viewer evidence: `model-integration-20260909/README.md`. Source components are not whole landmarks. Source-local collision, exact native terrain, dependency migrations and stable window seeds are tested;264 viewer unit tests pass. Remaining podium/terrain candidates and existing Lantau components are under active review. R2's new working-material delta is being prepared separately; no production publication is claimed.

## 9 September — 89 native source parts installed and verified

HKS-214 is still agent-owned **In Progress**. This pass has installed5 cultural,2 terrain-corrected ancillary,23 grounded and59 supported parts; all89 have final viewer evidence and Neon installed-verified results. Source commitments:08a14ce4 cultural,66ae9cfc framing,38a71416 support; integration25fe49a2 cultural and2adda34d terrain/roads. Full evidence: `model-integration-20260909/README.md`. Source parts are not whole landmark completions. Pedder's heritage/height conflict is held by root despite earlier source-only approval. Missing native podiums for137 held parts are being acquired from71 exact government candidates; source absence, matching holds and terrain exceptions remain explicit. No user approval blocks continuing model work.

## 9 September — native cultural models installed; modelling continues

HKS-214 remains **In Progress**, executor `gpt-6-astra`, workflow `ai-software-factory`; no user action blocks the remaining work. Five exact West Kowloon cultural source parts are installed on the feature branch and recorded as `installed-verified` in Neon: M+ Pavilion, Xiqu Centre, M+ podium/tower and Hong Kong Palace Museum. Twenty real-route desktop/mobile day/night checks passed with no browser errors; native geometry, source picking and facade metadata are retained. Source review commit `08a14ce4`; evidence `model-integration-20260909/cultural-live/report.json`. This is exterior source-part integration, not photoreal materials, whole-campus/region completion, or production publication.

The new source-accounted Neon review ledger retains all459 selected parts, checks live source ownership on every result, and distinguishes prepared/held/approved/installed states. Three tests pass including a real-Neon stale-owner rejection. The remaining modelling and source/terrain reviews continue in parallel; earlier notes that this work is parked are superseded.

## 9 September — explicit model and workflow labels

Eleven modelling/pipeline issues now carry `gpt-6-astra`. HKS-199/202/203/209/212/214 use `ai-software-factory`: outstanding implementation and model review belong to the agent. Completed deliverables HKS-213/215/216/217/218 use `human-review-required`, with William named and concrete review scope/link recorded in each issue. Human sign-off closes those deliverables; it does not block continuing HKS-214. Other labels and issue statuses are preserved. Future checkpoints follow the same ownership distinction in the portable skill.

## 9 September — abandoned-agent recovery ready for review

[HKS-218](https://linear.app/stealth-company/issue/HKS-218) is **In Review**: atomic cross-batch source reservations, 30-minute expiry, five-minute automatic heartbeat for supervised commands, retained session/audit history, and deliberate audited takeover. Base commit 4b49976d; supervisor/recovery 9f0b2164; reusable skill 21c23b66. Twelve focused local tests and six unique live Neon cases passed; actual API/CLI supervised runs released their fixtures. Root independently verified a real-Neon run and broader shared suite (33 passed, 11 live-only skipped). Skill validation and diff checks pass. Evidence: `source-scripts/city/shared-modelling/reservation-verification.json` and `RESERVATIONS.md`. Executors: modelling_reservations implementation, landmark_visibility_fix independent review, root integration/tracking. Leaf, HKS-217/199 and milestone synced.

Manual AI sessions heartbeat at checkpoints. Only explicitly supervised commands renew automatically; arbitrary filesystem/R2 publication remains subject to existing guards and isolated outputs. No real model claims or production writes. Session history has no automatic deletion; exclusive ownership expires independently.

HKS-214 is **In Progress** following resumed model review. Commit 3071bb17 demonstrates 10/10 formerly inactive candidates load at individual close-up cameras with unchanged budgets. No runtime or model publication changes. Langham part landsd/235506:0 retains its hotel-versus-office identity hold; architectural and terrain acceptance remain open. Evidence: `docs/astra-city/landmark-visibility/`.

## 8 September — R2 cloud hand-off verified

HKS-216 is ready for In Review: full R2 upload and fresh-cache clean-checkout restore passed. hk-sandbox-assets/astra-modelling/ holds the immutable checkpoint at source commit 8d361811; manifest SHA 14dfae786d71b0a1f647284720c19507103791ad2b1c5d8348a4547ec12a2601. All 1,829 objects /1,761,277,880 bytes verified; 2,800 files +86 links restored. SQLite integrity, all inventory source hashes, and stage checks pass (346,115 forms; 29,760 historical jobs; 459 selected UIDs; 17 unchanged holds). Two real-R2 model workers also passed, exactly once per candidate. Detailed evidence: landmark-resume/R2-CLOUD-CHECKPOINT.json and shared-modelling/cloud-model-worker-verification.json. Eight transfer tests pass.

Neon HKS-217 remains In Review. Infrastructure verification gate is complete; user may raise effort for HKS-212/214 architectural work. No new model acceptance or viewer publication. Different-OS runtime installation remains untested; the clean checkout used this Mac's Python environment. Executors: Root bulk transfer/restore and pipeline checks; r2_cloud_model_check real worker transport. Earlier pending-credential notes below are superseded.

## 8 September — scripted preparation complete; portable processing infrastructure

The mechanical 213-landmark pass is complete: 459 selected source parts account for 133 already detailed, 273 prepared candidates, 36 checked source absences, nine matching holds and eight missing identities. All 326 jobs and 273 candidate CPU checks complete; all 245 terrain-flagged candidates have native terrain prerequisites. Gallery contains 166 assemblies/332 views, with four unresolved views and ten never-active candidate parts still explicit. No new whole-landmark acceptance or publication is implied. HKS-213 and HKS-215 are In Review; further identity/model review in HKS-212/214 is parked in Backlog pending infrastructure completion and higher-effort modelling.

HKS-217 now owns a persistent isolated Neon branch, astra-modelling (br-icy-firefly-b3zn5ogh), immutable inventory snapshots and a token-fenced leased queue. Full 749,546-row import committed with stored-content hashes verified; live queue concurrency/expiry tests passed. Round-trip export, source comparison and idempotent replay all pass. Two-process eight-building audit and two-process two-candidate preparation pass. HKS-217 is In Review. The audit and source-preserving cached-model processor are shared adapters; terrain/browser/publication scripts still require explicit wrappers before concurrent execution. Production remains untouched.

HKS-216 R2 implementation passed six local tests and a full clean-clone restore: 2,800 files/86 links; 2.607 GB logical, 1.761 GB content-addressed objects, zero-transfer repeat. Restored inventory hashes and stage checks pass. Cloud upload/restore remains pending bucket-scoped R2 credentials. Prefix: hk-sandbox-assets/astra-modelling/. Executors: Root queue/integration, postgres_inventory migration, r2_working_store cache/restore, shared_queue_review independent review.

The reusable skill now documents Neon shared state, local compatibility exports and separate R2 working files. Stay at the current effort for infrastructure; raise effort before architectural modelling. Earlier entries below are historical checkpoints, superseded by this one.

## 8 September — identity, source acquisition and installed models

User follows progress in chat; root maintains Linear. HKS-212/213 stay In Progress for remaining identities/sources; first passes are committed and verified.71identity proposals (67prior unresolved entries),88native models acquired across45tiles/14.3MB. Combined401UID pass skips132installed and prepares109candidates (84additional),109CPU checks,8.88MB. Three Asia components installed at94d6f563 and verified through actual catalogue;4,054detailed parts total. HKS-214 holds the next higher-effort model/terrain review. User notified to raise effort before that pass. All geometry remains1×; no production/R2 upload. Commitsd5012884,d4dd5d91,94d6f563,9151a562,8dd38a3f. Evidence in landmark-progress/, landmark-identity/, landmark-acquisition/ and landmark-visual-review/. Linear leaves/parents/milestone synced; no wholelandmark or region completion inferred.

## 7 September — verified wireframe and bulk preparation

HKS-210 is In Review at5724bd1c: Places → Inspect the mesh, actual source triangles, bounded view-centre radius, skin reveal and full restoration.244 tests and independent14-scene browser pass; current desktop Chrome frames16.7–33.3ms; physical phones unverified. HKS-211 is In Review atbaad46c9 for preparation:213 entries accounted,304 identified parts,158 completed jobs,25 staged candidates/CPU checks, zero downloads or publication.115 unresolved identities,59 entries with cache gaps,3 ambiguous groups and explicit placement holds remain. HKS-209 stays In Progress: three staged Asia Society recoveries from16 exceptions; remaining11 held/two absent. Installed models remain4,051. Parent HKS-182/202/199 and milestone synced; PR298 is still draft. Evidence in wireframe/, landmark-bulk/ and architecture-followup/.

## Wireframe inspection feature — 7 September 2026

[HKS-210](https://linear.app/stealth-company/issue/HKS-210/add-skin-reveal-wireframe-inspection-mode) added under HKS-182 in the Astra milestone. Backlog, Medium priority,4 points, assigned to William; Feature/Rendering. Solid, overlay and wireframe-only modes with a skin-reveal control expose actual terrain, building and bridge triangles. Preserve native1× coordinates; reuse legacy wireframe support and existing streaming. Mobile controls, material restoration, resource budgets and browser acceptance are included. Parent and milestone overview synced. Implementation has not started.

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

# Living Hong Kong delivery tracking

## Integrated island detail — 7 September 2026

Commit `78464134` integrates **302 additional government models**: Mui Wo +291 to **1,618/2,408 (67.2%)**, Tai O +7 to **539/1,030 (52.3%)**, Pui O +4 to **685/919 (74.5%)**. Seven source-derived terrain children and six guarded null-source base estimates are published together. All 346,115 forms and recorded government elevations remain intact. All 228 city tests, publisher rollback tests, 35 complete-terrain rays and 18 actual-browser model visits pass, including day/night/mobile, picking, walking arrivals, Fly-menu flight and failure/Retry. Source packages and root integration are committed for draft PR #298. [Evidence](island-detail-integration/README.md).

Mui Wo holds 21 acquired models for genuine native roof/foundation conflicts; remaining absent and mismatched source IDs stay explicit. Regular/temporary/open-sided structures are not interchangeable denominators. No whole section is signed off. Three source/terrain agents completed their bounded work; root completed shared publication and browser review. HKS-192/171 remain In Progress for remaining regional scope; user-set HKS-170 Ready to Merge is preserved.

## Detailed-model source hand-off — 7 September 2026

Three agents finished locally committed source packages; none is integrated or pushed. Live coverage remains Mui Wo 1,327/2,408 (55.1%), Tai O 532/1,030 (51.7%), Pui O 681/919 (74.1%). After acceptance, staged additions would yield Mui Wo 1,639 (68.1%; 287b81b1), Tai O 539 (52.3%; 4070e46b), Pui O 685 (74.5%; c43f948c). Mui Wo regular Tower-category coverage would reach 98.8%; remaining gaps largely concern temporary/open-sided structures lacking exact source models. Two Tai O and two Pui O additions need terrain correction; Mui Wo needs placement/browser screening. Agents report 17 focused tests plus actual shared-loader/picking/collision checks passing. Root verified hand-off files and commits and synchronised HKS-192/170/171, HKS-122/116 and milestone; independent browser review and publication remain pending. See each area's detail-completion README.

## Aircraft picker published — 7 September 2026

[6e8242e4](https://github.com/wiiiimm/hongkong-sandbox/commit/6e8242e4698308c98f0d99d0059352e1be632497) is published in draft PR #298. Fly now opens a pull-up chooser for all seven aircraft. All 226 city tests and fresh desktop/mobile browser checks pass, including keyboard/input isolation, in-flight continuity, races and failure/Retry. HKS-177 stays In Progress for remaining flight physics, landing, cameras and audio parity. [Evidence](aircraft-picker/README.md). Linear leaf, parent, parity roll-up and milestone updated.

## Draft checkpoint — 7 September 2026

[PR #298](https://github.com/wiiiimm/hongkong-sandbox/pull/298) is open as a draft. All 51 milestone issues have the PR attachment, with direct commit links on the relevant issues. Original commit hashes are retained. Source checkpoints b90c15f5 (HKS-192) and 7d3e3ff5 (HKS-196) are staged only; see their source notes for remaining acceptance. The 226 city tests and 13 focused source tests pass. No whole section is newly signed off.


## Stonecutters follow-up — 7 September 2026

HKS-196 is In Progress under HKS-126, related to HKS-191/HKS-125. Curie owns source/model/terrain staging; root owns integration and browser acceptance. Existing bridge runtime is reused. No Stonecutters delivery or whole-region sign-off is claimed. Linear leaf, parent and milestone are synchronised.

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
| HKS-191 · Tsing Ma + Ting Kau | Ready to Merge | `059f3b4d` source/assets + `ea9e96b0` integration: source models, corrected island foundations, actual picking, underwater rays, under-span flight, day/night and mobile checks pass. Curie complete; cables remain illustrative. |
| HKS-193 · Wan Chai–Central–Sheung Wan | In Progress | `80c42db` assets/evidence and `455761f` runtime: all 37 models passed desktop/mobile, picking/collision, night, Retry and card upgrade. Kant complete; placement and continuous public routes remain open. Six sections: 01.1–01.4 and 02.1–02.2. |
| HKS-180 · Remaining weather controls | In Progress | Tide/wave slice verified; remaining controls have no active executor. |
| HKS-194 · Numbered review grid | In Review | `13e3574`: optional 132-section layer and evidence-based readiness. |
| HKS-170 · Tai O | Ready to Merge | `5494ad6`: source channels, bridges and 607 m public walk. Private stilts/decks and wider north-west Lantau remain open. |

Root completed shared integration in `ea9e96b0`, browser review and Linear synchronisation. Heisenberg, Kant and Curie finished the previous bounded batch. Heisenberg completed staged Mui Wo checkpoint b90c15f5 and Curie completed staged Stonecutters checkpoint 7d3e3ff5. Both are committed in draft PR #298; live integration and final browser acceptance remain pending. Neither agent is still running on that checkpoint. Latest combined city suite: **226 tests pass** after compact model integration. GPU measurements use desktop Chrome, including mobile-sized viewports, and are serialised; physical-phone performance is unverified. New staged models and local route acceptance do not complete whole sections. Feature branch published for draft PR #298; no merge or production deployment.

Whole-section readiness remains **0 Ready, 0 Close, 12 Under review, 120 Base mapped**. [Review evidence and policy](review-sections/README.md). Latest evidence: [Mui Wo](mui-wo-completion/README.md), [haze](atmosphere/README.md), [golden sky and shadows](golden-hour/README.md).

[Current execution index](EXECUTION-ISSUES.md). Historical checkpoints below retain their original counts and scope.

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
