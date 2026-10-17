# HKS-214: four named towers and Elements native support

Astra, 9 September 2026. This is a prepared, source-reviewed package. **It is not installed in the viewer.** The user requested a pause after this pass; resume guarded integration on the next machine after restoring the R2 working snapshot.

## Scope and evidence

Five exact government components: Cullinan I `landsd/203728:0`, Cullinan II `landsd/203724:0`, China Resources Building `landsd/37369:0`, The Oakhill `landsd/323059:0`, and Elements `landsd/273061:0`. Existing Harbourside Tower 1 `landsd/204153:0` needs a metadata-only dependency migration in the same transaction. All six source geometries remain unchanged, using native HKPD heights at 1× vertical scale.

The original conservative matcher remains unchanged. Exact GeoRefNo identity plus tower-only geometry resolves the Cullinan lower-podium centroid mismatch. Native source height envelopes and surveyed footprint height attributes are retained independently; this is not a height correction or clipping operation.

- Cullinan I: 499/499 low-rim contacts with native Elements, maximum 0.134 m.
- Cullinan II: 566/566 contacts, maximum 0.146 m.
- China Resources: 42/42 contacts with surveyed podium `151601`, maximum 0.401 m; retain that fallback support.
- Oakhill: 55/57 contacts with surveyed podium `161320` within 0.5 m. The two projecting vertices (0.572/1.790 m) share a 338-vertex native connected component with all 55 supported anchors. Source-connected overhang evidence does not claim structural engineering verification.
- Existing Harbourside: 41/41 native Elements contacts, maximum 0.024 m. Its old fallback-only support requirement must migrate atomically.

Elements requires the accompanying 1 m native TIN patch. The previous terrain buried 2,923 source triangles, including 576 upward-facing faces. The patch leaves **zero wholly buried triangles across the five components**, zero boundary error and no water-mask changes. Native TIN covers 220,473/236,181 grid nodes; uncovered outer nodes retain the original parent height. Every actual low-rim/burial diagnostic point has native coverage. The patch ends at x=392.5, adjacent to the existing station patch, whose bytes remain unchanged.

## Browser qualification

`browser-terrain/report.json` retains 12 passing desktop views followed by the original whole-mall mobile framing failure. That camera fitted an unnecessarily large mall/tower bounding sphere outside the existing 1,800 m mobile detail range. The failure is preserved, not erased or counted as passing. No app range or memory budget was raised.

`browser-mobile-targeted/report.json` tests nearby tower framing, with native Elements still required for both Cullinans. It records day/night activation, picking, camera clearance, viewport fit and no horizontal UI overflow. The final north-east Cullinan view reveals the native roof and upper tower; surrounding Sorrento blocks still occlude portions of the lower levels. Desktop north-east views give broader assembly context. These are staged private source/terrain routes in the normal full-city scene, **not installed integration evidence**. No surrounding building meshes are hidden. Scene labels/minimap are hidden for inspection captures.

## Cross-device resume

1. Pull the feature branch and restore the complete R2 working snapshot, including `source-scripts/city/identity-four-native/`, the source acquisition batch `landmark-acquisition/batches/identity-four-native-20260909/`, both source terrain prerequisite batches referenced in `terrain_audit.py`, and the local read-only inventory cache. Git contains scripts, catalogues and evidence; ignored native source caches, packed GLBs and the terrain patch must come from R2.
2. Pull the correct Vercel environment and use the pinned Neon `astra-modelling` branch. Do not reuse old `/tmp` lease receipts. Claim the six UIDs in the three reservation groups below; failed normal claims mean another agent owns work, not permission to force takeover.
3. Check the current immutable Neon source snapshot and unchanged source SHA values against `supplemental-source-inventory.json`. At checkpoint the snapshot is `7d47a5f3c7362e9b`; query the current pointer instead of assuming it remains current.
4. Run `prepare_dependencies.py` to refresh the guarded Harbourside catalogue hash if the current live catalogue has unrelated changes; inspect the exact old dependency. Run `prepare_approved.py`. It verifies source bytes, evidence hashes, terrain checks and current reservations before recreating `publication-plan.json`.
5. Dry-run the guarded publisher command below. Only then apply integration and run installed-scene streaming, ground/collision, picking, fallback/Retry and mobile verification. Record `installed-verified` only after that evidence exists. This package alone approves five source parts, not complete landmarks or regions.

Commands from the repository root, with the restored Python environment:

```sh
python source-scripts/city/shared-modelling/reservations.py claim --owner identity-four-resume --batch HKS-214-four-tower-review --resource building:landsd/203724:0 --resource building:landsd/203728:0 --resource building:landsd/37369:0 --resource building:landsd/323059:0 --ttl 1800 --lease-file /tmp/astra-identity-four-review-lease.json
python source-scripts/city/shared-modelling/reservations.py claim --owner identity-four-resume --batch HKS-214-Elements-support --resource building:landsd/273061:0 --ttl 1800 --lease-file /tmp/astra-identity-four-elements-lease.json
python source-scripts/city/shared-modelling/reservations.py claim --owner identity-four-resume --batch HKS-214-Elements-dependent-migration --resource building:landsd/204153:0 --ttl 1800 --lease-file /tmp/astra-identity-four-dependent-lease.json
python source-scripts/city/identity-four-native/prepare_dependencies.py
python source-scripts/city/identity-four-native/prepare_approved.py
python source-scripts/city/model-integration-20260909/publish.py source-scripts/city/identity-four-native/publication-plan.json --receipt /tmp/astra-identity-four-review-lease.json --receipt /tmp/astra-identity-four-elements-lease.json --receipt /tmp/astra-identity-four-dependent-lease.json --phase identity-four-resume
```

Source rebuilding is optional when restored SHA-pinned assets are present. The reusable chain is `acquire_elements.py` → `prepare_review.py` → `support.mjs` / `oakhill_connectivity.py` / `terrain_audit.py` → `terrain_patch.py` → `surfaces.mjs` → `prepare_dependencies.py` → browser scripts → `prepare_approved.py`. Regenerating contact evidence requires regenerating the dependency sidecar. Run scripts under live ownership and refresh leases at checkpoints.

Photographic textures, facade paint and interiors remain outside this native geometry pass. No production publication is claimed. Whampoa is a separate already-installed two-part source request under HKS-219.
