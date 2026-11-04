# Citywalk receipt recovery v4: exact full external terminal lineage

Original terminal audit 08db0a8e includes fullExternalLogLineage separately from actualTerminalEvidenceRefs. V2 recovery failed when the repository-only freezer received the /tmp path; v3 correctly rejected that path because its allowlist omitted this separately declared field. Both terminal attempts exited 1 and released their canonical leases. Producers, numerical outputs, original audits and v1–v3 code remain unchanged.

This isolated v4 adds only the terminal audit's explicit fullExternalLogLineage path/hash to the v3 archive allowlist, after requiring notTrimmed, equal external/closedCopy hashes, exact closed-copy reference, and complete byte equality. All source/manifest/PID/current/lease/pin/end fences and the original canonical freezer remain unchanged. Seven adverse archival tests already passed; the same immutable helper is reused. No hash-bound source or terminal reference is discarded or silently rewritten.

No numerical replay, geometry changes, acceptance waiver, optimisation or installation credit. A fresh v4 context/local directory is used.
