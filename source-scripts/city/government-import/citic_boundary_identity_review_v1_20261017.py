"""Record a bounded AI source-identity review, never geometry modelling or installation."""
from pathlib import Path
from copy import deepcopy
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from citic_reviewed_boundary_identity_v1_20261017 import apply_review,UID,SOURCE,WORLD,REVIEW,BASE

def main():
 assert not REVIEW.exists();refs=[Path(__file__),HERE/'citic_reviewed_boundary_identity_v1_20261017.py'];pins={}
 names=['government-xl-citic-current-assembly-v1-20261017','government-xl-citic-current-boundary-review-v1-20261017','government-xl-citic-exact-contacts-v1-20261017','government-xl-citic-current-primary-boundaries-v1-20261017']
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  for name in names:
   p=BASE/name/'result.json';r=read(p);assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(p)
   for ref in r['evidenceRefs']:
    path=ROOT/ref['path'];assert digest(path.read_bytes())==ref['sha256'];refs.append(path);pins[ref['path']]=ref['sha256']
 rawpath=BASE/names[0]/'landsd-232579-0-identity.json';assert digest(rawpath.read_bytes())==pins[str(rawpath.relative_to(ROOT))];raw=read(rawpath)
 decision=dict(uid=UID,sourceSHA256=SOURCE,worldTrianglesSHA256=WORLD,completeSourceFaces=1762,foreignUIDs=['landsd/123871:0','landsd/234783:0','landsd/256427:0'],identityOnlyApproved=True,installationApproved=False,sourceIdentityReviewUsedAI=True,modelGeometryChanges=0,
  basis='Exact government source root/GeoRef/type/CSUID match, whole-cell coverage and 99.87% target footprint coverage identify the complete CITIC podium. Current official records independently confirm stable BuildingID/CSUID/type for all five actors. Complete original context views place the named excess on the rear adjoining roof/wall boundary, not on a different building body. This named source-role interpretation resolves identity attribution only.',
  retainedLimitations='16.096964m2 raw unrelated-footprint excess remains. Exact source contacts remain 51 lines and 8 points, not a clearance proof. Tamar provider/current boundary differences are retained; no universal exact shared-boundary claim. All three foreign actors stay independent; no shared property/support ownership, foreign suppression, coordinate change, tolerance change or geometry edit.',
  remainingRequired='Current full physical acceptance for podium and tower, strict support interface and compound foundation, original finite clearance, production loading/picking/collision, complete affected-neighbour checks, desktop/mobile browser review, failed-dependency fallback and atomic publication/accounting.')
 REVIEW.mkdir();save(REVIEW/'decision.json',decision);save(REVIEW/'expected-raw-identity.json',raw)
 out=apply_review(raw,raw,decision);assert out['passed'] and out['installationApproved'] is False and out['physicalAccepted'] is False and out['rawIdentityVerbatim']==raw
 tests=[]
 for key,value in [('sourceSHA256','changed'),('worldTrianglesSHA256','changed'),('uid','landsd/other:0'),('reasons',raw['reasons']+['new-placement-failure'])]:
  changed=deepcopy(raw);changed[key]=value
  try:apply_review(changed,raw,decision)
  except AssertionError:tests.append(key)
  else:raise AssertionError('Altered evidence accepted: '+key)
 changed=deepcopy(raw);changed['freshCurrentIdentity']['intersectingForms'].pop()
 try:apply_review(changed,raw,decision)
 except AssertionError:tests.append('missing-current-form')
 else:raise AssertionError('Missing foreign actor accepted')
 changed=deepcopy(decision);changed['installationApproved']=True
 try:apply_review(raw,raw,changed)
 except AssertionError:tests.append('publication-escalation')
 else:raise AssertionError('Publication escalation accepted')
 save(REVIEW/'identity-proof.json',out);save(REVIEW/'adversarial-checks.json',dict(rejectedMutations=tests,rawEvidenceRetained=True,physicalApproval=False,installationApproval=False))
 result=module('citic_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(REVIEW.name,'exact-citic-rear-boundary-source-identity-review-v1',list(dict.fromkeys(refs)),dict(uids=[UID],identityAccepted=True,sourceIdentityReviewUsedAI=True,physicalAccepted=False,installationApproved=False,newlyInstalled=0,modelGeometryChanges=0,adversarialChecks=len(tests)))
 print(dict(jobId=result['jobId'],identityAccepted=True,installationApproved=False),flush=True)
if __name__=='__main__':main()
