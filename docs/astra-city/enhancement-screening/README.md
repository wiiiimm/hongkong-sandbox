# Skip-first enhancement planning — 10 September 2026

Executor: Codex root. Implements the user's goal to avoid changing buildings that
are already sufficient. No building geometry, elevations, source assets or
architectural acceptance records were changed. No Lantau reference maps were used.

The pinned modelling Neon branch now has the additive
`astra_modelling.enhancement_screening_events` table and lookup index. Decisions
are append-only through the script, with current input/evidence hashes, source
reservation fencing, retry IDs and retained history. The existing review ledger
is separate. The portable skill requires this pass before enhancement work and
makes light effort the default, with specific exceptions rather than blanket
high-effort processing.

The planner produces skip/enhance/assess partitions. Accepted good-to-go decisions
can skip unchanged buildings without generating models. No AI calls occur during
planning. New visual adequacy is not inferred from a clean diagnostic or a low
triangle count; until a calibrated rule exists, a new good-to-go decision requires
evidenced human/agent assessment. Full-city automatic visual screening is not
claimed by this implementation.

Initial authoritative plan: 346,108 source forms, 280 existing verified forms
skipped, zero new enhancements queued, 345,828 unassessed. No fabricated good-to-go
records were seeded. See `initial-plan.json`. All four public categories sum to the
total; the ready count includes enhanced plus good to go. A current rework decision
overrides historical enhancement credit. Source forms are not whole buildings.

## Verification

- Nine Node tests: counts, deduplication, stale hashes/policies, current rework,
  changed geometry/context, empty data and invalid totals.
- Four Python tests including a live Neon rollback-only test: evidence/current
  input checks, planner partition, retained revisions, idempotent retry and
  missing-ownership rejection. No fixture decisions remain in Neon.
- Local Vercel preview build passes with the unchanged explicit output directory.
- `browser.json`: actual production dialog HTML/CSS/module at 1280, 390 and320px;
  no horizontal overflow, accessible meters, keyboard dismissal; missing, stale,
  empty, mixed and invalid statistics handled. The chart-focused test excludes
  unrelated 3D startup. PNG dimensions are those exact viewport widths.
- `live-dialog.png`: separate full city-page smoke check using agent-browser;
  page content and chart rendered, no browser errors reported. Saved desktop and
  narrow chart images visually inspected. The old full-scene test was superseded
  after slow startup; no whole-city rendering/performance regression claim.

Commands, input invalidation limits and recovery are in
`source-scripts/city/enhancement-screening/README.md`. Global terrain changes
currently invalidate good-to-go decisions conservatively, even outside a
building's neighbourhood. The existing audit has local dependency keys that can
be adopted in a later policy version.
