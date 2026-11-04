"""Verify each flagged witness has a finite same-face path to original podium."""
from pathlib import Path
from fractions import Fraction
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from pool_incident_wall_contacts_v1_20261017 import closest
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-victoria-mall-finite-segment-verification-v1-20261020';DOC=BASE/BATCH
SRC=BASE/'government-xl-victoria-mall-incident-finite-contacts-v1-20261020';CAP=BASE/'government-xl-victoria-mall-actual-render-attributes-v1-20261020';OLD=BASE/'government-xl-victoria-mall-complete-source-lower-joins-context-v1-20261012'
assert not DOC.exists();refs=[Path(__file__),HERE/'pool_incident_wall_contacts_v1_20261017.py'];pins={}
with connect()as c:
 c.execute('SET TRANSACTION READ ONLY')
 for folder in [SRC,CAP,OLD]:
  r=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json');pins[folder.name]={e['path']:e['sha256']for e in r['evidenceRefs']}
def consume(folder,name):
 p=folder/name;assert digest(p.read_bytes())==pins[folder.name][str(p.relative_to(ROOT))];refs.append(p);return read(p)
capture=consume(CAP,'attributes.json.gz');old=consume(OLD,'context.json.gz');summary=[]
for mode,field in [('original',None),('literal','completeLiteralWorldPosition'),('explicitLeftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('explicitBalancedF32','completeExplicitBalancedFloat32WorldPosition')]:
 world={u:np.asarray(t,dtype='<f8')for u,t in old['all4CompleteOriginalWorldTriangles'].items()}if field is None else {r['uid']:np.asarray(r[field],dtype='<f8').reshape(-1,3)[np.asarray(r['completeOriginalIndex']).reshape(-1,3)]for r in capture['rows']}
 rows=[]
 for target in consume(SRC,mode+'-targets.json.gz')['rows']:
  start=np.asarray(target['rawWitness']['position']);candidates=[]
  for contact in target['contactRows']:
   assert contact['dimension']>0
   points=np.array([[float(Fraction(v))for v in p]for p in contact['exactPoints']]);end=points.mean(0);face=world[target['uid']][contact['sourceFaceA']]
   normal=np.cross(face[1]-face[0],face[2]-face[0]);normal/=np.linalg.norm(normal)
   residual=max(float(np.linalg.norm(closest(p,face)-p))for p in [start,end])
   # Convex finite triangle: two endpoints inside imply the entire segment is
   # inside. Report residual and slope explicitly; no change to strict policy.
   candidates.append(dict(sourceFaceId=contact['sourceFaceA'],supportFaceId=contact['sourceFaceB'],start=start.tolist(),end=end.tolist(),endpointResidualM=residual,pathLengthM=float(np.linalg.norm(end-start)),wallNormalY=float(normal[1]),contact=contact))
  best=min(candidates,key=lambda c:(c['endpointResidualM']>.001,c['pathLengthM']))
  rows.append(dict(uid=target['uid'],rawWitness=target['rawWitness'],**best,finiteSameFaceSegment=best['endpointResidualM']<=.001))
 save(DOC/(mode+'.json.gz'),dict(rows=rows,installationApproved=False))
 item=dict(mode=mode,targets=len(rows),finiteSameFaceSegments=sum(r['finiteSameFaceSegment']for r in rows),maximumEndpointResidualM=max(r['endpointResidualM']for r in rows),maximumPathLengthM=max(r['pathLengthM']for r in rows),maximumAbsoluteNormalY=max(abs(r['wallNormalY'])for r in rows));summary.append(item);print(item,flush=True)
for p in refs:
 for mapping in pins.values():
  k=str(p.relative_to(ROOT))
  if k in mapping:assert digest(p.read_bytes())==mapping[k]
save(DOC/'summary.json',dict(rows=summary,installationApproved=False,strictPolicyFailuresPreserved=True,sourceGeometryChanges=0,qualification='Finite original face segment evidence only. No tolerance, architecture or physical acceptance change.'))
module('victoria_segment_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'finite-original-incident-wall-segment-verification',list(dict.fromkeys(refs)),dict(uids=['landsd/227593:0','landsd/251609:0','landsd/251615:0'],rows=summary,installationApproved=False))
