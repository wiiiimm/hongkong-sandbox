# HKS-219 — The Whampoa special request

Agent: `whampoa_ship_model` / GPT-6 Astra. Separate addition to the original 213-landmark baseline. Two unchanged Lands Department non-textured native model components, 4,808 triangles, 63,584 compressed runtime bytes. Both are approved for guarded integration; this directory alone is not installed or deployed proof.

| Source component | Native model | Footprint base/top HKPD | Native envelope HKPD |
| --- | --- | --- | --- |
| `landsd/144948:0` ship superstructure | `B376051834301063C0` | 5.6 / 21.0 m | 5.834 / 32.006 m |
| `landsd/225581:0` hull and platform | `B376111834002063C0` | 4.0 / 5.6 m | 4.165 / 13.316 m |

The native hull contains tall perimeter surfaces; it is not a uniform podium slab. The upper component contains curved stepped decks, bridge/funnel forms and a mast. The 21 m footprint height does not match the native upper superstructure envelope. Both source descriptions remain separately recorded; no model clipping, scaling, translation or invented surveyed precision resolves the difference.

The current coarse ground buried the low hull/platform by 1.09–1.73 m. All 69 native low-rim samples meet cached LandsD native terrain within 0.11 m. The bounded 1 m sampled patch covers 29,751 nodes, with complete source coverage, zero boundary error and unchanged water mask. After the patch, the actual runtime sampler finds zero wholly buried source triangles or upward faces in either component. Native ship-to-hull contacts: 56/60 low-rim points within 0.5 m; four are 0.5–0.523 m from the nearest hull triangle. This small source interface difference is explicitly accepted without changing shared thresholds or source vertices.

`browser-terrain/` contains six normal-scene before/after/day/night/desktop/emulated-mobile captures. `browser-isolated/` contains six labelled source-inspection captures; adjacent apartment blocks occlude parts of the ship in the normal wide mobile view. Isolation is diagnostic, not a claim that surrounding buildings disappear in the product. Both target IDs load and pick correctly. Root must perform installed runtime collision/streaming and terrain-render agreement checks after guarded publication.

Generic apartment window grids are disabled on both maritime components. Original neutral non-textured source materials are retained. Photographic textures, signage, authentic paint colours, portholes and decorative lighting are not supplied by this pass.

## Identity and provenance

- [Official mall overview](https://www.thewhampoa.com/en/contact.html) identifies the streamlined ship landmark and Site 6.
- [Hong Kong Home Affairs Department](https://www.gohk.gov.hk/en/spots/spot_detail.php?spot=The+Whampoa) identifies the cruise-liner landmark in Whampoa Garden.
- [Government building footprint layer](https://portal.csdi.gov.hk/server/rest/services/common/landsd_rcd_1637211194312_35158/MapServer/0): named records and exact source CSUIDs; retained current WGS84 response and request SHA in `live-footprints-*`.
- Government non-textured model dataset `landsd_rcd_1742809441342_98380`, sheet `11-NE-21C`, revision 2025-10-27T16:00Z. Original glTF/bin hashes retained in staged manifest and geometry envelope evidence. The source provider's archive key is public data-access metadata, not a user credential.

The supplied Google place-label pin (22.3047243,114.1903547) is north-east of the named government ship footprints (approximately22.30406,114.18994). The exact source geometry stays at its surveyed position; it is not moved to a map label. No Google imagery is bundled or used as model geometry.

## Reproduce and resume

From the Astra worktree, with the project's Python environment and Node24:

1. Claim both canonical `building:landsd/144948:0` and `building:landsd/225581:0` keys on the pinned `astra-modelling` Neon branch. Save the receipt at `/tmp/astra-whampoa-lease.json`; this receipt is temporary coordination metadata, never committed.
2. Run `source-scripts/city/whampoa-special/acquire.py`. The 10 MB bounded downloader reuses completed caches: the second run retained 79,987 charged bytes and transferred no new source payload. It uses the existing exact-ID downloader and decoder.
3. Run `pack.py`, `support.mjs`, `terrain.py`, `surfaces.mjs`, `browser.mjs`; use `WHAMPOA_ISOLATED=1` for the additional isolated diagnostic captures. Retained native terrain comes from the existing `terrain-final-increment` cache for11-NE-21C; use the shared R2 restore workflow on a new device.
4. Review `visual-acceptance.json`, then run `prepare_approved.py`. It validates source/asset/screenshot hashes, exact target IDs, source contacts, terrain coverage and burial checks, and creates `publication-plan.json` for root's guarded publisher.
5. Apply the plan with live reservations, verify the installed scene, then record `installed-verified` in the current Neon review snapshot. Do not mark whole-landmark visual perfection or production deployment from this staging checkpoint.

Neon request job `8684beb4926859367e8e732be2dab9f4fcf8497b383f421eb40c27a1dab43932`; source inventory supplement `41bc2bb6beaf282f` is merged into shared snapshot `f61930a5e4dfa572`. Both source reviews are `approved-for-integration`. HKS-219 remains agent-owned In Progress until installation is verified.
