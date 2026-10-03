# Tai O government-model slice

HKS-170 uses a small area configuration around the existing Mui Wo model/terrain pipeline. See [source counts, before/after evidence, limitations and rebuild commands](../../../docs/astra-city/tai-o-models/README.md).

`config.json` chooses only 9-SW-23A/23B. `index.json` / `index-request.txt` retain the official source index query. `official-selection.json.gz` is a labelled derived projection of the retained territory GeoJSON for matching; `building-selection.json.gz` retains whole existing source forms and attributes. These inputs are preserved for ordinary rebuilds.

`run.py` calls the shared byte-range downloader, source geometry baker, terrain builder and current-territory publisher; it does not introduce a second renderer or source-matching pipeline. `audit.py` reuses the source-TIN, baseline terrain and public-path arrival audits. `test_models.py` runs the existing model checks with this area's explicit 532-model coverage expectation, while the default Mui Wo test retains its original >900-new-model safeguard.

Large compact source ZIPs and extracted geometry are ignored. Download metadata retains exact public URLs, revisions, transfer ranges, CRC/SHA-256 and the distinction between compact cache versus complete source archive. Original glTF/bin entries can be recovered from the ignored cache or reproducibly acquired from those URLs. `staged/*/manifest.json` and source terrain grids remain inspectable. Runtime detailed geometry is attached to ordinary city building tiles, keyed by verified official UID and BuildingCSUID.
