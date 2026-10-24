"""Reuse canonical original-support checks for an explicit source pair; no approval."""
import argparse, subprocess
import numpy as np
from shapely.geometry import Polygon
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for key in ['batch', 'capture', 'supported', 'support']:
        p.add_argument('--' + key, required=True)
    a = p.parse_args()
    assert a.batch.startswith('government-xl-') and '/' not in a.batch
    assert a.supported != a.support
    base = ROOT / 'docs/astra-city/government-import'
    doc, capture = base / a.batch, base / a.capture
    assert not doc.exists()
    _, pins = authenticate(capture)
    refs = [__import__('pathlib').Path(__file__), capture / 'result.json']
    def take(path):
        assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)
    selected = take(capture / 'selection.json.gz')['rows']
    sources = {r['uid']: r for r in selected}
    assert set(sources) == {a.supported, a.support}
    for r in sources.values():
        path = ROOT / r['candidate']['path']
        assert digest(path.read_bytes()) == r['sourceSHA256']
        refs.append(path)
    save(doc / 'support-inputs.json', dict(pairs=[dict(uid=a.supported, supportUid=a.support)], sources=selected))
    tool = HERE / 'original-support-closure-interfaces.mjs'
    subprocess.run(['node', str(tool), str(doc.relative_to(ROOT)) + '/'], cwd=ROOT, check=True)
    checks = read(doc / 'support-checks.json.gz')
    assert len(checks['rows']) == 1
    interface = checks['rows'][0]['interface']
    for path, sha in checks['inputHashes'].items():
        assert digest((ROOT / path).read_bytes()) == sha
        refs.append(ROOT / path)
    rows = {r['uid']: r for r in take(HERE / 'local' / a.capture / 'runtime-geometry.json.gz')['rows']}
    def world(r):
        return np.asarray(r['position'], dtype='<f8').reshape(-1, 3)[np.asarray(r['index']).reshape(-1, 3)]
    target, support = world(rows[a.supported]), world(rows[a.support])
    assert len(target) == sources[a.supported]['triangles'] and len(support) == sources[a.support]['triangles']
    ground = np.asarray(rows[a.supported]['drawnGroundGeometry'], dtype='<f8').reshape(-1, 3, 3)
    f = sources[a.supported]['source']['building']
    final = module('pair_support_foundation', HERE / 'xl-final-script-pass.py')
    foundation = final.foundation_context(target, np.concatenate([ground, support]), Polygon(f['rings'][0], f['rings'][1:]))
    save(doc / 'compound-foundation.json', foundation)
    summary = dict(uids=sorted(sources), supportedUid=a.supported, supportUid=a.support,
                   sourceSHA256ByUid={u: r['sourceSHA256'] for u, r in sources.items()},
                   sourceFacesByUid={u: r['triangles'] for u, r in sources.items()},
                   interface={k: interface.get(k) for k in ['passed', 'samples', 'strictContacts', 'wallIntersections']},
                   unresolvedSamples=len(interface['unresolved']), compoundFoundation=foundation,
                   physicalSupportAccepted=False, installationApproved=False, sourceGeometryChanges=0,
                   qualification='Existing canonical original-support closure and complete literal-runtime source/ground diagnostics. All unresolved samples and buried faces remain. No support, identity, collision or installation approval; source geometry/pose unchanged.')
    save(doc / 'summary.json', summary)
    refs += [tool, HERE / 'xl-final-script-pass.py']
    module('original_pair_support_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch, 'explicit-original-pair-support-diagnostic', refs, summary)
    print(dict(interface=summary['interface'], unresolved=summary['unresolvedSamples'], buried=foundation['fullyBuriedTriangles']), flush=True)


if __name__ == '__main__':
    main()
