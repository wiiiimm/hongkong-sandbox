"""Recover completed exact review receipt after tuple/list JSON readback mismatch."""
from pathlib import Path
import json
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from ocean_native_junction_role_review_v1_20261027 import BATCH,SOURCES,PAIRS
STAGE='four-original-harbour-city-native-junction-source-role-review-v1'
def main():
 base=ROOT/'docs/astra-city/government-import';doc=base/BATCH;assert not(doc/'result.json').exists()
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');rows=c.execute('SELECT id,status,result FROM astra_modelling.jobs WHERE batch=%s AND stage=%s',(BATCH,STAGE)).fetchall()
 assert len(rows)==1;job,status,result=rows[0];assert status=='complete'and result['jobId']==job and result['batch']==BATCH and result['stage']==STAGE
 assert result['sourceSHA256ByUid']==SOURCES and result['sourceSpecificArchitecturalInterfaceInterpretationAccepted']is True
 assert result['pairs']==[list(p)for p in PAIRS] and not result['physicalAcceptance']and not result['visualAcceptance']and not result['installationApproved']and not result['publication']and result['newlyInstalled']==0
 for ref in result['evidenceRefs']:assert digest((ROOT/ref['path']).read_bytes())==ref['sha256'],ref['path']
 review=read(doc/'ROOT-JUNCTION-ROLE-REVIEW.json');assert review['sourceSHA256ByUid']==SOURCES and review['sourceSpecificArchitecturalInterfaceInterpretationAccepted']and not review['physicalAcceptance']and not review['installationApproved']
 save(doc/'result.json',result);save(doc/'neon-sync.json',dict(jobId=job,resultVerified=True,localReceiptRecoveredWithoutJobMutation=True))
 recovery=BATCH.replace('role-review-v1','role-receipt-recovery-v1');out=base/recovery
 explanation=dict(originalJobId=job,originalStatus='complete',originalJobUnchanged=True,roleEvidenceUnchanged=True,reason='The original producer supplied pairs as Python tuples; JSONB returned lists. Its final Python equality check failed after the transaction had already completed. Canonical stored JSON and every pre-existing evidence hash verified. This recovery writes the exact stored completed result locally, without rerunning the review or changing approval fields.',sourceGeometryChanges=0,installationApproved=False)
 save(out/'recovery.json',explanation)
 module('ocean_junction_role_receipt_recovery',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(recovery,'completed-original-junction-role-review-receipt-recovery-v1',[Path(__file__),doc/'result.json',doc/'ROOT-JUNCTION-ROLE-REVIEW.json'],dict(uids=list(SOURCES),**explanation))
 print(dict(originalJobId=job,verified=True))
if __name__=='__main__':main()
