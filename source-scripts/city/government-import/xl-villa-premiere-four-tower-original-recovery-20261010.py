"""Recover four exact provider tower originals for independent silhouette evidence."""
import importlib.util
import json
import uuid
from pathlib import Path
from run import ROOT, HERE, read, save, digest, reservations

BATCH = 'government-xl-villa-premiere-four-tower-original-recovery-20261010'
DOC = ROOT / 'docs/astra-city/government-import' / BATCH
LOCAL = HERE / 'local' / BATCH
IDS = [58497, 63823, 121309, 148052]


def main():
    assert not DOC.exists() and not LOCAL.exists()
    claim = reservations.claim('villa-premiere-originals-' + str(uuid.uuid4()),
        ['building:landsd/' + str(i) + ':0' for i in IDS], batch=BATCH, ttl=3600)
    assert claim['ok'], claim
    lease = claim['reservation']
    save(LOCAL / 'reservation.json', json.loads(json.dumps(lease, default=str)))
    try:
        spec = importlib.util.spec_from_file_location('villa_pinned_source_recovery', HERE / 'xl-aqua-marine-original-recovery-20261010.py')
        recovery = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(recovery)
        recovery.BATCH, recovery.DOC, recovery.LOCAL = BATCH, DOC, LOCAL
        recovery.GROUPS = {'89917': IDS}
        recovery.owned()
        selection = read(DOC / 'selection.json.gz')
        for row in selection['rows']:
            row['triangles'] = row['native']['model']['triangles']
        save(DOC / 'selection.json.gz', selection)
        spec = importlib.util.spec_from_file_location('villa_recovery_fence', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py')
        fence = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(fence)
        paths = [Path(__file__), HERE / 'xl-aqua-marine-original-recovery-20261010.py', HERE / 'xl-next-support-recovery-20261005.py']
        paths += [p for p in LOCAL.rglob('*') if p.is_file() and p.name != 'reservation.json']
        paths += [ROOT / ref['path'] for ref in selection['evidenceRefs']]
        result = fence.freeze(BATCH, 'villa-premiere-four-tower-unchanged-original-acquisition-v1', paths,
            dict(uids=[row['uid'] for row in selection['rows']],
                 missing=selection['missing'], manifestSHA256=selection['manifestSHA256'],
                 completeOriginalFaceCounts={row['uid']: row['triangles'] for row in selection['rows']},
                 identityAccepted=False, physicalAccepted=False, installationApproved=False,
                 qualification='Byte-identical original provider acquisition and exact current native membership only. Distinct current identities/foreign actors remain distinct. No overhead identity interpretation, source contact/support or installed credit.'))
        print(json.dumps(dict(jobId=result['jobId'], recovered=len(selection['rows']), missing=selection['missing'])), flush=True)
    finally:
        assert reservations.release(lease)['ok']


if __name__ == '__main__':
    main()
