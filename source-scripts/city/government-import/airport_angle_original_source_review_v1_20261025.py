"""Bind the exact Airport Angle Station original pair to completed source review."""
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles

BASE = ROOT / 'docs/astra-city/government-import'
P = 'government-xl-airport-angle-two-after-pier-'
BATCH = P + 'final-source-review-v1-20261025'
SOURCES = {'landsd/177765:0': '5bb87aa10f46acd79787b43ed653e32d951eace276a50e0a0f7f16ec391fab4c',
           'landsd/176472:0': '00f5a12bd7bd460af8346b41e5bb0e14be79f09c3efb3be99f25016c44edf2c3'}
COUNTS = {'landsd/177765:0': 17401, 'landsd/176472:0': 16483}


def main():
    out = BASE / BATCH
    assert not out.exists()
    refs, pins = [Path(__file__)], {}
    def take(tag, name='summary.json'):
        batch = P + tag + '-20261025'
        if batch not in pins:
            pins[batch] = authenticate(BASE / batch)[1]
            refs.append(BASE / batch / 'result.json')
        path = BASE / batch / name
        assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)
    selected = take('seam-runtime-v2', 'selection.json.gz')
    assert {r['uid']: r['sourceSHA256'] for r in selected['rows']} == SOURCES
    take('attributes-v1', 'attributes.json.gz')
    raw = {}
    for row in selected['rows']:
        uid = row['uid']; number = uid.split('/')[1].split(':')[0]
        assert row['triangles'] == COUNTS[uid]
        asset = ROOT / row['candidate']['path']
        assert digest(asset.read_bytes()) == SOURCES[uid]
        refs.append(asset)
        assert row['candidate']['entry']['rootTranslation'] == [-834500, 0, 816500]
        assert row['candidate']['entry'].get('verticalPlacementOffsetHKPD', 0) == 0
        identity = take('identity-v1', number + ':0/identity.json')
        assert identity['sourceSHA256'] == SOURCES[uid]
        assert identity['originalOwnership']['sourceGraphVerified']
        assert identity['exactCurrentComponentRoute']['qualified']
        assert identity['freshCurrentIdentity']['exactObjectAndCSUID']
        assert identity['exactWholeCellCoverage']['covered']
        assert identity['exactWholeCellCoverage']['wholeOriginalFacesAccounted'] == COUNTS[uid]
        raw[uid] = identity['reasons']
        take(number + '-identity-views-v1')
        for name in ['whole-source-plan.png', 'whole-source-perspectives.png']:
            image = BASE / (P + number + '-identity-views-v1-20261025') / name
            assert digest(image.read_bytes()) == pins[P + number + '-identity-views-v1-20261025'][str(image.relative_to(ROOT))]
            refs.append(image)
        foundation = take(number + '-foundations-v2')
        assert foundation['establishedFoundationPolicyPassed'] and len(foundation['rows']) == 4
        for r in foundation['rows']:
            assert r['completeTerrainTriangles'] == r['triangles'] == COUNTS[uid]
            assert r['fullyBuriedUpwardTriangles'] == 0 and r['fullyBuriedAreaFraction'] <= .001
            assert r['fullyBuriedTriangles'] == (1 if number == '176472' else 0)
        ground = take(number + '-complete-ground-v2')
        assert len(ground['rows']) == 4
        for r in ground['rows']:
            assert r['negativeNonWallFaces'] == ([460] if number == '176472' else [])
            cap = take(number + '-complete-ground-v2', r['mode'] + '-cap-paths.json.gz')['proof']
            assert len(cap['paths']) == (19 if number == '176472' else 21)
            assert all(x['hasExactSharedEdgeClearCapPath'] for x in cap['paths'])
        if number == '176472':
            t = decode_original_world_triangles(asset.read_bytes())[460]
            n = np.cross(t[1] - t[0], t[2] - t[0])
            assert n[1] / np.linalg.norm(n) < -.999
    permit = take('complete-permit-v1')
    assert permit['permit'] == 'PR11/2006(OP)' and permit['exactSelectedPermitMembership']
    take('primary-records-v1')
    compound = take('compound-projection-v1')
    assert compound['completeOriginalFaces'] == sum(COUNTS.values())
    for r in compound['rows']:
        assert r['ownCoverageByWholeOriginalAssembly'] >= .99
        assert r['wholeCellCoveredByOriginalAssembly']
        assert not r['sourceExcessOverlapOutsideCurrentAssemblyByForeignUid']
    pairs = take('original-pairs-v1')
    assert len(pairs['rows']) == 4
    assert [r['positiveSurfaceContacts'] for r in pairs['rows']] == [258, 258, 260, 260]
    continuous = take('continuous-v2')
    assert all(r['upwardContinuousMinimumGapM'] >= -.5 for r in continuous['rows'])
    assert all(not r['stillUncoveredFaces'] for r in take('exact-coverage-v2')['rows'])
    patch = take('seam-terrain-v2')
    assert patch['status'] == 'private-terrain-validator-passed' and patch['terrainTriangles'] == 3358
    scope = take('seam-scope-v2', 'scope.json')
    assert scope['currentNativeActors'] == 6944 and not scope['touchingNativeUids']
    assert not scope['terrainContacts'] and scope['positiveAreaTerrainOverlaps'] == 0
    forms = {f['uid']: f for f in take('seam-scope-v2', 'form-obligations.json.gz')}
    model = take('model-scope-v1')
    for r in model['rows']:
        assert not r['nearbyNativeActors'] and r['currentNativeActorsChecked'] == 6944
        for item in take('model-scope-v1', r['uid'].split('/')[1] + '-forms.json.gz'):
            f = item['building']
            if f['uid'] in forms: assert forms[f['uid']] == f
            forms[f['uid']] = f
    assert set(forms) == set(SOURCES)
    neighbours = take('neighbours-v2')
    assert neighbours['forms'] == 2 and not neighbours['flagged'] and neighbours['ordinaryFlagged'] == 0
    checkpoint = take('progress-checkpoint-v1', 'remaining-work.json')
    images = checkpoint['imagesActuallyViewedByRoot']
    assert len(images) == 8
    for image in images:
        path = ROOT / image['path']; assert digest(path.read_bytes()) == image['sha256']; refs.append(path)
    reports = []
    for width in [390, 1280]:
        report = take('unapproved-browser-v1', str(width) + '/staged-browser.json')
        assert report['passed'] and not report['errors']
        views = [v for v in report['views'] if 'time' in v]
        assert len(views) == 4
        for v in views:
            assert v['active'] and v['visible'] and v['fullyFramed'] and v['solidAppearance']
            assert not v['fallbackFaces'] and v['pick'] == v['collision'] == v['uid']
            assert v['sourceSHA256'] == SOURCES[v['uid']]
        assert all({m['uid'] for m in j['models'] if m['active']} == set(SOURCES) for j in report['jointViews'])
        path = BASE / (P + 'unapproved-browser-v1-20261025') / str(width) / 'staged-browser.json'
        reports.append(dict(path=str(path.relative_to(ROOT)), sha256=digest(path.read_bytes())))
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == selected['manifestSHA256']; refs.append(manifest)
    resources = sorted(['building:' + u for u in forms] + ['terrain:city/data/terrain.json'])
    result = dict(uids=list(SOURCES), sourceSHA256ByUid=SOURCES, requiredOriginalAssembly=SOURCES,
                  supportByUid={}, retainedNativeUids=[], reviewer='ROOT', identityAccepted=True,
                  identityProof=dict(exactObjectId=True, exactBuildingCSUID=True, uniqueViewerMatch=True, identityAccepted=True),
                  currentManifest=dict(path=str(manifest.relative_to(ROOT)), sha256=digest(manifest.read_bytes())),
                  sourceSpecificPhysicalInterpretationAccepted=True, completeNeighbourInterpretationAccepted=True,
                  completeFourWorldFoundations=True, completeCurrentNeighbourChecks=2, totalNeighbourForms=2,
                  terrainAffectedForms=2, leaseResources=resources, visualAcceptance=True,
                  imagesActuallyViewed=images, browserReports=reports, originalSourceReviewAccepted=True,
                  rawIdentityReasonsRetained=raw, rawBasalAndExtentFailuresRetained=True,
                  sourceGeometryChanges=0, sourcePoseChanges=0, aiGeometryModelling=False,
                  sourceEvidenceInterpretationUsedAI=True, installationApproved=False,
                  observations=[
                      'Accept this exact two-member government station assembly. Exact native roots/graphs, unique ObjectID/CSUID routes, complete GeoRef cells and complete two-CSUID permit establish identity. Original diagrams show tall ground pillars with broad elevated cable gantries, platforms and roof extensions; coarse ground footprints do not bound these elevated original components. Compound footprint coverage exceeds 99 percent for each member. Retain the failed individual footprint/10m extent predicates (18.873669/43.120926m); this is no generic threshold change or name/proximity exemption.',
                      'The two originals form angled gantries at one station, not duplicated whole models. Their 258/260 authored surface junction contacts remain, without a zero-interpenetration or engineering-watertightness requirement. Each has its own original ground structure, so no invented support dependency is added. All current affected forms are these same two members; there are no current native neighbours or foreign positive footprint overlaps in scope.',
                      'Existing four-world foundation policy passes with zero upward burial. Preserve 176472 basal closure460 below grade at area fraction0.000587448 (limit0.001); normalY<-0.999. All19affected walls have exact clear cap paths;177765 has21. Raw nonwall/cap aggregate remains false. ROOT inspected the exact basal diagnostic and all source diagrams. No geometry modification or excavation to expose a downward closure.',
                      'Final3358triangle terrain retains3233old candidate faces plus125boundedFloat32seam covers; exact residual coverage and both current neighbour checks pass. Approximate28face residual flags are preserved beside the exact proof. Existing coastal/height/seam limits remain unchanged.',
                      'ROOT inspected all8private desktop/mobile day/night exports. Original angled roofs, pillars, equipment and stairs are readable; original materials remain dark at night. First mobile177765 capture shows companionBASIC during loading; later176472 images and final joint checks show both originals. No procedural windows. Fresh live exports and independent all6944oldassets/full521/globalBASIC readback remain mandatory.'
                  ])
    save(out / 'ROOT-PHYSICAL-REVIEW.json', result)
    save(out / 'ROOT-SOURCE-REVIEW.json', result)
    module('airport_angle_review_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH, 'bounded-original-airport-angle-source-role-physical-and-visual-review', list(dict.fromkeys(refs)), result)


if __name__ == '__main__': main()
