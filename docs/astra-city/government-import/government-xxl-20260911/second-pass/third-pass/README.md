# Government XXL third scripted pass — 12 September 2026

All 15 technical holds received another local-only pass. The batch finished with 15 Held-unknown/technical, zero Held-AI, zero Held-human and zero In-process. No model was published, no source geometry was changed and no modelling AI was used.

Exact triangle-surface checks narrowed the 13 models carrying a below-grade diagnostic. Two pass the new conservative source-surface and projected-identity checks: Elements and `landsd/136832:0`. Elements remains held because 21 neighbour/support forms are unresolved. The `landsd/136832:0` staging attempt remains held because its only recovered native terrain sheet leaves 3,360.123 m² of the required replacement rectangle uncovered. Of the other 11, nine remain outside the conservative component/identity contract and nine contain fully buried upward surfaces or exceed the small-foundation allowance; these groups overlap.

The three narrow terrain cases are now measured precisely:

- Telford Plaza I's 69 uncovered samples all sit along one recovered source-sheet edge, only 3.9–15.0 mm from the terrain boundary. This is a source seam problem, but no tolerance or interpolation rule has been applied. Identity also remains just outside the conservative scripted contract.
- Lei Yue Mun Park Block 10's proposed native patch covers its full 29,400 m² rectangle, but original source facets overlap by 367.492 m². It needs a verified highest-original-surface rule before neighbour and runtime checks can continue.
- The `landsd/136832:0` native patch has both a 3,360.123 m² coverage gap and 16.222 m² of projected overlap. The current fallback remains active.

The completed routing and evidence were saved and read back exactly from Neon job `ef9891074a41af4ce3253e7a8a688b2567345e2223f85b7bd8363621eb7a5b6c` (`government-xxl-technical-routing-v1`). See `final-results.json.gz`, `summary.json`, `neon-sync.json`, `source-surface-context.json` and `special-terrain-context.json`. Every row records whether more local compute, user judgment or AI is required; all 15 currently require local scripted engineering only.
