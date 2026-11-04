"""Source-only paths for retained vertical and lower-closure clearance findings."""
from collections import defaultdict,deque
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import BASE,CAPTURE,SOURCE,GROUND,PODIUM,module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_upper_ground_interfaces_20261009 import exact_upper_ground_interfaces
BATCH='government-xl-primrose-podium-remaining-roles-v1-20261015';DOC=BASE/BATCH;FINITE=BASE/'government-xl-primrose-podium-current-finite-v2-20261015'
def paths_to(tri,eligible,roots):
 edges=defaultdict(list);adj=defaultdict(set)
 for i in eligible:
  for a,b in zip(tri[i],np.roll(tri[i],-1,axis=0)):
   if tuple(a)!=tuple(b):edges[tuple(sorted((tuple(a),tuple(b))))].append(i)
 for ids in edges.values():
  for i in ids:adj[i].update(set(ids)-{i})
 parent={i:None for i in roots};todo=deque(roots)
 while todo:
  i=todo.popleft()
  for j in sorted(adj[i]):
   if j not in parent:parent[j]=i;todo.append(j)
 return parent

def trace(i,parent):
 if i not in parent:return []
 path=[i]
 while parent[path[-1]]is not None:path.append(parent[path[-1]])
 return path

def main():
 assert not DOC.exists();r=read(FINITE/'result.json')
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for q in r['evidenceRefs']:assert digest((ROOT/q['path']).read_bytes())==q['sha256']
 source=next(r for r in read(SOURCE/'selection.json.gz')['rows']if r['uid']==PODIUM);raw=(ROOT/source['candidate']['path']).read_bytes();assert digest(raw)==source['sourceSHA256'];worlds={'original':decode_original_world_triangles(raw)}
 c=next(r for r in read(CAPTURE/'attributes.json.gz')['rows']if r['uid']==PODIUM);ix=np.asarray(c['completeOriginalIndex']).reshape(-1,3)
 for mode,key in [('literal','completeLiteralWorldPosition'),('left','completeExplicitLeftAssociatedFloat32WorldPosition'),('balanced','completeExplicitBalancedFloat32WorldPosition')]:worlds[mode]=np.asarray(c[key]).reshape(-1,3)[ix]
 ground=np.asarray(read(GROUND/'after-ground.json.gz')['completeRelevantDrawnTriplets']).reshape(-1,3,3);summary=[];DOC.mkdir()
 for mode,tri in worlds.items():
  finite=read(FINITE/(mode+'.json.gz'));assert finite['worldSHA256']==digest(tri.tobytes())and finite['groundSHA256']==digest(ground.tobytes());records=finite['faces'];assert len(records)==len(tri)
  for i,f in enumerate(records):assert f['sourceFace']==i and f['proof']['sourceFaceSHA256']==digest(tri[i].tobytes())and f['proof']['groundProjectionCovered']
  normals=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);area=np.linalg.norm(normals,axis=1);valid=area>0;ratio=np.divide(normals[:,1],area,out=np.zeros_like(area),where=valid)
  bad={i for i,f in enumerate(records)if not f['proof']['existingOrdinaryClearanceBoundProved']};walls={i for i in bad if valid[i]and abs(ratio[i])<=.25};undersides=bad-walls;assert all(ratio[i]<-.25 for i in undersides)
  eligible={i for i in range(len(tri))if valid[i]and(abs(ratio[i])<=.25 or records[i]['proof']['existingOrdinaryClearanceBoundProved'])};roofs={i for i in eligible if ratio[i]>.25}
  wallparents=paths_to(tri,sorted(eligible),sorted(roofs));lower={i for i in range(len(tri))if valid[i]and ratio[i]<-.25 and np.all(tri[i,:,1]==tri[999,0,1])};lowerparents=paths_to(tri,sorted(lower),[999]);grade=exact_upper_ground_interfaces(tri,sorted(walls),ground)
  result=dict(mode=mode,sourceSHA256=source['sourceSHA256'],worldSHA256=digest(tri.tobytes()),groundSHA256=digest(ground.tobytes()),rawUnprovedFaces=sorted(bad),wallPaths=[dict(sourceFace=i,pathToStrictClearUpwardFace=trace(i,wallparents))for i in sorted(walls)],undersidePaths=[dict(sourceFace=i,pathToPreviouslyReviewedUnderside999=trace(i,lowerparents))for i in sorted(undersides)],exactGradeInterfaces=grade,fullAcceptance=False,qualification='Complete raw finite findings retained. Paths are exact shared-edge source context, not engineering support or acceptance. Downward findings are excluded from wall/clear-roof paths.')
  save(DOC/(mode+'.json.gz'),result);item=dict(mode=mode,walls=len(walls),undersides=len(undersides),wallsWithClearRoofPath=sum(bool(trace(i,wallparents))for i in walls),undersidesConnectedTo999=sum(bool(trace(i,lowerparents))for i in undersides),gradeContactFaces=sorted({x['sourceFace']for x in grade}));summary.append(item);print(item,flush=True)
 for q in r['evidenceRefs']:assert digest((ROOT/q['path']).read_bytes())==q['sha256']
 paths=[ROOT/q['path']for q in r['evidenceRefs']]+[FINITE/'result.json',Path(__file__),HERE/'exact_original_upper_ground_interfaces_20261009.py',HERE/'primrose_compound_foundation_v2_20261015.py']
 module('roles_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'source-wall-grade-and-reviewed-underside-connectivity-v1',paths,dict(uids=[PODIUM],rows=summary,fullAcceptance=False))
if __name__=='__main__':main()
