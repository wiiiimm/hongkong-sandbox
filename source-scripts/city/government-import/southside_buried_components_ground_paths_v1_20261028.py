"""First exact finite terrain contact and native shared-edge path per residual body."""
import argparse,sys,uuid
from pathlib import Path
from collections import defaultdict,deque
import numpy as np
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-southside-buried-components-ground-paths-v1-20261028';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json';UID='landsd/315025:0';ROLES='government-xl-southside-four-buried-face-roles-v1-20261028';CAP='government-xl-la-marina-three-original-assembly-v1-20261028-runtime';GROUND='government-xl-la-marina-southside-original-terrain-v1-20261028'
def owned():
 lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists();refs=[Path(__file__),HERE/'exact_original_finite_triangle_contacts_20261010.py',HERE/'exact_original_component_contacts_20261009.py',HERE/'exact_original_shell_intersections_20261009.py'];pins={}
 for batch in [ROLES,CAP,GROUND]:
  _,bound=authenticate(BASE/batch);pins.update(bound);refs.append(BASE/batch/'result.json')
 def take(path):
  assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))];refs.append(path);return read(path)
 roles=take(BASE/ROLES/'summary.json');g=next(r for r in take(HERE/'local'/CAP/'runtime-geometry.json.gz')['rows']if r['uid']==UID);tri=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];terrain=np.asarray(take(HERE/'local'/GROUND/'original-terrain.json.gz')['triangles']);assert g['sourceSHA256']==roles['sourceSHA256']and len(tri)==roles['completeSourceFaces'];vertices,inv=np.unique(tri.reshape(-1,3),axis=0,return_inverse=True);faces=inv.reshape(-1,3);edges=defaultdict(list);face_edges=[]
 for i,f in enumerate(faces):
  keys=[tuple(sorted((int(a),int(b))))for a,b in [(f[0],f[1]),(f[1],f[2]),(f[2],f[0])]];face_edges.append(keys)
  for key in keys:edges[key].append(i)
 cached={};rows=[];tested=0
 for role in roles['rows']:
  start=role['faceIndex'];assert tri[start].tolist()==role['vertices'];queue=deque([start]);parents={start:None};contact=None;visited=[]
  while queue:
   fi=queue.popleft();visited.append(fi)
   if fi not in cached:cached[fi]=exact_finite_contacts(tri,[fi],terrain,range(len(terrain)),maximum_pairs=200000)
   result=cached[fi];tested+=result['trianglePairsTested'];assert tested<=200000
   positive=next((r for r in result['contacts']if r['sourcePrimitiveDimensionA']==r['sourcePrimitiveDimensionB']==2 and r['dimension']>=1 and r['maximumSpanM']>0),None)
   if positive:contact=positive;break
   for key in face_edges[fi]:
    for peer in sorted(edges[key]):
     if peer not in parents:parents[peer]=fi;queue.append(peer)
  path=[]
  if contact:
   cursor=contact['sourceFaceA']
   while cursor is not None:path.append(cursor);cursor=parents[cursor]
   path.reverse();assert path[0]==start
   for a,b in zip(path,path[1:]):assert set(face_edges[a])&set(face_edges[b])
  rows.append(dict(buriedFaceIndex=start,contactFound=contact is not None,firstPositiveFiniteSurfaceContact=contact,exactNativeSharedEdgePath=path,examinedSourceFaces=len(visited),allComponentFacesExamined=contact is None,componentExpectedFaces=role['edgeComponentFaces']))
 result=dict(uids=[UID],sourceSHA256=roles['sourceSHA256'],rows=rows,exactPairsTested=tested,sourceGeometryChanges=0,physicalAccepted=False,identityAccepted=False,installationApproved=False,qualification='First positive-dimensional exact surface intersection with authenticated original terrain, reached only by exact native shared-edge adjacency. Stop after a sufficient witness; no alternative path enumeration. This is body-to-ground geometry evidence, not a semantic bottom-cap classification or whole-building/support/identity/publication acceptance.')
 save(DOC/'summary.json',result);assert reservations.owns(lease);module('southside_ground_paths_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'native-shared-edge-paths-to-first-exact-original-terrain-contacts',refs,result);print([(r['buriedFaceIndex'],r['contactFound'],len(r['exactNativeSharedEdgePath']))for r in rows],flush=True)
def main():
 p=argparse.ArgumentParser();p.add_argument('--owned',action='store_true');a=p.parse_args()
 if a.owned:return owned()
 assert not DOC.exists()and not LOCAL.exists();c=reservations.claim('southside-exact-original-ground-paths-'+str(uuid.uuid4()),['building:'+UID],batch=BATCH,ttl=3600);assert c['ok'];execute_reserved(c['reservation'],LEASE,[sys.executable,__file__,'--owned'])
if __name__=='__main__':main()
