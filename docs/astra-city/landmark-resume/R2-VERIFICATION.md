# HKS-216 — working-material verification, 8 September 2026

## Completed locally

Ran the real `unmodified-cli-restore` inventory through the content-addressed local transport, then restored it into a fresh shared Git clone of source commit `9ba070c2f93556994c9f4d45c8255921a501da2d`. No working cache or SQLite existed in the clone beforehand. The shared Git clone saves object-store disk space but its ignored working files were restored independently.

- 2,800 regular files and 86 relative adapter links restored.
- 2,606,558,599 logical input bytes.
- 1,829 unique stored objects, 1,761,277,880 bytes (about 32.4% reduction through exact-byte deduplication).
- Every stored/reused object read back and checked for exact SHA-256 and size.
- Repeating the full snapshot uploaded **zero objects and zero bytes** and produced the same manifest digest.
- Restored SQLite `PRAGMA quick_check`: `ok`; 346,115 building rows and 29,760 historical job rows retained.
- Five automated tests pass: round-trip and restart; corrupt-object rejection before writing; credential/path escape rejection; preservation of conflicting existing files; manifest hash and duplicate-path rejection.

Manifest SHA-256: `13b20ee4c602d32982469d126dc6dc229e345cd492e8f0b259de02f1efc2eea0`.

Local-only evidence: `/tmp/astra-r2-working-manifest.json`, `/tmp/astra-r2-local-store/`, `/tmp/astra-r2-restore-check/`. These are temporary machine-local verification artefacts, not a remotely durable backup. The tool was executed from the source worktree during this pre-commit verification; subsequent portable checkpoints must include the committed tool/skill in their matching Git checkout.

## Still unverified

No R2 cloud request or upload occurred. The bucket is confirmed by the existing repository variable as `hk-sandbox-assets`, but no `R2_ACCOUNT_ID`, `R2_ACCESS_KEY_ID` or `R2_SECRET_ACCESS_KEY` was present in process variables, either checkout's environment files, or an AWS credential file. Vercel authentication and Neon credentials do not grant R2 S3 access. Supply a bucket-scoped S3 credential through the environment, then run and verify the remote checkpoint under `astra-modelling/`.

The S3 adapter's conditional create/download behaviour remains a cloud-integration test requirement. Local round-trip success does not verify R2 network retries, API permissions, bandwidth or cloud access from a second device. Neither this test nor the archive migrates the ledger into Neon, verifies PostgreSQL workers, performs a fresh browser capture or clears existing architectural/terrain acceptance holds. Optional full-resolution review JPEGs were not part of this core-profile test; their tracked compact contact sheet remains in Git.

## Restored-script checks and endpoint configuration

The restored clone's own `source-scripts/city/building-batch/status.py` completed successfully using `/tmp/astra-city-venv/bin/python`: **all inventory input hashes verified**, 346,115 forms, 4,054 installed detailed parts (1,859 embedded and 2,195 progressive), 12.009 seconds, zero AI/network calls. Its own `source-scripts/city/landmark-identity/stage_proposals.py check` also passed: 102 overlay entries, 194 selected groups, 459 selected UIDs and 17 known holds retained. These checks did not modify jobs or stage models. Reports are `/tmp/astra-restored-status.json` and `/tmp/astra-restored-overlay-check.json`.

No missing source/cache dependency was encountered by either restored command. Both reused the machine's existing Python virtual environment: this verifies restored working-material closure, not dependency installation on a second operating system. A new machine still needs the documented Python geometry dependencies and suitable Node/browser runtimes for later processing/capture.

The R2 adapter now accepts `R2_ENDPOINT_URL` as an alternative to `R2_ACCOUNT_ID`, validates an HTTPS Cloudflare R2 account host (including EU/FedRAMP jurisdiction hosts), rejects credentials/paths/query strings in the URL, and preserves the `hk-sandbox-assets` default bucket. `source-scripts/city/landmark-resume/requirements.txt` declares the optional remote `boto3` dependency. **Six tests now pass**, including malicious/invalid endpoint rejection. No full snapshot needed to be repeated for this configuration change, and no cloud request occurred.
