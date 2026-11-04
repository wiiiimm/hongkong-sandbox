# Source-bound BASIC fallback ownership

A retained government complex can legitimately suppress several bundled BASIC
forms. When a separately reviewed original is installed for one of those forms,
a failed download must leave that building's own BASIC geometry visible while
the complex remains active.

`manifest.basicFallbackProtections` records only explicitly reviewed pairs:

```json
{"uid":"landsd/1:0","buildingCSUID":"exact-current-CSUID","sourceSHA256":"<64 lowercase hex>","suppressorUid":"landsd/2:0","suppressorSourceSHA256":"<64 lowercase hex>"}
```

The publisher requires each new protection to accompany an accepted new original,
with exact UID/CSUID/asset SHA and an existing unchanged compound which actually
suppresses that UID. It verifies the compound's bytes, preserves all previous
protections, and rejects stale source bindings or edits to retained compound
metadata. This policy neither clears publication holds nor changes dependencies.

Streaming exempts only the matched BASIC form from that compound's suppression.
Normal source activation still removes its own BASIC geometry, and demotion or
failure restores it. Unprotected bundled forms and infrastructure exclusions keep
the existing behaviour. No policy means no change to current suppression rules.

The implementation is tested with actual baked BASIC feature geometry during
failed download, successful retry and demotion while a publication-held compound
stays active. Private browser overlays can stage exact pairs without changing the
installed manifest. Policy support alone does not approve or install a model.
Government source geometry, asset bytes, source scale and placement are unchanged.
