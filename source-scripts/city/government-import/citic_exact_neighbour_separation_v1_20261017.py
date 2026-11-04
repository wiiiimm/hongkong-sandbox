"""Closed original-facet separation diagnostic, including vertical and degenerate faces."""
from fractions import Fraction as F
from pathlib import Path
import uuid
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_closed_projection_intersection_20261010 import intersection,on
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-citic-exact-neighbour-separation-v1-20261017';DOC=BASE/BATCH
PREV=BASE/'government-xl-citic-neighbour-originals-v1-20261017';LOCAL=HERE/'local'/PREV.name

def rational(p):return tuple(F.from_float(float(x)) for x in p)
def height(face,p):
 a,b,c=list(map(rational,face));u=tuple(b[k]-a[k] for k in range(3));v=tuple(c[k]-a[k] for k in range(3));n=(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0])
 if n[1]:
  y=a[1]-(n[0]*(p[0]-a[0])+n[2]*(p[1]-a[2]))/n[1];return y,y
 ys=[]
 for a,b in [(a,b),(b,c),(c,a)]:
  ap=(a[0],a[2]);bp=(b[0],b[2])
  if not on(p,ap,bp):continue
  if ap==bp:ys.extend([a[1],b[1]])
  else:
   k=0 if bp[0]!=ap[0] else 1;t=(p[k]-ap[k])/(bp[k]-ap[k]);ys.append(a[1]+t*(b[1]-a[1]))
 assert ys;return min(ys),max(ys)
def compare(a,b):
 ap=a[:,[0,2]];bp=b[:,[0,2]];points=intersection(ap,bp)
 if not points:return None
 points=set(points)
 for p in list(ap)+list(bp):
  if intersection([p,p,p],ap) and intersection([p,p,p],bp):points.add(rational(p))
 gaps=[]
 for p in points:
  alo,ahi=height(a,p);blo,bhi=height(b,p);gaps.extend([alo-bhi,ahi-blo])
 lo,hi=min(gaps),max(gaps)
 return dict(minDelta=str(lo),maxDelta=str(hi),strictlySeparated=lo>0 or hi<0,minimumAbsoluteGap=str(min(abs(lo),abs(hi))) if lo>0 or hi<0 else '0')
def self_test():
 a=np.array([[0,0,0],[1,0,0],[0,0,1]],float)
 assert compare(a,a+np.array([0,2,0]))['strictlySeparated']
 assert not compare(a,a)['strictlySeparated']
 wall=np.array([[0,-1,0],[0,1,0],[0,1,1]],float)
 assert not compare(a,wall)['strictlySeparated']
 assert compare(a,wall+np.array([0,3,0]))['strictlySeparated']
 assert compare(a,a+np.array([3,0,0])) is None
 return 5

def main():
 assert not DOC.exists();tests=self_test();refs=[Path(__file__)]
 r=read(PREV/'result.json')
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 pins={x['path']:x['sha256'] for x in r['evidenceRefs']};refs.append(PREV/'result.json')
 def consume(p):
  raw=p.read_bytes();assert digest(raw)==pins[str(p.relative_to(ROOT))];refs.append(p);return raw
 consume(PREV/'source-records.json');rows=read(PREV/'source-records.json')
 podium=decode_original_world_triangles(consume(LOCAL/'assets/a8058e18e0fbdfa4a38b10b9b58a5dea5d62ddf0debf76df1e39198a07969b74.glb.gz'))
 claim=reservations.claim('citic-exact-separation-'+str(uuid.uuid4()),['building:'+x for x in ['landsd/232579:0']+[r['uid'] for r in rows]],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  DOC.mkdir();out=[]
  for row in rows:
   other=decode_original_world_triangles(consume(LOCAL/'assets'/(row['sourceSHA256']+'.glb.gz')));pairs=[];candidates=0
   lo=other[:,:,[0,2]].min(1);hi=other[:,:,[0,2]].max(1)
   for i,p in enumerate(podium):
    pl=p[:,[0,2]].min(0);ph=p[:,[0,2]].max(0);ids=np.flatnonzero(np.all(hi>=pl,axis=1)&np.all(lo<=ph,axis=1));candidates+=len(ids)
    for j in ids:
     q=compare(p,other[j])
     if q is not None:pairs.append(dict(podiumFace=i,neighbourFace=int(j),**q))
   unresolved=[x for x in pairs if not x['strictlySeparated']]
   summary=dict(uid=row['uid'],completePodiumFaces=len(podium),completeNeighbourFaces=len(other),boundingCandidatePairs=candidates,closedProjectionPairs=len(pairs),unresolvedPairs=len(unresolved),minimumGapMetres=float(min((F(x['minimumAbsoluteGap']) for x in pairs),default=F(0))))
   out.append(dict(**summary,pairs=pairs));print(summary,flush=True);assert reservations.heartbeat(lease)['ok']
  save(DOC/'proofs.json.gz',dict(rows=out,selfTests=tests,installationApproved=False,qualification='Exact facet separation only, not solid-interior, source identity or runtime acceptance.'))
  refs.extend(HERE/n for n in ['exact_packed_world_geometry_20261009.py','exact_original_closed_projection_intersection_20261010.py','exact_original_projection_coverage_20261009.py'])
  result=module('citic_exact_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'citic-exact-complete-closed-original-neighbour-facet-separation-v1',list(dict.fromkeys(refs)),dict(uids=['landsd/232579:0']+[r['uid'] for r in rows],rows=[{k:v for k,v in x.items() if k!='pairs'} for x in out],newlyInstalled=0,installationApproved=False))
  print(dict(jobId=result['jobId']),flush=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
