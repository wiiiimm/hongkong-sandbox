"""Register completed private shelter validation; no numeric replay or installation."""
from pathlib import Path
import json
import heritage128971_corrected_basic_validation_v1_20261015 as v
from exact_distinct_evidence_refs_v1_20261014 import distinct_refs
from run import connect

def main():
 completion=v.read(v.DOC/'completion.json');assert completion['complete']and completion['ordinaryRegressions']==[]and all(not x for x in completion['finiteCandidateUnproved'].values())
 inp=v.read(v.DOC/'input.json.gz');stream=v.read(v.DOC/'corrected-basic-streams.json.gz')
 prior=v.read(v.BASE/'government-xl-heritage165054-saved-full-actor-finite-v1-20261014/result.json')
 certificate=v.read(v.BASE/'government-xl-heritage165054-saved-full-actor-finite-v1-20261014/ROOT-VERIFIED.json')
 assert prior['jobId']==certificate['jobId']=='6ac185d95e1d60771144487eed72cf18b16ee403935d6fa87c6e9bf7f17f3d65'and certificate['allEvidenceHashesVerified']and certificate['leaseReleased']
 refs=distinct_refs(inp['evidenceRefs']+prior['evidenceRefs']+[dict(path=p,sha256=h)for p,h in stream['completeRecursiveProductionModuleClosure']['inputHashes'].items()]+[v.ref(Path(__file__))])
 for q in refs:v.check(q)
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY')
  assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(prior['jobId'],)).fetchone()==('complete',prior)
  groups=db.execute('SELECT owner,resources,released_at IS NOT NULL FROM astra_modelling.reservation_groups WHERE batch=%s',(v.BATCH,)).fetchall()
  actual=[r for r in groups if r[0].startswith('heritage-shelter-')]
  assert len(actual)==1 and actual[0][2]and len(actual[0][1])==47
 v.save(v.DOC/'completed-worker-lease-readback.json',dict(originalWorkerReleased=True,canonicalResourceCount=47,readbackSource='pinned Neon reservation_groups',noModelInstallation=True))
 freezer=v.capture.bounds.source.completed.prior.module(v.capture.bounds.source.completed.prior.old.FREEZER,'heritage_shelter_receipt_freezer')
 result=freezer.freeze(v.BATCH,'complete-corrected-terrain-estimated-basic-private-validation-no-install',[v.check(q)for q in refs],dict(uids=['landsd/165054:0',v.UID],sourceOnly=True,ordinaryNeighbourRegressions=[],completeBasicFaces=108,completeArithmeticModes=3,allFiniteCandidateBoundsProved=True,originalBeforeStatePreserved=True,estimatedBasicBaseChangedPrivately=True,governmentBuildingGeometryChanges=0,physicalAccepted=False,nextStep='Joint Museum private stage, exact original warning applicability and staged/live browser acceptance; atomic terrain and estimated-base publication only.'))
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(result['jobId'],)).fetchone()==('complete',result)
 for q in result['evidenceRefs']:v.check(q)
 v.save(v.DOC/'ROOT-VERIFIED.json',dict(jobId=result['jobId'],exactNeonReadback=True,allEvidenceHashesVerified=True,leaseReleased=True,evidenceRefs=len(result['evidenceRefs']),originalWorkerLeaseReadback=v.ref(v.DOC/'completed-worker-lease-readback.json'),sourceOnly=True,physicalAccepted=False,newlyInstalled=0))
 print(json.dumps(dict(jobId=result['jobId'],evidenceRefs=len(result['evidenceRefs']),verified=True)))
if __name__=='__main__':main()
