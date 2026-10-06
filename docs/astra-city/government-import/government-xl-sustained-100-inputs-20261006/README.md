# Sustained XL continuation inputs — 6 October 2026

Codex selected 100 explicit XL source forms from the 352-source inventory,
excluding current installations, review records and completed single-source
continuations. These are source forms, not a new count of physical buildings.

The source freeze rechecks exact original payload hashes, current building tiles,
full source projections and neighbouring form hashes under a renewable fenced
reservation. Fifteen sources pass the existing identity/projection preflight;
85 retain footprint-fit blockers. Failed preflight rows remain in the batch.
There is no source geometry edit, AI modelling, skip credit or publication.
Ignored original payloads and derived geometry are local caches; the tracked
inputs and receipts do not make those payloads portable.

Central Pier No. 8 (`landsd/213352:0`) is excluded because its pinned original
payload is absent locally and a previous bounded restore already failed. That
receipt is preserved; no unchanged acquisition is repeated and no global source
absence is inferred. Evangel College (`landsd/91306:0`) replaces it with verified
local original bytes. See `explicit-uids.json` for the exact selection.

Run each primary independently, then use existing guarded follow-up routes:

```sh
/tmp/astra-city-venv/bin/python source-scripts/city/government-import/xl-explicit-continuation.py \
  --base docs/astra-city/government-import/government-xl-sustained-100-inputs-20261006 \
  --batch government-xl-sustained-100-20261006
/tmp/astra-city-venv/bin/python source-scripts/city/government-import/xl-explicit-followthrough.py \
  --base docs/astra-city/government-import/government-xl-sustained-100-inputs-20261006 \
  --primary docs/astra-city/government-import/government-xl-sustained-100-20261006 \
  --batch government-xl-sustained-followthrough-20261006
/tmp/astra-city-venv/bin/python source-scripts/city/government-import/xl-explicit-support-continuation.py \
  --base docs/astra-city/government-import/government-xl-sustained-100-inputs-20261006 \
  --pairs-file docs/astra-city/government-import/government-xl-sustained-100-inputs-20261006/support-pairs.json \
  --batch government-xl-sustained-supports-20261006
```

Every child holds its own source scope and records exact Neon results. Child
command failures are retained separately from technical holds; independent
sources continue. Completed stages are immutable and must not be rerun.
Support candidates are spatial diagnostics only: exact original source matching,
full support interfaces and all acceptance gates remain necessary.

These commands do not publish. Installation requires current evidence plus
staged/live browser checks and the guarded publisher/ledger. The input freeze is
complete; consult child results and the final checkpoint for processing progress.
