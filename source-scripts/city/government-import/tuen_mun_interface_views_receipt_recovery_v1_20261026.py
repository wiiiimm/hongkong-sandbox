"""Restore an exact completed diagram receipt after JSON integer-key readback mismatch."""
import json
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module


def main():
    base=ROOT/'docs/astra-city/government-import'
    old=base/'government-xl-after-pok-oi-tuen-mun-four-neighbour-original-interface-views-v2-20261026'
    batch='government-xl-after-pok-oi-tuen-mun-interface-views-receipt-recovery-v1-20261026';out=base/batch
    assert not out.exists() and not (old/'result.json').exists()
    jobid='eee6b588471dd7c8d2e7596ca7eedf0f2dfed23da5e904eddca684b841296d09'
    with connect()as db:
        db.execute('SET TRANSACTION READ ONLY')
        record=db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jobid,)).fetchone()
    assert record and record[0]=='complete';result=record[1]
    assert result['batch']==old.name and result['stage']=='complete-original-contact-interface-source-close-views'
    summary=read(old/'summary.json');assert all(result[k]==v for k,v in summary.items())
    assert len(result['rows'])==5 and result['visualAcceptance']is False and result['installationApproved']is False
    before=json.loads(json.dumps(result))
    for row in before['rows']:
        row['dimensions']={int(k):v for k,v in row['dimensions'].items()}
    assert before!=result and json.loads(json.dumps(before))==result
    refs=[Path(__file__)]
    for ref in result['evidenceRefs']:
        path=ROOT/ref['path'];assert digest(path.read_bytes())==ref['sha256'];refs.append(path)
    save(out/'original-completed-result.json',result)
    save(out/'serialization-validation.json',dict(originalJobId=jobid,status='complete',allOriginalEvidenceHashesVerified=True,
         soleMismatch='Integer Counter dimension keys become strings in JSONB; reconstructing only those keys reproduces the failed Python equality.',
         exactJSONRoundTripVerified=True,numericalReplay=False,sourceGeometryChanges=0,originalProducerChanged=False))
    # Finalize missing local files from the exact original completed database value.
    save(old/'result.json',result);save(old/'neon-sync.json',dict(jobId=jobid,resultVerified=True))
    refs.extend([old/'result.json',old/'neon-sync.json'])
    report=dict(uids=result['uids'],originalJobId=jobid,receiptRecoveryOnly=True,originalCompletedResultUnchanged=True,
                imagesExported=5,imagesReviewed=False,sourceGeometryChanges=0,identityAccepted=False,
                physicalAcceptance=False,visualAcceptance=False,installationApproved=False,publication=False,
                qualification='Original completed job and every frozen evidence byte verified. Missing local receipt restored verbatim after reproducing solely integer-key JSON round-trip mismatch. No diagram/geometry rerun, original evidence mutation, review or installed credit.')
    module('interface_views_receipt_recovery_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(
        batch,'completed-exact-diagram-json-dimension-key-receipt-recovery',refs,report)
    with connect()as db:
        db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jobid,)).fetchone()==record


if __name__=='__main__':main()
