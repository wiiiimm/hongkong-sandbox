"""Bounded continuous original-wall paths to finite podium intersections; no approval."""
from pathlib import Path
from collections import defaultdict,deque
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from wave_incident_side_intersections_v1_20261017 import segment as transverse_segment
from shapely.geometry import Polygon,Point,LineString
from shapely.ops import nearest_points
from pool_local_wall_paths_v1_20261017 import clip_segment
from pool_incident_wall_contacts_v1_20261017 import closest
BASE=ROOT/'docs/astra-city/government-import';PREV=BASE/'government-xl-wave-all-original-support-distance-v1-20261017';BATCH='government-xl-wave-local-coplanar-paths-v3-20261017';DOC=BASE/BATCH

def segment(a,b,near):
 direct=transverse_segment(a,b)
 if direct is not None:return direct
 n=np.cross(a[1]-a[0],a[2]-a[0]);ln=np.linalg.norm(n)
 if ln==0:return None
 n=n/ln
 if np.max(np.abs((b-a[0])@n))>1e-8:return None
 axis=int(np.argmax(np.abs(n)));keep=[i for i in range(3)if i!=axis];pa=Polygon(a[:,keep]);pb=Polygon(b[:,keep])
 if not pa.is_valid or not pb.is_valid:return None
 shape=pa.intersection(pb)
 if shape.is_empty:return None
 q=np.array(nearest_points(Point(near[keep]),shape)[1].coords[0]);candidates=[]
 for d in [np.array([1.,0.]),np.array([0.,1.]),np.array([1.,1.])]:
  cut=shape.intersection(LineString([q-d,q+d]));parts=list(cut.geoms)if hasattr(cut,'geoms')else[cut]
  for part in parts:
   if part.geom_type!='LineString' or part.length<=1e-6:continue
   ends=np.array([part.coords[0],part.coords[-1]]);out=np.zeros((2,3));out[:,keep]=ends;out[:,axis]=a[0,axis]-((ends-a[0,keep])@n[keep])/n[axis];delta=out[1]-out[0];pt=out[0]+np.clip((near-out[0])@delta/(delta@delta),0,1)*delta;candidates.append((float(np.linalg.norm(pt-near)),out))
 return min(candidates,key=lambda c:c[0])[1]if candidates else None

def clip_ball(a,b,p,radius=.5):
 d=b-a;u=a-p;aa=d@d
 if aa==0:return None
 bb=2*(u@d);cc=u@u-radius*radius;disc=bb*bb-4*aa*cc
 if disc<=0:return None
 low=max(0.,(-bb-np.sqrt(disc))/(2*aa));high=min(1.,(-bb+np.sqrt(disc))/(2*aa))
 return np.array([a+low*d,a+high*d]) if high>low else None

def witness(tri,support,f,wall_only=True):
 p=np.array(f['position']);radius=.5;half=radius;lo=p-half;hi=p+half
 normal=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);length=np.linalg.norm(normal,axis=1);eligible=(length>0)&((np.abs(normal[:,1])<=.1*length) if wall_only else np.ones(len(tri),dtype=bool))&((tri.max(1)>=lo)&(tri.min(1)<=hi)).all(1)
 edges=defaultdict(list)
 for i in np.flatnonzero(eligible):
  for k in range(3):edges[tuple(sorted((tuple(tri[i,k]),tuple(tri[i,(k+1)%3]))))].append(int(i))
 adj=defaultdict(list)
 for edge,ids in edges.items():
  if len(ids)<2:continue
  cut=clip_ball(np.array(edge[0]),np.array(edge[1]),p,radius)
  if cut is None or np.linalg.norm(cut[1]-cut[0])<=1e-9:continue
  for i in ids:
   for j in ids:
    if i!=j:adj[i].append((j,cut))
 starts=[x['faceIndex']for x in f['originalSourceFaces']if eligible[x['faceIndex']]and np.linalg.norm(closest(p,tri[x['faceIndex']])-p)<=.001];parents={i:None for i in starts};crossings={};queue=deque(starts)
 while queue:
  i=queue.popleft()
  for j,edge in adj[i]:
   if j not in parents:parents[j]=i;crossings[j]=edge;queue.append(j)
 candidates=np.flatnonzero(((support.max(1)>=lo)&(support.min(1)<=hi)).all(1));hits=[]
 for i in parents:
  for j in candidates:
   cut=segment(tri[i],support[j],p)
   if cut is None:continue
   cut=clip_ball(cut[0],cut[1],p,radius)
   if cut is None or np.linalg.norm(cut[1]-cut[0])<=1e-6:continue
   d=cut[1]-cut[0];q=cut[0]+np.clip((p-cut[0])@d/(d@d),0,1)*d
   if np.linalg.norm(closest(q,tri[i])-q)>.001 or np.linalg.norm(closest(q,support[j])-q)>.001:continue
   hits.append((float(np.linalg.norm(q-p)),i,int(j),q,cut))
 hits.sort(key=lambda h:h[0]);proof=None
 if hits:
  distance,i,j,q,cut=hits[0];chain=[i]
  while parents[chain[-1]]is not None:chain.append(parents[chain[-1]])
  chain.reverse();proof=dict(sourceFaces=chain,supportFace=j,contact=q.tolist(),finiteContactSegment=cut.tolist(),distanceM=distance,sharedEdges=[crossings[k].tolist()for k in chain[1:]],localBall=dict(centre=p.tolist(),radiusM=radius),maximumRadiusM=radius,normalY=[float(normal[k,1]/length[k])for k in chain],startDistanceM=float(np.linalg.norm(closest(p,tri[chain[0]])-p)))
 return dict(position=f['position'],reason=f['reason'],reachableWallFaces=len(parents),witness=proof)
def main():
 assert not DOC.exists();r=read(PREV/'result.json');refs=[Path(__file__),PREV/'result.json']+[HERE/n for n in ['exact_packed_world_geometry_20261009.py','wave_incident_side_intersections_v1_20261017.py','pool_local_wall_paths_v1_20261017.py','pool_incident_wall_contacts_v1_20261017.py']];pins={}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for e in r['evidenceRefs']:
  assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 sources=read(PREV/'support-inputs.json')['sources'];meshes={s['uid']:decode_original_world_triangles((ROOT/s['candidate']['path']).read_bytes())for s in sources};output=[]
 for row in read(PREV/'support-checks.json.gz')['rows']:
  records=[dict(wall=witness(meshes[row['uid']],meshes['landsd/301560:0'],f,True),surface=witness(meshes[row['uid']],meshes['landsd/301560:0'],f,False))for f in row['unresolved']];summary=dict(uid=row['uid'],failedSamples=len(records),localWallWitnesses=sum(x['wall']['witness']is not None for x in records),localSurfaceWitnesses=sum(x['surface']['witness']is not None for x in records));output.append(dict(**summary,rows=records));print(summary,flush=True)
 save(DOC/'paths.json.gz',dict(rows=output,fullAcceptance=False,qualification='Nonzero exact shared edges connect original incident triangles within the existing 0.5m ball. Wall-only and all-surface context remain separate. Finite original podium intersection required, with 1mm independent endpoint contact checks. Source-specific geometric evidence only; no canonical failures waived.'))
 out=module('wave_local_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'bounded-original-coplanar-and-transverse-surface-paths-v3',list(set(refs)),dict(uids=[r['uid']for r in output]+['landsd/301560:0'],fullAcceptance=False,newlyInstalled=0));print(out['jobId'],flush=True)
if __name__=='__main__':main()
