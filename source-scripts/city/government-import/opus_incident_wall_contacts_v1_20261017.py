"""Exact incident-face/podium intersections; source-only nomination, no waiver."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from pool_incident_wall_contacts_v1_20261017 import closest
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-opus-incident-wall-contacts-v1-20261017';DOC=BASE/BATCH;PRIOR=BASE/'government-xl-opus-exact-wall-interfaces-v1-20261017'
def main():
 assert not DOC.exists();r=read(PRIOR/'result.json')
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for q in r['evidenceRefs']:assert digest((ROOT/q['path']).read_bytes())==q['sha256']
 inp=read(PRIOR/'input.json');g=next(g for g in read(ROOT/inp['geometryPath'])['rows']if g['uid']=='landsd/248432:0');support=np.array(g['position']).reshape(-1,3)[np.array(g['index']).reshape(-1,3)];a=support[:,0];u=support[:,1]-a;v=support[:,2]-a;det=u[:,0]*v[:,2]-u[:,2]*v[:,0];valid=np.abs(det)>1e-12;results=[]
 for row in read(PRIOR/'interfaces.json.gz')['rows']:
  output=[]
  for f in row['unresolved']:
   p=np.array(f['position']);candidates=[]
   if f.get('gap')is not None:
    deck=p.copy();deck[1]-=f['gap']
    for face in f['sourceFaces']:
     t=np.array(face['vertices']);q=closest(deck,t);delta=q-a;s=np.divide(delta[:,0]*v[:,2]-delta[:,2]*v[:,0],det,out=np.full_like(det,np.nan),where=valid);z=np.divide(u[:,0]*delta[:,2]-u[:,2]*delta[:,0],det,out=np.full_like(det,np.nan),where=valid);ids=np.flatnonzero(valid&(s>=-1e-8)&(z>=-1e-8)&(s+z<=1+1e-8));heights=a[ids,1]+s[ids]*u[ids,1]+z[ids]*v[ids,1];gaps=q[1]-heights;hits=[dict(faceIndex=int(i),height=float(h),gapM=float(gap))for i,h,gap in zip(ids,heights,gaps)if abs(gap)<=.001]
     distance=float(np.linalg.norm(q-p));start=float(np.linalg.norm(closest(p,t)-p));wall=abs(face['normal'][1])<=.1
     candidates.append(dict(sourceFace=face['faceIndex'],normal=face['normal'],sourceStartDistanceM=start,contact=q.tolist(),travelM=distance,embeddingHeightM=float(q[1]-p[1]),supportContacts=hits,boundedIncidentWallCandidate=bool(wall and hits and start<=.001 and distance<=.5 and q[1]>=p[1])))
   output.append(dict(position=f['position'],reason=f['reason'],originalGap=f.get('gap'),candidates=candidates,hasBoundedIncidentWallCandidate=any(x['boundedIncidentWallCandidate']for x in candidates)))
  results.append(dict(uid=row['uid'],remaining=len(output),boundedIncidentCandidates=sum(x['hasBoundedIncidentWallCandidate']for x in output),rows=output))
 DOC.mkdir();save(DOC/'contacts.json.gz',dict(rows=results,fullAcceptance=False,qualification='Same incident original triangle and actual original podium contact within1mm; bounded0.5m nomination only. Not complete support/acceptance or a wall-angle policy change. Missing deck samples remain unresolved.'))
 save(DOC/'summary.json',dict(rows=[{k:v for k,v in r.items()if k!='rows'}for r in results],fullAcceptance=False))
 refs=[Path(__file__),PRIOR/'result.json',HERE/'pool_incident_wall_contacts_v1_20261017.py',*[ROOT/q['path']for q in r['evidenceRefs']]]
 out=module('opus_incident_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-opus-incident-wall-contact-nomination-v1',refs,dict(uids=['landsd/248432:0','landsd/319559:0','landsd/322573:0'],fullAcceptance=False,newlyInstalled=0));print(dict(jobId=out['jobId'],summary=read(DOC/'summary.json')),flush=True)
if __name__=='__main__':main()
