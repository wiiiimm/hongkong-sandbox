"""Stage qualified BASIC-only footings while keeping government assets immutable.

The retained registry forbids native activation or suppression of these forms.
Changing their local native terrain geometry requires fresh footing validation.
"""
import copy
import hashlib
import json
import math

POLICY = 'terrain-derived-basic-podium-footing-v1'


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode()


def value_sha(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def terrain_geometry_sha(terrain):
    assert terrain.get('nativeMesh') and terrain['meta']['georef']
    return value_sha({key: terrain.get(key) for key in ['coarseCells', 'w', 'h', 'elev', 'renderedElev', 'nativeMesh']} | {'georef': terrain['meta']['georef']})


def stage_basic_podium_footings(root, plan, manifest, edits, report, load, sha, encoded):
    updates = plan.get('basicPodiumFootings', [])
    registry = copy.deepcopy(manifest.get('basicOnlyFootings', []))
    if not updates and not registry:
        return
    assert isinstance(updates, list) and isinstance(registry, list)

    def effective(path):
        return json.loads(edits[path]) if path in edits else load(path)

    def bound(ref):
        path = (root / ref['path']).resolve()
        assert path.is_relative_to(root.resolve()), 'Footing evidence path escaped repository'
        assert sha(path) == ref['sha256'], 'Footing evidence changed'
        return load(path)

    models = [m for url in manifest.get('officialModelCatalogues', [])
              for m in effective(root / '3d-viewer' / url)['models']]
    native = {m['uid'] for m in models}
    suppressed = {uid for m in models for uid in m.get('suppressesBuildingUids', [])}
    terrain_urls = {t['url'] for t in manifest.get('terrainPatches', [])}
    seen = {r['uid'] for r in registry}
    assert len(seen) == len(registry), 'Duplicate retained BASIC footing'
    applied = []
    for update in updates:
        uid = update['uid']
        assert uid not in seen, 'BASIC footing already registered or duplicated'
        seen.add(uid)
        assert uid not in native and uid not in suppressed, 'Footing target must remain BASIC and visible'
        tile = update['tile']
        matches = [t for t in manifest['tiles'] if t['url'] == tile]
        assert len(matches) == 1
        path = (root / '3d-viewer' / tile).resolve()
        assert path.is_relative_to((root / '3d-viewer/city/data/tiles').resolve())
        assert sha(path) == update['tileSHA256'], 'Footing tile changed'
        data = copy.deepcopy(effective(path))
        matches_b = [b for b in data['buildings'] if b['uid'] == uid]
        assert len(matches_b) == 1
        b = matches_b[0]
        assert b == update['before'], 'Footing source form changed'
        assert not b.get('modelGeometry') and b.get('foundationBase') is None and b.get('foundationPolicy') is None
        assert b['structureType'] == 'Podium' and b['kind'] == 'yes' and b['minimum'] == 0
        assert b['baseSource'] == b['heightSource'] == 'landsd'
        assert b['base'] == b['baseHeightHKPD'] and b['base'] + b['height'] == b['topHeightHKPD']
        assert b['buildingCSUID'] and b['height'] > 0
        value = update['foundationBase']
        assert type(value) in (int, float) and math.isfinite(value) and value < b['base'] - .02
        proposal = bound(update['proposal'])
        assert proposal['uid'] == uid and proposal['originalBase'] == b['base'] and proposal['foundationBase'] == value
        assert proposal['surveyedElevationsUnchanged'] is True
        review = bound(update['evidence'])
        assert review['status'] == 'approved-for-integration' and review['policy'] == POLICY
        assert review['uid'] == uid and review['buildingCSUID'] == b['buildingCSUID']
        assert review['sourceFormSHA256'] == value_sha(b) and review['tileSHA256'] == update['tileSHA256']
        assert review['proposalSHA256'] == update['proposal']['sha256'] and review['foundationBase'] == value
        for key in ['completeBasicBodyAndIndicesExactlyUnchanged', 'surveyedElevationsAndRoofUnchanged',
                    'fullFootprintCovered', 'fullPositiveAreaGroundWithinFooting',
                    'nativeCoverageMatchesActualDrawnGround', 'collisionReviewApproved', 'visualReviewApproved']:
            assert review[key] is True, 'Missing qualified footing evidence: ' + key
        assert review['verticalGroundContactsRequireReview'] == 0
        assert review['sourceGeometryChanges'] == review['governmentGeometryChanges'] == 0
        assert review['aiGeometryModelling'] is False
        uncovered = review['nativeCoverageUncoveredAreaM2']
        assert type(uncovered) in (int, float) and math.isfinite(uncovered) and 0 <= uncovered < 1e-8
        low, high = review['groundRange']
        assert all(type(v) in (int, float) and math.isfinite(v) for v in [low, high])
        assert low <= high < b['base'] - .02 and value == low - .02, 'Footing is not the minimal computed ground extension'
        deps = review['nativeTerrainDependencies']
        assert isinstance(deps, list) and deps and len({d['url'] for d in deps}) == len(deps)
        b['foundationBase'] = value
        b['foundationPolicy'] = POLICY
        unchanged = copy.deepcopy(b)
        unchanged.pop('foundationBase'); unchanged.pop('foundationPolicy')
        assert unchanged == update['before'], 'Footing changed surveyed/source fields'
        edits[path] = encoded(data)
        matches[0]['bytes'] = len(edits[path])
        registry.append(dict(uid=uid, tile=tile, policy=POLICY, buildingCSUID=b['buildingCSUID'],
                             retainedFormSHA256=value_sha(b), nativeTerrainDependencies=deps,
                             evidence=update['evidence'], mustRemainBasicAndUnsuppressed=True,
                             nativeReplacementRequiresFootingRemovalAndRevalidation=True))
        applied.append(dict(uid=uid, foundationBase=value, evidence=update['evidence']))

    checked = []
    for item in registry:
        uid = item['uid']
        assert item['policy'] == POLICY and item['mustRemainBasicAndUnsuppressed'] is True
        assert item['nativeReplacementRequiresFootingRemovalAndRevalidation'] is True
        assert uid not in native and uid not in suppressed, 'Retained BASIC footing cannot activate a native model or be suppressed: ' + uid
        path = (root / '3d-viewer' / item['tile']).resolve()
        assert path.is_relative_to((root / '3d-viewer/city/data/tiles').resolve())
        matches = [b for b in effective(path)['buildings'] if b['uid'] == uid]
        assert len(matches) == 1
        b = matches[0]
        assert value_sha(b) == item['retainedFormSHA256'] and b['buildingCSUID'] == item['buildingCSUID']
        assert not b.get('modelGeometry') and b['foundationPolicy'] == POLICY
        bound(item['evidence'])
        assert item['nativeTerrainDependencies']
        for dep in item['nativeTerrainDependencies']:
            assert dep['url'] in terrain_urls, 'Footing terrain owner was removed; revalidation required'
            tpath = (root / '3d-viewer' / dep['url']).resolve()
            assert tpath.is_relative_to((root / '3d-viewer/city/data').resolve())
            assert terrain_geometry_sha(effective(tpath)) == dep['geometrySHA256'], 'Footing local terrain changed; revalidation required'
        checked.append(uid)
    manifest['basicOnlyFootings'] = registry
    report['basicPodiumFootings'] = applied
    report['retainedBasicOnlyFootingChecks'] = checked
