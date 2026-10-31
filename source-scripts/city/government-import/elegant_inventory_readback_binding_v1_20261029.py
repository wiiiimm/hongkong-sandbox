"""Bind completed whole-runtime readback to the existing bounds-refresh schema.

No re-review or new installation: immutable input receipts remain unchanged.
"""
import argparse
import sys
import uuid
from pathlib import Path
from run import ROOT, HERE, read, save, digest, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved

BASE = ROOT / 'docs/astra-city/government-import'
BATCH = 'government-xl-elegant-inventory-readback-binding-v1-20261029'
INSTALLED = BASE / 'government-xl-elegant-garden-original-installed-v1-20261028'
CHECKED = BASE / 'government-xl-elegant-garden-installed-independent-readback-v1-20261028'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--owned', action='store_true')
    args = parser.parse_args()
    out, lp = BASE / BATCH, HERE / 'local' / BATCH / 'reservation.json'
    assert not out.exists()
    if not args.owned:
        assert not lp.parent.exists()
        claim = reservations.claim('installed-readback-schema-binding-' + str(uuid.uuid4()),
                                   ['source-count-audit:' + BATCH], batch=BATCH, ttl=1800)
        assert claim['ok']
        return execute_reserved(claim['reservation'], lp, [sys.executable, __file__, '--owned'])
    lease = read(lp)
    assert reservations.owns(lease)
    installed, _ = authenticate(INSTALLED)
    checked, checkedpins = authenticate(CHECKED)
    assert installed['publication'] and installed['newlyInstalled'] == 2
    assert checked['installationReadbackPassed'] and checked['allRuntimeAssetBytesVerified']
    assert checked['installedReceiptJob'] == installed['jobId']
    assert checked['snapshotId'] == installed['snapshotId']
    assert checked['uids'] == sorted(installed['sourceSHA256ByUid']) == sorted(installed['installedUids'])
    assert checked['wholeRuntimeActors'] == installed['completeCurrentCatalogueModels'] == 7007
    assert checked['originalActorsPreserved'] == 6991
    manifestpath = ROOT / '3d-viewer/city/data/manifest.json'
    assert digest(manifestpath.read_bytes()) == checkedpins[str(manifestpath.relative_to(ROOT))] == installed['manifest']['sha256']
    refs = [Path(__file__), INSTALLED / 'result.json', CHECKED / 'result.json', manifestpath]
    current = {}
    for url in read(manifestpath)['officialModelCatalogues']:
        path = ROOT / '3d-viewer' / url
        assert digest(path.read_bytes()) == checkedpins[str(path.relative_to(ROOT))]
        refs.append(path)
        for model in read(path)['models']:
            assert model['uid'] not in current
            current[model['uid']] = model
            if model['uid'] in installed['sourceSHA256ByUid']:
                asset = path.parent / model['asset']
                assert digest(asset.read_bytes()) == model['sha256'] == installed['sourceSHA256ByUid'][model['uid']]
                refs.append(asset)
    assert len(current) == 7007
    pointer = ROOT / 'docs/astra-city/model-integration-20260909/current-source-review.json'
    assert read(pointer)['snapshotId'] == checked['snapshotId']
    refs.append(pointer)
    result = dict(uids=checked['uids'], snapshotId=checked['snapshotId'],
        sourceSHA256ByUid=installed['sourceSHA256ByUid'], installationIndependentlyVerified=True,
        underlyingInstalledJob=installed['jobId'], underlyingWholeRuntimeReadbackJob=checked['jobId'],
        sourceGeometryChanges=0, installationApproved=False, publication=False,
        qualification='Schema binding only: independently verified means the existing completed all-runtime readback passed for the exact installed job/snapshot/source set and still-current catalogue/asset bytes. No historical receipt altered, no new source/physical review or installation approval. Existing bounds-refresh checks remain unchanged.')
    save(out / 'summary.json', result)
    assert reservations.owns(lease)
    module('installed_inventory_readback_binding_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH, 'completed-exact-installed-whole-runtime-readback-schema-binding', refs, read(out / 'summary.json'))
    print('Completed readback bound to unchanged inventory-refresh contract; no new installation.', flush=True)


if __name__ == '__main__':
    main()
