# Astra installed-model follow-up inventory — 13 October 2026

Executor: Codex. Read-only comparison against fetched Astra commit `7f678c48a2f2fdbf11cbdcb6835b6fda3f8006fd`, using the complete 12 October compression snapshot as the baseline.

The current committed manifest links 219 catalogues containing 6,650 unique installed UIDs. All previous 6,649 source revisions are unchanged; zero removals and zero changed source/metadata revisions. There is one additional installed source:

| UID | Label | Gzip source bytes | Triangles |
| --- | --- | ---: | ---: |
| landsd/79099:0 | Nam Fung Court | 147,127 | 13,061 |

The source hash was independently verified from committed Git bytes: `7ca5a8202c6903f0e765d4586bcbd7597a009b8a997528431c4ed3e2963362fb`. Exact revision: `b5fa863e9918579e36e6c4d93ad559ccd2db3ccd5675840b5cd40f86240bd4d9`. Its catalogue is `3d-viewer/city/data/official-models/government-xl-nam-fung79099-unchanged-private-stage-v1-20261013/catalogue.json` and is linked from the current manifest; its filename alone is not installation evidence.

A read-only query against the pinned Neon modelling connection found no optimisation source/variant rows for this UID. It therefore needs all four candidates: lossless/original, high, balanced and lightweight. No follow-up compression jobs were launched and no database records changed during this check.

See [inventory.json](inventory.json) for exact source metadata, manifest hash, all comparison counts and Neon coverage. Review flags do not filter compression selection (`installed-v1`). Pending or unlinked staged sources are outside this installed comparison. Original government source provenance is retained in the inventory; no historical-map reference images used.

The compression branch's earlier delivery was already committed and pushed. This read-only follow-up does not merge the newer Astra parent or alter the live viewer. Synchronise the parent and freeze a new immutable installed snapshot before executing the follow-up batch; do not edit the old 12 October receipts.
