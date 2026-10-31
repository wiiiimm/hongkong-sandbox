"""Replay finite roof paths against current complete geometry; diagnostic only.

Historical path witnesses are permitted only when the existing V2 contract
revalidates every path against freshly measured source/support/raw probes.
No identity, neighbour, visual or publication acceptance is inferred.
"""
import argparse
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, save, digest, jobs
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from finite_embedded_basic_support_contract_v2_20261025 import verify_mode


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ['batch', 'runtime', 'modes', 'basic-contacts', 'continuous', 'scope']:
        parser.add_argument('--' + key, required=True)
    parser.add_argument('--paths', action='append', required=True, help='uid,batch')
    a = parser.parse_args()
    assert a.batch.startswith('government-xl-') and '/' not in a.batch
    base = ROOT / 'docs/astra-city/government-import'
    out = base / a.batch
    assert not out.exists()
    refs = [Path(__file__), HERE / 'finite_embedded_basic_support_contract_v2_20261025.py']
    pins = {}

    def take(batch, name, local=False):
        if batch not in pins:
            pins[batch] = authenticate(base / batch)[1]
            refs.append(base / batch / 'result.json')
        p = (HERE / 'local' if local else base) / batch / name
        assert digest(p.read_bytes()) == pins[batch][str(p.relative_to(ROOT))]
        refs.append(p)
        return read(p)

    paths = dict(v.split(',') for v in a.paths)
    assert len(paths) == len(a.paths) and paths
    selection = take(a.runtime, 'selection.json.gz')
    sources = {r['uid']: r for r in selection['rows'] if r['uid'] in paths}
    assert set(sources) == set(paths)
    scope = take(a.scope, 'summary.json')
    assert set(scope['uids']) == set(paths)
    payloads = take(a.modes, 'mode-inputs.json.gz')['rows']
    checks = take(a.modes, 'mode-checks.json.gz')['rows']
    basics = {r['uid']: r for r in take(a.basic_contacts, 'checks.json.gz')['rows']}
    captured = {r['uid']: r for r in take(a.runtime, 'runtime-geometry.json.gz', True)['rows']}
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifest.read_bytes()) == selection['manifestSHA256'] == scope['currentManifestSHA256']
    assert pins[a.modes][str(manifest.relative_to(ROOT))] == selection['manifestSHA256']
    refs.append(manifest)
    natives, suppressed = set(), set()
    for url in read(manifest)['officialModelCatalogues']:
        p = ROOT / '3d-viewer' / url
        refs.append(p)
        for entry in read(p)['models']:
            natives.add(entry['uid'])
            suppressed.update(entry.get('suppressesBuildingUids', []))
    rows, contexts, bindings = [], [], []
    for uid, source in sources.items():
        current = basics[uid]
        payload = next(r for r in payloads if r['uid'] == uid)
        assert current['sourceSHA256'] == payload['sourceSHA256'] == captured[uid]['sourceSHA256'] == source['sourceSHA256']
        assert current['basicIsCurrentFinalSupport'] and current['canonicalContactPassed'] is False
        support = current['supportUid']
        assert support == payload['supportUid'] and support not in natives | suppressed
        form = current['supportForm']
        assert form['uid'] == support and form['structureType'] == 'Podium' and form['heightSource'] == 'landsd'
        assert form['parent'] == source['source']['building']['parent'] and form['parent']
        forms = take(a.scope, uid.split('/')[1] + '-forms.json.gz')
        actual_form = next(f for f in forms if f['building']['uid'] == support)
        tile = ROOT / '3d-viewer' / actual_form['tile']
        assert digest(tile.read_bytes()) == actual_form['tileSHA256']
        assert actual_form['building'] == form == next(b for b in read(tile)['buildings'] if b['uid'] == support)
        refs.append(tile)
        g = payload['supportGeometry']
        assert g == current['supportGeometry']
        podium = np.asarray(g['position']).reshape(-1, 3)[np.asarray(g['index']).reshape(-1, 3)]
        record = captured[uid]
        actual = np.asarray(record['position']).reshape(-1, 3)[np.asarray(record['index']).reshape(-1, 3)]
        assert len(payload['modes']) == 4 and {m['mode'] for m in payload['modes']} == {'original', 'literal', 'leftF32', 'balancedF32'}
        for mode in payload['modes']:
            x = mode['geometry']
            tri = np.asarray(x['position']).reshape(-1, 3)[np.asarray(x['index']).reshape(-1, 3)]
            assert np.array_equal(tri, actual), 'Different indexed worlds need separate continuous context'
            raw = next(r['proof'] for r in checks if r['uid'] == uid and r['mode'] == mode['mode'])
            detail = take(paths[uid], mode['mode'] + '.json.gz')
            proof = verify_mode(tri, podium, raw, detail)
            rows.append(dict(uid=uid, mode=mode['mode'], sourceSHA256=source['sourceSHA256'],
                             sourceWorldSHA256=detail['sourceWorldSHA256'], supportWorldSHA256=detail['supportWorldSHA256'], **proof))
        context = take(a.continuous, uid.split('/')[1] + '.json.gz')
        assert context['sourceSHA256'] == source['sourceSHA256']
        assert context['wholeSourceFaces'] == len(actual) == len(context['faces'])
        assert context['wholeSourceUncoveredFaces'] == 0 and not context['continuousAffectedFaces']
        ground = np.asarray(record['drawnGroundGeometry'], dtype='<f8').reshape(-1, 3, 3)
        contexts.append(dict(uid=uid, sourceSHA256=source['sourceSHA256'], sourceFaces=len(actual),
                             allFourWorldIndexedTrianglesExactlyEqual=True, worldTrianglesSHA256=digest(actual.astype('<f8').tobytes()),
                             drawnGroundSHA256=digest(ground.tobytes()), completeContinuousContextReusedForIdenticalTriangles=True,
                             upwardContinuousMinimumGapM=context['upwardContinuousMinimumGapM'], wholeSourceUncoveredFaces=0))
        bindings.append(dict(uid=uid, supportUid=support, supportCSUID=form['buildingCSUID'],
                             dependencyMode='retained-current-basic-podium', currentBasicForm=form,
                             currentBasicFormSHA256=digest(jobs.encode(form).encode()),
                             completeIndexedBasicGeometrySHA256=digest(jobs.encode(g).encode()),
                             sourceSHA256=source['sourceSHA256'], mustRemainBasicAndUnsuppressed=True,
                             futureReplacementRequiresDependentRevalidation=True))
    summary = dict(uids=sorted(sources), sourceSHA256ByUid={u:r['sourceSHA256'] for u,r in sources.items()},
                   rows=rows, identicalWorldContinuousContext=contexts, verifiedFinitePaths=sum(r['verifiedPaths'] for r in rows),
                   separateFiniteSupportEvidence=True, completeFourWorldCanonicalRetainedBasicSupport=False,
                   completeFourWorldFiniteRetainedBasicSupport=True, physicalSupportAccepted=False,
                   physicalAcceptance=False, installationApproved=False, publication=False, sourceGeometryChanges=0)
    if len(sources) == 1:
        uid = next(iter(sources))
        summary.update(sourceSHA256=sources[uid]['sourceSHA256'], supportUid=bindings[0]['supportUid'])
    save(out / 'finite-basic-evidence.json', summary)
    support_ref = dict(path=str((out / 'finite-basic-evidence.json').relative_to(ROOT)), sha256=digest((out / 'finite-basic-evidence.json').read_bytes()))
    for binding in bindings:
        binding['supportEvidence'] = support_ref
    save(out / 'support-bindings.json', bindings)
    save(out / 'summary.json', summary)
    assert digest(manifest.read_bytes()) == selection['manifestSHA256']
    module('current_finite_basic_bindings_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch, 'current-replayed-original-finite-basic-support-lifetime-bindings-diagnostic', list(dict.fromkeys(refs)), summary)
    print(dict(sources=len(sources), verifiedFinitePaths=summary['verifiedFinitePaths'], physicalAcceptance=False), flush=True)


if __name__ == '__main__':
    main()
