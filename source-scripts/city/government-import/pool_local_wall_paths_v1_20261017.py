"""Local connected original-wall witnesses inside existing half-metre embedding radius."""
from pathlib import Path
from collections import deque
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-sham-shui-po-pool-local-wall-paths-v1-20261017';DOC=BASE/BATCH

def clip_segment(a,b,lo,hi):
 d=b-a;t0,t1=0.,1.
 for i in range(3):
  if abs(d[i])<1e-14:
   if a[i]<lo[i]-1e-9 or a[i]>hi[i]+1e-9:return None
  else:
   x,y=sorted(((lo[i]-a[i])/d[i],(hi[i]-a[i])/d[i]));t0=max(t0,x);t1=min(t1,y)
 if t0>t1+1e-10:return None
 return np.array([a+t0*d,a+t1*d])

def main():
 assert np.allclose(clip_segment(np.array([-1.,0,0]),np.array([2.,0,0]),np.zeros(3),np.ones(3)),[[0,0,0],[1,0,0]])
 assert clip_segment(np.array([-1.,2,0]),np.array([2.,2,0]),np.zeros(3),np.ones(3)) is None
 assert not DOC.exists();prior=BASE/'government-xl-sham-shui-po-pool-connected-wall-contacts-v1-20261017';r=read(prior/'result.json');refs=[Path(__file__),prior/'result.json'];pins={q['path']:q['sha256'] for q in r['evidenceRefs']}
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 path=HERE/'local/government-xl-sham-shui-po-pool-original-group-v1-20261016/runtime-geometry.json.gz';g=next(g for g in read(path)['rows'] if g['uid']=='landsd/271043:0');tri=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];normals=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);lengths=np.linalg.norm(normals,axis=1);normals=np.divide(normals,lengths[:,None],out=np.zeros_like(normals),where=lengths[:,None]>0)
 edges={}
 for i,t in enumerate(tri):
  if lengths[i]==0 or abs(normals[i,1])>.1:continue
  for j in range(3):edges.setdefault(tuple(sorted((tuple(t[j]),tuple(t[(j+1)%3])))),[]).append(i)
 result=[]
 for row in read(prior/'contacts.json')['rows']:
  point=np.array(row['position']);rise=np.sqrt(.5**2-2*.05**2);lo=point+[-.05,0,-.05];hi=point+[.05,rise,.05];adj={i:[] for i in range(len(tri))}
  for edge,faces in edges.items():
   clipped=clip_segment(np.array(edge[0]),np.array(edge[1]),lo,hi)
   if clipped is None:continue
   for a in faces:
    for b in faces:
     if a!=b:adj[a].append((b,clipped))
  starts=row['originalIncidentFaces'];parents={i:None for i in starts};crossings={};q=deque(starts)
  while q:
   i=q.popleft()
   for j,edge in adj[i]:
    if j not in parents:parents[j]=i;crossings[j]=edge;q.append(j)
  candidates=[c for c in row['candidates'] if c['sourceFace'] in parents and c['supportContacts'] and np.all(np.array(c['contact'])>=lo-1e-9) and np.all(np.array(c['contact'])<=hi+1e-9)]
  candidates.sort(key=lambda c:np.linalg.norm(np.array(c['contact'])-point));witness=None
  if candidates:
   c=candidates[0];chain=[c['sourceFace']]
   while parents[chain[-1]] is not None:chain.append(parents[chain[-1]])
   chain.reverse();witness=dict(contact=c,faces=chain,triangles=[tri[i].tolist() for i in chain],clippedSharedEdges=[crossings[i].tolist() for i in chain[1:]],normalY=[float(normals[i,1]) for i in chain],localPrism=[lo.tolist(),hi.tolist()],maximumPrismRadiusM=.5,continuousOriginalSurface=True,qualification='Each triangle intersection with the convex prism is convex; consecutive original triangles share the saved clipped edge. Start and contact lie in their incident triangles. Therefore a continuous local source-surface path exists, with every point inside the half-metre radius. This is geometric evidence, not standalone installation approval.')
  result.append(dict(position=row['position'],witness=witness,localReachableFaces=len(parents)))
 DOC.mkdir();save(DOC/'paths.json',dict(rows=result,fullAcceptance=False,sourceGeometryChanged=False));refs.append(path)
 out=module('pool_local_paths_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'local-original-wall-contact-path-witnesses-v1',list(dict.fromkeys(refs)),dict(uids=['landsd/265480:0','landsd/271043:0'],witnesses=sum(r['witness'] is not None for r in result),total=len(result),fullAcceptance=False,newlyInstalled=0))
 print(dict(jobId=out['jobId'],witnesses=sum(r['witness'] is not None for r in result),total=len(result)),flush=True)
if __name__=='__main__':main()
