"""Restore a completed diagnostic receipt after tuple/list JSON serialization mismatch."""
import argparse,json
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--batch',required=True);ap.add_argument('--original',required=True);a=ap.parse_args()
    assert all(n.startswith('government-xl-')and'/'not in n for n in [a.batch,a.original])
    base=ROOT/'docs/astra-city/government-import';old=base/a.original;out=base/a.batch
    assert not out.exists()and not(old/'result.json').exists()
    with connect()as db:
        db.execute('SET TRANSACTION READ ONLY')
        rows=db.execute("SELECT id,status,result FROM astra_modelling.jobs WHERE batch=%s AND stage=%s",(a.original,'negative-original-face-exact-component-context')).fetchall()
    assert len(rows)==1;jobid,status,result=rows[0];assert status=='complete'and result['jobId']==jobid
    summary=read(old/'summary.json');assert all(result[k]==v for k,v in summary.items())
    assert result['physicalAcceptance']is False and result['installationApproved']is False
    reconstructed=json.loads(json.dumps(result))
    for row in reconstructed['rows']:
        for face in row['faces']:
            for edge in face['exactEdgeIncidence']:edge['endpoints']=[tuple(p)for p in edge['endpoints']]
    assert reconstructed!=result and json.loads(json.dumps(reconstructed))==result
    refs=[Path(__file__)]
    for ref in result['evidenceRefs']:
        path=ROOT/ref['path'];assert digest(path.read_bytes())==ref['sha256'];refs.append(path)
    save(old/'result.json',result);save(old/'neon-sync.json',dict(jobId=jobid,resultVerified=True))
    refs.extend([old/'result.json',old/'neon-sync.json'])
    report=dict(uids=result['uids'],originalJobId=jobid,receiptRecoveryOnly=True,
                soleMismatch='Exact edge endpoints were Python tuples; JSONB stores lists. Only reconstructing those endpoints reproduces the failed equality.',
                exactJSONRoundTripVerified=True,numericalReplay=False,originalProducerChanged=False,
                sourceGeometryChanges=0,physicalAcceptance=False,installationApproved=False,publication=False)
    module('component_receipt_recovery_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'exact-completed-component-context-json-receipt-recovery',refs,report)
    with connect()as db:
        db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(jobid,)).fetchone()==(status,result)


if __name__=='__main__':main()
