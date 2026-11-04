"""Bounded review of eleven exact original Harbour Glory/Alexandra components.

Keep every raw foundation, support, projection and foreign-contact warning.
No source geometry/pose edits, generic tolerance changes or publication here.
"""
import sys
import uuid
from fractions import Fraction
from pathlib import Path
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module
from original_supported_model_only_contract_v1_20261025 import verify_metadata

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-harbour-glory-source-physical-review-v1-20261102'
CURRENT = 'government-xl-harbour-glory-eleven-after-shangrila-v2-20261102'
FOUND = 'government-xl-harbour-glory-eleven-current-foundations-support-v1-20261102'
PREVIEW = 'government-xl-harbour-glory-eleven-framed-preview-v4-20261102'
IDENTITY = 'government-xl-harbour-glory-eleven-exact-component-identity-review-v2-20261102'
PAIR = 'government-xl-harbour-glory-current-pair-binding-v1-20261102'
FOREIGN = 'government-xl-harbour-glory-eleven-current-foreign-v2-20261102'
BOUNDARY = 'government-xl-harbour-glory28391-current-boundary-v2-20261102'
EDGE = 'government-xl-harbour-glory-sung-shared-edge-context-v2-20261102'
SUPPORTS = {'landsd/35148:0': 'landsd/247461:0', 'landsd/108870:0': 'landsd/247461:0',
            'landsd/260014:0': 'landsd/247461:0', 'landsd/258158:0': 'landsd/28391:0',
            'landsd/271909:0': 'landsd/28391:0', 'landsd/273684:0': 'landsd/28391:0',
            'landsd/67682:0': 'landsd/28391:0'}
MODES = {'original', 'literal', 'leftF32', 'balancedF32'}


def main():
    out = BASE / BATCH
    lp = HERE / 'local' / (BATCH + '-lease') / 'reservation.json'
    assert not out.exists()
    pins, refs = {}, [Path(__file__), HERE / 'original_supported_model_only_contract_v1_20261025.py']

    def take_path(batch, path):
        if batch not in pins:
            _, pins[batch] = authenticate(BASE / batch)
            refs.append(BASE / batch / 'result.json')
        assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    def take(batch, name='summary.json', local=False):
        return take_path(batch, (HERE / 'local' / batch if local else BASE / batch) / name)

    selected = take(CURRENT + '-runtime', 'selection.json.gz')
    sources = {r['uid']: r['sourceSHA256'] for r in selected['rows']}
    assert len(sources) == 11 and set(SUPPORTS) < set(sources)
    scope = take(CURRENT + '-terrain-scope', 'scope.json')
    forms = {r['uid']: r for r in take(CURRENT + '-terrain-scope', 'form-obligations.json.gz')}
    assert len(forms) == 26
    model_scope = take(CURRENT + '-model-scope')
    assert set(model_scope['uids']) == set(sources)
    for row in model_scope['rows']:
        assert row['currentNativeActorsChecked'] == 7076 and not row['nearbyNativeActors']
        for item in take(CURRENT + '-model-scope', row['uid'].split('/')[1] + '-forms.json.gz'):
            f = item['building']
            assert f['uid'] not in forms or forms[f['uid']] == f
            forms[f['uid']] = f
    assert len(forms) == 27 and set(sources) <= set(forms)
    edge = take(EDGE)
    old_urls = [r['url'] for r in edge['oldTerrainBindings']]
    assert old_urls == ['city/data/government-xl-sung-original-assembly-terrain-20261024.json']
    resources = sorted([('building:' if u.startswith('landsd/') else 'source-form:') + u for u in forms]
                       + ['terrain:city/data/terrain.json', *['terrain:' + u for u in old_urls]])
    if '--owned' not in sys.argv:
        assert not lp.parent.exists()
        c = reservations.claim('harbour-original-physical-' + str(uuid.uuid4()), resources, batch=BATCH, ttl=3600)
        assert c['ok'], c
        return execute_reserved(c['reservation'], lp, [sys.executable, __file__, '--owned'])
    lease = read(lp)
    assert reservations.owns(lease) and set(lease['resources']) == set(resources)
    original = {r['uid']: r['candidate']['entry'] for r in selected['rows']}
    cat = take(PREVIEW, 'catalogue.json', local=True)
    assert verify_metadata(cat['models'], sources, SUPPORTS, original)
    dependency_path = BASE / 'government-xl-harbour-glory-current-dependency-preflight-v1-20261102.json'
    dependencies = read(dependency_path)
    assert {r['uid'] for r in dependencies['rows']} == set(sources)
    assert not any(r['blockers'] for r in dependencies['rows'])
    refs.append(dependency_path)
    for name, expected in dependencies['inputHashes'].items():
        path = ROOT / name
        assert digest(path.read_bytes()) == expected
        refs.append(path)
    for row in selected['rows']:
        path = ROOT / row['candidate']['path']
        assert digest(path.read_bytes()) == sources[row['uid']]
        refs.append(path)
    identity = take(IDENTITY)
    assert identity['identityAccepted'] and identity['sourceSHA256ByUid'] == sources
    proofs = {r['uid']: r['identityProof'] for r in identity['rows']}
    assert set(proofs) == set(sources) and all(all(p.values()) for p in proofs.values())
    for uid in sources:
        take(IDENTITY, uid.split('/')[1] + '-identity-review.json')
    foundation = {}
    for uid in sources:
        d = take(FOUND + '-' + uid.split('/')[1].replace(':', '-') + '-foundations')
        assert {r['mode'] for r in d['rows']} == {'original', 'literal', 'explicitLeftF32', 'explicitBalancedF32'}
        for row in d['rows']:
            assert row['uid'] == uid and row['completeTerrainTriangles'] == row['triangles']
            expected = (31, 10) if uid == 'landsd/247461:0' else (2, 0) if uid == 'landsd/232659:0' else (0, 0)
            assert (row['fullyBuriedTriangles'], row['fullyBuriedUpwardTriangles']) == expected
        foundation[uid] = d
    below = take('government-xl-alexandra247461-current-below-drawn-floor-v2-20261102')
    assert below['sourceSHA256'] == sources['landsd/247461:0'] and len(below['rows']) == 4
    assert all(r['buriedFaces'] == r['belowFloorCoveredFaces'] == 31 and r['upwardBuriedFaces'] == 10
               and not r['aboveFloorOrNotExactlyCoveredFaceIds'] for r in below['rows'])
    below_details = {}
    for mode in MODES:
        detail = take('government-xl-alexandra247461-current-below-drawn-floor-v2-20261102', mode + '.json.gz')
        assert len(detail['buriedFaces']) == 31 and not detail['uncoveredSampledFaces']
        assert all(r['belowFloorFullyCovered'] and r['entirelyBelowObservedGroundMinimum']
                   and r['exactCoverage']['exactProjectionCovered'] and r['exactCoverage']['noToleranceOrBufferCredit']
                   and Fraction(r['exactVerticalSeparationLowerBoundM']) > 0 for r in detail['buriedFaces'])
        below_details[mode] = detail
    caps = {}
    for number in [247461, 28391, 92999, 232659]:
        prefix = FOUND + '-232659' if number == 232659 else CURRENT + '-' + str(number)
        d = take(prefix + '-cap-paths')
        uid = 'landsd/' + str(number) + ':0'
        assert d['sourceSHA256'] == sources[uid] and len(d['rows']) == 4
        for r in d['rows']:
            part = r['completeGroundClearancePartition']
            assert part['negativeNonWallFaces'] == (list(range(1970, 1980)) if number == 247461 else [])
            expected = set(part['negativeSourceFaces']) - set(part['negativeNonWallFaces'])
            assert len(part['paths']) == len(expected) and {p['sourceFace'] for p in part['paths']} == expected
            assert all(p['hasExactSharedEdgeClearCapPath'] for p in part['paths'])
            if number == 247461:
                assert not part['allAffectedHavePaths'] and not d['allFourCompleteGroundClearCapPaths']
                mode = {'left': 'leftF32', 'balanced': 'balancedF32'}.get(r['mode'], r['mode'])
                detail = below_details[mode]
                assert detail['sourceWorldSHA256'] == r['sourceWorldSHA256']
                assert set(part['negativeNonWallFaces']) <= {f['faceIndex'] for f in detail['buriedFaces']}
            else:
                assert part['allAffectedHavePaths'] and d['allFourCompleteGroundClearCapPaths']
        caps[uid] = d
    supports, paths = {}, {}
    for uid, parent in SUPPORTS.items():
        number = uid.split('/')[1].split(':')[0]
        d = take(FOUND + '-' + number + '-support')
        assert d['supportedUid'] == uid and d['supportUid'] == parent
        assert d['sourceSHA256ByUid'] == {u: sources[u] for u in [uid, parent]}
        assert {r['mode'] for r in d['rows']} == MODES
        for row in d['rows']:
            compound = row['compoundFoundation']
            assert compound['completeTerrainTriangles'] == compound['triangles']
            assert compound['fullyBuriedTriangles'] == compound['fullyBuriedUpwardTriangles'] == 0
            assert row['support']['strictContacts'] > 0
        if not d['allFourModesPassed']:
            route = FOUND + '-' + number + '-paths'
            p = take(route)
            assert p['sourceSHA256ByUid'] == d['sourceSHA256ByUid'] and len(p['rows']) == 4
            for row in d['rows']:
                mode = row['mode']
                detail = take(route, mode + '.json.gz')
                assert detail['noIntercomponentJoins'] and detail['originalEndpointHeightGatePreserved']
                assert detail['sourceWorldSHA256'] == row['sourceWorldSHA256ByUid'][uid]
                assert detail['supportWorldSHA256'] == row['sourceWorldSHA256ByUid'][parent]
                assert [r['witness'] for r in detail['rows']] == row['support']['unresolved']
                assert all(r['hasUnrestrictedFiniteAttachment'] and r['passesExistingEndpointHeight']
                           and r['riseAboveEndpointsM'] == 0 and r['maximumResidualM'] <= .001 for r in detail['rows'])
            paths[uid] = p
        supports[uid] = d
    assert set(paths) == {'landsd/' + str(n) + ':0' for n in [35148, 260014, 271909, 273684, 67682]}
    neighbour = take('government-xl-harbour-glory-eleven-current-neighbours-v1-20261102')
    assert neighbour['forms'] == 26 and not neighbour['nativeRows'] and not neighbour['requiredNativeUids']
    assert {r['uid'] for r in neighbour['basicFlags']} == {'landsd/' + str(n) + ':0' for n in [35148, 67682, 108870, 232659, 258158, 271909, 273684]}
    assert all(r['reasons'] == ['increased-neighbour-ground-gap'] and r['uid'] in sources for r in neighbour['basicFlags'])
    pair = take(PAIR)
    assert pair['sourceSHA256ByUid'] == sources and pair['completeUnorderedPairs'] == 55 and len(pair['rows']) == 220
    assert pair['completeFourWorldArraysIdentical'] and pair['completeSourceRecordsIdentical'] and pair['productionClosureIdentical']
    area_interfaces = []
    for row in pair['rows']:
        if 'rawPath' not in row:
            assert row['strictBoundsSeparated']
            continue
        raw = take_path(PAIR, ROOT / row['rawPath'])
        assert raw['allPairsExamined']
        area = [c for c in raw['contacts'] if c['dimension'] == 2]
        if area:
            assert {row['uid'], row['peerUid']} == {'landsd/108870:0', 'landsd/260014:0'}
            assert len(area) == 2
            ys = {Fraction(p[1]) for c in area for p in c['exactPoints']}
            assert len(ys) == 1
            area_interfaces.append(dict(mode=row['mode'], exactSharedRoofY=str(next(iter(ys))), contacts=area))
    assert len(area_interfaces) == 4
    foreign, boundary = take(FOREIGN), take(BOUNDARY)
    assert foreign['foreignPairs'] == 46 and not foreign['independentlyMeasuredOverlappingNativePairs']
    assert not foreign['nativeCompleteFourWorldSeparation']
    external = []
    for row in foreign['rows']:
        if row['foreignUid'] in sources:
            continue
        positive = [r for r in row['modes'] if r['mode'] != 'before-basic' and r['allFiniteContactPairs']]
        if positive:
            assert row['uid'] == 'landsd/28391:0'
            expected = {'landsd/102335:0': 24, 'landsd/261967:0': 15}[row['foreignUid']]
            for mode in positive:
                context = next(r for r in boundary['rows'] if r['foreignUid'] == row['foreignUid'] and r['mode'] == mode['mode'])
                assert mode['allFiniteContactPairs'] == context['finiteContactPairs'] == expected
                assert context['areaContactPairs'] == 0
            external.append(dict(uid=row['uid'], foreignUid=row['foreignUid']))
    assert len(external) == 2
    # The recorded observations must bind actual exported PNGs; a green harness
    # alone cannot attest that the selected original was not visually occluded.
    observed_path = BASE / 'government-xl-harbour-glory-final-source-observations-v1-20261102.json'
    seen = read(observed_path)
    assert seen['visualAcceptance'] and seen['reviewer'] == 'Codex ROOT'
    refs.append(observed_path)
    images = seen['imagesActuallyViewed']
    assert len(images) >= 44
    for item in images:
        path = ROOT / item['path']
        assert digest(path.read_bytes()) == item['sha256'] and item['uid'] in sources
        refs.append(path)
    seen_paths = {i['path'] for i in images}
    prior_preview = 'government-xl-harbour-glory-eleven-current-preview-v2-20261102'
    prior_cat = take(prior_preview, 'catalogue.json', local=True)
    def unchanged_scene_entries(catalogue):
        keys = ['uid', 'sha256', 'worldBounds', 'rootTranslation', 'supportDependencies', 'proceduralWindows']
        return {m['uid']: {k: m.get(k) for k in keys} for m in catalogue['models']}
    assert unchanged_scene_entries(prior_cat) == unchanged_scene_entries(cat)
    # The small232659component has clearer earlier own-views in this identical
    # current scene. Bind them explicitly rather than credit an occluded view.
    for width in [1280, 390]:
        prior_report = take(prior_preview, str(width) + '/staged-browser.json')
        assert prior_report['passed'] and not prior_report['errors']
        views = [v for v in prior_report['views'] if v.get('uid') == 'landsd/232659:0' and 'time' in v]
        assert len(views) == 2
        for view in views:
            assert view['active'] and view['visible'] and view['fullyFramed'] and not view['fallbackFaces']
            assert view['sourceSHA256'] == sources['landsd/232659:0']
            assert str((BASE / prior_preview / str(width) / view['file']).relative_to(ROOT)) in seen_paths
    reports = []
    for width in [1280, 390]:
        r = take(PREVIEW, str(width) + '/staged-browser.json')
        assert r['passed'] and not r['errors']
        views = [v for v in r['views'] if 'time' in v]
        assert len(views) == 22 and {v['uid'] for v in views} == set(sources)
        for view in views:
            assert view['active'] and view['visible'] and view['fullyFramed'] and view['solidAppearance']
            assert not view['fallbackFaces'] and view['pick'] == view['collision'] == view['uid']
            assert view['sourceSHA256'] == sources[view['uid']]
            assert str((BASE / PREVIEW / str(width) / view['file']).relative_to(ROOT)) in seen_paths
        assert r['jointViews'] and all({m['uid']: m['sourceSHA256'] for m in j['models']} == sources
            and all(m['active'] and m['visible'] and not m['fallbackFaces'] for m in j['models']) for j in r['jointViews'])
        path = BASE / PREVIEW / str(width) / 'staged-browser.json'
        reports.append(dict(path=str(path.relative_to(ROOT)), sha256=digest(path.read_bytes())))
    terrain = take(CURRENT + '-inset')
    assert terrain['status'] == 'private-terrain-validator-passed'
    assert set(terrain['uids']) == {'landsd/247461:0', 'landsd/28391:0', 'landsd/92999:0'}
    assert not scope['touchingNativeUids'] and scope['positiveAreaTerrainOverlaps'] == 0
    assert edge['contract'] == 'existing-finite-native-shared-edge-context-v1' and len(edge['rows']) == 1
    assert edge['rows'][0]['comparison']['passed'] and edge['rows'][0]['comparison']['toleranceM'] == .01
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    sha = digest(manifest.read_bytes())
    assert sha == selected['manifestSHA256'] == identity['currentManifestSHA256'] == pair['currentManifestSHA256'] == boundary['currentManifestSHA256'] == edge['currentManifestSHA256']
    refs.append(manifest)
    assert reservations.owns(lease)
    result = dict(uids=list(sources), sourceSHA256ByUid=sources, requiredOriginalAssembly=sources,
        supportByUid=SUPPORTS, identityAccepted=True, identityProofByUid=proofs,
        identityProof=proofs['landsd/35148:0'], sourceSpecificPhysicalInterpretationAccepted=True,
        completeNeighbourInterpretationAccepted=True, visualAcceptance=True,
        leaseResources=resources, currentManifest=dict(path=str(manifest.relative_to(ROOT)), sha256=sha),
        currentManifestSHA256=sha, rawCanonicalFailuresPreserved=True, rawFoundations=foundation,
        rawSupportRows=supports, originalAttachmentPaths=paths, completeClearCapPartitions=caps,
        completeBelowDrawnFloorContext=below, rawNeighbourFlags=neighbour['basicFlags'],
        acceptedForeignBoundaryPairs=external, unresolvedExternalBasicContacts=[],
        rawForeignContacts=foreign['rows'], exactOriginalSharedRoofInterfaces=area_interfaces,
        unchangedBasicSupportProofs=[], imagesActuallyViewed=images, browserReports=reports,
        sourceGeometryChanges=0, sourcePoseChanges=0, genericThresholdChanges=0,
        terrainEdits=True, publicTerrainWritesPerformed=False, installationApproved=False, publication=False,
        sourceEvidenceInterpretationUsedAI=True, aiGeometryModelling=False,
        interpretation=[
            'Accept only these exact eleven government components, fixed1x/HKPD and unchanged node poses. Current exact component identity is separate from whole-complex completeness; both raw projection shape failures remain.',
            'Retain all31 sampled buried247461faces and10upward sourcefaces. Exact complete finite projected coverage places all31 wholly below actual drawn floor. Other negative walls have complete on-original clear-cap paths.232659has two buriedwallfaces and complete clear-cap paths; no basement architectural role or new horizontal floor is invented. Other nine originals have zero fully buried/upward facets.',
            'All seven original tower/support compounds have complete ground coverage and zero buried/upward facets. Two strict interfaces pass directly; all remaining warnings on five towers have original shared-edge paths to independently measured strict anchors, zero rise beyond endpoint ceiling and unchanged1mm incidence. The direct predicates remain false; no fabricated root, shifted source or structural certification is claimed.',
            'All55source pairs were checked in four coordinate streams and rebound by complete source-array equality. The only shared-plane area contacts are two original roof-facet intersections between108870and260014 per stream, at one exact shared roof height. These are adjoining authored source components; their full raw line/point/area records remain unchanged.',
            'Every27union form remains an obligation. Seven terrain BASIC-gap warnings belong to these coimported originals and are resolved by their current original source grounding/support proofs, not by dropping their obligations. No old native actor bounds touch and no old terrain has positive area overlap. The Sung shared70medge passes the unchanged complete finite1cm checker.',
            'Two external28391contacts are confined to the recorded complete facing boundary strips of coarse BASIC102335and261967; all finite points/lines and the new261967delta remain. No shared-plane area contacts, source pose edits, neighbour removal or generic centimetre collision threshold are accepted. This is bounded exact original/source-versus-proxy interpretation.',
            *seen['observations'],
            'Current desktop/mobile source and joint loading,picking,collision,failure/retry and runtime-budget checks pass. No measuredFPS, physical-phone,every-facade or whole-landmark claim. Guarded publication, live verification and independent whole521/oldasset/global-support readback remain mandatory.'])
    save(out / 'ROOT-PHYSICAL-REVIEW.json', result)
    save(out / 'ROOT-SOURCE-REVIEW.json', result)
    module('harbour_original_physical_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH, 'bounded-exact-original-harbour-glory-component-assembly-review', list(dict.fromkeys(refs)), result)


if __name__ == '__main__':
    main()
