# Bounded Sol evidence review — 2 October 2026

Codex root completed one user-authorised review batch of ten held source forms,
using the requested GPT-6.1 Sol / High session setting. Work interprets cached
identity, source component and terrain evidence and develops reusable scripts.
No AI geometry generation/remodelling, source geometry/elevation edits, model
installation or acceptance waiver occurred. Attributable token counters and
runtime model telemetry were unavailable; no token total is inferred. The local
scripts themselves make no AI API calls; this is not a zero-token session claim.

All ten are **Held for unknown technical state**, with exact next compute steps
in `review.json`. There are zero in process, Held-AI or Held-human at this review
checkpoint. No need for AI remodelling or a human decision is established. This
completes evidence review, not installation. The wider 352-form XL selection
remains 38 Installed / 314 Held; runtime assets and progress are unchanged.

| Source | Remaining technical work |
| --- | --- |
| Festival Walk podium 91827 | Resolve remaining runtime terrain-intersection exception; joint foundation/neighbours now pass |
| Festival Walk upper component 104302 | Classify failed support rim regions, then complete pair acceptance |
| Parkview Block 3 | Resolve embedded/unsupported rim regions against the exact installed podium and current terrain |
| Parkview Block 11 | Resolve rim regions and four buried upward faces under neighbour-preserving terrain |
| Beverly Hill A | Resolve exact supporting podium burial and incomplete contact |
| China Merchants East 264206 | Investigate original podium components and nested terrain; label is not the tower component |
| Kowloon Park Administration | Resolve four intersecting forms and original base burial |
| Yoho Mall II | Resolve two buried faces and podium membership without removing residential towers |
| Citywalk | Resolve ten buried upward faces while preserving installed Citywalk 2 and Vision City towers |
| Ocean Pride Tower 2 | Recover/prove exact Tsuen Wan West podium 175935; nearby Citywalk is not a substitute |

## Reusable improvements

`support-contact.mjs` samples unique lowest-band vertices plus low-rim edge
interiors at <=1 m spacing against the highest exact vertically intersected
support triangle. It avoids treating nearby side walls or a count of contact
vertices as support proof. Six regression tests cover holes, edge interiors,
slopes/negative coordinates, walls, overlapping higher surfaces and preservation
of original buffers. Passing/failing samples remain conservative diagnostics:
overhangs and embedded components require context; the module grants no credit.

Four original pairs were measured. Contacts/samples: Festival Walk 605/1,224,
Parkview 3 74/144, Parkview 11 101/131, Beverly Hill A 116/134. Missing vertical
support samples: 212, 16, 13 and seven respectively. Exact hashes, gap ranges and
failed positions are preserved in `support-contact.json`. This supersedes neither
existing acceptance policies nor source architectural evidence.

`PREPARE_MULTIPLE` explicitly permits joint diagnostic preparation only. Four
unit checks show that default preparation rejects multiple components and the
publication path remains single-form, even when the option is enabled. The
Festival Walk pair now shares the candidate set, eliminating the false fallback
neighbour hold. Fresh joint checks cover 18,484 + 16,522 source faces with no fully
buried faces and all 91 surrounding forms pass. Both load and fit mobile budgets;
remaining runtime/source-contact concerns still block publication. Full evidence
is adjacent in `../festival-pair-rescue-diagnostic-20261002/`.

## Neon and resumption

Completed job `4b297779a1528be6dc5917dbf7a6a7c3071fd47c44c74d25d2146aef3603b6f2`
contains every review result, frozen evidence references, model settings and
next action. Exact readback and an idempotent read-only retry passed. Source/job
writes were fenced, and the ten-form reservation was released. `neon-sync.json`
is the receipt. Existing review snapshot 3618dd30ef538e40 also records the Citywalk
held review with effort metadata and stable retry ID. The other nine are not
members of that preflight snapshot and remain in the completed import job;
`ledger-sync.json` explicitly records this without creating artificial membership.

All ten local original source assets match the frozen SHA-256s; see
`source-integrity.json`. Supplementary current diagnostics are not installed assets.
Prior reconciliation/history is retained; do not repeat the AI review or reacquire
verified sources. Resume the exact grouped compute action in `review.json`, taking
new source ownership and rechecking current manifest/terrain hashes first.

Commands from the Astra checkout, with its documented Python environment:

```sh
python source-scripts/city/government-import/sol-pilot-20261002.py sync
node --test source-scripts/city/government-import/support-contact.test.mjs
python -m unittest discover -s source-scripts/city/government-import -p test_joint_diagnostic.py
```

The first command reuses/verifies the completed job; it does not repeat the review.
Rerunning preparation would require live source ownership. Local caches are not
new R2 backups. No browser/publication acceptance was run for held geometry.
