"""Fenced installation of reviewed unsurveyed BASIC foundations.

Separate from the roof-only and surveyed podium routes. This never qualifies a
private diagnostic, changes source metadata, or grants native support credit.
"""
import copy
import json
import math
from basic_podium_footings import terrain_geometry_sha, value_sha

POLICY = 'terrain-derived-unsurveyed-basic-foundation-v1'
# Explicitly scoped recovery; adding another source requires a reviewed route.
SOURCES = {
    'landsd/31181:0': ('4521121843T20071025', 'university', 'Open-sided Structure'),
    'landsd/309838:0': ('4519122180T20210421', 'shed', 'Temporary Structure'),
    'landsd/339024:0': ('4530221998T20170110', 'university', 'Temporary Structure'),
}
COMMON_PROOFS = (
    'recordedFieldsAndRoofUnchanged', 'fullGroundCoverage',
    'conservativeVerticalGroundAccounted', 'wholeRoofClear',
    'collisionReviewApproved', 'jointSceneReviewApproved',
    'desktopDayNightReviewed', 'mobileDayNightReviewed',
    'loadingPickingFailureRetryApproved', 'fallbackLifecycleApproved',
)


def stage_unsurveyed_foundations(root, plan, manifest, edits, report, load, sha, encoded):
    updates = plan.get('unsurveyedBasicFoundations', [])
    registry = copy.deepcopy(manifest.get('unsurveyedBasicFoundations', []))
    if not updates and not registry:
        return
    assert isinstance(updates, list) and isinstance(registry, list)
    root = root.resolve()

    def effective(path):
        return json.loads(edits[path]) if path in edits else load(path)

    def bound(ref):
        path = (root / ref['path']).resolve()
        assert path.is_relative_to(root), 'Evidence escaped repository'
        assert sha(path) == ref['sha256'], 'Foundation evidence changed'
        return load(path)

    def tilepath(url):
        path = (root / '3d-viewer' / url).resolve()
        assert path.is_relative_to(root / '3d-viewer/city/data/tiles')
        return path

    models = [m for url in manifest.get('officialModelCatalogues', [])
              for m in effective(root / '3d-viewer' / url)['models']]
    unavailable = {m['uid'] for m in models} | {
        uid for m in models for uid in m.get('suppressesBuildingUids', [])}
    seen = {r['uid'] for r in registry}
    assert len(seen) == len(registry), 'Duplicate retained foundation'
    applied = []
    for update in updates:
        uid = update['uid']
        assert uid in SOURCES and uid not in seen and uid not in unavailable
        seen.add(uid)
        path = tilepath(update['tile'])
        matches = [t for t in manifest['tiles'] if t['url'] == update['tile']]
        assert len(matches) == 1 and sha(path) == update['tileSHA256']
        data = copy.deepcopy(effective(path))
        forms = [b for b in data['buildings'] if b['uid'] == uid]
        assert len(forms) == 1
        b = forms[0]
        assert b == update['before'], 'Source form changed'
        assert (b['buildingCSUID'], b['kind'], b['structureType']) == SOURCES[uid]
        assert b['baseSource'] == 'terrain-estimated' and b['heightSource'] == 'estimated'
        assert b.get('baseHeightHKPD') is None and b.get('topHeightHKPD') is None
        assert not b.get('modelGeometry') and b.get('foundationBase') is None and b.get('foundationPolicy') is None
        value = update['foundationBase']
        assert type(value) in (int, float) and math.isfinite(value) and value < b['base'] - .02
        review = bound(update['evidence'])
        assert review['status'] == 'approved-for-integration' and review['policy'] == POLICY
        assert review['uid'] == uid and review['sourceFormSHA256'] == value_sha(b)
        assert review['tileSHA256'] == update['tileSHA256'] and review['foundationBase'] == value
        assert all(review[k] is True for k in COMMON_PROOFS), 'Incomplete foundation acceptance'
        assert review['governmentGeometryChanges'] == 0 and review['sourcePoseChanges'] == 0
        assert review['aiGeometryModelling'] is False and review['nativeSupportCredit'] is False
        # These refs must include exact renderer, terrain, collision and browser
        # receipts. A true summary flag alone is not a publication record.
        evidence = review['evidence']
        for category in ['geometry', 'ground', 'collision', 'jointScene', 'desktop', 'mobile', 'fallback']:
            assert evidence[category]
            for ref in evidence[category]:
                bound(ref)
        proof = bound(review['renderProof'])
        assert proof['governmentGeometryChanges'] == 0
        assert proof['inputHashes']
        for rel, expected in proof['inputHashes'].items():
            src = (root / rel).resolve()
            assert src.is_relative_to(root) and sha(src) == expected, 'Renderer changed'
        if b['structureType'] == 'Open-sided Structure':
            for k in ['roofPartsExactlyUnchanged', 'allXZExactlyUnchanged', 'onlyIllustrativePostBottomVerticesChanged']:
                assert proof[k] is True
        else:
            for k in ['originalBodyAndRoofPartsExactlyUnchanged', 'originalBodyVerticesAndWindowMasksExactlyUnchanged',
                      'allNewXZFromOriginalFootprint', 'collisionVolumesExactlyMatchRenderedParts', 'foundationOnlyBelowOriginalBase']:
                assert proof[k] is True
            assert proof['newFoundationWindows'] is False
        assert review['minimumCoveredGroundHKPD'] == value, 'Non-minimal or invented foundation depth'
        deps = review['nativeTerrainDependencies']
        assert isinstance(deps, list) and deps and len({d['url'] for d in deps}) == len(deps)
        b['foundationBase'] = value
        b['foundationPolicy'] = POLICY
        unchanged = copy.deepcopy(b)
        unchanged.pop('foundationBase'); unchanged.pop('foundationPolicy')
        assert unchanged == update['before']
        edits[path] = encoded(data)
        matches[0]['bytes'] = len(edits[path])
        registry.append(dict(uid=uid, tile=update['tile'], policy=POLICY,
                             retainedFormSHA256=value_sha(b), evidence=update['evidence'],
                             nativeTerrainDependencies=deps, mustRemainBasicAndUnsuppressed=True))
        applied.append(uid)

    terrain_urls = {t['url'] for t in manifest.get('terrainPatches', [])}
    checked = []
    for item in registry:
        uid = item['uid']
        assert uid in SOURCES and uid not in unavailable
        assert item['policy'] == POLICY and item['mustRemainBasicAndUnsuppressed'] is True
        forms = [b for b in effective(tilepath(item['tile']))['buildings'] if b['uid'] == uid]
        assert len(forms) == 1 and value_sha(forms[0]) == item['retainedFormSHA256']
        assert forms[0]['foundationPolicy'] == POLICY and not forms[0].get('modelGeometry')
        bound(item['evidence'])
        assert item['nativeTerrainDependencies']
        for dep in item['nativeTerrainDependencies']:
            assert dep['url'] in terrain_urls, 'Foundation terrain removed; revalidation required'
            path = (root / '3d-viewer' / dep['url']).resolve()
            assert path.is_relative_to(root / '3d-viewer/city/data')
            assert terrain_geometry_sha(effective(path)) == dep['geometrySHA256'], 'Foundation terrain changed; revalidation required'
        checked.append(uid)
    manifest['unsurveyedBasicFoundations'] = registry
    report['unsurveyedBasicFoundations'] = applied
    report['retainedUnsurveyedBasicFoundationChecks'] = checked
