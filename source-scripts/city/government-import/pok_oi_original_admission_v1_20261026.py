"""Closed, immutable-source admission for the reviewed Pok Oi original pair.

This profile grants no generic wall, terrain, support or collision exception.
Canonical publisher guards and all other installed actors remain untouched.
"""
from pathlib import Path
from fractions import Fraction
from run import ROOT, HERE, read, digest
from china_ferry_current_foundations_v1_20261020 import authenticate

MAIN, PODIUM = 'landsd/213579:0', 'landsd/71329:0'
SOURCES = {MAIN: 'bb031a70c651cbee10f12cbc0f9d5608dbdb90f5fb976bd4e3ad19caf7556522',
           PODIUM: '3dcaacddbaca34d781fb2ae236b612018167e63fbc73c9c62d24429faa1a74ea'}
MAIN_WALLS = [3977,3978,4018,4019,4020,4044,4045,7774,7775,7783,7784,7795,7796,7802,7803,7804,7805,7806,7807,8168]
PODIUM_WALLS = list(range(3,27))+[942,943,946,947,967,968,969,972,2226,2427,2428,2430,2431,2432,2433,2538,2539,2542,2543,2545,2546,2551,2552,2555,2556,2559,2560,2564,2565,2566]+list(range(2593,2689))+[2699,2700,2701]
COLUMNS = [list(range(3,27)), list(range(2617,2641))]
GRAPH = {PODIUM: MAIN}
PREFIX = 'government-xl-after-ying-hoi-pok-oi-'
BASE = ROOT / 'docs/astra-city/government-import'


def verify_closed_contract(config, review):
    assert config['sources'] == review['sourceSHA256ByUid'] == SOURCES
    assert config['supportByUid'] == review['supportByUid'] == GRAPH
    assert review['runtimeAvailabilityDependenciesByUid'] == GRAPH
    assert review['physicalSupportByUid'] == {}, 'Availability is not strict physical support'
    assert review['retainedBasicSupportDependencies'] == [] and review['retainedNativeEntries'] == {}
    assert review['acceptedGroundWallFacesByUid'] == {MAIN: MAIN_WALLS, PODIUM: PODIUM_WALLS}
    assert review['groundedIsolatedWallComponents'] == COLUMNS
    assert review['belowGradeLowerWallStripFaces'] == [2699]
    assert review['terrainEdits'] is False and review['sourceGeometryChanges'] == review['sourcePoseChanges'] == 0
    assert config['currentNativeActors'] == 6968 and config['neighbourForms'] == review['completeCurrentNeighbourChecks'] == 8
    return True


def replay(config, review):
    verify_closed_contract(config, review)
    refs, pins = [Path(__file__)], {}
    def take(suffix, filename='summary.json'):
        batch = PREFIX + suffix + '-20261026'
        if batch not in pins:
            pins[batch] = authenticate(BASE / batch)[1]; refs.append(BASE / batch / 'result.json')
        path = BASE / batch / filename
        assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
        refs.append(path); return read(path)
    selection = take('pair-bound-ground-v1', 'selection.json.gz')
    assert {r['uid']:r['sourceSHA256'] for r in selection['rows']} == SOURCES
    for row in selection['rows']:
        asset = ROOT / row['candidate']['path']; assert digest(asset.read_bytes()) == SOURCES[row['uid']]; refs.append(asset)
        form = row['source']['building']; tile = ROOT / '3d-viewer' / row['source']['tile']
        assert next(r for r in read(tile)['buildings'] if r['uid'] == row['uid']) == form
        assert form['name'] == 'POK OI HOSPITAL' and form['parent'] == 'way/375224148'
        assert row['candidate']['entry']['rootTranslation'] == [-834500,0,816500]
        assert not row['candidate']['entry'].get('verticalPlacementOffsetHKPD',0)
        refs.append(tile)
        identity = take('pair-bound-identity-v1',row['uid'].split('/')[1]+'/identity.json')
        assert identity['originalOwnership']['sourceGraphVerified'] and identity['exactCurrentComponentRoute']['qualified']
        assert identity['freshCurrentIdentity']['exactObjectAndCSUID'] and identity['exactWholeCellCoverage']['covered']
        assert identity['freshCurrentIdentity']['targetCoveredBySourceProjection'] > .99
        assert identity['originalOwnership']['originalRootName'] == row['modelId']
        foundation = take('main-foundation-v1' if row['uid']==MAIN else 'podium-foundation-v1')
        assert foundation['establishedFoundationPolicyPassed'] and len(foundation['rows']) == 4
        assert all(r['completeTerrainTriangles']==r['triangles']==row['triangles'] and r['fullyBuriedUpwardTriangles']==r['fullyBuriedTriangles']==0 for r in foundation['rows'])
    for uid, ids in [(MAIN,MAIN_WALLS),(PODIUM,PODIUM_WALLS)]:
        suffix = uid.split('/')[1].split(':')[0]+'-complete-clearance-v1'
        clearance = take(suffix)
        assert len(clearance['rows']) == 4
        for row in clearance['rows']:
            assert row['exactAffectedFaces'] == ids and row['negativeNonWallFaces']==[] and row['allAffectedWallLike']
            if uid==MAIN:
                assert row['compoundCapPathsPassed'] and row['allAffectedHaveExposedHighestVertex']
        for mode in ['original','literal','left','balanced']:
            cap = take(suffix,mode+'-cap-paths.json.gz')['proof']
            if uid==PODIUM:
                assert [r['sourceFace'] for r in cap['paths'] if not r['hasExactSharedEdgeClearCapPath']] == sorted(i for g in COLUMNS for i in g)
                assert next(r for r in cap['paths'] if r['sourceFace']==2699)['hasExactSharedEdgeClearCapPath']
                roots = take('podium-grounded-components-v1',mode+'.json.gz')
                assert [r['sourceFaces'] for r in roots['rows']] == COLUMNS
                for r in roots['rows']:
                    assert r['positiveTerrainContactPairs']==24 and r['directFiniteTerrainContact'] and r['everyHighestWallVertexExposed']
                    assert r['completeContacts']['allPairsExamined'] and not r['completeContacts']['sourceFacesOmitted']
                thin = take('podium-thin-wall-vertices-v1',mode+'.json.gz')
                assert thin['sourceFace']==2699 and len(thin['vertices'])==3
                assert all(r['finiteGroundProofs'] and not r['aboveEveryOverlappingGroundFace'] for r in thin['vertices'])
                # A retained below-grade wall strip, not a fabricated exposed vertex.
                assert all(Fraction(r['minimumGapM']) < 0 for r in thin['vertices'])
    scope = take('pair-bound-scope-v1')
    assert all(r['currentNativeActorsChecked']==6968 and r['nearbyNativeActors']==[] for r in scope['rows'])
    forms = {}
    for row in scope['rows']:
        for r in take('pair-bound-scope-v1',row['uid'].split('/')[1]+'-forms.json.gz'):
            forms[r['building']['uid']] = r['building']
    assert len(forms)==8 and set(review['leaseResources']) == {'building:'+u for u in forms}
    foreign = take('pair-bound-foreign-v1')
    assert foreign['foreignPairs']==12
    expected = {(MAIN,PODIUM):54,(PODIUM,MAIN):154,(PODIUM,'landsd/56488:0'):14}
    for row in foreign['rows']:
        for mode in row['modes']:
            count = 0 if mode['mode']=='before-basic' else expected.get((row['uid'],row['foreignUid']),0)
            assert mode['positiveContactPairs']==count
    roles = take('pair-roles-v1')
    assert roles['sourceSHA256ByUid']==SOURCES and len(roles['rows'])==4
    assert all(r['contactCount']==238 and r['roles']=={'transverse-surface-crossing':238} for r in roles['rows'])
    metrics = take('pair-bound-ground-v1','metrics.json')
    from primrose_compound_foundation_v2_20261015 import module
    policy = module('pok_oi_unmodified_acceptance',HERE/'acceptance-policy.py');refs.append(HERE/'acceptance-policy.py')
    for row in metrics['rows']:
        assert policy.reasons(dict(state='runtime-validated-awaiting-acceptance',sourceSHA256=SOURCES[row['uid']],identityProof=review['identityProof']),row,metrics['profiles']['mobile'])==['terrain-intersects-source-over-0.5m']
    browser = take('pair-private-preview-v1')
    assert browser['allBrowserDiagnosticsPassed'] and browser['canonicalPublisherDryRunPassed']
    assert browser['proposedSupportByUid']==GRAPH
    for width in [1280,390]:
        report = take('pair-private-preview-v1',str(width)+'/staged-browser.json')
        assert report['passed'] and report['errors']==[]
        views = [v for v in report['views'] if 'time' in v]
        assert len(views)==4
        for v in views:
            assert v['sourceSHA256']==SOURCES[v['uid']] and v['fullyFramed'] and v['solidAppearance'] and not v['fallbackFaces']
            assert v['pick']==v['collision']==v['uid']
        assert any({r['uid'] for r in j['models']}==set(SOURCES) and all(r['active'] and r['visible'] and not r['fallbackFaces'] for r in j['models']) for j in report['jointViews'])
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == selection['manifestSHA256'] == scope['currentManifestSHA256'] == review['currentManifest']['sha256']
    refs.append(manifest)
    for q in review['imagesActuallyViewed']+review['diagnosticImagesActuallyViewed']:
        path = ROOT/q['path'];assert digest(path.read_bytes())==q['sha256'];refs.append(path)
    return list(dict.fromkeys(refs))
