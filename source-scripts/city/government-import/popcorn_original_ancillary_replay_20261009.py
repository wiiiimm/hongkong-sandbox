"""Replay all immutable original PopCorn source-role evidence before identity reuse."""
from run import ROOT,read,digest,connect
from popcorn_original_ancillary_identity_20261009 import verify_collection
RECEIPT=ROOT/'docs/astra-city/government-import/government-xl-popcorn-source-access-ownership-20261009/result.json'
JOB='eb88cbdd893c8b4d4456352e844894d01f86d5358eb9421381e22eed361f4bb2'
def verify_frozen_role_receipt():
 receipt=read(RECEIPT);assert receipt['jobId']==JOB and receipt['identityAccepted'] and not receipt['installationApproved']
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(JOB,)).fetchone()==('complete',receipt)
 for ref in receipt['evidenceRefs']:
  path=ROOT/ref['path'];assert path.resolve().is_relative_to(ROOT.resolve());assert digest(path.read_bytes())==ref['sha256'],ref['path']
 current=verify_collection();assert current==receipt['identityProof'];return {**current,'immutableIdentityJobId':JOB,'everyIndependentEvidenceHashReplayed':True,'installationApproved':False,'physicalAcceptance':False,'runtimeAccepted':False}
if __name__=='__main__':
 p=verify_frozen_role_receipt();print({'identityAccepted':p['identityAccepted'],'everyIndependentEvidenceHashReplayed':p['everyIndependentEvidenceHashReplayed'],'physicalAccepted':False,'installationApproved':False},flush=True)
