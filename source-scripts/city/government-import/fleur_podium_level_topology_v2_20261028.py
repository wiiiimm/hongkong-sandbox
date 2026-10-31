"""Exact source-level topology context, with no burial waiver or installation credit."""
import argparse,sys,uuid
from collections import defaultdict,Counter
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BATCH='government-xl-fleur-podium-level-topology-v2-20261028'
BASE=ROOT/'docs/astra-city/government-import';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json';UID='landsd/23296:0'
def owned():
 lease=read(LEASE);assert reservations.owns(lease) and 'building:'+UID in lease['resources'] and not DOC.exists()
 prior=BASE/'government-xl-fleur-four-original-components-20261007';_,pins=authenticate(prior);selection=prior/'selection.json.gz';assert digest(selection.read_bytes())==pins[str(selection.relative_to(ROOT))]
 row=next(r for r in read(selection)['rows'] if r['uid']==UID);asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256'];tri=decode_original_world_triangles(asset.read_bytes());assert len(tri)==3657
 normal=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);areas=np.linalg.norm(normal,axis=1)/2
 horizontal=np.ptp(tri[:,:,1],axis=1)<1e-8;level=float(tri[horizontal,:,1].mean(axis=1)[np.argmin(abs(tri[horizontal,:,1].mean(axis=1)-32.007))]);ids=np.flatnonzero(horizontal & (abs(tri[:,:,1].mean(axis=1)-level)<1e-8) & (normal[:,1]>0))
 vertices,inv=np.unique(tri.reshape(-1,3),axis=0,return_inverse=True);faces=inv.reshape(-1,3);edges=defaultdict(list)
 for i,f in enumerate(faces):
  for a,b in [(f[0],f[1]),(f[1],f[2]),(f[2],f[0])]:edges[tuple(sorted((int(a),int(b))))].append(i)
 target=set(map(int,ids));boundary=[];counts=Counter()
 for edge,incident in edges.items():
  selected=[i for i in incident if i in target]
  if not selected:continue
  external=[i for i in incident if i not in target]
  if len(selected)==1:
   ys=tri[external,:,1] if external else np.empty((0,3));relation=dict(boundaryEdgeVertices=vertices[list(edge)].tolist(),selectedFace=selected[0],adjacentFaces=external,adjacentYRange=[float(ys.min()),float(ys.max())]if external else None)
   relation['hasAdjacentBelow']=bool(external and (ys<level-1e-8).any());relation['hasAdjacentAbove']=bool(external and (ys>level+1e-8).any());boundary.append(relation);counts['edges']+=1;counts['withBelow']+=relation['hasAdjacentBelow'];counts['withAbove']+=relation['hasAdjacentAbove'];counts['open']+=not external
 result=dict(uids=[UID],uid=UID,sourceSHA256=row['sourceSHA256'],sourceWorldSHA256=digest(tri.astype('<f8').tobytes()),completeOriginalFaces=len(tri),sourceYRange=[float(tri[:,:,1].min()),float(tri[:,:,1].max())],examinedUpwardLevelMHKPD=level,upwardLevelFaces=len(ids),upwardLevelAreaM2=float(areas[ids].sum()),isAtCompleteSourceMinimum=bool(abs(level-tri[:,:,1].min())<1e-8),boundaryEdgeCounts=dict(counts),sourceGeometryChanges=0,terrainEdits=False,physicalAccepted=False,identityAccepted=False,installationApproved=False,qualification='Exact vertex equality and complete original source faces only. This examines all upward horizontal faces at the observed buried-face level; it does not assert that every such face is buried. Adjacency is source-topology context, never proof of real-world role or a burial/placement exception.')
 save(DOC/'level-faces-and-boundaries.json.gz',dict(faceIndices=ids.tolist(),boundary=boundary));save(DOC/'summary.json',result);assert reservations.owns(lease)
 module('fleur_level_topology_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'immutable-original-podium-level-topology-context',[Path(__file__),asset,selection,prior/'result.json',HERE/'exact_packed_world_geometry_20261009.py'],result);print(result,flush=True)
def main():
 p=argparse.ArgumentParser();p.add_argument('--owned',action='store_true');a=p.parse_args()
 if a.owned:return owned()
 assert not DOC.exists() and not LOCAL.exists();c=reservations.claim('fleur-level-topology-'+str(uuid.uuid4()),['building:'+UID],batch=BATCH,ttl=1800);assert c['ok'];execute_reserved(c['reservation'],LEASE,[sys.executable,__file__,'--owned'])
if __name__=='__main__':main()
