"""Restore two missing local receipts from already-complete, fully rehashed jobs.

The view producer compared tuple-valued Python display bounds with JSON lists
on readback. The database jobs completed successfully; no job is rerun or edited.
"""
from pathlib import Path
from run import ROOT, HERE, read, save, digest, connect
from primrose_compound_foundation_v2_20261015 import module


def main():
    base = ROOT / 'docs/astra-city/government-import'
    out = base / 'government-xl-depot120104-view-receipt-recovery-v1-20261029'
    assert not out.exists()
    refs, rows = [Path(__file__)], []
    for canopy in ['177363', '178180']:
        batch = 'government-xl-depot120104-canopy' + canopy + '-views-v1-20261029'
        directory = base / batch
        assert not (directory / 'result.json').exists()
        with connect() as db:
            db.execute('SET TRANSACTION READ ONLY')
            jobs = db.execute('SELECT id,status,result FROM astra_modelling.jobs WHERE batch=%s', (batch,)).fetchall()
        assert len(jobs) == 1
        job, status, result = jobs[0]
        assert status == 'complete' and result['jobId'] == job and result['batch'] == batch
        assert result['stage'] == 'unchanged-original-current-basic-contact-context-views'
        assert result['uids'] == ['landsd/120104:0'] and result['retainedUid'] == 'landsd/' + canopy + ':0'
        assert result['sourceSHA256'] == '655eb47347eec12814da670830672cf5808a23bbb590e520b22b0d21f6ce360f'
        assert result['installationApproved'] is False and result['visualAcceptance'] is False and result['publication'] is False
        assert all(result[k] == v for k, v in read(directory / 'summary.json').items())
        for entry in result['evidenceRefs']:
            path = (ROOT / entry['path']).resolve()
            assert path.is_relative_to(ROOT) and digest(path.read_bytes()) == entry['sha256']
            refs.append(path)
        save(directory / 'result.json', result)
        assert read(directory / 'result.json') == result
        with connect() as db:
            db.execute('SET TRANSACTION READ ONLY')
            assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (job,)).fetchone() == ('complete', read(directory / 'result.json'))
        save(directory / 'neon-sync.json', dict(jobId=job, resultVerified=True, restoredMissingLocalReceipt=True, databaseWrites=0))
        refs.extend([directory / 'result.json', directory / 'neon-sync.json'])
        rows.append(dict(batch=batch, jobId=job, allReferencesRehashed=True, storedSummaryExactlyMatchesDatabase=True))
    result = dict(uids=['landsd/120104:0'], restored=rows, databaseWrites=0,
                  installationApproved=False, publication=False,
                  qualification='Already-complete diagnostic jobs read back unchanged; every source/image/code reference was rehashed and serialized summary compared exactly before restoring missing local receipts. Tuple/list display-bound mismatch is not a model failure or an approval.')
    save(out / 'summary.json', result)
    module('depot_view_receipt_recovery_freeze', HERE / 'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(out.name, 'read-only-verified-complete-view-receipt-recovery', refs, result)


if __name__ == '__main__':
    main()
