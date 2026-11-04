"""Exact dyadic 2D separating-axis proof, including all zero-projection faces."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';NAME='government-xl-villa-canopy-exact-projection-separation-v2-20261015';DOC=BASE/NAME
CAPTURE=BASE/'government-xl-villa-five-placed-canopy-collision-v1-20261015';CANOPY=BASE/'government-xl-villa-private-canopy-collision-v2-20261015'
def separate(a,b):
 # Integer vertices are exact scaled IEEE doubles, never rounded coordinates.
 for poly in [a,b]:
  for i in range(3):
   dx=poly[(i+1)%3][0]-poly[i][0];dz=poly[(i+1)%3][1]-poly[i][1]
   for x,z in [(dx,dz),(-dz,dx)]:
    if x==z==0:continue
    pa=[v[0]*x+v[1]*z for v in a];pb=[v[0]*x+v[1]*z for v in b]
    if max(pa)<min(pb)or max(pb)<min(pa):return True
 return False
def integerize(tri,scale):
 return [[tuple(int(float(v).as_integer_ratio()[0])*(scale//float(v).as_integer_ratio()[1])for v in p)for p in t]for t in tri]
def main():
 assert not DOC.exists();refs={}
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY')
  for d in [CAPTURE,CANOPY]:
   r=read(d/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
   for q in r['evidenceRefs']:
    if d==CANOPY and not (ROOT/q['path']).is_relative_to(CANOPY):continue
    assert q['path']not in refs or refs[q['path']]==q['sha256'];refs[q['path']]=q['sha256']
 for p,h in refs.items():assert digest((ROOT/p).read_bytes())==h,p
 captured=read(CAPTURE/'placed.json.gz');canopy=np.concatenate([np.asarray(r['position']).reshape(-1,3)[np.asarray(r['index']).reshape(-1,3)]for r in read(CANOPY/'rendered.json')['rows']if r['mode']=='privateCandidate'])[:,:,[0,2]];assert len(canopy)==148
 DOC.mkdir();summaries=[]
 for r in captured['rows']:
  for mode in ['literal','leftAssociatedPerMultiplyAddFloat32WorldPosition','balancedPerMultiplyAddFloat32WorldPosition']:
   tri=np.concatenate([np.asarray(m[mode]).reshape(-1,3)[np.asarray(m['index']).reshape(-1,3)]for m in r['meshes']])[:,:,[0,2]];assert len(tri)==r['completeFaces']
   scale=max(float(v).as_integer_ratio()[1]for v in np.concatenate([tri.reshape(-1),canopy.reshape(-1)]));a=integerize(tri,scale);b=integerize(canopy,scale);lo=tri.min(1);hi=tri.max(1);tested=0;unresolved=[]
   for j,t in enumerate(canopy):
    ids=np.flatnonzero(((hi>=t.min(0))&(lo<=t.max(0))).all(1))
    for i in ids:
     tested+=1
     if not separate(a[int(i)],b[j]):unresolved.append([int(i),j])
   summary=dict(uid=r['uid'],mode=mode,sourceFaces=len(tri),canopyFaces=len(canopy),allPairs=len(tri)*len(canopy),aabbSeparatedPairs=len(tri)*len(canopy)-tested,exactIntegerAxisTestedPairs=tested,unresolvedPairs=unresolved,scale=scale,allProjectionSeparated=not unresolved)
   summaries.append(summary);print({k:v for k,v in summary.items()if k!='unresolvedPairs'},'unresolved',len(unresolved),flush=True)
 save(DOC/'summary.json',dict(rows=summaries,allProjectionSeparated=all(r['allProjectionSeparated']for r in summaries),qualification='Exact projected convex triangles are strictly disjoint. Both source/canopy coordinates are represented exactly as dyadic integers; no face omitted including lines and points. AABB broad phase uses extrema of unchanged finite coordinates. Strict separation in XZ rules out any 3D contact or containment for these placed streams. Only literal and two declared matrix orders, not all possible GPU arithmetic.',fullAcceptance=False))
 for p,h in refs.items():assert digest((ROOT/p).read_bytes())==h,p
 module('villa_separation_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(NAME,'complete-placed-original-exact-projection-separation',[Path(__file__),CAPTURE/'result.json',CANOPY/'result.json']+[ROOT/p for p in refs],dict(uids=[r['uid']for r in captured['rows']],allProjectionSeparated=all(r['allProjectionSeparated']for r in summaries),comparisons=len(summaries),fullAcceptance=False,sourceGeometryChanges=0))
if __name__=='__main__':main()
