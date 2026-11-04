"""Reuse disjoint complete captures only after exact current-runtime array parity."""
import argparse
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--batch', required=True)
    p.add_argument('--runtime', required=True)
    p.add_argument('--attributes', action='append', required=True)
    a = p.parse_args()
    base = ROOT/'docs/astra-city/government-import'
    doc = base/a.batch
    assert a.batch.startswith('government-xl-') and '/' not in a.batch and not doc.exists()
    assert len(a.attributes) == len(set(a.attributes)) == 2
    refs, pins, rows, hashes = [Path(__file__)], {}, {}, {}
    for name in [a.runtime, *a.attributes]:
        _, bound = authenticate(base/name)
        refs.append(base/name/'result.json')
        for path, sha in bound.items():
            assert path not in pins or pins[path] == sha
            pins[path] = sha
    for path, sha in pins.items():
        assert digest((ROOT/path).read_bytes()) == sha, path
        refs.append(ROOT/path)
    selection = read(base/a.runtime/'selection.json.gz')['rows']
    geometry = {r['uid']: r for r in read(HERE/'local'/a.runtime/'runtime-geometry.json.gz')['rows']}
    closure = None
    for name in a.attributes:
        data = read(base/name/'attributes.json.gz')
        assert data['startEndAllInputsVerified'] is True
        current = data['completeRecursiveProductionModuleClosure']
        if closure is None:
            closure = current
        else:
            assert closure == current, 'Production closures differ'
        for path, sha in data['inputHashes'].items():
            assert path not in hashes or hashes[path] == sha
            assert digest((ROOT/path).read_bytes()) == sha
            hashes[path] = sha
        for row in data['rows']:
            uid = row['uid']
            assert uid not in rows
            g = geometry[uid]
            assert g['sourceSHA256'] == row['sourceSHA256']
            assert np.array_equal(np.asarray(g['index']), np.asarray(row['completeOriginalIndex']))
            assert np.array_equal(np.asarray(g['position']), np.asarray(row['completeLiteralWorldPosition']))
            rows[uid] = row
    expected = {r['uid']: r['sourceSHA256'] for r in selection}
    assert {u: r['sourceSHA256'] for u, r in rows.items()} == expected
    assert set(rows) == set(geometry)
    save(doc/'attributes.json.gz', dict(rows=[rows[u] for u in sorted(rows)], inputHashes=hashes,
        completeRecursiveProductionModuleClosure=closure, startEndAllInputsVerified=True,
        exactCurrentRuntimeArraysVerified=True, sourceGeometryChanges=0,
        currentAcceptance=False, nativeReacceptance=False,
        explicitArithmeticOnlyNotUniversalGPUCameraGuarantee=True))
    result = dict(uids=sorted(rows), completeSources=len(rows),
        sourceSHA256ByUid=expected, exactLiteralArraysAndIndexesMatchCurrentRuntime=True,
        previousCapturesRecomputed=False, sourceGeometryChanges=0,
        installationApproved=False, qualification='Exact disjoint array reuse only; all prior bytes/module closures rehashed, all literal arrays and complete indices equal the fresh current runtime. No source, physical, GPU or publication approval transfers.')
    save(doc/'summary.json', result)
    module('merge_exact_attributes_freeze', HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch, 'exact-current-runtime-render-array-reuse', list(dict.fromkeys(refs)), result)
    print(dict(completeSources=len(rows), exactCurrentRuntimeParity=True), flush=True)


if __name__ == '__main__':
    main()
