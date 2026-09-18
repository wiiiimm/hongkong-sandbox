# Mui Wo section10.6 completion

See [scope, evidence and limitations](../../../docs/astra-city/mui-wo-completion/README.md). Run from the Astra worktree with the existing Python environment and Node runtime. All commands below stage output until explicit publication.

```sh
PY=/tmp/astra-city-venv/bin/python
$PY source-scripts/city/mui-wo-completion/audit_existing.py
SSL_CERT_FILE=/etc/ssl/cert.pem $PY source-scripts/city/mui-wo-completion/fetch_terrain.py
$PY source-scripts/city/mui-wo-completion/terrain_stage.py
$PY source-scripts/city/mui-wo-completion/terrain_audit.py
$PY source-scripts/city/mui-wo-completion/infrastructure_stage.py
$PY source-scripts/city/mui-wo-completion/hydro.py
$PY source-scripts/city/mui-wo-completion/hydro_terrain_stage.py
$PY source-scripts/city/mui-wo-completion/routes.py
$PY source-scripts/city/mui-wo-completion/promenade_route.py
node source-scripts/city/mui-wo-completion/promenade_walk.mjs
node source-scripts/city/mui-wo-completion/approaches.mjs
$PY source-scripts/city/mui-wo-completion/package.py
node source-scripts/city/mui-wo-completion/route_final.mjs
$PY source-scripts/city/mui-wo-completion/arrivals.py
$PY source-scripts/city/mui-wo-completion/arrival_connector.py
node source-scripts/city/mui-wo-completion/arrival_connector.mjs
$PY -m unittest discover -s source-scripts/city/mui-wo-completion -p 'test_*.py' -v
```

The original `infrastructure-config.json` fixes reviewed face IDs against source glTF hashes. The small retained `opening-scan.json` is reproducible using `openings.py` then `opening_scan.mjs`; no cached manual path is substituted for the final collision/navigation checks. `route-config.json` excludes two source edges that intersect retained buildings and selects the checked Tai Tei Tong main public approach.

Large raw ZIPs/extracted glTF assets are ignored source caches, not runtime content. `download.json` retains URLs, revisions, remote archive sizes, byte ranges and entry/cache hashes. Compact original GML and full source5m grid samples remain; clipped grids and the staged terrain patch are reproducible derivatives. No photographic texture data is required.

After shared generic infrastructure and composite hydro integration, coordinate these stages with root:

```sh
$PY source-scripts/city/mui-wo-completion/publish.py --geometry
# Root merges the standalone hydro-mui-wo-terrain.json with Tai O/Tsing Ma,
# preserving per-region bounds and the existing Tai O source record.
$PY source-scripts/city/mui-wo-completion/publish.py --places-and-infrastructure
node source-scripts/city/mui-wo-completion/browser.mjs after
```

Publication reuses `mui-wo-models/publish.py`, `publish_tiles.py`, `repair_arrivals.py` and `build_regional.py`. Run this regional supplement after broader regional generation when rebuilding; it restores the five additional source-backed places reproducibly. The original generic source buildings, IDs, heights and roof triangles remain; absent base estimates and existing illustrative foundation/audit metadata follow the established policy.
