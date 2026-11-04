"""Bind the four exact originals, bounded roles and current inspected browser evidence."""
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, save, digest, connect, NATIVE_RUN
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_supported_catalogue_scope_v1_20261024 import verify as verify_support_scope

BASE = ROOT / 'docs/astra-city/government-import'
P = 'government-xl-greenfield-after-fung-yip-'
BATCH = P + 'final-original-source-review-v1-20261025'
PRIMARY = 'landsd/258419:0'
SUPPORTS = {f'landsd/{n}:0': PRIMARY for n in [195705, 198115, 332916]}
BROWSER = P + 'unapproved-browser-v2-20261025'
COUNTS = {PRIMARY: 10007, 'landsd/195705:0': 26, 'landsd/198115:0': 86, 'landsd/332916:0': 700}


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

    identity = take(P + 'bounded-source-identity-review-v1-20261025', 'ROOT-IDENTITY-REVIEW.json')
    assert identity['identityAccepted'] and identity['rawFootprintAndCellFailuresPreserved']
    assert not identity['footprintCoverageGatePassedFor198115'] and not identity['wholeCellGatePassedFor195705']
    sources = identity['sourceSHA256ByUid']
    selected = take(P + 'seam-runtime-v2-20261025', 'selection.json.gz')
    rows = {r['uid']: r for r in selected['rows']}
    assert {u: r['sourceSHA256'] for u, r in rows.items()} == sources
    assert {u: r['triangles'] for u, r in rows.items()} == COUNTS
    attrs = take(P + 'attributes-v1-20261025', 'attributes.json.gz')
    assert attrs['startEndAllInputsVerified']
    oldattrs = take('government-xl-greenfield-four-source-grade-attributes-v1-20261024', 'attributes.json.gz')
    assert attrs['rows'] == oldattrs['rows']
    attrs = {r['uid']: r for r in attrs['rows']}
    hashes = {}
    for u, row in rows.items():
        asset = ROOT / row['candidate']['path']
        assert digest(asset.read_bytes()) == sources[u] == attrs[u]['sourceSHA256']
        refs.append(asset)
        tile = ROOT / '3d-viewer' / row['source']['tile']
        assert next(f for f in read(tile)['buildings'] if f['uid'] == u) == row['source']['building']
        refs.append(tile)
        assert row['candidate']['entry']['rootTranslation'] == [-834500, 0, 816500]
        ix = np.asarray(attrs[u]['completeOriginalIndex']).reshape(-1, 3)
        worlds = dict(original=decode_original_world_triangles(asset.read_bytes()), **{
            mode: np.asarray(attrs[u][key]).reshape(-1, 3)[ix]
            for mode, key in [('literal', 'completeLiteralWorldPosition'), ('leftF32', 'completeExplicitLeftAssociatedFloat32WorldPosition'), ('balancedF32', 'completeExplicitBalancedFloat32WorldPosition')]})
        assert all(len(t) == COUNTS[u] for t in worlds.values())
        hashes[u] = {m: digest(t.astype('<f8').tobytes()) for m, t in worlds.items()}
    follow = take('government-xl-greenfield-four-source-support-followthrough-v1-20261024')
    assert len(follow['rows']) == 3
    support_records = []
    for row in follow['rows']:
        u = row['uid']
        assert SUPPORTS[u] == row['supportUid'] == PRIMARY and row['allUnresolvedHaveFinitePaths']
        strict, paths = take(row['strictBatch']), take(row['pathsBatch'])
        assert strict['sourceSHA256ByUid'] == {u: sources[u], PRIMARY: sources[PRIMARY]}
        assert len(strict['rows']) == len(paths['rows']) == 4 and paths['allUnresolvedHaveFinitePaths']
        expected = {'landsd/195705:0': 2, 'landsd/198115:0': 42, 'landsd/332916:0': 27}[u]
        for s, p in zip(strict['rows'], paths['rows']):
            assert s['mode'] == p['mode']
            assert s['sourceWorldSHA256ByUid'] == {v: hashes[v][s['mode']] for v in [u, PRIMARY]}
            assert p['sourceWorldSHA256'] == hashes[u][p['mode']] and p['supportWorldSHA256'] == hashes[PRIMARY][p['mode']]
            assert p['targets'] == p['verifiedPaths'] == expected and p['remaining'] == 0
        support_records.append(dict(uid=u, supportUid=PRIMARY, strictPassed=strict['allFourModesPassed'], finitePathsPerWorld=expected))
    foundations = []
    ground_records = {}
    for u in sources:
        n = u.split('/')[1].split(':')[0]
        batch = f'government-xl-greenfield-{n}-after-fung-yip-foundations-v2-20261025'
        foundation = take(batch)
        assert foundation['uids'] == [u] and len(foundation['rows']) == 4
        for r in foundation['rows']:
            assert r['triangles'] == r['completeTerrainTriangles'] == COUNTS[u]
            assert r['fullyBuriedTriangles'] == r['fullyBuriedUpwardTriangles'] == 0
            take(batch, r['mode'] + '.json')
        foundations.append(dict(uid=u, batch=batch, completeFaces=COUNTS[u], coordinateStreams=4))
        batch = f'government-xl-greenfield-{n}-after-fung-yip-complete-ground-v2-20261025'
        ground = ground_records[u] = take(batch)
        assert ground['sourceSHA256'] == sources[u] and len(ground['rows']) == 4
        for r in ground['rows']:
            assert r['completeSourceFaces'] == COUNTS[u] and not r['negativeNonWallFaces']
            if u == PRIMARY:
                assert len(r['exactAffectedFaces']) == 85 and r['allAffectedWallLike'] and r['allAffectedHaveExposedHighestVertex']
                assert not r['compoundCapPathsPassed']
                cap = take(batch, r['mode'] + '-cap-paths.json.gz')['proof']
                assert sorted(p['sourceFace'] for p in cap['paths'] if not p['hasExactSharedEdgeClearCapPath']) == list(range(9427, 9459))
            else:
                assert r['noAffectedFaces'] and not r['exactAffectedFaces']
    columns = take(P + 'two-original-columns-context-v1-20261025')
    assert columns['sourceSHA256'] == sources[PRIMARY] and len(columns['rows']) == 4
    for row in columns['rows']:
        assert not row['strictSharedEdgeCapPathPassed'] and len(row['groups']) == 2
        assert all(g['positiveSourceJoinPairs'] == 0 for g in row['groups'])
    column_image = ROOT / columns['actuallyInspectedImage']['path']
    assert digest(column_image.read_bytes()) == columns['actuallyInspectedImage']['sha256']
    refs.append(column_image)
    continuous = take(P + 'seam-continuous-v2-20261025')
    assert all(not r['otherAffectedFaces'] and r['upwardContinuousMinimumGapM'] >= -.5 for r in continuous['rows'])
    coverage = take(P + 'exact-coverage-v2-20261025')
    assert len(coverage['rows']) == 4 and all(not r['stillUncoveredFaces'] for r in coverage['rows'])
    patch = take(P + 'seam-terrain-v2-20261025', 'result.json')
    assert patch['status'] == 'private-terrain-validator-passed' and patch['terrainTriangles'] == 791
    assert patch['seamCover']['unchangedOriginalTerrainTriangles'] == 701 and patch['seamCover']['addedTerrainTriangles'] == 90
    terrain = ROOT / patch['candidate']['path']
    assert digest(terrain.read_bytes()) == patch['candidate']['sha256']
    assert read(terrain)['meta']['targetUids'] == [PRIMARY]
    refs.append(terrain)
    scope = take(P + 'seam-scope-v2-20261025', 'scope.json')
    terrain_forms = take(P + 'seam-scope-v2-20261025', 'form-obligations.json.gz')
    assert scope['currentNativeActors'] == 6938 and len(terrain_forms) == scope['intersectingForms'] == 8
    assert not scope['terrainContacts'] and not scope['touchingNativeUids'] and scope['positiveAreaTerrainOverlaps'] == 0
    neighbours = take(P + 'neighbours-v2-20261025')
    assert neighbours['forms'] == 8 and not neighbours['flagged'] and neighbours['ordinaryFlagged'] == 0
    model_scope = take(P + 'model-scope-v1-20261025')
    forms = {f['uid']: f for f in terrain_forms}
    for r in model_scope['rows']:
        assert not r['nearbyNativeActors'] and r['currentNativeActorsChecked'] == 6938
        for item in take(P + 'model-scope-v1-20261025', r['uid'].split('/')[1] + '-forms.json.gz'):
            f = item['building']
            if f['uid'] in forms:
                assert forms[f['uid']] == f
            forms[f['uid']] = f
    assert len(forms) == 32
    context = take(P + 'source-footprint-context-v1-20261025')
    permit_forms = {f['uid'] for f in context['permitViewerForms']}
    foreign = take(P + 'foreign-contacts-v1-20261025')
    towers = {f'landsd/{n}:0' for n in [74283, 74484, 74656, 74814, 75206, 75256, 75421, 75422, 75605]}
    assert towers <= permit_forms and 'landsd/217024:0' not in permit_forms
    positive = set()
    for r in foreign['rows']:
        if r['foreignUid'] not in sources and any(m['positiveContactPairs'] for m in r['modes'] if m['mode'] != 'before-basic'):
            assert r['uid'] == PRIMARY
            positive.add(r['foreignUid'])
    assert positive == towers | {'landsd/217024:0'}
    canopy = forms['landsd/217024:0']
    assert canopy['structureType'] == 'Open-sided Structure' and canopy['baseHeightHKPD'] == 5.6 and canopy['topHeightHKPD'] == 10.2
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        assert not db.execute('SELECT model_id FROM astra_modelling.native_model_sizes WHERE run_id=%s AND building_csuid=%s', (NATIVE_RUN, canopy['buildingCSUID'])).fetchall()
    inspection = take(P + 'private-export-inspection-v2-20261025', 'ROOT-EXPORT-INSPECTION.json')
    assert inspection['visualAcceptance'] and inspection['reviewer'] == 'ROOT' and len(inspection['imagesActuallyViewed']) == 16
    images = inspection['imagesActuallyViewed']
    assert {(i['uid'], i['width'], i['time']) for i in images} == {(u, w, t) for u in sources for w in [390, 1280] for t in ['15:00', '22:00']}
    reports = []
    for width in [390, 1280]:
        report = take(BROWSER, f'{width}/staged-browser.json')
        assert report['passed'] and not report['errors'] and report['retainedNativeOwnViews'] == []
        for v in [v for v in report['views'] if 'time' in v]:
            assert v['fullyFramed'] and v['solidAppearance'] and v['active'] and v['visible'] and not v['fallbackFaces']
            assert v['pick'] == v['collision'] == v['uid'] and v['sourceSHA256'] == sources[v['uid']]
            p = BASE / BROWSER / str(width) / v['file']
            q = next(i for i in images if i['path'] == str(p.relative_to(ROOT)))
            assert digest(p.read_bytes()) == q['sha256'] == pins[BROWSER][q['path']]
            refs.append(p)
        assert report['jointViews'] and all({m['uid']: m['sourceSHA256'] for m in j['models']} == sources and all(m['active'] and m['visible'] and not m['fallbackFaces'] for m in j['models']) for j in report['jointViews'])
        if width == 390:
            failed = [v for v in report['views'] if v.get('phase') == 'failed-download']
            assert len(failed) == 4 and {v['uid'] for v in failed if v['fallbackRetained']} == set(sources)
        p = BASE / BROWSER / str(width) / 'staged-browser.json'
        reports.append(dict(path=str(p.relative_to(ROOT)), sha256=digest(p.read_bytes())))
    catalogue = take(BROWSER, 'catalogue.json', local=True)
    assert verify_support_scope(catalogue['models'], sources, SUPPORTS)
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert dict(path=str(manifest.relative_to(ROOT)), sha256=digest(manifest.read_bytes())) == identity['currentManifest']
    refs.append(manifest)
    resources = sorted({('building:' if u.startswith('landsd/') else 'source-form:') + u for u in forms} | {'terrain:city/data/terrain.json'})
    result = dict(uids=sorted(sources), sourceSHA256ByUid=sources, requiredOriginalAssembly=sources, supportByUid=SUPPORTS, supportEvidence=support_records, reviewer='ROOT', currentManifest=identity['currentManifest'], identityAccepted=True, identityProof=identity['identityProof'], identityProofByUid=identity['identityProofByUid'], sourceSpecificPhysicalInterpretationAccepted=True, completeNeighbourInterpretationAccepted=True, completeFourWorldFoundations=True, fourWorldFoundationEvidence=foundations, completeCurrentNeighbourChecks=32, totalNeighbourForms=32, terrainAffectedForms=8, leaseResources=resources, retainedNativeUids=[], visualAcceptance=True, imagesActuallyViewed=images, browserReports=reports, originalSourceReviewAccepted=True, completeModelGeometryUnchanged=True, sourceEvidenceInterpretationUsedAI=True, sourceGeometryChanges=0, sourcePoseChanges=0, aiGeometryModelling=False, installationApproved=False, publication=False, rawSharedEdgeCapPathsStillFalse=True, originalColumnExactJoinPairsZero=True, observations=[
        'Approve only these four complete immutable government bodies and their three exact original-to-original support dependencies:71finite source paths in every renderer stream. Old complete renderer attribute rows are identical. Raw strict-support failures remain. No BASIC actor supplies support credit, and no source primitive, pose or unit scale changes.',
        'All10819faces have exact current drawn-ground coverage after90boundedFloat32seam covers preserve701oldterrain triangles. All4world whole-source foundations have zero wholly buried or wholly buried upward facets. Three auxiliary sources have no actual-ground negative faces. The primary has85lower vertical wall negatives, all with highest vertices exposed above actual ground.53have exact shared-edge clear-cap paths.',
        'The remaining32faces9427..9458are the sides of two original polygonal columns. ROOT inspected their complete two-angle ground/source diagnostic. Their lower stems cross the ground and their upper vertices remain exposed. They have no exact positive finite joins to the rest of the original in any stream; preserve that source topology limitation and the false cap-path result. Accept these authored column/ground intersections as a faithful original import, without inventing a welded-cap, engineering load-bearing or per-component watertightness requirement. Do not weld, extend or remodel the posts to manufacture a cap certificate.',
        'All8terrain-affected forms pass; the full source/terrain obligation union is32forms and none of6938installed originals touches the source scope. Complete34pair current BASIC contacts retain nine estate-tower interfaces and the separately identified low open-sided canopy217024. The towers map to the three main-podium permit families. The canopy is not in that packet and has no separately indexed original by exact CSUID; retain its independent BASIC geometry and metadata. Accept the original podium/BASIC low-level interface as an incremental source representation, without common-ownership claims, suppression or a new zero-interpenetration engineering gate.',
        'The separate bounded numeric identity review retains19811594.4009percent current planar coverage and195705failed whole-cell coverage. It accepts exact registered roots/CSUIDs/routes and inspected full bodies, not architectural completion or changed numerical limits.',
        *inspection['observations'],
        'Private qualification only. Guarded dry-run/prepare-only, qualification commit/push, actual live installation, fresh16exports and whole6938oldactors/full521ledger/globalBASICfallback readback remain mandatory before installation credit.'
    ])
    save(out / 'ROOT-PHYSICAL-REVIEW.json', result)
    save(out / 'ROOT-SOURCE-REVIEW.json', result)
    refs += [HERE / 'exact_packed_world_geometry_20261009.py', HERE / 'original_supported_catalogue_scope_v1_20261024.py']
    module('greenfield_final_source_review', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH, 'bounded-current-four-original-greenfield-source-physical-browser-review', list(dict.fromkeys(refs)), result)


if __name__ == '__main__':
    main()
