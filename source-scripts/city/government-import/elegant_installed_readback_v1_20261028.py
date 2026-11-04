"""Independent whole-runtime and fixed-cohort readback after completed installation."""
import uuid
from pathlib import Path
from run import ROOT, HERE, read, save, digest, connect, reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
import elegant_live_install_v1_20261028 as install
import argparse
import sys

BATCH = install.stage.P + 'installed-independent-readback-v1-20261028'
OUT = install.BASE / BATCH


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--owned', action='store_true')
    args = parser.parse_args()
    lp = HERE / 'local' / BATCH / 'reservation.json'
    assert not OUT.exists()
    if not args.owned:
        assert not lp.parent.exists()
        claim = reservations.claim('elegant-independent-readback-' + str(uuid.uuid4()),
                                   ['source-count-audit:' + BATCH], batch=BATCH, ttl=1800)
        assert claim['ok']
        return execute_reserved(claim['reservation'], lp, [sys.executable, __file__, '--owned'])
    lease = read(lp)
    assert reservations.owns(lease)
    result, pins = authenticate(install.DOC)
    assert result['publication'] and result['newlyInstalled'] == 2
    assert result['completeCurrentCatalogueModels'] == 7007
    refs = [Path(__file__), install.DOC / 'result.json', install.DOC / 'installed-acceptance.json']
    for relative, sha in pins.items():
        assert digest((ROOT / relative).read_bytes()) == sha, relative
    pointer = read(install.POINTER)
    assert pointer['snapshotId'] == result['snapshotId']
    refs.append(install.POINTER)
    manifest = ROOT / '3d-viewer/city/data/manifest.json'
    current = read(manifest)
    beforepath = install.LOCAL / 'historical-current/3d-viewer/city/data/manifest.json'
    before = read(beforepath)
    refs.extend([manifest, beforepath])
    before_models = [m for url in before['officialModelCatalogues'] for m in read(ROOT / '3d-viewer' / url)['models']]
    models = []
    for url in current['officialModelCatalogues']:
        catalogue = ROOT / '3d-viewer' / url
        refs.append(catalogue)
        for model in read(catalogue)['models']:
            asset = catalogue.parent / model['asset']
            assert digest(asset.read_bytes()) == model['sha256'] and asset.stat().st_size == model['bytes']
            refs.append(asset)
            models.append(model)
    added = read(install.stage.STAGE / 'catalogue.json')['models']
    assert models == before_models + added
    assert len(before_models) == 6991 and len(models) == len({m['uid'] for m in models}) == 7007
    assert len(added) == 16
    reportpath = install.DOC / 'live-http/report.json'
    assert install.verify_live(read(reportpath), added)
    refs.append(reportpath)
    countpath = install.DOC / 'full-xl-current-count.json'
    count = read(countpath)
    previous = read(install.PREVIOUS)
    assert count['counts'] == dict(total=521, installedVerified=398, remaining=123)
    assert len(count['rows']) == len({r['sourceKey'] for r in count['rows']}) == 521
    old = {r['sourceKey']: r for r in previous['rows']}
    changed = [r for r in count['rows'] if r['installedVerified'] != old[r['sourceKey']]['installedVerified']]
    assert len(changed) == 2 and {r['uid'] for r in changed} == {'landsd/173532:0', 'landsd/173768:0'}
    assert all(r['installedVerified'] and r['runtimeSourceSHA256'] == r['indexedSourceSHA256'] for r in changed)
    unmapped = [r['sourceKey'] for r in previous['rows'] if r['uid'] is None]
    assert len(unmapped) == 2
    assert all(next(r for r in count['rows'] if r['sourceKey'] == key)['uid'] is None for key in unmapped)
    refs.extend([countpath, install.PREVIOUS])
    terminalpath = install.BASE / 'government-xl-terminal-revision-accounting-v1-20261028/summary.json'
    terminal = read(terminalpath)
    disposition = terminal['terminalDisposition']
    decisionpath = ROOT / disposition['path']
    assert digest(decisionpath.read_bytes()) == disposition['sha256']
    authenticate(decisionpath.parent)
    terminalrows = [r for r in terminal['rows'] if r['terminalForExactRevision']]
    assert len(terminalrows) == 3
    for row in terminalrows:
        currentrow = next(r for r in count['rows'] if r['sourceKey'] == row['sourceKey'])
        assert not currentrow['installedVerified'] and currentrow['indexedSourceSHA256'] == row['sourceSHA256']
    refs.extend([terminalpath, decisionpath])
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        for model in added:
            assert db.execute('SELECT review_state,source_sha256 FROM astra_modelling.model_reviews WHERE snapshot_id=%s AND uid=%s',
                              (pointer['snapshotId'], model['uid'])).fetchone() == ('installed-verified', model['sha256'])
    assert all(digest((ROOT / p).read_bytes()) == sha for p, sha in result['protectedDirtyFilesUnchanged'].items())
    summary = dict(uids=sorted(m['uid'] for m in added), snapshotId=pointer['snapshotId'],
                   installedReceiptJob=result['jobId'], wholeRuntimeActors=7007, originalActorsPreserved=6991,
                   allRuntimeAssetBytesVerified=True, fixedXLCounts=count['counts'], newlyInstalledFixedXL=2,
                   goalAccounting=dict(installed=398, notInstallableExactRevision=3, outstanding=120, total=521),
                   sourceKeysUnchanged=True, unmatchedSourceKeysPreserved=unmapped,
                   sourceGeometryChanges=0, publication=False, installationReadbackPassed=True)
    save(OUT / 'summary.json', summary)
    assert reservations.owns(lease)
    module('elegant_independent_readback_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        BATCH, 'independent-all-runtime-bytes-neon-source-reviews-and-full-fixed-xl-readback',
        list(dict.fromkeys(refs)), read(OUT / 'summary.json'))
    print(dict(readbackPassed=True, actors=7007, counts=count['counts']), flush=True)


if __name__ == '__main__':
    main()
