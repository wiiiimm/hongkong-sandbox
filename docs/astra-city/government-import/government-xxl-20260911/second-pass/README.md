# Government XXL second pass — 11 September 2026

Codex/Astra completed the authorised scripted follow-up. Original government building meshes, coordinates and elevations remain unchanged. This report supersedes the first-pass status counts; the earlier files remain historical evidence.

| Human status | XXL source parts |
| --- | ---: |
| Installed | 6 |
| To do | 0 |
| Held for human decision | 0 |
| Held for AI processing | 1 |
| Held for unknown state / technical resolution | 15 |
| In process | 0 |

The table records the completed scripted second-pass job before the later approved Sol review. Current routing after that review is six Installed, 15 Held-unknown/technical, zero Held-AI and one In process (queued for ordinary scripted acceptance; no live worker). The append-only review job preserves this transition without rewriting the frozen second-pass result.

The installed XXL parts are HSBC Main Building, Two IFC, M+, Hong Kong Central Library, Hong Kong West Kowloon Station and Saxon Tower. This second pass newly installs **Saxon Tower plus its original supporting podium**, committed and pushed as `cb666244`. The podium is an additional installed source part outside the 22-part XXL denominator. West Kowloon Station is a classification correction: the exact source hash was already installed under its resolved identity, although the native matcher had no UID. It does not increase city progress.

The site now has **295 enhanced forms**, including **288 / 212,669** matched government-source forms ready (0.1354%), with 212,381 remaining. Total mapped source forms: 346,108. These are source-part counts, not whole-building completion. The earlier 200-form batch remains 11 installed / 189 held.

## Remaining work

| Primary hold | Count | Work completed / next dependency |
| --- | ---: | --- |
| Source extends below original government terrain | 12 | Full original-mesh/native-TIN diagnostics saved; resolve source components, basements or engineering context. Several also have identity-fit holds. AI need is not established. |
| Incomplete native terrain coverage — Telford Plaza I | 1 | Adjacent sheets recovered; 69 of 1,090,338 samples remain uncovered. Identity also remains held. |
| Neighbour support — Elements | 1 | Prior exact source approval preserved; missing terrain recreated byte-for-byte. Current checks flag 38 of 87 neighbours; 17 have complete vertex-support diagnostics, 21 remain incomplete. Not published. |
| Overlapping native terrain surfaces — Lei Yue Mun Park Block 10 | 1 | Original model passes complete native contact checks; terrain patch guard rejects overlapping height surfaces. No patch applied. |
| Component interpretation — Lui Seng Chun | 1 | Proposed bounded GPT-5.6 Sol review, not started. Actual mesh projects beyond the recorded footprint despite native contact passing. |

All configured scripts have finished and all source reservations are released. The 15 technical holds have recorded blockers, but a safe resolution is unproven; a failed check alone does not establish a need for AI or a user decision. Unmatched native IDs retain proposed exact current CSUID/ObjectID candidates as diagnostic evidence only. [All outcomes](human-status.csv) and [held reasons/actions](technical-holds.csv) preserve this distinction.

The [Sol review](sol-review-proposal/README.md) was completed after explicit user approval with GPT-5.6 Sol at Medium reasoning. It supports Lui Seng Chun as a one-source architectural assembly: exact identifiers agree, 99.57% of the footprint is covered, exterior projection overlaps only 0.27 square metres of another mapped building, and all native terrain checks pass. This resolves the AI identity hold without editing geometry. Installation remains unapproved pending the normal recorded-height, runtime and browser gates. Attributable token counters were unavailable, so no measured total is claimed.

## Original-source installation and checks

Saxon Tower has 206,425 triangles; its original podium has 3,153. Combined compressed assets: 2,703,964 bytes. Actual podium triangles support all 124 tower low-rim samples, with a maximum 0.331 m gap; 120 are within 0.1 m. The podium passes strict identity and all 12,886 native contact samples. A source-backed 1,389-triangle terrain patch retains 1× HKPD and blends to unchanged parent terrain. Neither building mesh was moved or remodelled.

An initial broad terrain patch flagged seven neighbours. The final local patch flags three of 24; conservative checks prove each is supported by an unchanged existing source form with no terrain regression. Original warnings and separate support proof remain recorded. The tower/podium pair is installed with an explicit support dependency. The [supported-pair policy](../../../../../source-scripts/city/government-import/DIRECT-IMPORT-POLICY.md) documents these gates.

Staged and installed desktop/mobile day/night checks passed for both models, including actual loader, picking/collision, terrain rays, complete framing and mobile failure/retry. Sixteen PNGs were decoded and checked for dimensions, nonblank pixels and hashes by script. All 29 import tests, JavaScript syntax and skill v1.8.5 validation pass. No AI appearance scoring, physical-phone benchmark or dense-scene FPS certification is claimed.

## Durable checkpoint and source provenance

All 22 outcomes and detailed evidence were saved and read back exactly from completed Neon job `874a9e7eccac63f3adaaad6f868caf0259603961e1ee63d85600df5fca1d80c2` (`government-xxl-second-pass-v1`). Snapshot `1063980984fc18f3` includes the two new installed reviews. Source/result hashes and job writes were fenced; existing held review states and Elements approval were preserved. See `final-results.json.gz`, `final-summary.json` and `neon-sync.json`. Resume from these receipts; do not repeat completed installation or overwrite historical jobs.

All 18 held original assets were recovered and checked: six existing exact caches, 12 government member recoveries. Thirty-nine native terrain sheets were verified, including 22 adjacent sheets. Recorded initial source-member transfers total 207,484,085 bytes, excluding archive lookup overhead and extra Saxon support acquisition. Local recovery caches are not a new R2 backup; credentials were unavailable. Accepted Saxon assets and terrain are committed in the portable stage and runtime catalogue. Elements is only an unpublished stage and has a warning README.

Reproduction scripts are `xxl-second-pass.py`, `xxl-complete-context.py`, `xxl-restore-elements.py`, `xxl-stage-elements.py`, `xxl-stage-terrain.py`, the `xxl-saxon-*` / `xxl-stage-*saxon*` helpers, `xxl-review-packet.py` and `xxl-finish-second.py` under `source-scripts/city/government-import/`. Reuse frozen input hashes and acquire fresh source reservations before any future mutation. Generic territory queue construction remains deferred.

## Deployment and tracking

Commit `cb666244` is pushed on `codex/astra-hong-kong-city` (PR #298). [Verified preview](https://hongkong-sandbox-cscewx4js-stealth-factory.vercel.app/city.html): Vercel deployment `dpl_EfQJXDU9d8W258LoKErEv9xxA9u6` is READY; all seven checked hosted files match committed local bytes, including City HTML, manifest, progress, catalogue, both original model assets and native terrain. See `preview.json`. The earlier push approval rejection was resolved by explicit user authorization.

HKS-203, HKS-222, HKS-215, HKS-220, parent HKS-199 and the Astra milestone overview were updated successfully. Leaves remain In Review and the parent In Progress for broader work.
