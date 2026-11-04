# City model codec provenance

The browser viewer vendors pinned decoder files so model loading does not depend
on a runtime CDN:

- `DRACOLoader.js`, `draco_decoder.js`, `draco_decoder.wasm`, and
  `draco_wasm_wrapper.js` come from `three@0.160.0` (`examples/jsm` and its
  glTF Draco build). `DRACOLoader.js` has only its package import adjusted to
  the adjacent vendored `three.module.js`. The Three.js MIT licence is in
  `THREE-LICENSE`; Draco's pinned Apache License 2.0 and upstream notices are
  in `DRACO-LICENSE`, copied from the official `google/draco` `1.5.7/LICENSE`.
- `meshopt_decoder.module.js` comes from `meshoptimizer@0.24.0`. Its MIT
  licence and upstream README are retained as `MESHOPT-LICENSE.md` and
  `MESHOPT-README.md`.

`city/model-codecs.js` loads and configures a decoder only when a selected
approved variant declares the corresponding codec. Draco uses one shared
worker; Meshopt uses one browser worker when available and direct decoding in
non-browser runtimes.
