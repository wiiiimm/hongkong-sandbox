# HKS-213 · identity-v2-extra

Executor: Codex acquisition agent. Pinned input: `source-scripts/city/landmark-identity/extra-targets-v2.json`, SHA-256 `91079674f8fb8058f6a8bf5bd65ffc329d6fb4b8818e41f129994f54ad68538f`. Source identities remain unapproved proposals; native source acquisition does not approve landmark membership.

- 47 exact-ID targets across 13 sheets; all sheets completed and verified.
- 44 native models staged; 42 exact-CSUID matches; 2 conservative matching holds.
- 3 checked source absences; 0 transfer deferrals.
- 88 native members verified with complete-directory checks, source CRC/length, cache/staged SHA-256 and unchanged 1× HKPD coordinates.
- 7,723,127 bytes including official metadata; 8 directories and 8 native members reused. Four workers shared a durable 500 MB cap; no monolithic source archive downloads.
- Repeat acquisition transferred 0 bytes and added no requests.

Matching holds: CHAMPION TOWER (`landsd/233905:0`), LANGHAM PLACE HOTEL (`landsd/81387:0`).

`report.json` preserves per-target UID/outcome/sheetsChecked evidence. `verification.json` verifies retained payloads; logs preserve initial acquisition and zero-transfer resume. No registry, shared SQLite, runtime terrain, geometry or publication changes. Any remaining identity interpretation or architectural/terrain correction requires a separate review.
