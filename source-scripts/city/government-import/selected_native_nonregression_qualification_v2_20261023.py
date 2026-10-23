"""Qualify a terrain change using exact unchanged installed-actor context.

Raw failed support checks are retained and never become support approvals.
"""
import argparse
from pathlib import Path
from copy import deepcopy
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from retained_native_nonregression_v1_20261023 import terrain_decision


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for key in ['batch', 'neighbours']:
        p.add_argument('--' + key, required=True)
    p.add_argument('--context', action='append', required=True)
    a = p.parse_args()
    assert a.batch.startswith('government-xl-') and '/' not in a.batch
    base = ROOT / 'docs/astra-city/government-import'
    out = base / a.batch
    assert not out.exists()
    refs, cache = [Path(__file__), HERE / 'retained_native_nonregression_v1_20261023.py'], {}
    def take(batch, name):
        if batch not in cache:
            cache[batch] = authenticate(base / batch)[1]
            refs.append(base / batch / 'result.json')
        path = base / batch / name
        assert digest(path.read_bytes()) == cache[batch][str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)
    raw = take(a.neighbours, 'summary.json')
    assert not raw['basicFlags']
    contexts = [take(n, 'summary.json') for n in a.context]
    byuid = {r['nativeUid']: r for r in contexts}
    assert len(byuid) == len(contexts)
    assert set(byuid) == {r['uid'] for r in raw['nativeRows'] if not r['passed']}
    assert {r['uid'] for r in raw['nativeRows']} == set(raw['requiredNativeUids'])
    manifestpath = ROOT / '3d-viewer/city/data/manifest.json'
    pins = cache[a.neighbours]
    assert digest(manifestpath.read_bytes()) == pins[str(manifestpath.relative_to(ROOT))]
    refs.append(manifestpath)
    installed = {}
    for url in read(manifestpath)['officialModelCatalogues']:
        path = ROOT / '3d-viewer' / url
        assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]
        refs.append(path)
        for r in read(path)['models']:
            assert r['uid'] not in installed
            installed[r['uid']] = r
    qualified = []
    for row in raw['nativeRows']:
        assert row['terrain']['newlyWhollyBuried'] == row['terrain']['newlyUpwardWhollyBuried'] == 0
        qualified.append(deepcopy(row) if row['passed'] else {**deepcopy(row), **terrain_decision(row, byuid[row['uid']], installed)})
    assert all(r['passed'] for r in qualified)
    # Keep original rows and ordinary checks byte-for-value, alongside the
    # separately named terrain-change decisions used by integration guards.
    result = deepcopy(raw)
    result.update(nativeRows=qualified, nativeResolved=sorted(raw['requiredNativeUids']), rawNativeRows=deepcopy(raw['nativeRows']), exactUnchangedContextBatches=a.context, legacySupportFailuresReapproved=False, nonregressionOnly=True, qualification='Only the proposal terrain change is qualified for exactly unchanged legacy actor/support contexts. Raw support failures remain false in rawNativeRows and each decision.rawNativeRegression. No support, source identity, model geometry or existing actor reapproval.')
    save(out / 'summary.json', result)
    ordinary = take(a.neighbours, 'neighbour-checks.json')
    save(out / 'neighbour-checks.json', ordinary)
    for n in a.context:
        for path, sha in cache[n].items():
            assert digest((ROOT / path).read_bytes()) == sha
            refs.append(ROOT / path)
    module('native_nonregression_qualification_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch, 'exact-installed-native-proposal-terrain-nonregression', list(dict.fromkeys(refs)), result)


if __name__ == '__main__':
    main()
