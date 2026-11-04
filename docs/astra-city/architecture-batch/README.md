# Expanded architecture batch 1 — HKS-208

25 reviewed new government model components, 1,269,800 compressed bytes. The14 selected landmark groups contain58 source parts:17 already detailed, 6 placement holds and10 requiring source/identity follow-up. Model parts are not whole landmarks or regional completion percentages.

| Landmark group | New detailed | Prior detailed | Placement hold | Source review |
| --- | ---: | ---: | ---: | ---: |
| Hong Kong Convention and Exhibition Centre | 0 | 1 | 0 | 0 |
| Tai Kwun — Centre for Heritage and Arts | 13 | 3 | 2 | 1 |
| Cheung Kong Centre | 0 | 3 | 0 | 0 |
| Lippo Centre — Tower 2 and connected complex | 3 | 0 | 0 | 0 |
| Asia Society Hong Kong Centre | 6 | 3 | 2 | 4 |
| Opus Hong Kong | 0 | 0 | 1 | 0 |
| The Peak Tower | 0 | 0 | 1 | 2 |
| The Henderson | 0 | 0 | 0 | 1 |
| Flagstaff House Museum of Tea Ware | 0 | 4 | 0 | 2 |
| Court of Final Appeal Building | 1 | 0 | 0 | 0 |
| Central Government Offices | 0 | 1 | 0 | 0 |
| Legislative Council Complex | 0 | 1 | 0 | 0 |
| Chief Executive’s Office | 0 | 1 | 0 | 0 |
| Hysan Place | 2 | 0 | 0 | 0 |

[Visual comparisons](comparison.html) · [Per-component decisions](../../../source-scripts/city/architecture-batch/acceptance.json) · [Native terrain/support audit](../../../source-scripts/city/architecture-batch/placement-context.json) · [Acquisition evidence](../../../source-scripts/city/architecture-batch/missing-source-report.json)

All source geometry uses unchanged EPSG:2326/HKPD coordinates at fixed1× scale. No terrain, surveyed elevations or other building forms changed. Lippo/Hysan towers must retain supporting podiums. Native roofs may exceed footprint TopHeight (e.g. Court of Final Appeal dome/finial); footprint metadata is preserved separately. These are non-textured government meshes with existing procedural city materials, not photographic models.

## Evidence and limits

[Atomic publication receipt](publication.json) records the25 installed assets. [Installed CPU checks](live-validation.json) cover all25 (the generic validator retains its `staged/published:false` labels; the publication receipt is authoritative). [Installed browser checks](installed-browser/after/verification.json) cover five representative landmark views without staged routes.

All31 candidates pass the shared model loader, native-roof picking/collision and rendered-terrain/sampler checks. All31 underwent staged browser checks including day/night, mobile viewport budgets, walk/Fly arrivals and failed-download fallback/Retry.229 city regression tests pass. Isolated foundation images are labelled diagnostic; unrelated geometry is hidden only for inspection. Ordinary-scene screenshots and installed verification remain separate. Desktop frame intervals are not physical-phone performance proof.

HKS-209 tracks held foundations and unresolved source matches. Four exactGeoRef candidates (Asia Society3089/3090/4314, Flagstaff143421) fail the conservative matching screen and need individual investigation. Missing exact models in checked sheet revisions are not proof that no model exists anywhere. The expensive0.25m Tai Kwun terrain experiment remains unpublished.

## Reproduce

```sh
/tmp/astra-city-venv/bin/python source-scripts/city/architecture-batch/prepare.py
node source-scripts/city/building-batch/validate_candidates.mjs --candidates source-scripts/city/architecture-batch/compact
python3 source-scripts/city/architecture-batch/review.py prepare
python3 source-scripts/city/architecture-batch/review.py publish
```

Preparation reuses existing cached decoder/matcher/packer with no AI calls. Four newly acquired models used15,356,700 HTTP-range bytes under a20MB guard; acquisition manifests and complete directory hashes document scope. Raw source/staged payloads and terrain experiment are local, ignored caches. Approved runtime assets are committed for PR298; production R2 offload is HKS-206, not performed here. Publication is deliberately one-shot and refuses duplicate IDs or changed reviewed inputs.
