# Historical skip audit — 12 October 2026

Executor: Codex. No historical-map references were used. All 2,377 originally excluded UIDs have installed catalogue entries and current asset hashes verified against those entries. None was skipped because its asset was missing or its codec failed.

| Original catalogue-only exclusion | Count | Latest installed review with matching source and intact evidence | Pending / held in latest review ledger | No review-ledger entry |
| --- | ---: | ---: | ---: | ---: |
| `placementReviewed=false`, publication/identity fields absent | 2,157 | 61 | 32 pending / 1 held | 2,063 |
| `identityReviewApproved=false`, placement/publication true | 131 | 131 | 0 | 0 |
| `publicationApproved=false`, placement/identity true | 89 | 89 | 0 | 0 |

The original filter required affirmative publication or placement flags and rejected explicit negative identity/publication fields. It did not consult Neon installed-review evidence. This conflated proposed landmark identity with native source-component acceptance for some entries: 101 have explicit `sourceIdentityReviewed=true` plus placement/publication approval despite the identity flag. All 281 latest installed reviews above have matching source bytes and evidence-file SHA-256; those historical reviews do not independently certify current poses/terrain/support. Their records are preserved, including 32 pending and one held result.

**User instruction after this audit:** ignore reviews when selecting compression inputs; every installed asset needs compressed variants. The new explicit `installed-v1` selection policy includes all 6,649 installed UIDs without changing acceptance records. Missing/negative review flags are recorded metadata, not processing exclusions. The historical 2,377 hold list stays immutable so earlier counts remain explainable. `accepted-v1` remains available to re-audit the original frozen lossless batch.

- [Exact UID-by-UID flags, observations and evidence checks](held-audit.json)
- [Exact latest Neon review archive](latest-neon-reviews.json.gz)
- [Verified Neon audit checkpoint](neon-sync.json)

Original source assets and reviews remain unchanged. The audit is diagnostic bookkeeping; generated variants have their own processing, measurement and publication state.
