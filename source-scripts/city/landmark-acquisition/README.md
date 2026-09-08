# HKS-213 · Missing landmark source acquisition

This is a mechanical, exact-ID acquisition/staging pipeline. The original checkpoint covers 115 `cache-absent` source parts in the pinned HKS-211 bulk report; named batches expand it without altering that evidence. It does not identify unknown landmarks, alter the registry or SQLite inventory, approve source placement, change terrain or publish models.

From the Astra worktree root, using the existing source environment:

```sh
# Resume the pinned 152-target identity batch. Completed sheets transfer zero bytes.
/private/tmp/astra-city-venv/bin/python source-scripts/city/landmark-acquisition/acquire.py --batch identity-v1-remaining --workers 4
/private/tmp/astra-city-venv/bin/python source-scripts/city/landmark-acquisition/verify.py --batch identity-v1-remaining
PYTHONDONTWRITEBYTECODE=1 /private/tmp/astra-city-venv/bin/python -m unittest discover -s source-scripts/city/landmark-acquisition -p 'test_*.py' -v

# Pin a NEW approved exact-ID input; choose a distinct batch name for changed IDs.
/private/tmp/astra-city-venv/bin/python source-scripts/city/landmark-acquisition/acquire.py --batch approved-follow-up --targets-source source-scripts/city/landmark-identity/extra-targets-v2.json --budget-mb 500 --workers 4
```

The last command is a template: its input must exist and contain confirmed source identities. Inputs accept the original bulk report, an identity stage summary (`parts` whose state is `not-in-retained-staged-models`), or an explicit `targets` array of UID strings/records. Source identities are checked against the retained inventory through a read-only SQLite connection. The full input is copied and SHA-256 pinned; subsequent input/budget changes are rejected. Do not rerun the original default acquisition just to inspect it: use its committed report and verification, preserving its pinned evidence.

Named batches default to four independent sheet workers, while the original defaults to one. `--workers 1..8` controls concurrency and `--limit-tiles N` bounds an invocation. Requests share one locked ledger; sheets have isolated source/staging folders. JSON writes replace complete files atomically with unique temporary names, allowing progress reports while other workers finish. Run only one acquisition process per batch at a time. Repeating a command skips completed sheets and resumes verified members in unfinished sheets. `--refresh-head` revalidates source ETags; a changed source is held rather than overwriting evidence. A later source revision should use a new batch.

## Transfer boundary and restart safety

The original cumulative budget is **100,000,000 response bytes**. The expanded identity batch records **500,000,000 response bytes**, sufficient for the user-authorised remaining mechanical work. Each batch cap includes official metadata and any uncertain in-flight request reservations. It is not reset on restart. Every request reserves its maximum before dispatch. Failed/interrupted requests keep their full reservation because the exact transfer is uncertain. Confirmed responses replace that reservation with their actual byte count. HTTP HEAD requests read no body. ZIP requests require HTTP 206, the exact requested range, stable ETag, valid local header, member byte count and source CRC. A server ignoring Range is rejected without reading its archive body.

`transfer-ledger.json` is the resumable account. It retains request/range hashes and a whitelist of provenance response headers; cookies and transient session/request headers are omitted. Do not edit the ledger to obtain more allowance. A fresh larger acquisition requires a new authorised batch.

## Reuse and native geometry

The live official Lands Department non-textured model service is retained as `service.json` and its complete paginated EPSG:2326 tile index as `index.json`. Source parts are assigned to all official tiles intersecting their retained government footprint plus a 1 m edge guard. Exact ten-digit GeoRefNo prefixes are used; no name-only identity match is introduced.

Existing source caches are considered first. Reuse requires the same official URL, revision and current ETag. Complete directories are parsed without allocating a whole source archive. Retained compact ZIPs and selected members are verified against SHA-256 and native directory CRC/length. Missing members are fetched as individual local-header/payload byte ranges. No monolithic tile download or imagery extraction is performed.

`mui-wo-models/fetch.py` supplies the established selective ZIP approach; `architecture-batch/acquire_missing.py` supplies the prior exact-ID acquisition/staging pattern. This pass adds persistent per-member recovery, full directory validation, retained-cache reuse, a cumulative reservation ledger and bounded HTTP handling.

Original glTF and binary members remain byte-identical. The existing `prepare_model_sample.stage` decoder writes the staged manifests with the established root translation `[-834500, 0, 816500]`, native 1× HKPD heights and unchanged source node matrices. The source archive checksum stays explicitly unknown: the compact selected cache has its own checksum and is never represented as the full official ZIP.

## Outputs and interpretation

- `batch.json` and `target-input.json` (named batches): immutable input hash and recorded byte envelope.
- `plan.json`: pinned report/index hashes, exact source identities and official sheets.
- `sources/<sheet>/`: source HEAD provenance, complete directory, resumable members, derived compact ZIP, download record and state.
- `staged/<sheet>/manifest.json`: unchanged decoder output and source-model matching results.
- `docs/astra-city/landmark-acquisition/report.json`: each source part classified as acquired/staged, no exact model in all complete checked sheets, or deferred.
- `docs/astra-city/landmark-acquisition/verification.json`: complete-directory, native-member, compact-cache, staged-file and 1× coordinate checks.

Named batch files live under `batches/<batch>/` in both the script and documentation trees. Native caches and staged files remain local and ignored by Git; metadata, ledgers, plans, reports and verification are tracked. Original paths remain unchanged.

“No exact model” is limited to the current official sheets checked for that retained footprint. It is not proof that no government model exists elsewhere. A staged model is not placement acceptance or a complete landmark. Exact CSUID matches remain separate from source availability. Ambiguous identity, native models intersecting terrain, unsupported geometry or reconstructive modelling require a separate, higher-effort review; this mechanical batch does not attempt those fixes.

## Native terrain prerequisites

`terrain.py` accepts the preflight `downloadPrerequisites` inventory, pins its complete-directory/member metadata, and reuses the same reservation ledger, cache checks and selective ranges. Exact member name, native offset, CRC and sizes must agree. It stages through the existing decoder, preserving native geometry while omitting terrain photo references. It never applies terrain to the viewer.

```sh
/private/tmp/astra-city-venv/bin/python source-scripts/city/landmark-acquisition/terrain.py --batch terrain-prerequisites --workers 4
/private/tmp/astra-city-venv/bin/python source-scripts/city/landmark-acquisition/terrain.py --batch terrain-prerequisites --verify-only --workers 4
```

For a new terrain inventory, pass a new `--batch`, `--targets-source <inventory.json>` and recorded `--budget-mb 500`. Terrain evidence is deliberately named `terrain-report.json` / `terrain-verification.json`, distinct from building-source reports. Standard staged terrain manifests and compact source ZIPs are discoverable by preflight. Native glTF hashes refer to the original cache members; the texture-free derived glTF has a separate checksum.
