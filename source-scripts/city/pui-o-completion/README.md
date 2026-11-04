# Pui O source package · HKS-171

This folder is a bounded configuration of the existing government source/model/TIN pipeline for sheets `14-NW-1A/B/C/D`. It stages 681 matched detailed models, a 5 m terrain patch and one continuously verified public beach-edge route. It does not complete section 10.7 or publish live data by default.

See [the hand-off](../../../docs/astra-city/pui-o-completion/README.md) for counts, limits, evidence and publication commands. All four source ZIPs are derived compact caches of original glTF/bin members, acquired with the existing HTTP range fetcher. Source metadata retains full URLs, source revisions, range hashes, entry CRC/SHA-256 and the distinction between a compact-cache hash and a full archive hash. Large caches and extracted native geometry are ignored; the source grids, match metadata and usable compact GLBs remain reviewable.

`run.py` imports existing helpers with area-specific paths; it contains no new renderer, terrain interpolation or model matching algorithm. `compact.py` calls `central-completion/pack_models.py:pack()` unchanged. `publish.py` defaults to checking source identity/hashes and writing a plan in the documentation folder. `--apply` is reserved for the root agent's coordinated local integration; it reuses `mui-wo-models/publish.py:publish_models()` and preserves all existing patch/catalogue/hydro entries.

The retained `building-selection.json.gz` is the before-publication source snapshot. Ordinary rebuilds reuse it; do not rerun `select` after publication and silently replace the baseline. Native official source attributes in `official-selection.json.gz` remain unchanged.

`browser.mjs` is the bounded actual-app acceptance runner. It first verifies the live catalogue and patch hashes against this package, then tests desktop/mobile views, source picking/collision, arrivals, beach walking, flight and a failed-download fallback with Retry. The bounded actual browser run now passes; repeat it only after coordinated local publication and a GPU release. Evidence is written to the documentation folder's `browser/` directory.
