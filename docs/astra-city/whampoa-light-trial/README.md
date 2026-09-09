# Five-place lightweight trial — HKS-225

Open `/whampoa-comparison.html` on the city preview. Select The Whampoa ship, Site 8, Site 12, Hong Kong Cultural Centre or Hong Kong Space Museum. Orbit/zoom synchronises all three cameras; mesh mode and reset are available. Narrow screens stack the cards.

The **high** column reuses existing native government geometry for the ship and two cultural landmarks. It does not claim a new high-effort AI pass. Site 8/12 high slots remain explicitly pending HKS-226, including the requested eventual main-map integration. No live city assets or source-review pointer were replaced.

## Trial scope and results

| Location | Source forms | Detailed triangles | Light triangles | Detailed gzip bytes | Light gzip bytes |
| --- | ---: | ---: | ---: | ---: | ---: |
| The Whampoa ship | 2 | 4,808 | 3,272 | 63,584 | 45,785 |
| Cultural Centre | 7 | 21,872 | 16,173 | 608,484 | 239,723 |
| Space Museum | 3 | 7,827 | 5,768 | 216,724 | 82,177 |
| Site 8 / Gourmet Place | 1 | Pending | 456 | Pending | Shared footprint and shader |
| Site 12 / Bamboo Mansions | 9 | Pending | 1,852 | Pending | Shared footprint and shader |

The authoritative exact sizes/hashes are in `3d-viewer/city/data/whampoa-light-trial/manifest.json`; the table should be regenerated if settings change. The existing footprint rings/heights are unchanged, including their known differences from native architectural roof envelopes. Basic is the supplied footprint extrusion without façade styling; it is not a claim that the current city has no windows.

The native light method welds/averages vertices in one-metre local cells, rejects degenerate faces, recomputes normals and drops unused colour attributes. The upper 20% of each mesh's local elevation is protected to retain prominent tips. Original source nodes and translations remain unchanged. Maximum measured original-vertex-to-cluster displacement is about 0.94 m for the ship, 1.03 m for the Cultural Centre and 0.96 m for the museum. This is **not** a Hausdorff surface-error bound or architectural acceptance. Some loss of thin rails, edges and roof detail is visible. Size savings include attribute removal and deduplication as well as triangle reduction. All views use the same neutral material and lighting to isolate geometry differences.

Estate light versions use a shared illustrative façade shader, not new surveyed roof/balcony geometry or photographs. The source footprint and height remain identical to basic. They add no model triangles or per-building texture files; shader work can still add GPU cost, which has not been benchmarked on a physical phone.

Site 8 is Whampoa Plaza / Gourmet Place (`landsd/324574:0`). Site 12 has nine named Bamboo Mansions towers. [Rating and Valuation Department building-name reference](https://www.rvd.gov.hk/doc/en/urban.pdf) identifies Site 8 at 7 Tak On Street and Site 12 as Bamboo Mansions. Ancillary Site 8 and shared Site 12 podium/landscape membership remain for the high pass. The Cultural Centre comparison includes its seven existing detailed components, including **Auditoria Building**; six separately unmatched canopy forms are excluded. No whole-site completion is claimed.

## Reproduce and continue

1. Read the model-improvement skill; claim exact source keys from `source-scripts/city/whampoa-light-trial/targets.json` using the shared reservation workflow.
2. Run `python source-scripts/city/whampoa-light-trial/generate.py` with the existing modelling Python environment. It reads cached government assets and the local source SQLite read-only, makes zero government requests and zero AI calls, and writes only separate trial files. Original source geometry is retained.
3. Run `node source-scripts/city/whampoa-light-trial/verify.mjs` against preview port 4176. The browser test visits all five selections at 1440px and 390px, confirms nonempty meshes, expected high-pending slots, no overflow and no browser errors, and saves screenshots. Emulated mobile is not physical-device performance certification.
4. Inspect screenshots, then use `register.py --ship-receipt PATH --other-receipt PATH` to record the frozen trial in Neon. It seeds an independent snapshot and writes **held / comparison-only** events with lightweight method, output references and script-run identity. Generation has no AI calls, so reasoning is recorded as not-applicable, not guessed from the session UI. Existing installed reviews stay intact. `neon.json` records the result.
5. Release reservations. After the user changes effort to High, follow HKS-226 to complete source membership, high-detail variants and guarded main-map integration. Retain comparison assets and append subsequent events.

New lightweight assets are committed with the preview, not uploaded as replacement production assets to R2. Existing full government caches in R2 are unaffected. Local cache portability still follows the existing R2 resume workflow. Adding these two requests does not rewrite historical source-selection plans.
