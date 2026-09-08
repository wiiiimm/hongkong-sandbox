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

## Latest review checkpoints

- `5724bd1c` — HKS-210 bounded mesh inspection, In Review.
- `baad46c9` — HKS-211 bulk preparation, In Review;25 candidates, no publication.
- `e76e79aa` — HKS-209 sixteen exceptions audited; three staged candidates,13 held/missing, In Progress.
- `323bbe1a` — HKS-199/202 read-only current-job status; excludes superseded pending rows.

# Astra milestone commit and Linear issue index

Commit links indicate scope, not completion. Older mappings remain intact; new entries use explicit HKS references.

Branch: `codex/astra-hong-kong-city`. Snapshot: `d288106a`. Base: `5777bc98`. The tracking documentation commit follows this snapshot.

| Commit | Change | Linear issues |
| --- | --- | --- |
| [c9911162](https://github.com/wiiiimm/hongkong-sandbox/commit/c9911162242d791123f5b399c4d81b72890b9ce2) | feat(city): import attributed Central and harbour building data | HKS-116 |
| [5404b4e9](https://github.com/wiiiimm/hongkong-sandbox/commit/5404b4e93d6b6cfde95e0d06a1838c8e91596ea8) | feat(city): add playable Astra city explorer | HKS-116, HKS-117 |
| [7c17150d](https://github.com/wiiiimm/hongkong-sandbox/commit/7c17150dcf95422e0d0277f236c698a77c6303e4) | docs(city): record scope and browser verification evidence | HKS-116, HKS-117 |
| [e447c692](https://github.com/wiiiimm/hongkong-sandbox/commit/e447c69236c27026dfa9183f20120c0481500a13) | feat(city): expand attributed building data across Hong Kong Island Kowloon and Lantau | HKS-116 |
| [7e07f14a](https://github.com/wiiiimm/hongkong-sandbox/commit/7e07f14a9c698c36805024dbea8eb7bcc3aa3624) | feat(city): stream neighbourhoods with regional travel and global building search | HKS-116 |
| [25c31330](https://github.com/wiiiimm/hongkong-sandbox/commit/25c3133055bac58c8f4f6239cce5e2e9ad56bfae) | docs(city): track 132 geographic sections and required original-game parity | HKS-116, HKS-117 |
| [0a6e38f4](https://github.com/wiiiimm/hongkong-sandbox/commit/0a6e38f44e4832559099564042c57b2bb2dde67b) | feat(city): let building windows sleep through a full night cycle | HKS-121 |
| [fb558786](https://github.com/wiiiimm/hongkong-sandbox/commit/fb558786305878a9dd5411e3190003643f9aa190) | docs(city): record night-cycle behaviour and rendered verification | HKS-121 |
| [7ed00d9f](https://github.com/wiiiimm/hongkong-sandbox/commit/7ed00d9f72b0e42e0fb02821b4d4363b07956da0) | feat: classify Hong Kong buildings by mapped activity and land use | HKS-121 |
| [99b19224](https://github.com/wiiiimm/hongkong-sandbox/commit/99b192247a8f29ee6e6a1bbdb1ec56ea93ac9c00) | feat: add a circular 24-hour clock and varied city night lighting | HKS-115, HKS-121 |
| [ee6c1400](https://github.com/wiiiimm/hongkong-sandbox/commit/ee6c140016d04ee0b8a24b50f7ca18370c6aacde) | docs: record clock and night-lighting browser verification | HKS-115, HKS-121 |
| [52ddd77e](https://github.com/wiiiimm/hongkong-sandbox/commit/52ddd77e6c6a4f60b66573260cd918b26cd9ebc5) | feat: restore dated astronomy and catalogue stars for the city | HKS-119, HKS-129 |
| [a6933b46](https://github.com/wiiiimm/hongkong-sandbox/commit/a6933b4657959a282abd9fdc2f25fe780f29460b) | feat: add manual weather and timestamped HKO observations | HKS-120, HKS-129 |
| [4d4da800](https://github.com/wiiiimm/hongkong-sandbox/commit/4d4da80005c3e6c617d079eb75e0a330b798b31b) | feat: extend city coverage across Hong Kong and refine island villages | HKS-116, HKS-118 |
| [156c0143](https://github.com/wiiiimm/hongkong-sandbox/commit/156c0143f2a51cafc6066f8526bf25436f537d33) | feat: improve and restore the original aircraft collection | HKS-120 |
| [aae22c32](https://github.com/wiiiimm/hongkong-sandbox/commit/aae22c324d7766e79cb3233a5a61cec03a9016d7) | feat: tune evening activity and make 4am substantially quieter | HKS-121 |
| [78cc0723](https://github.com/wiiiimm/hongkong-sandbox/commit/78cc07235044aa716361df1a188f1b603978bf9c) | feat: integrate dated sky weather and aircraft controls across the city | HKS-117, HKS-119, HKS-120 |
| [29af4f93](https://github.com/wiiiimm/hongkong-sandbox/commit/29af4f93920b3df320fc97de0b8f0bdee28fe1a1) | docs: track HKS-116 regional delivery and HKS-117 feature parity | HKS-116, HKS-117 |
| [5ae3900e](https://github.com/wiiiimm/hongkong-sandbox/commit/5ae3900e5c3743135d90c5eca30cf1e639c247f3) | feat: expand regional city detail and mapped footbridges (HKS-116, HKS-153) | HKS-116, HKS-153 |
| [c85ac0b7](https://github.com/wiiiimm/hongkong-sandbox/commit/c85ac0b771a97b908a7c240a9919b0897e5498f7) | feat: restore Mui Wo government building coverage and 3D detail (HKS-164) | HKS-164 |
| [ff68cf15](https://github.com/wiiiimm/hongkong-sandbox/commit/ff68cf15241edf578326450b0abe2fc428516b62) | feat: integrate verified government buildings across Hong Kong (HKS-116) | HKS-116, HKS-164 |
| [5318e366](https://github.com/wiiiimm/hongkong-sandbox/commit/5318e3665d1fdeb94aa54887f35b7c0157609d07) | docs: organise Astra delivery into executable subissues (HKS-116, HKS-117) | HKS-116, HKS-117 |
| [8aa4996b](https://github.com/wiiiimm/hongkong-sandbox/commit/8aa4996b13876d33a187e8dea9646f7823b84c43) | feat: restore shooting stars and storm audio in the city (HKS-168, HKS-169) | HKS-168, HKS-169 |
| [fd644358](https://github.com/wiiiimm/hongkong-sandbox/commit/fd6443585a27e7f5b18a62c7510b949eaae994e2) | feat: extend official Mui Wo buildings and terrain detail (HKS-167) | HKS-167 |
| [ab4be9ec](https://github.com/wiiiimm/hongkong-sandbox/commit/ab4be9ec2187687f74515c0d541ec6dced42cde2) | docs: record verified parallel delivery and Linear progress (HKS-116, HKS-117) | HKS-116, HKS-117 |
| [a6f43bca](https://github.com/wiiiimm/hongkong-sandbox/commit/a6f43bca0c075540cf4385808702bc572fa62047) | feat: restore tides and shoreline waves in the city (HKS-180) | HKS-180 |
| [e2c50f9a](https://github.com/wiiiimm/hongkong-sandbox/commit/e2c50f9a642346b2f0cc273b4676bdc2cc8dc173) | feat: add mobile controls and timelapse (HKS-189, HKS-190) | HKS-189, HKS-190 |
| [04d3fac7](https://github.com/wiiiimm/hongkong-sandbox/commit/04d3fac76fb02eca0cf9702397b1c609ff681dbc) | docs: record city controls and timelapse delivery (HKS-189, HKS-190) | HKS-189, HKS-190 |
| [c9f1a797](https://github.com/wiiiimm/hongkong-sandbox/commit/c9f1a797b603a6408b3aeaf2c6f5daad0b4c151d) | fix: clarify city speed controls and data sources (HKS-189) | HKS-189 |
| [9538e031](https://github.com/wiiiimm/hongkong-sandbox/commit/9538e031cbe2dc3b0ad0de74de4896b7fdfd1749) | docs: record speed-control follow-up (HKS-189) | HKS-189 |
| [46b67edf](https://github.com/wiiiimm/hongkong-sandbox/commit/46b67edf48e1b8e20e363c7d76e54e8c24a0f303) | feat: give city time controls their own tab (HKS-190) | HKS-190 |
| [619cf515](https://github.com/wiiiimm/hongkong-sandbox/commit/619cf51575729f9dd46d2431632c6700dbd4fafc) | docs: track time tab and active Tai O model pass (HKS-170) | HKS-170 |
| [72df3cf6](https://github.com/wiiiimm/hongkong-sandbox/commit/72df3cf6a559c01167ba211c5287daa1518ee394) | feat: add detailed Tai O government models (HKS-170) | HKS-170 |
| [2aeb545e](https://github.com/wiiiimm/hongkong-sandbox/commit/2aeb545e65b738f58bdb5be82dcaee32a57c84f6) | docs: record verified Tai O delivery in Linear (HKS-170) | HKS-170 |
| [7757ee69](https://github.com/wiiiimm/hongkong-sandbox/commit/7757ee696b151f4ab18844a03792dc6ffeffd789) | docs: require Linear updates when work is completed | HKS-116, HKS-117 |
| [783cb624](https://github.com/wiiiimm/hongkong-sandbox/commit/783cb6240ad65323beb6d5b6e2afc8be1b603bf8) | feat: toggle live city time and group weather shimmer (HKS-190) | HKS-190 |
| [59b67e8d](https://github.com/wiiiimm/hongkong-sandbox/commit/59b67e8d907efe0b64cc540f6249b4041e8f2869) | docs: record clock delivery and active Tai O completion (HKS-190) | HKS-190 |
| [27960d43](https://github.com/wiiiimm/hongkong-sandbox/commit/27960d43e0cbe3a9dedfa97ddf31199dd5b121f7) | docs: track Tsing Ma Bridge model and terrain repair (HKS-191) | HKS-191 |
| [ceab3000](https://github.com/wiiiimm/hongkong-sandbox/commit/ceab30009fe574f02758b40537b2b6a1bfefb373) | docs: track parallel bridge and regional work (HKS-191) | HKS-191 |
| [5494ad65](https://github.com/wiiiimm/hongkong-sandbox/commit/5494ad6579f9240f3a14d7e33a756627ad967162) | feat: complete Tai O channels and public village walk (HKS-170) | HKS-170 |
| [03ded3de](https://github.com/wiiiimm/hongkong-sandbox/commit/03ded3de616f284c200aacd7be85dcbe57094288) | docs: record Tai O acceptance and Central hand-off (HKS-170) | HKS-170 |
| [13e3574f](https://github.com/wiiiimm/hongkong-sandbox/commit/13e3574fcb4b2a44bd6f612300afeef2ee275dc9) | feat: add numbered Hong Kong review sections (HKS-194) | HKS-194 |
| [2f497f80](https://github.com/wiiiimm/hongkong-sandbox/commit/2f497f80d61d7509b2cd444282b4499477d3f64b) | docs: sync section grid delivery and regional hand-offs (HKS-194) | HKS-194 |
| [0e40ef7f](https://github.com/wiiiimm/hongkong-sandbox/commit/0e40ef7facf95bf6c6f53a7a86b54fef199812d6) | docs: record second bridge scope clarification (HKS-191) | HKS-191 |
| [703f222f](https://github.com/wiiiimm/hongkong-sandbox/commit/703f222feeba31a10e9b6f713fffb047fe735692) | feat: support regional source infrastructure and water packages (HKS-192) | HKS-192 |
| [8e8a1817](https://github.com/wiiiimm/hongkong-sandbox/commit/8e8a181765d238aede7a08e390afd60b1e3fad21) | feat: control haze with live visibility and manual clarity (HKS-195) | HKS-195 |
| [367cc1bb](https://github.com/wiiiimm/hongkong-sandbox/commit/367cc1bb3bdcb1e6ece2241988a6242cc648d26c) | fix: restore original golden sky and celestial shadow alignment (HKS-119) | HKS-119 |
| [9a330456](https://github.com/wiiiimm/hongkong-sandbox/commit/9a3304561c3c7051fe00e9085be1c561c188e727) | feat: complete Mui Wo terrain and public village route pass (HKS-192) | HKS-192 |
| [0a2f5f0f](https://github.com/wiiiimm/hongkong-sandbox/commit/0a2f5f0f865e3ec3c4d428337704f99a3fe2872b) | docs: sync verified city deliveries and regional execution (HKS-192) | HKS-192 |
| [455761f7](https://github.com/wiiiimm/hongkong-sandbox/commit/455761f7aab75a2f7fe4078c90e45a4f17f94373) | feat: stream verified building models and bridge cables (HKS-193) | HKS-193, HKS-191 |
| [80c42dbb](https://github.com/wiiiimm/hongkong-sandbox/commit/80c42dbb3d05bb6b96e4f846bcef1c9076021bea) | feat(city): add sourced Central and corridor models | HKS-193 |
| [72810711](https://github.com/wiiiimm/hongkong-sandbox/commit/72810711a39eda2c69c34e1cafa16beaf4372a41) | feat(city): add source-backed Pui O buildings and terrain | HKS-171 |
| [059f3b4d](https://github.com/wiiiimm/hongkong-sandbox/commit/059f3b4ddbe144920fe8592b3884cf8bd9d630bf) | feat(city): restore sourced Tsing Ma and Ting Kau bridges (HKS-191) | HKS-191 |
| [62a89a29](https://github.com/wiiiimm/hongkong-sandbox/commit/62a89a29024839c8bb91d3354d796cb9319b24d7) | docs(city): audit south Lantau model availability (HKS-171) | HKS-171 |
| [ea9e96b0](https://github.com/wiiiimm/hongkong-sandbox/commit/ea9e96b0db958ae670dfde3dcf7862437c70ed07) | feat: integrate regional models and source bridge terrain (HKS-191) | HKS-191, HKS-171, HKS-192, HKS-193 |
| [70afe855](https://github.com/wiiiimm/hongkong-sandbox/commit/70afe8559bd526b52cbcf928598df7f8edaa429c) | docs: sync reviewed regional deliveries with Linear (HKS-191) | HKS-191 |
| [fc36a645](https://github.com/wiiiimm/hongkong-sandbox/commit/fc36a64518659611de0095a15f9ccc1d0e22f3af) | docs: track Stonecutters reconstruction and section status (HKS-196) | HKS-196 |
| [e4e5367a](https://github.com/wiiiimm/hongkong-sandbox/commit/e4e5367ae028878d97be81efe108422219d0b247) | docs: resume remaining Mui Wo conflict review (HKS-192) | HKS-192 |
| [33f83a1a](https://github.com/wiiiimm/hongkong-sandbox/commit/33f83a1ac867bd48a99ee511eafefe951d68a3b6) | test: record Stonecutters terrain baseline (HKS-196) | HKS-196 |
| [33baf810](https://github.com/wiiiimm/hongkong-sandbox/commit/33baf810c97634e1fcc5e3c93a98b15dcda31368) | docs: index Astra milestone commits and Linear issues (HKS-116, HKS-117) | HKS-116, HKS-117 |
| [7d3e3ff5](https://github.com/wiiiimm/hongkong-sandbox/commit/7d3e3ff50b93f16c90eefe22e010a03afacf885c) | feat(city): stage Stonecutters bridge sources (HKS-196) | HKS-196 |
| [b90c15f5](https://github.com/wiiiimm/hongkong-sandbox/commit/b90c15f5ee59d77ba9a134aea761bc3c93d7506f) | fix(city): stage source-backed Mui Wo terrain refinements | HKS-192 |
| [a18401fc](https://github.com/wiiiimm/hongkong-sandbox/commit/a18401fcd2b67c7d065cfa4f866b863e523411ee) | docs: link milestone draft and staged checkpoints (HKS-116, HKS-117) | HKS-116, HKS-117 |
| [6e8242e4](https://github.com/wiiiimm/hongkong-sandbox/commit/6e8242e4698308c98f0d99d0059352e1be632497) | feat(city): add fly dock aircraft chooser (HKS-177) | HKS-177 |
| [9b034a02](https://github.com/wiiiimm/hongkong-sandbox/commit/9b034a02ecb8862c287492b60a32bd152bb18516) | docs: sync aircraft picker delivery (HKS-177) | HKS-177 |
| [4070e46b](https://github.com/wiiiimm/hongkong-sandbox/commit/4070e46bbb1ba110e274129e6067ec409ecaa43a) | chore(city): audit and stage remaining Tai O model candidates | HKS-170 |
| [287b81b1](https://github.com/wiiiimm/hongkong-sandbox/commit/287b81b1b152338a73537705a5d6f2fc863861fc) | feat(city): stage 312 additional Mui Wo government models (HKS-192) | HKS-192 |
| [c43f948c](https://github.com/wiiiimm/hongkong-sandbox/commit/c43f948cc17914542d3844a035e71903fb166426) | feat(city): audit Pui O detailed coverage and stage missing models (HKS-171) | HKS-171 |
| [1dd06dbf](https://github.com/wiiiimm/hongkong-sandbox/commit/1dd06dbf3a8f9515d9debb37980bd32a1f6e42cc) | docs: record staged island model coverage (HKS-192, HKS-170, HKS-171) | HKS-170, HKS-171, HKS-192 |
| [2eff93ea](https://github.com/wiiiimm/hongkong-sandbox/commit/2eff93ea7a4b17e4baa5aed0fe91a4fbbddb72b0) | fix(city): stage source terrain corrections for Tai O additions | HKS-170 |
| [48733cc9](https://github.com/wiiiimm/hongkong-sandbox/commit/48733cc9ac840bcfb52ddc73a8a6590ac2e28a50) | fix(city): stage source terrain for Pui O model gaps (HKS-171) | HKS-171 |
| [de41464c](https://github.com/wiiiimm/hongkong-sandbox/commit/de41464c589cf8fdd4e9c3763ecb773d32275147) | fix(city): render nested source terrain across chunks (HKS-192, HKS-170, HKS-171) | HKS-170, HKS-171, HKS-192 |
| [3a769cc1](https://github.com/wiiiimm/hongkong-sandbox/commit/3a769cc179ef8931a2555513ae7304965d2360aa) | fix(city): screen Mui Wo model placement and refine terrain (HKS-192) | HKS-192 |
| [78464134](https://github.com/wiiiimm/hongkong-sandbox/commit/78464134d469b78def31a8e464864c70fdfcc2b8) | feat(city): integrate 302 island government models (HKS-192, HKS-170, HKS-171) | HKS-170, HKS-171, HKS-192 |
| [9c7ab987](https://github.com/wiiiimm/hongkong-sandbox/commit/9c7ab987a9c2ffe8522ac312d9e6467bc09c670c) | docs: sync island detail delivery and Linear references (HKS-116, HKS-192, HKS-170, HKS-171) | HKS-116, HKS-170, HKS-171, HKS-192 |
| [1cc2cf0f](https://github.com/wiiiimm/hongkong-sandbox/commit/1cc2cf0ff849388135174f44e4f40a69fe2fd0e3) | feat(data): index existing city buildings in local SQLite (HKS-200) | HKS-200 |
| [306b4d9b](https://github.com/wiiiimm/hongkong-sandbox/commit/306b4d9bc9f9eeeb08413f1208119a9a0197fedf) | docs: track local building automation and inventory delivery (HKS-199) | HKS-199 |
| [962b54a8](https://github.com/wiiiimm/hongkong-sandbox/commit/962b54a8482b951fcef97698b222eaad19fcfbc1) | feat(data): select tourist trial and run resumable preflight (HKS-201, HKS-202) | HKS-201, HKS-202 |
| [21a77377](https://github.com/wiiiimm/hongkong-sandbox/commit/21a77377dcad257df81f89572894ba6b91ee6904) | docs: sync tourist trial review and runner progress (HKS-199) | HKS-199 |
| [a308b861](https://github.com/wiiiimm/hongkong-sandbox/commit/a308b86131e756bdc25c2ae839c962e0b3bbac33) | feat: batch cached government models with placement diagnostics (HKS-202, HKS-203) | HKS-202, HKS-203 |
| [a3ca9c1a](https://github.com/wiiiimm/hongkong-sandbox/commit/a3ca9c1a7069110a033ef75c1752fceadb7aaf8c) | docs: sync cached-model batch progress to Linear (HKS-199) | HKS-199 |
| [d69c97fb](https://github.com/wiiiimm/hongkong-sandbox/commit/d69c97fb0b5a234d830ae80e2d11bc546a983d51) | docs: track production R2 asset offload (HKS-206) | HKS-206 |
| [63a707c6](https://github.com/wiiiimm/hongkong-sandbox/commit/63a707c672f22677674c0b4dbe50bb598be41ae3) | feat: publish reviewed tourist model trial (HKS-203, HKS-204) | HKS-203, HKS-204 |
| [df11cd69](https://github.com/wiiiimm/hongkong-sandbox/commit/df11cd699475ee25383b6c3fc71fc03e54a37667) | docs: record visual trial review and preview delivery (HKS-203, HKS-204) | HKS-203, HKS-204 |
| [62ff8233](https://github.com/wiiiimm/hongkong-sandbox/commit/62ff8233620b58340ed70ff9cc6ff0f93dd33aae) | docs(city): exclude vertical exaggeration from parity (HKS-117, HKS-131, HKS-182, HKS-187) | HKS-117, HKS-131, HKS-182, HKS-187 |
| [c8a5fddb](https://github.com/wiiiimm/hongkong-sandbox/commit/c8a5fddb24892dd09de6163edcbb52847ca7786a) | feat(city): complete source-accounted landmark pass (HKS-202, HKS-203, HKS-204, HKS-174) | HKS-202, HKS-203, HKS-204, HKS-174 |
| [aa34ac1e](https://github.com/wiiiimm/hongkong-sandbox/commit/aa34ac1ec7ce951890d532f26317c311d1bf762f) | feat(city): upgrade Space Museum and Cultural Centre (HKS-207) | HKS-207 |
| [52b965d0](https://github.com/wiiiimm/hongkong-sandbox/commit/52b965d019e1f9c806bf9ce6da9bd5de9152d745) | feat(data): expand sourced landmark discovery registry (HKS-201) | HKS-201 |
| [94f78403](https://github.com/wiiiimm/hongkong-sandbox/commit/94f78403b929b9618c069e5661514ad306f3ef8d) | docs: sync landmark deliveries and discovery review (HKS-201, HKS-207, HKS-116) | HKS-201, HKS-207, HKS-116 |
| [d288106a](https://github.com/wiiiimm/hongkong-sandbox/commit/d288106a5c2670d88eec51bcc3410202b89c199a) | feat(city): add reviewed architecture landmark batch | HKS-208, HKS-209, HKS-201 |
