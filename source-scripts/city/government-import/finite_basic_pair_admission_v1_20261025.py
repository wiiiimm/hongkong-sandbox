"""Admission for an exact two-original pair on retained BASICs with no installed neighbours.

Canonical strict support remains false. The separate finite V2 proof, complete
continuous context, exact pair contacts and directional availability graph must
all be bound. Existing canonical and retained-native publishers are unchanged.
"""
import numpy as np
from run import ROOT, HERE, read, digest, jobs
from china_ferry_current_foundations_v1_20261020 import authenticate
from finite_embedded_basic_support_contract_v2_20261025 import verify_mode
from finite_basic_availability_graph_v1_20261025 import expected_dependencies
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts
BASE = ROOT/'docs/astra-city/government-import'

def replay(config, review):
    refs = [HERE/name for name in ['finite_basic_pair_admission_v1_20261025.py',
            'finite_embedded_basic_support_contract_v2_20261025.py',
            'finite_basic_availability_graph_v1_20261025.py',
            'exact_packed_world_geometry_20261009.py', 'exact_original_finite_triangle_contacts_20261010.py']]
    pins = {}
    def take(batch, name, *, local=False):
        if batch not in pins:
            pins[batch] = authenticate(BASE/batch)[1]
            refs.append(BASE/batch/'result.json')
        path = (HERE/'local' if local else BASE)/batch/name
        assert digest(path.read_bytes()) == pins[batch][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)
    assert review['sourceSpecificPhysicalInterpretationAccepted'] is True
    assert review['completeNeighbourInterpretationAccepted'] is True
    assert review['completeFourWorldCanonicalRetainedBasicSupport'] is False
    assert review['completeFourWorldFiniteRetainedBasicSupport'] is True
    assert review['completeFourWorldSourceClearance'] is True
    assert review['sourceGeometryChanges'] == review['sourcePoseChanges'] == 0
    assert review['terrainEdits'] is False and review['retainedNativeEntries'] == {}
    sources = config['sources']
    assert len(sources) == 2 and sources == review['sourceSHA256ByUid']
    assert config['retainedNativeUids'] == [] and review['retainedImagesActuallyViewed'] == []
    selection = take(config['runtime'], 'selection.json.gz')
    selected = {r['uid']:r for r in selection['rows']}
    assert set(selected) == set(sources)
    actual = {}
    for uid, row in selected.items():
        asset = ROOT/row['candidate']['path']
        assert digest(asset.read_bytes()) == sources[uid] == row['sourceSHA256']
        refs.append(asset)
        actual[uid] = decode_original_world_triangles(asset.read_bytes())
    finite = take(config['finiteEvidence'], 'summary.json')
    bindings = take(config['finiteEvidence'], 'support-bindings.json')
    assert finite['sourceSHA256ByUid'] == sources
    assert finite['completeFourWorldCanonicalRetainedBasicSupport'] is False
    assert finite['completeFourWorldFiniteRetainedBasicSupport'] is True
    assert review['retainedBasicSupportDependencies'] == bindings
    by_binding = {d['uid']:d for d in bindings}
    assert len(bindings) == len(by_binding) == len(sources) and set(by_binding) == set(sources)
    support_ref = dict(path=str((BASE/config['finiteEvidence']/'summary.json').relative_to(ROOT)),
                       sha256=digest((BASE/config['finiteEvidence']/'summary.json').read_bytes()))
    payloads = take(config['finiteModes'], 'mode-inputs.json.gz')['rows']
    checks = take(config['finiteModes'], 'mode-checks.json.gz')['rows']
    geometry = {r['uid']:r for r in take(config['runtime'], 'runtime-geometry.json.gz', local=True)['rows']}
    assert len(payloads) == 2 and {r['uid'] for r in payloads} == set(sources) and len(checks) == 8
    mode_names = {'original','literal','leftF32','balancedF32'}
    for payload in payloads:
        uid = payload['uid']
        binding = by_binding[uid]
        assert payload['sourceSHA256'] == sources[uid] == binding['sourceSHA256']
        assert payload['supportUid'] == binding['supportUid'] and binding['supportEvidence'] == support_ref
        support = payload['supportGeometry']
        assert digest(jobs.encode(support).encode()) == binding['completeIndexedBasicGeometrySHA256']
        podium = np.asarray(support['position']).reshape(-1,3)[np.asarray(support['index']).reshape(-1,3)]
        assert len(payload['modes']) == 4 and {m['mode'] for m in payload['modes']} == mode_names
        uid_checks = [c for c in checks if c['uid'] == uid]
        assert len(uid_checks) == 4 and {c['mode'] for c in uid_checks} == mode_names
        captured = geometry[uid]
        captured_triangles = np.asarray(captured['position']).reshape(-1,3)[np.asarray(captured['index']).reshape(-1,3)]
        assert np.array_equal(captured_triangles, actual[uid])
        for mode in payload['modes']:
            name = mode['mode']
            source = mode['geometry']
            triangles = np.asarray(source['position']).reshape(-1,3)[np.asarray(source['index']).reshape(-1,3)]
            assert np.array_equal(triangles, actual[uid]), 'Fresh distinct-world ground proof required'
            detail = take(config['finitePathsByUid'][uid], name+'.json.gz')
            canonical = next(c['proof'] for c in uid_checks if c['mode'] == name)
            replayed = verify_mode(triangles, podium, canonical, detail)
            recorded = [r for r in finite['rows'] if r['uid'] == uid and r['mode'] == name]
            assert len(recorded) == 1 and all(recorded[0][k] == v for k,v in replayed.items())
        context = take(config['continuous'], uid.split('/')[1]+'.json.gz')
        assert context['sourceSHA256'] == sources[uid]
        assert context['wholeSourceFaces'] == len(actual[uid]) == len(context['faces'])
        assert context['wholeSourceUncoveredFaces'] == 0 and not context['continuousAffectedFaces']
        evidence = next(r for r in finite['identicalWorldContinuousContext'] if r['uid'] == uid)
        ground = np.asarray(captured['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3)
        assert evidence['worldTrianglesSHA256'] == digest(actual[uid].astype('<f8').tobytes())
        assert evidence['drawnGroundSHA256'] == digest(ground.tobytes())
    scope = take(config['scope'], 'summary.json')
    empty = take(config['emptyNative'], 'summary.json')
    assert empty['emptyNativeContactSetProved'] is True and empty['rows'] == []
    assert set(empty['uids']) == set(scope['uids']) == set(sources)
    assert sum(r['currentFormsWithinTwoMetreRegion'] for r in scope['rows']) == config['neighbourForms'] == review['completeCurrentNeighbourChecks']
    forms = {}
    for row in scope['rows']:
        assert row['currentNativeActorsChecked'] == config['currentNativeActors'] and row['nearbyNativeActors'] == []
        assert row['sourceSHA256'] == sources[row['uid']]
        for item in take(config['scope'], row['uid'].split('/')[1]+'-forms.json.gz'):
            form = item['building']
            assert form['uid'] not in forms or forms[form['uid']] == form
            forms[form['uid']] = form
            tile = ROOT/'3d-viewer'/item['tile']
            assert digest(tile.read_bytes()) == item['tileSHA256']
            assert next(f for f in read(tile)['buildings'] if f['uid'] == form['uid']) == form
            refs.append(tile)
    assert set(review['leaseResources']) == {'building:'+u for u in forms}
    for uid, binding in by_binding.items():
        assert forms[binding['supportUid']] == binding['currentBasicForm']
        assert forms[uid]['parent'] == binding['currentBasicForm']['parent']
    pair = take(config['pairContacts'], 'summary.json')
    assert set(pair['uids']) == set(sources) and pair['sourceSHA256ByUid'] == sources
    assert review['acceptedExactOriginalPair'] is True
    pair_ref = dict(path=str((BASE/config['pairRoles']/'summary.json').relative_to(ROOT)),
                    sha256=digest((BASE/config['pairRoles']/'summary.json').read_bytes()))
    assert review['acceptedOriginalPairRoles'] == pair_ref
    roles = take(config['pairRoles'], 'summary.json')
    assert roles['sourceSHA256ByUid'] == sources and len(roles['rows']) == 4
    left,right = pair['uids']
    recalculated = exact_finite_contacts(actual[left],range(len(actual[left])),actual[right],range(len(actual[right])))
    assert recalculated['allPairsExamined'] and recalculated['sourceFacesOmitted'] == 0
    assert len(pair['rows']) == 4 and {r['mode'] for r in pair['rows']} == mode_names
    for row in pair['rows']:
        assert row['sourceWorldSHA256ByUid'] == {u:digest(actual[u].astype('<f8').tobytes()) for u in sources}
        assert take(config['pairContacts'],row['mode']+'.json.gz') == recalculated
    foreign = take(config['foreignBasics'], 'summary.json')
    assert set(foreign['uids']) == set(sources)
    replacements = config['replacementDependenciesByUid']
    for row in foreign['rows']:
        uid,other = row['uid'],row['foreignUid']
        assert uid in sources
        after = [m for m in row['modes'] if m['mode'] != 'before-basic']
        assert len(after) == 4 and {m['mode'] for m in after} == mode_names
        if other == by_binding[uid]['supportUid']:
            continue
        if other in sources:
            if any(m['positiveContactPairs'] > 0 for m in after):
                assert replacements.get(uid) == other, 'Original neighbour replacement dependency missing'
        else:
            assert all(m['positiveContactPairs'] == 0 and m['projectedOverlapAreaM2'] == 0 for m in after)
    private = take(config['browser'], 'catalogue.json', local=True)['models']
    assert {m['uid']:m['sha256'] for m in private} == sources
    expected = expected_dependencies(private, bindings, replacements, include_basic=False)
    assert all(m.get('supportDependencies',[]) == expected[m['uid']] for m in private)
    for report_ref in review['browserReports']:
        path = ROOT/report_ref['path']
        assert digest(path.read_bytes()) == report_ref['sha256']
        refs.append(path)
        report = read(path)
        assert report['passed'] and not report['errors'] and report['retainedNativeOwnViews'] == []
        widths = {v['width'] for v in report['views'] if 'time' in v}
        assert len(widths) == 1
        if widths == {390}:
            witnesses = report['candidateDependencyFallbacks']
            assert {(w['uid'],w['failedUid']) for w in witnesses} == set(replacements.items())
            for w in witnesses:
                assert w['width'] == 390 and not w['active'] and w['basicLoaded'] and not w['basicHidden']
                assert not w['detailSuppressed'] and w['basicGroupVisible'] and w['ownFeaturePresent']
    manifest = ROOT/'3d-viewer/city/data/manifest.json'
    expected_manifest = dict(path=str(manifest.relative_to(ROOT)),sha256=digest(manifest.read_bytes()))
    assert review['currentManifest'] == expected_manifest
    assert selection['manifestSHA256'] == scope['currentManifestSHA256'] == empty['currentManifestSHA256'] == expected_manifest['sha256']
    refs.append(manifest)
    return list(dict.fromkeys(refs))
