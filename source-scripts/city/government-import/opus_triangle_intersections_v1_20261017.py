"""Original triangle intersection witnesses; diagnostic only, no source edits."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from pool_incident_wall_contacts_v1_20261017 import closest
from require_remaining_xl import require_remaining
BASE=ROOT/'docs/astra-city/government-import'
PRIOR=BASE/'government-xl-opus-exact-wall-interfaces-v1-20261017'
BATCH='government-xl-opus-triangle-intersections-v1-20261017';DOC=BASE/BATCH

def edge_hits(source,target):
 n=np.cross(target[1]-target[0],target[2]-target[0]);length=np.linalg.norm(n)
 if length==0:return []
 n=n/length;hits=[]
 for i in range(3):
  a,b=source[i],source[(i+1)%3];da=float(np.dot(a-target[0],n));db=float(np.dot(b-target[0],n))
  if abs(da-db)<1e-12:continue # Coplanar edges need separate evidence.
  t=da/(da-db)
  if t < -1e-10 or t > 1+1e-10:continue
  q=a+np.clip(t,0,1)*(b-a)
  if np.linalg.norm(closest(q,target)-q)<=1e-8:hits.append(q)
 return hits

def contact(p,a,b):
 hits=edge_hits(a,b)+edge_hits(b,a)
 if not hits:return None
 candidates=list(hits)
 for x in hits:
  for y in hits:
   d=y-x;den=np.dot(d,d)
   if den>0:candidates.append(x+np.clip(np.dot(p-x,d)/den,0,1)*d)
 q=min(candidates,key=lambda q:np.linalg.norm(q-p))
 assert np.linalg.norm(closest(q,a)-q)<1e-7
 assert np.linalg.norm(closest(q,b)-q)<1e-7
 return q

def main():
 a=np.array([[0.,0,0],[1,0,0],[0,0,1]])
 b=np.array([[.2,-1,.2],[.2,1,.2],[.2,0,.8]])
 q=contact(np.array([.2,0,.4]),a,b);assert q is not None and np.linalg.norm(q-[.2,0,.4])<1e-9
 assert contact(np.zeros(3),a,b+[10,0,0]) is None
 assert not DOC.exists()
 count=BASE/'government-xl-sham-shui-po-pool-original-installed-v1-20261017/full-xl-current-count.json'
 require_remaining(count,'landsd/322573:0','e3c4ad4fff2acda8844233c83b6885dbbd73c1da9acb0a0efc7ec9778f57d764')
 r=read(PRIOR/'result.json')
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for ref in r['evidenceRefs']:assert digest((ROOT/ref['path']).read_bytes())==ref['sha256']
 inp=read(PRIOR/'input.json');g=next(g for g in read(ROOT/inp['geometryPath'])['rows'] if g['uid']=='landsd/248432:0')
 support=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];lo=support.min(axis=1);hi=support.max(axis=1);rows=[]
 for row in read(PRIOR/'interfaces.json.gz')['rows']:
  for f in row['unresolved']:
   p=np.array(f['position']);candidates=[]
   ids=np.flatnonzero(np.all(hi>=p-.5,axis=1)&np.all(lo<=p+.5,axis=1))
   for face in f['sourceFaces']:
    a=np.array(face['vertices'])
    for i in ids:
     q=contact(p,a,support[i])
     if q is None:continue
     distance=float(np.linalg.norm(q-p))
     if distance<=.5 and q[1]>=p[1]-1e-8:
      candidates.append(dict(sourceFace=face['faceIndex'],supportFace=int(i),contact=q.tolist(),distanceM=distance,sourceNormal=face['normal'],sourceTriangle=a.tolist(),supportTriangle=support[i].tolist()))
   candidates.sort(key=lambda x:x['distanceM'])
   rows.append(dict(uid=row['uid'],position=f['position'],originalReason=f['reason'],originalGap=f.get('gap'),witness=candidates[0] if candidates else None,candidateCount=len(candidates)))
 summary=dict(samples=len(rows),withIntersection=sum(x['witness'] is not None for x in rows),missingVerticalSamples=sum(x['originalGap'] is None for x in rows),missingVerticalWithIntersection=sum(x['originalGap'] is None and x['witness'] is not None for x in rows),fullAcceptance=False,newlyInstalled=0)
 DOC.mkdir();save(DOC/'contacts.json.gz',dict(rows=rows,qualification='Exact original noncoplanar triangle intersections, within half metre and not below rim. No wall-role, coordinate-mode, terrain or whole-model acceptance implied. Coplanar-only contacts are not evaluated.'));save(DOC/'summary.json',summary)
 refs=[Path(__file__),HERE/'pool_incident_wall_contacts_v1_20261017.py',HERE/'require_remaining_xl.py',count,PRIOR/'result.json',*[ROOT/x['path'] for x in r['evidenceRefs']]]
 out=module('opus_triangle_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-opus-triangle-intersection-witnesses-v1',refs,dict(uids=['landsd/248432:0','landsd/319559:0','landsd/322573:0'],**summary));print(dict(jobId=out['jobId'],**summary),flush=True)
if __name__=='__main__':main()
