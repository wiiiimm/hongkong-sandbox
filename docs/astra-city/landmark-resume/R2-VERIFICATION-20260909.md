# HKS-216 / HKS-217 · Incremental checkpoint verified

The current committed model pass is portable at **d6f25b3bd3bdc55c0e2b068dfb4df0e493da3395**. Later commits and 57 active residual-cache paths were excluded. Parent checkpoint `14dfae786d71b0a1f647284720c19507103791ad2b1c5d8348a4547ec12a2601` remains unchanged and linked in the new full manifest.

- Bucket/prefix: `hk-sandbox-assets/astra-modelling/`.
- Manifest SHA: `c3aa0026ce8c8ec2e43490362edefa1beafa65f603308e595364c8382a1d6f55`.
- Manifest key: `astra-modelling/snapshots/c3aa0026ce8c8ec2e43490362edefa1beafa65f603308e595364c8382a1d6f55.json`.
- Incremental upload: **492 objects /295,395,337 bytes**, all independently read back and hashed, 52.468 seconds. All 1,829 old objects reused without retransferring them during upload.
- Clean restore: **2,321 objects /2,056,673,217 bytes**, retrieved into a fresh empty cache in 80.696 seconds. Restored 3,924 files and 86 relative links; every restored file hash rechecked. No upload-cache reuse.
- All tracked files remained unchanged. **5,552 local glTF buffer references and 5,105 catalogue asset references checked; zero gaps**, including exact asset copies in alternative staging locations.
- Restored historical SQLite `quick_check`: ok. Guarded Neon `db.py check` and `ledger.py status --snapshot 11a25ce297101f9e` succeeded from the clean checkout.

The changed 640 MB local SQLite was deliberately not uploaded. The parent SQLite is preserved **as historical source/job state**. New review state remains in Neon; the recorded readback is a point-in-time observation, not an immutable review snapshot or permission to reuse active leases. Do not run legacy stage/queue mutations assuming the restored SQLite is current.

## Restore

Create a clean checkout at the exact commit above, install the documented Python dependencies, and use a private environment file on that device:

```sh
python source-scripts/city/landmark-resume/remote_checkpoint.py restore \
  --root /path/to/clean-checkout --cache /path/to/empty-download-cache \
  --manifest /path/to/downloaded-manifest.json \
  --manifest-sha256 c3aa0026ce8c8ec2e43490362edefa1beafa65f603308e595364c8382a1d6f55 \
  --env-file /path/to/private-r2.env --workers 8 --report /path/to/restore-report.json
python source-scripts/city/shared-modelling/configure.py --vercel-env /path/to/private-vercel.env
python source-scripts/city/shared-modelling/db.py check
python source-scripts/city/model-review-ledger/ledger.py status --snapshot 11a25ce297101f9e
```

The last two commands were executed successfully in the clean checkout, using `MODELLING_ENV_FILE` to reference the existing private branch-pinned configuration. A fresh device instead runs configure once. Credentials are never checkpoint payloads. The older inventory export command in shared-modelling/INVENTORY.md exports immutable source history; it does not merge current review/job results into SQLite.

Evidence: `R2-CLOUD-CHECKPOINT-20260909.json` and `checkpoint-d6f25b3b-manifest.json.gz`. Same-Mac clean restoration reused the installed Python environment; another operating system is not verified. Optional full-resolution browser images are omitted. This is working-cache continuity, not production asset publication or whole-landmark architectural acceptance.
