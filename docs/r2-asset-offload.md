# R2 asset offload (HKS-50)

Serve the heavy `3d-viewer/data/**` JSON (DEM meshes, vector overlays, POIs)
from a Cloudflare R2 bucket at **`assets.hk-sandbox.wiiiimm.codes`** instead of
the app host. On Vercel (metered bandwidth) this keeps the bulk egress on
Cloudflare, where R2 egress is free. Forks are unaffected — `ASSET_BASE` is
hostname-gated, so only the official host points at the bucket.

Pieces:

- **Bucket**: `hk-sandbox-assets` (Cloudflare account *stealth co.*, `b2585820…`) — already created.
- **App wiring**: `ASSET_BASE` / `asset()` in `main.js` (HKS-46) route every `/data/` fetch through the base.
- **Sync**: `.github/workflows/sync-r2-assets.yml` mirrors `3d-viewer/data/**` → `r2://hk-sandbox-assets/data` on every push to `main` that touches the data (and via manual dispatch).

## One-time setup (dashboard — maintainer only)

### 1. R2 S3 API token → GitHub secrets

Cloudflare dashboard → **R2 → Manage R2 API Tokens → Create API Token**:

- Permissions: **Object Read & Write**, scoped to the `hk-sandbox-assets` bucket.
- Copy the **Access Key ID** and **Secret Access Key**.

GitHub → repo **Settings → Secrets and variables → Actions**, add:

| Secret | Value |
|---|---|
| `R2_ACCESS_KEY_ID` | the Access Key ID |
| `R2_SECRET_ACCESS_KEY` | the Secret Access Key |
| `CLOUDFLARE_ACCOUNT_ID` | `b2585820a66e6dd6bf22d856890d3727` (already set for the Pages deploy) |

### 2. Bind the public custom domain

R2 → `hk-sandbox-assets` → **Settings → Custom Domains → Connect Domain** →
`assets.hk-sandbox.wiiiimm.codes`. This creates the DNS record in the
`wiiiimm.codes` zone and makes the bucket publicly readable at that host
(served through Cloudflare's CDN, so JSON is auto-Brotli'd on the edge).

### 3. CORS — allow the app origin to fetch cross-origin

R2 → `hk-sandbox-assets` → **Settings → CORS policy**:

```json
[
  {
    "AllowedOrigins": [
      "https://hk-sandbox.wiiiimm.codes",
      "https://hongkong-sandbox-git-main-stealth-engine.vercel.app"
    ],
    "AllowedMethods": ["GET", "HEAD"],
    "AllowedHeaders": ["*"],
    "MaxAgeSeconds": 3600
  }
]
```

`assets.hk-sandbox.wiiiimm.codes` is a different origin from the app, so without
this the browser blocks the fetch. Drop the `*.vercel.app` line once DNS is cut
over and the app is only served from `hk-sandbox.wiiiimm.codes`.

### 4. Populate the bucket

Trigger the sync once manually: GitHub → **Actions → “Sync data assets to R2” →
Run workflow**. Thereafter it runs automatically whenever `3d-viewer/data/**`
changes on `main`.

Verify it served correctly (expect `200`, `access-control-allow-origin`, and
`content-encoding: br` with `Accept-Encoding`):

```sh
curl -sI -H "Accept-Encoding: br" -H "Origin: https://hk-sandbox.wiiiimm.codes" \
  https://assets.hk-sandbox.wiiiimm.codes/data/hk-b50k-vectors.json
```

## Final step — activate (merge LAST, only after 1–4 verify)

`ASSET_BASE` still defaults to relative, so nothing uses R2 until the app is
told to. Add this hostname-gated line to `3d-viewer/index.html` (before
`main.js` loads) so **only** the official host uses R2 — forks and the bare
`*.vercel.app` previews stay on relative `/data/`:

```html
<script>
  // HKS-50: serve heavy /data/ from R2 on the official host only (forks stay relative)
  if (location.hostname === 'hk-sandbox.wiiiimm.codes')
    window.ASSET_BASE = 'https://assets.hk-sandbox.wiiiimm.codes';
</script>
```

> ⚠️ Do not merge the activation until steps 1–4 are done and the `curl` check
> passes — otherwise production would try to load `/data/` from a domain that
> isn't serving yet and the map would fail to load.
