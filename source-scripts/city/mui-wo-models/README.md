# Mui Wo official-model extension

HKS-167. Reuses the original source glTF/terrain helpers and the existing city tile renderer. See [method, source accounting, images and rebuild commands](../../../docs/astra-city/mui-wo-buildings/extension/README.md).

`index.json` and `index-request.txt` retain the official sheet query. `sources/*/download.json` records either a complete archive hash or a clearly labelled compact geometry cache with original ZIP-entry hashes and validated HTTP byte ranges. Raw caches and extracted assets are ignored. `staged/*/manifest.json` and `terrain-source-5m.json` retain per-sheet source matching and terrain samples. `model-geometries.json.gz` is the compact, reproducible combined geometry payload; live building tile geometry remains in the usual city data location.
