# Landmark identity proposals — HKS-212

The scripted pass accounts for all **213 registry entries** and proposes an unapplied overlay for **71 entries / 118 source records**, including **106 newly identified UIDs**. It proposes matches for **67 of the previous 115 no-identity entries**, geographically separates all three ambiguous same-name groups, and adds one separately named Island Shangri-La hotel component. The other entries retain their previous identity evidence or explicit exceptions.

These are **reviewed identity proposals**, not verified complete landmarks, geometry acquisitions, placement approvals or live replacements. No master registry, database, runtime or published asset was changed. The SQLite connection is read-only.

| Current identity state | Entries |
| --- | ---: |
| Prior identities retained | 92 |
| Proposed overlay | 71 |
| No supported identity | 44 |
| Candidate needs independent location evidence | 3 |
| Historical interior / unverified host | 3 |

[Full report](report.json) · [Invariant checks](validation.json) · [Proposed overlay](../../../source-scripts/city/landmark-identity/proposed-overlay.json)

## Evidence and boundaries

The script joins retained government names, stable UID/CSUID/object IDs and unmodified footprint positions to the registry's previously sourced geographic hints. It uses the existing EPSG:4326 → EPSG:2326 projection and world origin of 834500/816500. The geographic hints are discovery evidence, chiefly from the retained tallest-buildings table; they are not substituted for government coordinates. Every new proposed record has an explicit name relationship and lies within 250 m of a sourced hint. There is no nearest-building acceptance, invented coordinate, fuzzy edit-distance match or model-height change.

Rules handle punctuation, accents, optional Tower/Block/Hotel words, spacing such as Metro Town/Metrotown, recorded phase prefixes, and government A/B subtowers. They preserve source tower numbers. Literal ranges stay explicit: a missing Tower 4 is recorded as a membership question, not fabricated or silently assumed to be omitted.

Previous source-component identities are retained. The three held same-name groups use their own sourced location to exclude distant names: Harbourside, Central Plaza and Manhattan Heights. Related unnamed podiums and annexes are never assigned solely because they are nearby. All proposals retain `componentMembershipComplete: false` and `publicationApproved: false`; held architectural work remains held.

The report contains input hashes, exact government records, accepted/rejected/weak candidates, distances, source URLs, prior holds and unresolved nearby names. A few bounded official-source checks are recorded in [reference-notes.json](../../../source-scripts/city/landmark-identity/reference-notes.json): MALIBU subtower naming, the built Chu Hai campus, Wings at Sea II phase naming and the existing 133 Wai Yip Street renovation. These checks did not create unsupported aliases or coordinates.

## Remaining work and effort

- **Higher-effort geometry/terrain work:** the 16 HKS-209 records and previous unsupported Ngong Ping pagoda remain explicitly unapproved in `higherEffortPlacementQueue`. This identity pass does not resolve those physical problems.
- **Identity research:** renamed commercial buildings, phase aliases such as Le Point and Hemera, and sources with no reliable geographic hint need further documentary joins. Existing nearby names are leads only.
- **Component membership:** grouped towers, A/B subtowers, connected podiums and annexes need complete source accounting before a whole landmark can be approved.
- **Historical/interior records:** Potato Head and other old venue names need verified host identities. Chu Hai must refer to the existing campus, not an unbuilt architectural proposal. No model should be generated from an unresolved label.

## Reproduce

```sh
/tmp/astra-city-venv/bin/python source-scripts/city/landmark-identity/resolve.py
/tmp/astra-city-venv/bin/python source-scripts/city/landmark-identity/validate.py
```

Processing used no AI or network requests; separate bounded source research is described above. Runs took approximately 3–7 seconds locally. A repeated run produced byte-identical overlay output and identical report data excluding elapsed time; see [determinism.json](../../../source-scripts/city/landmark-identity/determinism.json).

The overlay uses the existing selection `landmarks[].records` identity shape. A caller must consciously merge the proposed records, honour `replacePriorIdentity` for the three corrected groups, and preserve component/placement holds. Merely reading this overlay must not refresh or inflate the previous bulk-model staging claims.
