# Mui Wo detailed-source completion · HKS-192

Run `run.py fetch`, `run.py build`, and `test_completion.py` with `/tmp/astra-city-venv/bin/python` from this directory or the Astra worktree root. Outputs stay here and in `docs/astra-city/mui-wo-detail-completion`; no live assets are changed.

Reuses the existing government byte-range fetcher, exact GeoRefNo/footprint matching, original geometry decoder and lossless GLB packer. Baseline models and terrain are preserved. Retains one reason record for every Mui Wo UID, including models the official detailed product does not supply. Missing source detail is never replaced by invented geometry labelled as government data.

Integration follow-up: `placement.py`, `refine_placement.py`, `verify_placement.py`, then `test_placement.py` prepare and validate `publication/catalogue.json` (291models). Use this screened subset with its three-child `terrain-refinements.json`, local guarded `building-estimate-updates.json`, and scoped `diagnostic-updates.json`. The312-model `compact/catalogue.json` remains the source inventory, not the final publication list. See the detailed integration notes.
