# Actual HTTP/IP progress verification

Produced by Codex on 10 October 2026 for HKS-203. This checks the current progress display over `http://100.89.99.102:4176/city.html`, with the real progress module, manifest and statistics. The app entry is replaced only by the minimal progress harness; this is not a whole-map rendering test.

All four cases pass: available statistics at desktop1280/mobile390 widths, stale statistics and a failed503 statistics request. The two available screenshots were independently inspected. Total346108 source forms, enhanced4476 and matched-government4459 match the current manifest-bound receipt. There are no page errors or horizontal overflows; this nonsecure IP origin has no SubtleCrypto. Stale/missing data stays visibly unavailable rather than reporting a stale success.

The previous attempt in `building-progress-glorious-http-20261010` is preserved: it failed because no server listened on4176. A Python HTTP server bound to0.0.0.0:4176 restored reachability; the actual IP returned200 before this retry. No product code or government geometry was changed. No historical map reference was used.
