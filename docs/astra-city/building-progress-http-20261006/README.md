# Model progress over HTTP/IP

The progress counter called `crypto.subtle.digest` directly, which is unavailable on the nonsecure `http://100.89.99.102:4176` origin. It now shares the existing SHA-256 WebCrypto/pure-JavaScript fallback used by government asset integrity checks. Manifest matching remains mandatory; source/model integrity limits are unchanged. The model asset hash export remains compatible.

Actual nonsecure-origin browser verification passed at desktop (1280) and mobile (390), with `isSecureContext=false` and no WebCrypto subtle API. The real final data shows 346,108 map source forms, 4,398 enhanced forms and 4,384 of 212,669 matched government sources installed. Stale-manifest and missing-response cases correctly retain unavailable statistics. No page errors or mobile overflow.

This harness isolates the statistics binding on the real city HTML and real manifest/progress data; it does not assert whole-scene model rendering. Separate per-model staged/live acceptance verifies the six new installations. Thirteen hash/progress unit tests passed. Screenshots and result JSON are adjacent.
