# HKS-216 — portable working material

The shared PostgreSQL ledger coordinates workers; R2 retains immutable working inputs and prepared outputs. The legacy SQLite file is backed up consistently for migration/history, not used as a remotely shared live database. The production viewer's `data/` objects and delivery configuration are untouched.

The existing GitHub `R2_BUCKET` variable identifies **hk-sandbox-assets**. This tool uses only **astra-modelling/**, with `objects/sha256/<first-two>/<digest>` and `snapshots/<manifest-digest>.json`. It never deletes objects or updates a mutable latest pointer. A snapshot's manifest digest is the checkpoint identifier: record it with the task's commit and database checkpoint. Interrupted uploads can be repeated; identical content is reused only after byte verification. Concurrent uploads use conditional object creation. Snapshot references are immutable, so workers cannot silently replace each other's checkpoints.

## Commands

Use Python 3.10+ and install `python3 -m pip install -r source-scripts/city/landmark-resume/requirements.txt` for R2 transport. The base local transport uses the standard library; the parallel CLI/test suite also needs python-dotenv from the requirements. Export bucket-scoped `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY` and either `R2_ENDPOINT_URL` or `R2_ACCOUNT_ID` securely in the process. Endpoint URLs must be HTTPS Cloudflare R2 account endpoints; credentials, non-443 ports, query strings and bucket paths are rejected. The default bucket remains `hk-sandbox-assets`. The script does not load `.env` files or log credentials. Vercel database credentials and its OIDC token do not provide R2 S3 access. GitHub Actions secret values cannot be retrieved through the GitHub API.

```sh
python3 source-scripts/city/landmark-resume/r2_snapshot.py snapshot \
  --root "$PWD" \
  --inventory docs/astra-city/landmark-resume/cache-inventory.json \
  --manifest /tmp/astra-working-manifest.json
```

The default profile is `unmodified-cli-restore`, retaining ignored extraction/staging caches. Add `--profile unmodified-cli-restore --profile optional-review-evidence` to include full-resolution review captures. Git-tracked files must come from the manifest's exact `gitCommit`; they are not duplicated into R2. SQLite uses the online backup API followed by `PRAGMA quick_check`. Every uploaded or reused object is downloaded and SHA-256/size verified before a manifest is published. Source workers must be idle at checkpoint creation: SQLite backup is consistent, but other files do not have a cross-file transactional snapshot. This is archival checkpointing, not a live bidirectional directory sync.

On another machine, clone the matching Git commit and download the manifest by its recorded key. Verify the expected digest through the task/ledger record, then restore:

```sh
python3 source-scripts/city/landmark-resume/r2_snapshot.py restore \
  --root "$PWD" --manifest /tmp/astra-working-manifest.json \
  --manifest-sha256 '<recorded SHA-256>'
```

Files are verified in temporary staging before any payload is restored. Existing different files are never overwritten; identical restores are restart-safe. Relative adapter links are recreated only inside the checkout. The tool refuses path traversal, absolute paths, out-of-checkout links, Git/runtime/credential directories, `.env*`, `.pem` and `.key` files. It accepts only selected inventory entries; never substitute an unreviewed directory inventory. Filename exclusions are not a general-purpose secret-content scanner.

`--local-store /tmp/astra-r2-local-store` runs the same object/manifest contract against a local directory, without credentials or network. Test with:

```sh
python3 -m unittest discover -s source-scripts/city/landmark-resume -p 'test_*.py' -v
```

## Boundaries

A successful byte restore does not prove an old processing command works against PostgreSQL, restore Neon branch state, or approve building architecture/terrain placement. Install the documented Python/Node/browser dependencies and run the existing read-only validation against restored inputs separately. The tool deliberately requires an exact Git commit and a recorded manifest digest. It does not provide automatic manifest discovery, credentials distribution, retention/garbage collection or a mutable shared cache.

The current cloud checkpoint passed actual R2 upload/readback and a fresh-cache clean-clone restore. See R2-VERIFICATION-20260909.md and R2-CLOUD-CHECKPOINT-20260909.json for its exact commit, manifest and remaining platform limitations.

## Bounded parallel transfer and direct cloud restoration

The parallel wrapper uses the same snapshot format. It loads only R2 variables from a private env file, caps concurrency at 16 (default 8), and publishes the remote manifest only after all unique objects pass readback. Keep its local staging cache outside Git.

```sh
python source-scripts/city/landmark-resume/remote_checkpoint.py upload \
  --root "$PWD" --inventory docs/astra-city/landmark-resume/cache-inventory.json \
  --cache /tmp/astra-upload-cache --manifest /tmp/astra-manifest.json \
  --env-file .env.local --report /tmp/astra-upload-report.json
```

For recovery, check out the exact sourceGitCommit in R2-CLOUD-CHECKPOINT-20260909.json first. Supply credentials from this device's private env file (the checkpoint never includes them), then download using the recorded manifestSHA256:

```sh
python source-scripts/city/landmark-resume/remote_checkpoint.py restore \
  --root "$PWD" --cache /tmp/astra-fresh-download-cache \
  --manifest /tmp/astra-downloaded-manifest.json --manifest-sha256 RECORDED_SHA256 \
  --env-file .env.local --report /tmp/astra-restore-report.json
```

The restore wrapper downloads the manifest and every unique object from R2 even if another local cache has them, verifies them, then invokes the existing safe restore. Report remoteTransfer fields are actual cloud payload counts; upload's outer uploadedObjects/uploadedBytes describe local staging-cache additions only.
