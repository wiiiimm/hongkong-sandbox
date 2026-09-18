# Restored city tides and waves · HKS-180

Open the City **Weather** tab. In Manual weather, **Sea level** controls −1 to +4 m HKPD and **Waves** controls the surface motion. In Live weather, the city shows HKO astronomical tide predictions, rising/falling/slack trend and a 24-hour graph. Automatic station selection uses the nearer of Cheung Chau and Quarry Bay; either may also be selected explicitly. Manual preferences return when leaving Live.

Curie restored the original tide interpolation and shared water/shoreline shaders. The primary agent integrated the controls, graph, ferry level, walking admission and camera clearance. There is one water update per frame. The original game remains available.

- [Original comparison, methods, official sources and limitations](RESTORATION.md)
- [Actual city browser results and screenshots](browser/README.md)
- [Original-viewer compatibility evidence](original-browser/verification.json)

The tide/wave slice is implemented and locally verified. **HKS-180 remains In Progress** for its remaining typhoon, sky-height, snow-accumulation and other manual controls. Full original-feature parity remains open. Work is isolated on `codex/astra-hong-kong-city`.
