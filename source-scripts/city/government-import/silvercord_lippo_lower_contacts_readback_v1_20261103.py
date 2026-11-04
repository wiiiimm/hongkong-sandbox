"""Recover the already complete contact job after integer JSON-key readback.

Read-only Neon access; no requeue, geometry work or model-state mutation.
"""
import hashlib
import uuid
from pathlib import Path
from run import ROOT, HERE, read, save, digest, reservations, connect, jobs

BATCH = 'government-xl-silvercord-lippo-lower-patch-source-contacts-v1-20261103'
STAGE = 'complete-four-world-low-downward-source-facet-finite-contacts'


def main():
    doc = ROOT / 'docs/astra-city/government-import' / BATCH
    summary = read(doc / 'summary.json')  # JSON round trip normalizes category keys.
    assert summary['uids'] == ['landsd/233997:0', 'landsd/231645:0'] and len(summary['rows']) == 8
    assert summary['sourceRoleAccepted'] is summary['physicalAcceptance'] is summary['installationApproved'] is False
    claim = reservations.claim('lower-contact-readback-' + str(uuid.uuid4()), ['source-context:' + BATCH], batch=BATCH, ttl=1800)
    assert claim['ok'], claim
    lease = claim['reservation']
    try:
        with connect() as db:
            db.execute('SET TRANSACTION READ ONLY')
            rows = db.execute('SELECT id,status,result,payload,owner,token,lease_until FROM astra_modelling.jobs WHERE batch=%s AND stage=%s', (BATCH, STAGE)).fetchall()
        assert len(rows) == 1
        job_id, status, result, payload, owner, token, expiry = rows[0]
        assert status == 'complete' and owner is token is expiry is None
        assert job_id == hashlib.sha256(jobs.encode([BATCH, STAGE, payload]).encode()).hexdigest()
        assert result['jobId'] == job_id and result['batch'] == BATCH and result['stage'] == STAGE
        assert result['uids'] == payload['uids'] == summary['uids']
        assert result['evidenceRefs'] == payload['evidenceRefs']
        for key, value in summary.items():
            assert result[key] == value, key
        for key in ['newlyInstalled', 'modelGeometryChanges', 'terrainGeometryChanges', 'scriptExternalAICalls']:
            assert result[key] == 0
        for key in ['publication', 'aiGeometryModelling', 'installationApproved', 'permanentRejection']:
            assert result[key] is False
        for ref in result['evidenceRefs']:
            path = (ROOT / ref['path']).resolve()
            assert path.is_relative_to(ROOT) and digest(path.read_bytes()) == ref['sha256']
        assert reservations.owns(lease)
        path = doc / 'result.json'
        if path.exists():
            assert read(path) == result
        else:
            save(path, result)
        save(doc / 'neon-sync.json', dict(jobId=job_id, resultVerified=True, readOnlyRecovery=True,
              originalFailure='Python integer contact-dimension category keys differ from JSONB string keys',
              geometryComputationsRepeated=0, databaseWrites=0,
              recoveryScript=dict(path=str(Path(__file__).relative_to(ROOT)), sha256=digest(Path(__file__).read_bytes()))))
        print(dict(jobId=job_id, alreadyCompleteOnNeon=True, allEvidenceBytesVerified=True, geometryComputationsRepeated=0), flush=True)
    finally:
        assert reservations.release(lease)['ok']


if __name__ == '__main__':
    main()
