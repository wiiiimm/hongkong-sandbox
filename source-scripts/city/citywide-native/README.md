# Territory-wide mechanical native preparation (HKS-222)

This pipeline exhausts the indexed government building glTF/bin source without an AI call per model. It does not publish models, approve architecture, or change terrain elevations. Native HKPD geometry stays at 1× scale.

## Resume on another machine

1. Check out the Astra feature branch at the recorded pipeline commit. Restore the HKS-221 source-directory checkpoint and retained government footprint input using the existing Hong Kong model-improvement skill. Pull private environment configuration; never commit it.
2. Install the existing Python modelling dependencies and Node. Use the project's pinned `.env.modelling` Neon branch; R2 credentials point to `hk-sandbox-assets`, with working objects under `astra-modelling/`. Set `CITYWIDE_NODE` only if Node is not on PATH.
3. Run `python source-scripts/city/citywide-native/prepare.py` to partition source records against the current viewer identities. This is deterministic and rebuildable.
4. Run `python source-scripts/city/citywide-native/runner.py --batch territory-native --workers 6 --env-file /absolute/path/to/private.env`. Optional `--sheets 10-SW-17A,10-SW-17B` selects a trial. `--report-only` reads shared completion for the same frozen inputs.

Workers claim expiring, fenced Neon jobs. The same frozen input is reused across machines and batch names. No two owners can accept the same job; stale workers cannot finish after ownership changes. A code, source, footprint or terrain change creates a new stage identity. Frozen inputs changing during a run cause failure rather than mixed-version acceptance.

Each sheet retains original unmodified source members, exact directory and official matching inputs, packed building assets, native terrain geometry without photographs, per-model outcomes and placement diagnostics. The bundle is uploaded to R2 and fully read back for SHA/size verification before its result is committed to Neon. Only that attempt's temporary folder is deleted after shared acceptance. Prior source bundles can supply original members when processing code changes; the current source directory still validates member CRC and sizes.

The runner limits workers to eight and stops below 8 GiB free disk. Download ranges are grouped, ETag-pinned and byte-bounded; dependencies and malformed sources receive explicit treatment. Three failures per invocation leave an explicit failed job for investigation. Do not call these failures completed modelling or silently skip them.

## What completion means

Every indexed source model must have an accounted outcome, and all retryable mechanical failures must be investigated. `packed-needs-placement-review` means mechanically compatible geometry, not installed or visually accepted. `source-match-held` retains usable geometry for identity/assembly review. Unsupported-source and failed outcomes require diagnosis before deciding whether any remaining work actually needs modelling judgement.

Neon holds compact searchable outcomes and content-addressed R2 references. Large original and derived geometry stays in R2. Local run receipts are disposable copies; retain a small final summary and the immutable run ID in the repository and Linear. Original sources absent from the government index cannot be created by this pipeline.

See `store-readme.md` and `converter-readme.md` for contracts, caveats and validation. Do not confuse building model parts with individual landmarks or completed regions.
