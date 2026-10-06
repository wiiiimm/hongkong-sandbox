# Overlapping rendered terrain and recovery metadata fix

Codex, 6 October 2026, HKS-203. The sampler previously selected the first containing terrain child even when a higher sibling was also drawn. It now queries the pointwise highest child surface, retaining nested parent-cell exclusion and the parent water-bed comparison. No model or terrain data bytes, elevations, placement, source identity limits or acceptance limits change.

Seven renderer-based tests pass, including sibling order reversal, crossing slopes and nested parent exclusion. Acceptance and diagnostic input hashes now include the imported rendered-height helper. The published-original recovery writer now supplies required landmarkIds for sources absent from the current inventory. Python compilation passes.

Prior failed recovery receipts remain untouched. Fresh physical and browser checks are required under these code hashes before current-review recovery earns completion credit. Current verified XL status remains 24 new / 68 installed / 284 not installed; the 100-install goal continues. Zero external modelling AI calls. No historical Lantau imagery used.
