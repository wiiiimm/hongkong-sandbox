# Exact source-face lookup acceleration — 5 October 2026

Codex root used AI for reusable workflow/code development only. No architectural
AI review, model generation or source geometry/elevation edits; scripts make zero
external AI calls. This is a fresh continuation of the earlier dependency stage,
not a repeated installer or a new acceptance decision.

`source-face-query.mjs` builds one conservative triangle index per immutable loaded
source, then uses the same exact Three.js triangle distance test as the previous
full scan. The output retains original face indices, winding, coordinates, normals,
distance and order. The broad phase has tolerance-expanded bounds and a bounded
large-face fallback. No nearby bounding box becomes support proof.

Applied to **1,031 unresolved source samples** across Festival Walk, Parkview 3/11,
Beverly Hill A and five Vision City towers supporting the held Citywalk import.
All 1,031 samples have original source-face coverage. Complete face-query results
equal the previous method for every sample. This locates the source evidence; it
does not resolve missing/too-high support or buried-face/terrain holds.

Local CPU lookup benchmark, including index construction:

| Source group | Samples | Full scan | Indexed lookup |
| --- | ---: | ---: | ---: |
| Festival Walk upper | 619 | 4,459ms | 97.6ms |
| Parkview Block 3 | 70 | 604.7ms | 63.0ms |
| Parkview Block 11 | 30 | 119.8ms | 28.4ms |
| Beverly Hill Block A | 18 | 123.8ms | 34.4ms |
| Five Vision City towers | 294 | 756.6ms | 77.8ms |
| Total | 1,031 | 6,064ms | 301.2ms |

About **20.1× faster for this specific lookup**. Full scans were measured once per
source; indexed warm queries three times with median query time plus index build.
This excludes asset decoding, support indexing, terrain checks, publication and
browser work. It is not whole-pipeline throughput or viewer FPS. The preceding
wall-check trial showed no aggregate speed gain and is recorded separately.

29 focused tests pass: 23 Node source/index/support checks and six Python dependency
checks. `source-face-checks.json.gz` retains full per-sample source evidence,
separate phase timings and hashes. `support-inputs.json` from the prior stage pins
original assets/current forms; ignored acquisition payloads remain local-only.

`neon-sync.json` confirms complete fenced result readback. All reservations were
released by the supervised wrapper. No viewer or acceptance state changes. Pilot:
one Installed / nine Held technical, zero In process/Held-AI/Held-human. Wider XL:
39 Installed / 313 Held; **zero new installations this continuation**.

Use the index once per loaded source in subsequent source/component probes; do
not spend time repeating the slow baseline for every model. Freeze code/input
hashes and recheck equivalence when the algorithm changes. Run dependency metadata
preflight before expensive terrain/browser stages, and continue independent forms
when an assembly remains held. Existing terrain and guarded publication gates stay.

No human decision or need for AI modelling is established. Citywalk still needs an
authoritative resolution of its exact native interfaces, not a larger contact cap.
Other source/context holds retain their saved next steps in the final `result.json`.
