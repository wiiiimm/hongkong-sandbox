"""Recover an already committed diagnostic receipt after tuple/JSON-list mismatch.

Read-only job verification; the completed producer and database row are immutable.
"""
import uuid
from pathlib import Path
from run import ROOT, HERE, read, save, digest, connect, reservations
from primrose_compound_foundation_v2_20261015 import module

BASE = ROOT/'docs/astra-city/government-import'
PRIOR = 'government-xl-elegant-garden-source-edit-separation-v1-20261028'
BATCH = 'government-xl-elegant-garden-separation-receipt-readback-v1-20261028'
DOC = BASE/BATCH
JOB = 'b53136cda7d527b4de2902d953755547a090bc96e9e4421f5948f3843719695b'


def main():
    assert not DOC.exists() and not (BASE/PRIOR/'result.json').exists()
    summary = read(BASE/PRIOR/'summary.json')
    with connect() as db:
        db.execute('SET TRANSACTION READ ONLY')
        status, result = db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (JOB,)).fetchone()
    assert status == 'complete' and result['batch'] == PRIOR
    assert result['stage'] == 'complete-original-project-neighbour-edit-separation-diagnostic'
    # JSON readback normalises only tuples to arrays; every original summary
    # field and value must match, not merely selected diagnostic counts.
    assert all(result[key] == value for key, value in summary.items())
    assert result['jobId'] == JOB and result['installationApproved'] is False
    for ref in result['evidenceRefs']:
        assert digest((ROOT/ref['path']).read_bytes()) == ref['sha256'], ref['path']
    claim = reservations.claim('elegant-receipt-readback-'+str(uuid.uuid4()), ['source-context:'+PRIOR], batch=BATCH, ttl=1800)
    assert claim['ok']
    lease = claim['reservation']
    try:
        save(BASE/PRIOR/'result.json', result)
        save(BASE/PRIOR/'neon-sync.json', dict(jobId=JOB, resultVerified=True,
            recovery='Independent complete JSON-normalised summary and every input hash verified; no database row or completed producer changed.'))
        with connect() as db:
            db.execute('SET TRANSACTION READ ONLY')
            assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s', (JOB,)).fetchone() == ('complete', read(BASE/PRIOR/'result.json'))
        out = dict(uids=summary['uids'], recoveredCompletedJobId=JOB,
            completeJSONSummaryEquality=True, allEvidenceHashesVerified=True,
            databaseWritesToPriorJob=0, geometryRecomputed=False,
            failedProducerPreserved=True, installationApproved=False,
            qualification='The producer completed its database transaction, then its Python tuple-versus-JSON-list comparison failed. Independent readback confirms every normalised summary value and every bound byte. Only missing local result/readback files are materialised; no geometric diagnostic or approval is changed.')
        save(DOC/'summary.json', out)
        module('elegant_separation_readback_freeze', HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
            BATCH, 'completed-diagnostic-json-receipt-independent-readback',
            [Path(__file__), BASE/PRIOR/'summary.json', BASE/PRIOR/'result.json', BASE/PRIOR/'neon-sync.json'], out)
        print(dict(recoveredJobId=JOB, allBoundInputsVerified=True), flush=True)
    finally:
        assert reservations.release(lease)['ok']


if __name__ == '__main__':
    main()
