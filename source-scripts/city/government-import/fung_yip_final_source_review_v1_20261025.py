"""Bind exact Fung Yip originals to current ground, neighbours and inspected views."""
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_supported_catalogue_scope_v1_20261024 import verify as verify_support_scope

BASE = ROOT / 'docs/astra-city/government-import'
P = 'government-xl-fung-yip-after-inone-'
BATCH = P + 'final-source-review-v1-20261025'
TOWER, PODIUM = 'landsd/254815:0', 'landsd/79883:0'
SUPPORTS = {TOWER: PODIUM}
RETAINED = {'landsd/79882:0', 'landsd/12728:0', 'landsd/338946:0'}
BROWSER = P + 'unapproved-browser-v4-20261025'


def main():
    out = BASE / BATCH
    assert not out.exists()
    refs, pins, receipts = [Path(__file__)], {}, {}

    def take(batch, name='summary.json', local=False):
        if batch not in pins:
            receipts[batch], pins[batch] = authenticate(BASE / batch)
            refs.append(BASE / batch / 'result.json')
        if name == 'result.json' and not local:
            return receipts[batch]
        p = (HERE / 'local' / batch if local else BASE / batch) / name
        assert digest(p.read_bytes()) == pins[batch][str(p.relative_to(ROOT))]
        refs.append(p)
        return read(p)

    identity = take('government-xl-fung-yip-independent-permit-identity-review-v1-20261025', 'ROOT-IDENTITY-REVIEW.json')
    assert identity['identityAccepted'] and not identity['boundaryCertificateAccepted']
    sources = identity['sourceSHA256ByUid']
    selected = take(P + 'seam-runtime-v2-20261025', 'selection.json.gz')
    rows = {r['uid']: r for r in selected['rows']}
    assert {u: r['sourceSHA256'] for u, r in rows.items()} == sources
    assert set(sources) == {TOWER, PODIUM}
    attrs = take(P + 'attributes-v1-20261025', 'attributes.json.gz')
    assert attrs['startEndAllInputsVerified']
    attrs = {r['uid']: r for r in attrs['rows']}
    worlds = {}
    for u, row in rows.items():
        asset = ROOT / row['candidate']['path']
        assert digest(asset.read_bytes()) == sources[u] == attrs[u]['sourceSHA256']
        refs.append(asset)
        tile = ROOT / '3d-viewer' / row['source']['tile']
        assert next(f for f in read(tile)['buildings'] if f['uid'] == u) == row['source']['building']
        refs.append(tile)
        assert row['candidate']['entry']['rootTranslation'] == [-834500, 0, 816500]
        ix = np.asarray(attrs[u]['completeOriginalIndex']).reshape(-1, 3)
        triangles = {'original': decode_original_world_triangles(asset.read_bytes())}
        for mode, key in [('literal', 'completeLiteralWorldPosition'),
                          ('leftF32', 'completeExplicitLeftAssociatedFloat32WorldPosition'),
                          ('balancedF32', 'completeExplicitBalancedFloat32WorldPosition')]:
            triangles[mode] = np.asarray(attrs[u][key]).reshape(-1, 3)[ix]
        assert all(len(t) == row['triangles'] for t in triangles.values())
        worlds[u] = {m: digest(t.astype('<f8').tobytes()) for m, t in triangles.items()}
    assert sum(r['triangles'] for r in rows.values()) == 10573

    rebound = take(P + 'original-contact-rebind-v1-20261025')
    assert rebound['completeRendererAttributeRowsIdentical'] and rebound['sourceSHA256ByUid'] == sources
    old = 'government-xl-fung-yip-full-native-domain-'
    strict = take(old + 'support-followthrough-v1-20261024-254815-79883-strict')
    paths = take(old + 'support-followthrough-v1-20261024-254815-79883-paths')
    assert strict['sourceSHA256ByUid'] == sources and not strict['allFourModesPassed']
    assert paths['allUnresolvedHaveFinitePaths'] and len(paths['rows']) == len(strict['rows']) == 4
    for s, p in zip(strict['rows'], paths['rows']):
        mode = s['mode']
        assert mode == p['mode']
        assert s['sourceWorldSHA256ByUid'] == {u: worlds[u][mode] for u in sources}
        assert p['sourceWorldSHA256'] == worlds[TOWER][mode] and p['supportWorldSHA256'] == worlds[PODIUM][mode]
        assert s['support']['strictContacts'] == 143 and len(s['support']['unresolved']) == 32
        assert p['targets'] == p['verifiedPaths'] == 32 and p['remaining'] == 0
        assert s['compoundFoundation']['fullyBuriedTriangles'] == s['compoundFoundation']['fullyBuriedUpwardTriangles'] == 0
    compound = take(old + 'tower-compound-clearance-v1-20261024')
    assert compound['sourceSHA256'] == sources[TOWER] and compound['supportSHA256'] == sources[PODIUM]
    assert len(compound['rows']) == 4
    for r in compound['rows']:
        assert len(r['exactAffectedFaces']) == 19 and {6520, 6525} <= set(r['exactAffectedFaces'])
        assert r['allAffectedWallLike'] and not r['negativeNonWallFaces'] and r['compoundCapPathsPassed']
        assert not r['allAffectedHaveExposedHighestVertex']

    foundations = []
    for u, row in rows.items():
        n = u.split('/')[1].split(':')[0]
        batch = f'government-xl-fung-yip-{n}-after-inone-seam-foundations-v2-20261025'
        f = take(batch)
        assert f['uids'] == [u] and len(f['rows']) == 4
        assert {r['mode'] for r in f['rows']} == {'original', 'literal', 'explicitLeftF32', 'explicitBalancedF32'}
        for r in f['rows']:
            assert r['uid'] == u and r['triangles'] == r['completeTerrainTriangles'] == row['triangles']
            assert r['fullyBuriedTriangles'] == r['fullyBuriedUpwardTriangles'] == 0
            take(batch, r['mode'] + '.json')
        foundations.append(dict(uid=u, batch=batch, completeFaces=row['triangles'], coordinateStreams=4))
        ground = take(P + ('tower' if u == TOWER else 'podium') + '-complete-ground-v2-20261025')
        assert ground['sourceSHA256'] == sources[u] and len(ground['rows']) == 4
        for r in ground['rows']:
            assert r['completeSourceFaces'] == row['triangles'] and not r['negativeNonWallFaces']
            if u == TOWER:
                assert r['noAffectedFaces'] and not r['exactAffectedFaces']
            else:
                assert set(r['exactAffectedFaces']) == {49, 50, 120, 122, 143, 253, 256, 257}
                assert r['compoundCapPathsPassed'] and r['allAffectedWallLike'] and r['allAffectedHaveExposedHighestVertex']
    continuous = take(P + 'seam-continuous-v2-20261025')
    assert len(continuous['rows']) == 2
    assert all(not r['continuousAffectedFaces'] and not r['otherAffectedFaces'] and r['upwardContinuousMinimumGapM'] >= -.5 for r in continuous['rows'])
    coverage = take(P + 'exact-coverage-v2-20261025')
    assert all(not r['stillUncoveredFaces'] for r in coverage['rows'])
    patch = take(P + 'replacement-binding-v2-20261025', 'result.json')['candidate']
    assert patch['sha256'] == 'b344ed259099f66b74976eb8ed8c0e1a8fbfca5da8c560f5a74b8eda6d8fc3af'
    terrain = ROOT / patch['path']
    assert digest(terrain.read_bytes()) == patch['sha256'] and patch['triangles'] == 18418
    refs.append(terrain)
    scope = take(P + 'seam-scope-v2-20261025', 'scope.json')
    forms = {f['uid']: f for f in take(P + 'seam-scope-v2-20261025', 'form-obligations.json.gz')}
    assert len(forms) == scope['intersectingForms'] == 56 and scope['currentNativeActors'] == 6936
    assert set(scope['touchingNativeUids']) == RETAINED and scope['positiveAreaTerrainOverlaps'] == 1
    assert {r['url'] for r in scope['terrainContacts'] if r['coarseOverlapAreaM2'] > 0} == {patch['replaces']['url']}
    assert len(scope['terrainContacts']) == 2
    regression = take(P + 'native-regression-v2-20261025')
    assert regression['forms'] == 56 and not regression['basicFlags']
    assert set(regression['requiredNativeUids']) == set(regression['nativeResolved']) == RETAINED
    assert all(r['passed'] and r['terrain']['newlyWhollyBuried'] == r['terrain']['newlyUpwardWhollyBuried'] == 0 for r in regression['nativeRows'])
    modelscope = take(P + 'model-scope-v2-20261025')
    assert all(r['currentNativeActorsChecked'] == 6936 for r in modelscope['rows'])
    for r in modelscope['rows']:
        for f in take(P + 'model-scope-v2-20261025', r['uid'].split('/')[1] + '-forms.json.gz'):
            assert forms[f['building']['uid']] == f['building']
    contacts = take(P + 'foreign-contacts-v2-20261025')
    assert contacts['foreignPairs'] == 7
    for r in contacts['rows']:
        if r['foreignUid'] not in sources:
            assert all(m['positiveContactPairs'] == 0 for m in r['modes'])
    native = take(P + 'native-contacts-v2-20261025')
    assert len(native['rows']) == 4
    assert all(m['areaContactPairs'] == 0 for r in native['rows'] for m in r['modes'])
    take(P + 'native-bindings-v2-20261025', 'result.json')

    inspection = take(P + 'private-export-inspection-v4-20261025', 'ROOT-PRIVATE-EXPORT-INSPECTION.json')
    assert inspection['privateSceneFramingAccepted'] and inspection['reviewer'] == 'ROOT'
    inspected = {i['path']: i['sha256'] for i in inspection['imagesActuallyViewed']}
    assert len(inspected) == 20
    images, retained_images, reports = [], [], []
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    current = {m['uid']: m for url in read(manifest)['officialModelCatalogues'] for m in read(ROOT / '3d-viewer' / url)['models']}
    assert len(current) == 6936
    for width in [1280, 390]:
        report = take(BROWSER, f'{width}/staged-browser.json')
        assert report['passed'] and not report['errors']
        views = [v for v in report['views'] if 'time' in v]
        assert len(views) == 4 and len(report['retainedNativeOwnViews']) == 6
        for v in views:
            assert v['fullyFramed'] and v['solidAppearance'] and not v['fallbackFaces'] and v['active'] and v['visible']
            assert v['pick'] == v['collision'] == v['uid'] and v['sourceSHA256'] == sources[v['uid']]
        for v in report['retainedNativeOwnViews']:
            assert v['uid'] in RETAINED and v['sourceSHA256'] == current[v['uid']]['sha256']
            assert v['originalTriangles'] == current[v['uid']]['triangles'] and v['active'] and v['visible'] and v['fullyFramed'] and not v['fallbackFaces']
            assert all(v['meshVisibility']) and not any(v['wireframeFlags'])
        for collection, output in [(views, images), (report['retainedNativeOwnViews'], retained_images)]:
            for v in collection:
                p = BASE / BROWSER / str(width) / v['file']
                key, sha = str(p.relative_to(ROOT)), digest(p.read_bytes())
                assert sha == inspected[key] == pins[BROWSER][key]
                refs.append(p)
                output.append(dict(path=key, sha256=sha, uid=v['uid'], width=width, time=v['time']))
        assert report['jointViews'] and all({m['uid']: m['sourceSHA256'] for m in j['models']} == sources and all(m['active'] and m['visible'] and not m['fallbackFaces'] for m in j['models']) for j in report['jointViews'])
        if width == 390:
            failures = [v for v in report['views'] if v.get('phase') == 'failed-download']
            assert len(failures) == 2 and {v['uid'] for v in failures if v['fallbackRetained']} == set(sources)
        p = BASE / BROWSER / str(width) / 'staged-browser.json'
        reports.append(dict(path=str(p.relative_to(ROOT)), sha256=digest(p.read_bytes())))
    catalogue = take(BROWSER, 'catalogue.json', local=True)
    assert verify_support_scope(catalogue['models'], sources, SUPPORTS)
    assert dict(path=str(manifest.relative_to(ROOT)), sha256=digest(manifest.read_bytes())) == identity['currentManifest']
    refs.append(manifest)
    resources = {('building:' if u.startswith('landsd/') else 'source-form:') + u for u in forms}
    resources |= {'terrain:city/data/terrain.json'} | {'terrain:' + r['url'] for r in scope['terrainContacts']}
    result = dict(
        uids=sorted(sources), sourceSHA256ByUid=sources, requiredOriginalAssembly=sources,
        supportByUid=SUPPORTS, reviewer='ROOT', currentManifest=identity['currentManifest'],
        identityAccepted=True, identityProof=identity['identityProof'], identityProofByUid=identity['identityProofByUid'],
        sourceSpecificPhysicalInterpretationAccepted=True, completeNeighbourInterpretationAccepted=True,
        completeFourWorldFoundations=True, fourWorldFoundationEvidence=foundations,
        completeCurrentNeighbourChecks=56, visualAcceptance=True, imagesActuallyViewed=images,
        retainedImagesActuallyViewed=retained_images, browserReports=reports,
        retainedNativeUids=sorted(RETAINED), retainedNativeRegression=regression,
        exactTerrainReplacement=patch['replaces'], leaseResources=sorted(resources),
        installedMetadataChanges=False, sourceGeometryChanges=0, sourcePoseChanges=0,
        sourceEvidenceInterpretationUsedAI=True, aiGeometryModelling=False,
        originalSourceReviewAccepted=True, completeModelGeometryUnchanged=True,
        installationApproved=False, publication=False,
        rawStrictSupportPassed=False, rawBoundaryCertificateAccepted=False,
        observations=[
            'Approve only these two exact original H234/75 tower/podium sources at immutable bytes, fixed1x and source placement. Their143 strict contacts and32 finite original-edge paths in every renderer stream establish the bounded authored support assembly. Raw strict failures remain; no generic contact threshold is changed.',
            'All19 compound-envelope negatives are original vertical wall/return facets with finite clear-cap paths. Faces6520/6525 are below the higher original podium roof, not highest-exposed walls. Accept these own-assembly authored joins; they are not buried earth-facing floors and do not require source remodelling or a new zero-interpenetration engineering rule. Current actual-ground checks independently find zero tower negative faces and only8podium wall toes with checked clear-cap paths.',
            'Exact complete10573-face ground coverage and all56ordinary/3retained-native regressions pass under current terrain. The derived18418face terrain preserves all16351oldfaces and adds2067 bounded Float32 covers. The one positive-area native terrain overlap is its explicit replacement. The separate zero-area KwongFung corner remains in scope and leases; no touching source is omitted.',
            'All non-coimport BASIC contacts are zero. The separately identified1986 podium79882 and2015 Upton12728 have exact finite line contacts with the proposed originals but no area contact pairs in any stream; retain their own identities and metadata. Upton338946 is strictly source-bounds-separated. Existing338946-to12728 dependency binding remains installed and unchanged; it needs no metadata migration. These boundary interfaces do not imply shared ownership or source corruption.',
            'The failed4.927408mm boundary certificate and1.151m2 raw other-form overlap remain archived. Exact numeric identity is accepted on the independent complete H234/75 family, owned roots, current routes and whole-source evidence, without modifying generic identity policy.',
            *inspection['observations'],
            'Private source qualification only. Guarded dry-run/prepare-only, qualification commit/push, live installation and fresh20exports/full6936oldactor/full521ledger/globalBASICfallback readback remain mandatory.'
        ])
    save(out / 'ROOT-PHYSICAL-REVIEW.json', result)
    save(out / 'ROOT-SOURCE-REVIEW.json', result)
    refs += [HERE / 'exact_packed_world_geometry_20261009.py', HERE / 'original_supported_catalogue_scope_v1_20261024.py']
    module('fung_final_source_review', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH, 'bounded-current-original-fung-yip-source-physical-browser-review', list(dict.fromkeys(refs)), result)


if __name__ == '__main__':
    main()
