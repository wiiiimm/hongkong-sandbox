# HKS-213 / HKS-214 · Native terrain prerequisites

Executor: Codex acquisition agent. The pinned HKS-214 terrain-input snapshot required 26 missing source sheets. All 26 now have verified native glTF/bin caches and geometry-only staged manifests; no source deferrals remain for this snapshot.

The run transferred **140,499,783 bytes** through 78 bounded requests (26 HEAD, 52 member ranges), using four sheet workers and one durable 500 MB byte envelope. All 26 complete directories were reused from the pinned source caches and checked against current source ETags. The exact 52 native members pass source CRC/length and SHA-256 checks. Original glTF/bin bytes remain unchanged. The existing decoder only omits terrain photograph/material references in derived geometry glTF; native 1× HKPD node transforms and coordinates remain unchanged.

A second run and an independent verification pass both succeeded for 26/26 sheets with **0 additional bytes/requests**. The initial verification routine incorrectly expected the original terrain glTF in derived staging; it was corrected to verify original glTF against the retained native cache and derived glTF against its own SHA-256. `first-run-verifier-diagnostic.json` and `first-run.log` retain that resolved diagnostic; authoritative results are `terrain-report.json` and `terrain-verification.json`.

Compact ZIPs and native members remain local under `source-scripts/city/landmark-acquisition/batches/terrain-prerequisites/sources/<sheet>/`. Standard terrain manifests under the matching `staged/<sheet>/manifest.json` expose source hashes, derived hashes and native bounds for later preflight discovery. Reports use `terrain-` prefixes so they cannot overwrite building acquisition statuses.

The archival whole-Hong Kong 5 m DTM was already present and was not downloaded. No imagery was downloaded; no terrain was applied to the viewer, no placement was approved, and no geometry was reconstructed or published. Later combined inventory may identify additional sheets; those require separate pinned increments rather than silently modifying this snapshot.
