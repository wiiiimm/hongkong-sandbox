# Kai Tak Stadium — direct government model port

Executor: Codex root. Source UID `landsd/318723:0`, model
`B383792035701063C1`, government sheet `11-NE-16B` (revision 28 September 2025 UTC).
The 5,178-triangle model is 89,005 compressed bytes. No AI-generated geometry,
simplification, surveyed-height edits or terrain changes are used.

The original two government glTF/buffer members were downloaded through the existing
bounded, ETag/ZIP-directory/CRC-checked downloader: 108,032 source-member bytes,
plus the small ZIP directory check. The local Vercel R2 variables contained redacted
placeholders, so the original government source was used instead of R2 restoration.
The existing converter preserves geometry attributes and transforms. Normalising
only gzip's platform OS byte reproduces the previously cached asset SHA exactly:
`7f87b32b2203ad478087cfbec4d19ed274c39a37abb5f1363385f5ecc8ed5a9c`.

The existing podium `landsd/275446:0` covers the entire stadium footprint and ends
at 15.4 m HKPD. The native stadium begins at about 14.979 m, meeting that podium;
its apparent gap above the coarse terrain is not a reason to lower it. The podium
and all original city source records remain intact. The native top is 67.101 m HKPD;
the previous flat extrusion ended at 59.9 m. Geometry uses the existing city materials;
this is not a surveyed recreation of the stadium's iridescent facade materials.

Source evidence: `source-check.json`; original-member hashes and complete conversion
provenance in `source-scripts/city/kai-tak-port/conversion-summary.json`. Source imagery
from `references/lantau-maps/` was not used or modified.

Reproduce from the worktree root with the shared Python environment (NumPy, Shapely,
pyproj, psycopg and python-dotenv) and Node/Playwright:

```sh
python source-scripts/city/kai-tak-port/prepare.py
python source-scripts/city/kai-tak-port/stage.py
node source-scripts/city/kai-tak-port/browser.mjs staged
```

Publication uses the existing `model-integration-20260909/publish.py` wrapper with
`source-scripts/city/kai-tak-port/plan.json` and a live source reservation. Browser
checks retain before, staged and installed day/night views, verify the actual native
source UID, picking and collision, and exercise mobile failure/retry. The test-only
camera shortcut is not a new public place or an alteration to city geography.
Whole-neighbourhood completeness, stadium interiors, finished facade materials and
physical-device performance are outside this bounded source port.

The test host uses software WebGL. During loading the harness pauses GPU draw calls
while retaining the real simulation, source streaming and replacement pipeline, then
draws each captured frame through the actual city renderer. This is functional and
visual verification, not a frame-rate benchmark. Neighbouring tiles may still be
loading in the captures. The stadium itself must be active with its exact UID.

Focused native-model, streaming and progress tests: 33 passed.

Installed checks passed at 1280×900 and 390×900 in daylight and at night, including
native UID activation, picking, roof-surface collision and no horizontal overflow.
The mobile 503 test retained the fallback and the existing retry control restored
the native model. Saved images were inspected. The shared Neon review is
`installed-verified` under snapshot `87377e4c7a0f2fe9`, method `scripted`,
AI geometry model `null`; no attributable token count is claimed.
