# HKS-214 — named-landmark completion and existing native models

This audit joins the 213-name registry, source identity decisions, the pinned 529-part review inventory, a read-only Neon snapshot, and the actual viewer manifest/asset bytes. It keeps named landmarks, native components, supporting buildings, camera visibility and production deployment separate.

`report.json` provides deterministic per-landmark membership, installed/verified counts and concrete routing. `landmarks.md` is its compact index. A landmark with every currently known part installed still needs proof that the component membership is complete and the assembled architecture is correct. The current records contain no formal whole-landmark closure approval; this is an evidence gap, not a claim that no landmark looks good.

The audit found an inherited review gap: 133 parts were already detailed before the new candidate pass, so they did not have exact source hashes in the new review ledger. They comprise 130 compressed native assets and three embedded Mui Wo geometry records. Of the compressed assets, 38 have a previous placement-review flag and 92 need review evidence. The three embedded records also need reconciliation. They are already present in the viewer: reacquiring or republishing them would not add 133 new models.

`existing-133-source-supplement.json` is ready for a new versioned ledger snapshot. Compressed models use their exact file SHA256. Embedded records use canonical sorted `modelGeometry` JSON SHA256, retaining original source hashes separately; a whole tile hash is never presented as an individual model hash. The existing ledger and old 459-part snapshot are not modified by this script.

Eight OSM glass components around The Center remain explicitly routed for overlap/identity resolution. They are excluded from the government-part denominator but are not silently removed. Nineteen named entries still lack resolved members, including three interior venues that require host-building mapping. The identity report's existing alias evidence and weak candidates are retained so later work does not repeat acquisition or invent identities.

The first follow-up batch is twelve existing parts for One/Two IFC, Bank of China Tower, HSBC, Central Plaza, The Center and Cheung Kong Centre. `first12_support.mjs` reuses the established triangle-support method; `first12_surfaces.mjs` measures all source surfaces rather than interpreting triangle count as visible area. `first12_native.py` compares hidden geometry with original native terrain without extrapolating missing coverage. `first12_browser.mjs` captures normal desktop/mobile scenes and uses actual visibility rays for crowded small components. Review results remain separate from the inventory audit.

Run on a restored working cache:

```sh
python source-scripts/city/landmark-completion-audit/audit.py --refresh-neon
# Reproduce the same audit from its frozen read-only Neon response:
python source-scripts/city/landmark-completion-audit/audit.py
node source-scripts/city/landmark-completion-audit/first12_support.mjs
node source-scripts/city/landmark-completion-audit/first12_surfaces.mjs
python source-scripts/city/landmark-completion-audit/first12_native.py
node source-scripts/city/landmark-completion-audit/first12_browser.mjs
```

Use the project modelling Python environment with its pinned native geometry dependencies. Acquire live source reservations before performing or recording new model reviews. Runtime integration can advance independently, so refresh deliberately and retain the capture timestamp/input hashes when reporting counts. No runtime geometry, source archive, database or production asset is changed by the audit.
