# Mui Wo held-source completion · 2026-09-15

This pass completed all local scripted work for the 16 government sources held by the first Mui Wo import. It used the pinned Lands Department glTF assets and source TINs already recorded by `government-mui-wo-23-20260914`; it made no AI calls and did not edit, simplify, or regenerate model geometry.

## Outcome

- 13 installed and live-verified.
- 3 held after a complete script pass.
- 0 waiting for AI, human review, or an active process.
- Six small upper-shell sources retain their existing mapped extrusion as lower support.
- Two source assemblies reversibly suppress a second basic form covered by the exact source.

The installed sources passed exact object ID and Building CSUID checks, projected-fit checks, full-face native-terrain checks, source hash and mobile budget checks, and staged/live desktop/mobile day/night browser checks. Browser checks also cover picking, collision, fallback after a failed download, and retry.

## Remaining holds

| UID | Source model | Reason |
| --- | --- | --- |
| `landsd/172460:0` | `B178611539001062G0` | The source lower edge remains about 4.94 m above the mapped form and no government support component exists in the source sheet. |
| `landsd/201705:0` | `B179951563401062G0` | 23.13% of source surface area is fully buried and five faces lack complete native-terrain coverage at the source-sheet edge. |
| `landsd/208036:0` | `B171281503901062G0` | The complete source shell is below native terrain, including two upward faces. |

These are terminal local-compute holds, not AI queues. Their current basic forms remain visible. Any future placement correction or source substitution should start from `script-pass-results.json.gz` and preserve the pinned source hashes.

## Provenance

- Provider: Lands Department, HKSAR.
- Dataset: `landsd_rcd_1742809441342_98380`.
- CRS: EPSG:2326.
- Vertical datum: Hong Kong Principal Datum.
- First-pass source selection: `docs/astra-city/government-import/government-mui-wo-23-20260914/check-selection.json.gz`.
- Final Neon snapshot: `665c494347e868ec`.
- Neon terminal job and exact human counts are recorded in `terminal-summary.json`.
