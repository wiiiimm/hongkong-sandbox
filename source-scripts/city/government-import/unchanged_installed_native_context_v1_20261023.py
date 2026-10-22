"""Prove a scoped installed actor's whole terrain remains exactly unchanged."""
import argparse
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from retained_native_template_v3_20261023 import exact_rendered_face_multiset


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for k in ['batch', 'owner', 'uid', 'support', 'patch', 'inventory', 'neighbours']:
        p.add_argument('--' + k, required=True)
    a = p.parse_args()
    assert a.batch.startswith('government-xl-') and '/' not in a.batch
    base = ROOT / 'docs/astra-city/government-import'
    doc = base / a.batch
    assert not doc.exists()
    refs, pins, receipts = [Path(__file__)], {}, {}
    for batch in [a.patch, a.inventory, a.neighbours]:
        receipt, bound = authenticate(base / batch)
        receipts[batch] = receipt
        pins.update(bound)
        refs.append(base / batch / 'result.json')

    def take(path):
        assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]
        refs.append(path)
        return read(path)

    inventory = {r['uid']: r for r in take(base / a.inventory / 'complete-bounds.json.gz')['rows']}
    before = np.asarray(take(HERE / 'local' / a.patch / 'parent.json')['triangles'])
    candidate = take(ROOT / receipts[a.patch]['candidate']['path'])
    after = np.asarray(candidate['nativeMesh']['position']).reshape(-1, 3)[np.asarray(candidate['nativeMesh']['index']).reshape(-1, 3)]
    report = take(base / a.neighbours / 'summary.json')
    raw = next(r for r in report['nativeRows'] if r['uid'] == a.uid)
    assert raw['passed'] is False and raw['terrain']['maximumBurialIncrease'] == 0
    assert raw['terrain']['minimumGapBefore'] == raw['terrain']['minimumGapAfter']
    assert raw['terrain']['newlyWhollyBuried'] == raw['terrain']['newlyUpwardWhollyBuried'] == 0
    manifest = take(ROOT / '3d-viewer/city/data/manifest.json')
    entries = {}
    for url in manifest['officialModelCatalogues']:
        path = ROOT / '3d-viewer' / url
        assert digest(path.read_bytes()) == pins[str(path.relative_to(ROOT))]
        refs.append(path)
        for entry in read(path)['models']:
            if entry['uid'] in [a.uid, a.support]:
                assert entry['uid'] not in entries
                entries[entry['uid']] = (entry, path)
    assert set(entries) == {a.uid, a.support}
    rows = []
    for uid in [a.uid, a.support]:
        entry, catalogue = entries[uid]
        assert inventory[uid]['sourceSHA256'] == entry['sha256']
        asset = catalogue.parent / entry['asset']
        assert digest(asset.read_bytes()) == entry['sha256']
        refs.append(asset)
        bounds = np.asarray(inventory[uid]['completeFourWorldBounds'])
        low, high = bounds[:, 0].min(0), bounds[:, 1].max(0)
        def relevant(triangles):
            return triangles[np.all(triangles[:, :, [0, 2]].max(1) >= low[[0, 2]], axis=1) &
                             np.all(triangles[:, :, [0, 2]].min(1) <= high[[0, 2]], axis=1)]
        old_faces, new_faces = relevant(before), relevant(after)
        assert len(old_faces) and exact_rendered_face_multiset(old_faces, new_faces), 'Whole native bounds intersect changed rendered terrain'
        rows.append(dict(uid=uid, sourceSHA256=entry['sha256'], completeFourWorldBounds=bounds.tolist(),
                         completeIntersectingTerrainFaces=len(old_faces), exactRenderedTerrainMultisetUnchanged=True))
    result = dict(uids=[a.owner], nativeUid=a.uid, supportUid=a.support, rows=rows,
                  rawNativeRegression=raw, proposalTerrainNonRegressionProved=True,
                  existingNativeReaccepted=False, rawSupportPolicyPassed=False,
                  sourceGeometryChanges=0, installationApproved=False,
                  qualification='Complete inclusive terrain-face multisets across all four-world native/support bounds remain exactly unchanged, including duplicate multiplicities. Current source assets are hash-bound. Raw existing support negative retained; no new support, identity, source role or installation approval.')
    save(doc / 'summary.json', result)
    refs.append(HERE / 'retained_native_template_v3_20261023.py')
    module('unchanged_native_context_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        a.batch, 'exact-whole-installed-native-terrain-non-regression-context', refs, result)
    print(dict(rows=rows, rawSupportPolicyPassed=False), flush=True)


if __name__ == '__main__':
    main()
