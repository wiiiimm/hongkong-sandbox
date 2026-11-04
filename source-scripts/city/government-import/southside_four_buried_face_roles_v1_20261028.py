"""Trace four residual source faces through exact shared-edge components; no waiver."""
import argparse,sys,uuid
from pathlib import Path
from collections import defaultdict
import numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-southside-four-buried-face-roles-v1-20261028';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json';UID='landsd/315025:0';CAP='government-xl-la-marina-three-original-assembly-v1-20261028-runtime';GROUND='government-xl-la-marina-southside-original-terrain-v1-20261028'
def owned():
 lease=read(LEASE);assert reservations.owns(lease)and 'building:'+UID in lease['resources']and not DOC.exists();refs=[Path(__file__)];pins={}
 for name in [CAP,GROUND]:
  _,bound=authenticate(BASE/name);pins.update(bound);refs.append(BASE/name/'result.json')
 def take(path):
  assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))];refs.append(path);return read(path)
 selected=next(r for r in take(BASE/CAP/'selection.json.gz')['rows']if r['uid']==UID);g=next(r for r in take(HERE/'local'/CAP/'runtime-geometry.json.gz')['rows']if r['uid']==UID);tri=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];ground=np.asarray(take(HERE/'local'/GROUND/'original-terrain.json.gz')['triangles']);assert len(tri)==11699 and g['sourceSHA256']==selected['sourceSHA256'];asset=ROOT/selected['candidate']['path'];assert digest(asset.read_bytes())==selected['sourceSHA256'];refs.append(asset)
 final=module('southside_source_face_context',HERE/'xl-final-script-pass.py');original_samples=final.s.context.shared.samples;captured=[]
 def observe(*args,**kwargs):
  result=original_samples(*args,**kwargs);captured.append(result.copy());return result
 final.s.context.shared.samples=observe
 b=selected['source']['building'];foundation=final.foundation_context(tri,ground,Polygon(b['rings'][0],b['rings'][1:]));assert foundation==take(BASE/GROUND/'summary.json')['rows'][0]['originalTerrainFoundation'];assert len(captured)==1
 points=np.concatenate([tri,tri.mean(axis=1)[:,None,:]],axis=1);gaps=points[:,:,1]-np.asarray(captured[0]).reshape(-1,4);buried=np.flatnonzero(np.isfinite(gaps).all(axis=1)&(gaps<-.5).all(axis=1));assert len(buried)==4 and foundation['fullyBuriedUpwardTriangles']==0
 vertices,inv=np.unique(tri.reshape(-1,3),axis=0,return_inverse=True);faces=inv.reshape(-1,3);edges=defaultdict(list);parent=list(range(len(tri)))
 def find(i):
  while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
  return i
 for i,f in enumerate(faces):
  for a,c in [(f[0],f[1]),(f[1],f[2]),(f[2],f[0])]:edges[tuple(sorted((int(a),int(c))))].append(i)
 for incident in edges.values():
  for i in incident[1:]:parent[find(i)]=find(incident[0])
 components=defaultdict(list)
 for i in range(len(tri)):components[find(i)].append(i)
 rows=[]
 for raw in buried:
  i=int(raw);ids=components[find(i)];body=tri[ids];cross=np.cross(tri[i,1]-tri[i,0],tri[i,2]-tri[i,0]);normal=cross/np.linalg.norm(cross);adjacent=set()
  for a,c in [(faces[i,0],faces[i,1]),(faces[i,1],faces[i,2]),(faces[i,2],faces[i,0])]:adjacent.update(edges[tuple(sorted((int(a),int(c))))])
  adjacent.discard(i);rows.append(dict(faceIndex=i,vertices=tri[i].tolist(),unitNormal=normal.tolist(),sampleGapsM=gaps[i].tolist(),exactEdgeNeighbours=sorted(adjacent),edgeComponentFaces=len(ids),edgeComponentYRange=[float(body[:,:,1].min()),float(body[:,:,1].max())],faceAtComponentMinimum=bool((tri[i,:,1]==body[:,:,1].min()).all()),componentHasSamplesWithinOrdinaryHalfMetre=bool((np.isfinite(gaps[ids])&(abs(gaps[ids])<=.5)).any()),componentHasAboveTerrainSamples=bool((gaps[ids]>.5).any())))
 result=dict(uids=[UID],sourceSHA256=selected['sourceSHA256'],completeSourceFaces=len(tri),foundationUnchanged=True,rows=rows,sourceGeometryChanges=0,identityAccepted=False,physicalAccepted=False,installationApproved=False,qualification='Genuine unchanged foundation sampler observed, not replaced. Complete actual-renderer source triangles and authenticated original terrain. Exact shared-edge connectivity, normals and sample ranges only; no bottom-cap role assumption, tolerance change, support/identity approval or installation credit.')
 save(DOC/'summary.json',result);assert reservations.owns(lease);refs.extend([HERE/'xl-final-script-pass.py']);module('southside_four_face_roles_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'four-original-buried-face-exact-edge-component-context',refs,result);print([{k:v for k,v in r.items()if k not in ['vertices','exactEdgeNeighbours']}for r in rows],flush=True)
def main():
 p=argparse.ArgumentParser();p.add_argument('--owned',action='store_true');a=p.parse_args()
 if a.owned:return owned()
 assert not DOC.exists()and not LOCAL.exists();c=reservations.claim('southside-four-exact-face-roles-'+str(uuid.uuid4()),['building:'+UID],batch=BATCH,ttl=3600);assert c['ok'];execute_reserved(c['reservation'],LEASE,[sys.executable,__file__,'--owned'])
if __name__=='__main__':main()
