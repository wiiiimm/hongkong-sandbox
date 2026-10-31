# Independent government FBX source-format comparison — 9 October 2026

Agent: Codex identity research. Zero AI geometry modelling, source edits, live viewer changes or new installations. AI was used for source interpretation and diagnostic code.

Four original FBX ZIP members were recovered from the current official packages with fresh index metadata, archive ETags, member CRC/size/range records and independent SHA256 pins. All original files remain untouched. This new format does not inherit glTF identity/physical acceptance.

The complete FBX binary double vertex arrays have one exact provider mesh root per file, root-to-world connections, triangular source polygons and authored translation only. Original axes are East/North/Up and `UnitScaleFactor=100` centimetres, equivalent to one metre. Root translations place them at Hong Kong Grid East/North coordinates and HKPD heights consistent with their pinned glTF sources. The diagnostic expresses the same pose in the viewer's fixed frame: x=East−834500, y=HKPD height, z=816500−North. No fitted alignment, extra rotation, scale adjustment or coordinate rounding is used.

Blender 4.5.9 LTS factory-startup import independently inspected complete hierarchy, matrices and all imported objects. Its new C++ importer retains every source triangle and yields the same bounds/projection as raw extraction. The legacy Python importer produces fewer triangle entries; its output is retained as a crosscheck, not selected as the authoritative complete source. No `.blend` file, converted deliverable, edited vertex or replacement live asset was created.

| Official OP structure | Exact original FBX sources | Raw source triangles | Coverage | Maximum extent | Unrelated excess | glTF/FBX projection difference |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| K30/60, 5216458 | B350302046901063C0 + B350352046901063C0 | 22,908 | 94.818965% | 3.411513 m | 0.536054 m² | 0 m² |
| K300/63, 1645937 | B355371858701063C0 + B355371859301063C0 | 13,519 | 94.598802% | 2.407634 m | 1.901111 m² | 0 m² |

Both complete original FBX projections are exactly identical to the previously frozen complete glTF projections. The source-format route supplies no missing boundary areas. K30/60 still fails the unchanged 95% coverage requirement; K300/63 still fails coverage and the 1 m² unrelated-overlap threshold. These are source-version/provider-boundary disagreements, not evidence of corrupt models or permanently impossible buildings. No forms, neighbours, uncovered strips or authored polygons were omitted. `identityAccepted` and `installationApproved` remain false.

Next useful route: independently pinned, positive corrected provider outlines/older boundary lineage or a genuinely changed official source version. Current FBX format conversion is exhausted for these four exact versions; repeating the same glTF/FBX checks will not change their result. A source-backed alternative requires independent proof, not a tolerance waiver.

## Pinned records

- `untouched-current-fbx-sources.json`: exact member paths, original bytes/SHA256, package revisions and glTF lineage.
- `official-package-index.json`: fresh authoritative provider index query and request receipt.
- `raw-fbx-coordinate-proof.json`: original array type, axes/units, authored root translations, complete counts and hashes.
- `complete-source-format-comparison.json.gz`: source-specific original/Blender variants, current complete forms and strict measures.
- Per-pair GeoJSON retains full projection, target, uncovered area, source excess, unrelated neighbours and exact FBX/glTF difference.
- `result.json` and `neon-sync.json`: fenced Neon research receipt, written after evidence freezing and exact readback.

Local original source packages and full Blender/raw inspection arrays are under `source-scripts/city/government-import/local/government-xl-source-format-comparison-20261009/`. Source bytes, derivations, inspection matrices and scripts are individually hash-bound by the Neon receipt. Historical research receipts remain unchanged.

## Primary sources and reproducibility

- [Official Lands Department 3D model package index](https://portal.csdi.gov.hk/server/rest/services/common/landsd_rcd_1742809441342_98380/FeatureServer/0). The exact FBX ZIP URLs/revisions are in the source receipt.
- [Official building and OP relationship tables](https://portal.csdi.gov.hk/server/rest/services/common/landsd_rcd_1637211194312_35158/MapServer). Previous immutable OP research establishes the two structure relationships.
- [Blender 4.5 import/export release notes](https://developer.blender.org/docs/release_notes/4.5/pipeline_assets_io/) and [Blender 4.5 operator API](https://docs.blender.org/api/4.5/bpy.ops.wm.html) document the independent C++ importer.

Run the `source-format-comparison-20261009-acquire.py` script for fresh source acquisition, then Blender with `source-format-comparison-20261009-blender-inspect.py -- legacy` and `-- cpp`, then Blender with `source-format-comparison-20261009-raw-fbx.py`, then the Python `source-format-comparison-20261009-measures.py` diagnostic. Reproduction must use a new stage directory if source revisions or evidence change; existing completed receipts are immutable.
