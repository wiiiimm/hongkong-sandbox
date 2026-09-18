# Lantau and island walkthrough

GPT-6 Astra, 6 September 2026. The screenshots in this folder are native-size
Chrome captures of the current city explorer after the low-rise height correction
and dry-terrain arrival repair. The machine-readable run is
[verification.json](verification.json).

Run the focused walkthrough from the repository root:

```sh
node 3d-viewer/city/tests/islands-browser.mjs
```

It explicitly selects **Mui Wo, Tai O, Cheung Chau, Peng Chau, Pui O, Cheung Sha,
Tong Fuk, Shui Hau, Ngong Ping, Tung Chung valley and Tung Chung**, enters walking
mode at the configured public-path arrival, and walks at least 1.5 m at each.
The recorded run moved **1.56 m at all 11 destinations**, with no building collision,
page errors or failed local requests. Streaming stayed within its 30-tile cache
and 24-tile wanted limit. Mobile Peng Chau selection also passed at 390 × 844 with
no horizontal overflow. Desktop images are 1440 × 1000.

The separate streaming/data test checks **all 43 presets** against dry terrain
triangles and building collision volumes. The Lantau mountains preset is an
intentional landscape viewpoint, so the nearby-settlement density assertion does
not apply to it. The 11-place browser run is the explicit short walking check;
the other presets have data-level arrival validation rather than completed route
walkthroughs.

## Inspected views and remaining work

- [Mui Wo overview](muiwo-orbit-1440x1000.png) and
  [walking](muiwo-walk-1440x1000.png): the bay, mapped streets and settlement are
  visible. Explicitly tagged houses now use low-rise estimates. Shoreline corners,
  the promenade edge, beach and small watercourses remain coarse at 70 m terrain
  sampling; the waterfront surface is an approximate ground model.
- [Tai O overview](taio-orbit-1440x1000.png) and
  [walking](taio-walk-1440x1000.png): the sourced compact-village rule lowers 252
  forms while larger/public buildings retain their existing treatment. The camera
  and walking arrival use Yim Tin Square. Small tidal channels are not resolved
  in the current terrain, and the model does not yet recreate individual stilt
  supports, connecting decks, roof forms or historic façades. The village should
  not be considered architecturally complete.
- [Cheung Chau overview](cheungchau-orbit-1440x1000.png) and
  [walking](cheungchau-walk-1440x1000.png): the mapped harbour-side street pattern
  and village blocks load correctly. The low-rise correction distinguishes tagged
  houses from unresolved generic blocks. Generic heights, pier/deck geometry,
  coastal detail and roof character remain local review tasks.
- [Peng Chau overview](pengchau-orbit-1440x1000.png),
  [walking](pengchau-walk-1440x1000.png) and
  [mobile](peng-chau-mobile-390x844.png): the first inspected arrival exposed a
  partly submerged terrain triangle under the ferry-side path. The final arrival
  moves inland to a retained public path, 101 m from the pier reference, and its
  surrounding walking margin lies on fully dry triangles. No artificial pier or
  coastline fill was added. Generic residential heights still need verification.
- [Shui Hau](shuihau-orbit-1440x1000.png) is visibly sparse: just **22 forms** in
  the 800 m proximity audit. This is a source-completeness issue requiring better
  building references, not an invitation to add plausible invented buildings.
- [Pui O](puio-orbit-1440x1000.png),
  [Cheung Sha](cheungsha-orbit-1440x1000.png),
  [Tong Fuk](tongfuk-orbit-1440x1000.png),
  [Ngong Ping](ngongping-orbit-1440x1000.png) and
  [Tung Chung valley](tungchungvalley-orbit-1440x1000.png) now have explicit
  destination selection and verified short walking arrivals. Their individual
  landmarks, village boundaries, roofs and walking routes remain unreviewed.

Village identity and place coordinates come from retained OSM features. The
low-rise correction is explicitly estimated, with authoritative context and exact
selectors documented in [GEOGRAPHY-COVERAGE.md](../GEOGRAPHY-COVERAGE.md).
Building heights from source tags or levels are preserved. No source snapshots,
archival maps, terrain or coastline data were modified by the massing correction.

This functional walkthrough and visual limitation review does not mark any
section's detailed geography/gameplay checklist complete.
