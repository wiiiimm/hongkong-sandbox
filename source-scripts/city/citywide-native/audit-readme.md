# HKS-222 read-only result audit

```sh
python source-scripts/city/citywide-native/audit_run.py \
  --run-id RUN_ID \
  --output source-scripts/city/citywide-native/local/audits/RUN_ID
```

The audit opens a **read-only, repeatable-read** Neon transaction. It streams accepted sheet results through a bounded server cursor, preserving a consistent partial snapshot while the workers continue. It never changes jobs, candidates, model reviews, source geometry, leases, terrain or the viewer. The script is separate from the active converter's fingerprint.

Outputs:

- `summary.json`: indexed versus accepted model/sheet counts, original outcome states, grouped error messages, terrain diagnostics, cross-sheet UID collisions, full-source reference checks, and evidence hashes.
- `exceptions.jsonl`: source/model-level exception details and collisions. Categories distinguish confirmed source corruption, unknown conversion failures, unsupported converter capabilities, source identity review, sampled terrain intersections and elevated support checks. A model can have multiple diagnostic rows; exception row counts are not unique model counts.

For a completed mechanical audit, verify all of these:

- `runId` matches the intended run and `status` is `complete-mechanical-audit`.
- `acceptedSheets == expectedSheets`.
- `modelOutcomeRows == indexedModels` and `indexedModelsWithoutAcceptedOutcomes == 0`.
- `allAcceptedIndexedModelsAccounted == true`, `countMismatches == 0`.
- `rawFootprintAudit.matchesExpectedSourceSHA256 == true`.
- `unknownMechanicalFailures == 0` before claiming mechanical blockers exhausted.
- `exceptionLedgerSHA256` matches the retained exception ledger.

A complete **audit** may still report failed source files, identity holds, duplicate candidate UIDs or placement questions. `confirmedSourceCorruptModels` is separate from `unknownMechanicalFailures`; the original `failed` states remain unchanged. These are not approvals or whole-region readiness.

The optional known-defect evidence file is `docs/astra-city/citywide-native/source-defect-audit.json`. A corruption classification applies only when the sheet/model and immutable native-stage source hash match. The audit captures this evidence before querying and records `sourceDefectEvidenceSHA256`; later additions cannot retroactively alter the audit's classifications. Without matching evidence, a conversion failure stays unclassified. Source-blocked terrain checks are not counted again as an unrelated sampler defect.

For absent selected footprint references, the audit streams every record in the retained raw government GeoJSON. It checks exact GeoRefNo, numeric/whitespace/leading-zero normalisation and BuildingCSUID prefix. Normalisation is diagnostic only; no identity is rewritten. The raw gzip SHA is compared with a verified frozen official selection. A mismatching raw source produces `raw-source-mismatch-audit`, not a valid completion claim.

Cross-sheet candidate UID collisions remain unchanged and are reported as either identical native model+asset duplicates or differing source alternatives. The caller must deduplicate/review before publication. Model heights are never changed to address a collision or a sampled terrain discrepancy.

Tests use small fixtures and require no database/network writes:

```sh
python source-scripts/city/citywide-native/test_audit_run.py
```

Before a final audit, classify failed native JSON files mechanically with the separate bounded verifier:

```sh
python source-scripts/city/citywide-native/verify_source_defects.py --run-id RUN_ID
```

This command reuses matching frozen corruption proofs and conditionally fetches only newly failed JSON members. ETag, Content-Range, original ZIP CRC and lengths must agree. Only entirely NUL-filled payloads ending in CRLF are classified; every other source remains explicit and unclassified. It updates the evidence JSON, never converter/runtime/Neon state. Run it before the final audit so the audit records the resulting evidence SHA.

## Same-source terrain repair overlay

```sh
python source-scripts/city/citywide-native/audit_run.py \
  --run-id ORIGINAL_RUN_ID \
  --terrain-repair-run REPAIR_RUN_ID \
  --output source-scripts/city/citywide-native/local/audits/final
```

Only a failed original terrain entry with the exact `originalCacheKey`, native `sourceSha256` and `sourceEntry` can use an overlay. The repair stage must account for every selected entry and provide source hashes plus geometry proof for `prepared-geometry-only` or `source-empty`. No source/candidate is changed by this audit.

`terrainStates` and `terrainErrorPatterns` retain the original run. `effectiveTerrainStates` and `effectiveTerrainErrorPatterns` show the source-bound repairs. `terrainRepair` records the repair run ID, expected/accepted/pending sheets, selected entries, applied original failures, unused successful entries and validation errors. For a final checkpoint additionally require:

- `terrainRepair.pendingSheets == 0`.
- `terrainRepair.validationErrors` is empty.
- `terrainRepair.unusedPreparedEntries == 0`.
- `unknownMechanicalFailures == 0` after overlays.

Archive both original and repair ledgers. A verified empty source scene is accounted as `source-empty`, never invented geometry or a silently discarded original failure.
