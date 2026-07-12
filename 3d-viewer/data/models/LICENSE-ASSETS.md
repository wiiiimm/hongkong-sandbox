# Asset licences — `data/models/`

The **code** in this repository is licensed under the GNU AGPL-3.0 (see `/LICENSE`).
The **3D models and other bundled media in this folder are NOT covered by that
licence** — each asset carries its own licence, recorded per-file in `README.md`
(source URL, author, exact licence, and any modifications we made).

## Accepted asset licences

- **CC0 / public domain** — preferred; no conditions.
- **CC BY / permissive (MIT, etc.)** — accepted; attribution is **load-bearing**
  and must appear in the app's Credits drawer (en + 繁中) and in `README.md`.
- **CC BY-NC-SA / other NonCommercial licences** — accepted **only** under the
  fencing rules below.
- **ND (NoDerivatives) or unclear/unverified licences** — never accepted.

## NonCommercial (NC) asset rules

The app is currently free, unmonetised open source, so NC-licensed assets may be
bundled. Because NC restrictions follow the *asset* (not our code licence), every
NC asset must be fenced so it can be cleanly removed:

1. NC assets live under `data/models/nc/` — never mixed with freely-licensed files.
2. Each has a `README.md` entry marked **⚠ NC** with the exact licence quoted.
3. The code must degrade gracefully when an NC asset is absent (the same
   procedural-fallback pattern used for all model loads).
4. **Commercial use of any kind — by us or by a commercial licensee under
   `COMMERCIAL.md` — requires deleting `data/models/nc/` first.** A commercial
   licence to the code does not and cannot include these assets.
5. Modified NC-SA assets we produce (decimation, re-texturing) remain under the
   original NC-SA licence, noted in `README.md`.

If this project ever monetises (paid features, embeds, prints, commercial
licensing of a deployment), `data/models/nc/` must be emptied or every asset in
it replaced/relicensed **before** launch.
