"""Independent interval-coverage verification for exact unchanged Verdant source seams."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from pool_incident_wall_contacts_v1_20261017 import closest
BASE=ROOT/'docs/astra-city/government-import';PRIOR=BASE/'government-xl-wave-verdant-seam-bounds-v1-20261018';ASSEMBLY=BASE/'government-xl-wave-verdant-assembly-four-worlds-v1-20261017';BATCH='government-xl-verdant195000-seam-review-v1-20261018';DOC=BASE/BATCH;UID='landsd/195000:0'
def main():
 assert not DOC.exists();r=read(PRIOR/'result.json');pins={}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for e in r['evidenceRefs']:
  assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 foundations=read(ASSEMBLY/'summary.json')['rows'];rows=[]
 for mode in ['original','literal','left','balanced']:
  data=read(PRIOR/(mode+'-195000:0.json.gz'));support=np.asarray(read(ASSEMBLY/mode/'input.json.gz')['podium']);assert data['allFlaggedEdgesCertified']and len(data['edges'])==11
  f=next(r for r in foundations if r['mode']==mode and r['uid']==UID);assert f['strictFoundationAccepted']and f['buried']==f['upwardBuried']==0
  intervals=0;maximum=0.;edges=[]
  for e in data['edges']:
   assert e['certifiedWithinPointOneM']and not e['failed'];a,b=np.asarray(e['edge']);d=b-a;assert d@d>0;coverage=[];edges.append((a,b))
   for leaf in e['leaves']:
    x,y=np.asarray(leaf['a']),np.asarray(leaf['b']);mid=(x+y)/2;distance=np.linalg.norm(closest(mid,support[leaf['supportFace']])-mid);bound=float(distance+np.linalg.norm(y-x)/2);assert abs(bound-leaf['upperBoundM'])<1e-9 and bound<=.1
    u,v=sorted([float((x-a)@d/(d@d)),float((y-a)@d/(d@d))]);assert -.000000001<=u<=v<=1.000000001 and np.linalg.norm(x-(a+((x-a)@d/(d@d))*d))<1e-8 and np.linalg.norm(y-(a+((y-a)@d/(d@d))*d))<1e-8;coverage.append((u,v));maximum=max(maximum,bound);intervals+=1
   end=0.
   for u,v in sorted(coverage):assert u<=end+1e-9;end=max(end,v)
   assert end>=1-1e-9
  for point in data['unresolvedPoints']:
   p=np.asarray(point['position']);distance=np.linalg.norm(closest(p,support[point['supportFace']])-p);assert distance<=.1 and abs(distance-point['distanceM'])<1e-9
   assert min(np.linalg.norm(p-(a+np.clip((p-a)@(b-a)/((b-a)@(b-a)),0,1)*(b-a)))for a,b in edges)<.001
  rows.append(dict(mode=mode,completeFlaggedEdgesVerified=11,certifiedIntervals=intervals,maximumCertifiedDistanceM=maximum,maximumSampleDistanceM=max(p['distanceM']for p in data['unresolvedPoints']),strictContacts=f['strictContacts'],rawUnresolved=f['unresolved']))
 source=next(r for r in read(BASE/'government-xl-wave-verdant-podium-support-v1-20261017/support-inputs.json')['sources']if r['uid']==UID)
 review=dict(uid=UID,sourceSHA256=source['sourceSHA256'],sourceSpecificSeamInterpretationAccepted=True,fullAcceptance=False,installationApproved=False,currentMapAcceptance=False,rawStrictWarningsPreserved=True,rows=rows,sourceGeometryChanges=0,sourcePoseChanges=0,aiGeometryModelling=False,sourceEvidenceInterpretationUsedAI=True,reason='The original tower has extensive strict compound contact and zero wholly buried faces. All eleven residual rim samples and complete incident low-rim edges remain within the independently certified small seam of the unchanged compound support surfaces in every coordinate mode. Large vertical-ray differences at these side boundaries do not describe the measured physical seam. This exact-source interpretation does not change any generic vertical-support threshold or certify engineering support.',remaining=['Retained194544 neighbour source/placement issue','Current source identity, full affected-neighbour checks and current-map rebind','Complete staged/live browser and failed-download dependency checks','Guarded installation and installed ledger recording'])
 save(DOC/'ROOT-SEAM-REVIEW.json',review);out=module('verdant_seam_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'verdant-exact-original-complete-rim-seam-review-v1',[Path(__file__),PRIOR/'result.json',HERE/'pool_incident_wall_contacts_v1_20261017.py',*[ROOT/p for p in pins]],dict(uids=[UID],sourceSpecificSeamInterpretationAccepted=True,fullAcceptance=False,newlyInstalled=0));print(out['jobId'],flush=True);print(rows,flush=True)
if __name__=='__main__':main()
