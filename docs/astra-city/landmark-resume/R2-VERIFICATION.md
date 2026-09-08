# HKS-216 — R2 cloud checkpoint verified, 8 September 2026

**Actual cloud upload and clean restoration passed.** Bucket `hk-sandbox-assets`, prefix `astra-modelling/`. This supersedes the earlier local-only verification.

- Manifest: `astra-modelling/snapshots/14dfae786d71b0a1f647284720c19507103791ad2b1c5d8348a4547ec12a2601.json`
- Manifest SHA-256: `14dfae786d71b0a1f647284720c19507103791ad2b1c5d8348a4547ec12a2601`
- Required source Git commit: `8d361811e710c85bb5014f7681586c7e01e11f72`
- Profile: `unmodified-cli-restore`.
- 1,829 unique payload objects /1,761,277,880 bytes verified by remote readback. 1,827 objects were newly uploaded; two matching objects were already present from the real cloud-worker test and were verified/reused. The manifest is additional to payload-byte counts.
- Payload upload/readback: 165.349 seconds. Independent fresh-cache remote download/readback: 49.555 seconds, followed by local restoration.
- Restored 2,800 files +86 relative links into a clean checkout with no pre-existing SQLite or ignored cache. All downloads came from R2, including the manifest. The source object's local upload cache was not used for restoration.
- Restored SQLite quick_check: ok; 346,115 building records and 29,760 historical jobs. Existing status.py verified all input hashes and 4,054 installed detailed parts. Existing stage check passed 102 overlays /194 groups /459 UIDs /17 unchanged holds.
- Eight snapshot/transfer tests pass. Concurrent real-R2 model workers also passed for two candidates; separate evidence is in source-scripts/city/shared-modelling/cloud-model-worker-verification.json (commit 22f47aff).

Machine-readable evidence: [R2-CLOUD-CHECKPOINT.json](R2-CLOUD-CHECKPOINT.json). Neon inventory snapshot remains `f26ca1cad7e19b984c78d12877a8b35cca7af8f434ab1c7ec8756983ccdc0008` on astra-modelling; new shared job results live in Neon rather than the archived SQLite.

## Limits

The clean checkout was on the same Mac and used the existing Python environment. A different operating system/runtime installation is not tested. The checkpoint excludes optional full-resolution gallery captures; the compact tracked gallery is in Git. Secrets and Vercel configuration files are excluded. This is a versioned working checkpoint, not continuous folder synchronisation or a production asset deployment. Historical byte snapshots do not replace live Neon queue state. Model identity/terrain/architectural review holds remain open.

The earlier local-only test used 9ba070c2 and manifest 13b20ee4c602d32982469d126dc6dc229e345cd492e8f0b259de02f1efc2eea0. The cloud checkpoint above is the current portable hand-off.
