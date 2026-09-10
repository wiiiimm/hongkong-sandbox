# Model progress and government-source availability

The viewer shows the total displayed source forms, verified enhanced forms, forms
with a prepared government source match, and completion within that source group.
A source form is a model part (for example a tower, podium or wing), not a whole
physical building. Counts stay independent of the camera, streaming and LOD.

## Refresh

Run from the repository root with the existing shared-modelling Python dependencies
and pinned Neon configuration (this machine uses the enhancement-screening venv):

```sh
source-scripts/city/enhancement-screening/.venv/bin/python source-scripts/city/building-progress/export-government.py
source-scripts/city/enhancement-screening/.venv/bin/python source-scripts/city/building-progress/export.py --refresh
node 3d-viewer/scripts/build_progress.mjs
```

The government export reads the frozen native preparation run named by `--run-id`
(default recorded in the script). It captures unique UID/CSUID pairs from successfully
packed, uniquely matched candidates. Held, ambiguous, corrupt and unmatched sources
are excluded. The repeatable-read transaction is read-only; no source review or
acceptance changes. These are CPU/database operations with zero model AI calls.
Refresh when the source inventory changes, rather than querying Neon per visit.

Commit `3d-viewer/scripts/building-progress/government-source-proof.json.gz` and
updated review proof/statistics with a publication. The gzip source proof is a
build input, not an asset fetched by the browser. The static Vercel build runs
`node scripts/build_progress.mjs` within `3d-viewer`, requiring no database,
credentials, Python or files outside that app.

The generator intersects exact UID **and current CSUID** with deployed forms and
excludes suppressed bridge proxies. Government progress is `(enhanced + good to go)
/ matched forms` within that subset. Previously verified enhancements outside the
subset count toward all-map enhancements, not its numerator. No prepared source
counts as completed just because it downloaded. Matches still need identity,
placement/support and runtime checks; some existing detail needs verification
instead of replacement. The older all-city `percent` fields remain for compatibility;
version 3 UI uses `government.ready / government.available`.

An exact manifest digest guards stale map statistics; invalid, missing and zero-scope
statistics have explicit UI states. The source proof capture date and native run ID
are recorded separately from the accepted-review date. To reproduce a past build,
reuse its committed proof without refreshing. See
[latest UI evidence](../../../docs/astra-city/building-progress-government/README.md).
