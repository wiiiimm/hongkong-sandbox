"""Every original Yoho Tower8 component interface, exact and unedited."""
import collections,json,uuid
from pathlib import Path
import numpy as np
from shapely import STRtree,box
from run import ROOT,HERE,read,save,digest,reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_shell_intersections_20261009 import rational_face,intersection_points
from exact_original_component_contacts_20261009 import contact_measure
from source_closed_components import components
BATCH='government-xl-yoho-eight-complete-original-component-graph-20261009';DOC=ROOT/'docs/astra-city/government-import'/BATCH
INPUT=ROOT/'docs/astra-city/government-import/government-xl-yoho-eight-original-podium-contacts-20261009/diagnostic.json.gz'
SOURCE=HERE/'local/government-xl-spatial-surface-roles-20261009/assets/fd68a7cc21e0d2377e38ccb781bb2f3510bac0c757111cfcd341a941e7e3ea08.glb.gz'
def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':digest(p.read_bytes())}
def main():
 assert not DOC.exists();claim=reservations.claim('yoho-eight-complete-components-'+str(uuid.uuid4()),['building:landsd/146396:0'],batch=BATCH,ttl=3600);assert claim['ok'],claim
 try:
  d=read(INPUT);assert digest(SOURCE.read_bytes())==d['sourceSHA256s'][0];tri=decode_original_world_triangles(SOURCE.read_bytes());parts=components(tri)['components'];assert len(tri)==14792 and len(parts)==953
  part_by_face=np.zeros(len(tri),int)
  for k,p in enumerate(parts):part_by_face[p['faceIndices']]=k
  normal=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);valid=np.linalg.norm(normal,axis=1)>0;lo=tri.min(axis=1);hi=tri.max(axis=1);tree=STRtree(box(lo[:,0],lo[:,2],hi[:,0],hi[:,2]));rational={};records=[];adj={k:set() for k in range(len(parts))};pairs=0
  def face(i):
   if i not in rational:rational[i]=rational_face(tri[i])
   return rational[i]
  for i in range(len(tri)):
   if not valid[i]:continue
   for j in tree.query(box(lo[i,0],lo[i,2],hi[i,0],hi[i,2])):
    j=int(j)
    if j<=i or not valid[j] or part_by_face[i]==part_by_face[j] or np.any(hi[i]<lo[j]) or np.any(hi[j]<lo[i]):continue
    pairs+=1;points=intersection_points(face(i),face(j))
    if not points:continue
    measure=contact_measure(points);pa,pb=int(part_by_face[i]),int(part_by_face[j]);records.append({'originalFaces':[i,j],'originalComponents':[pa,pb],**measure})
    if measure['dimension']>0:adj[pa].add(pb);adj[pb].add(pa)
   if i%1000==0:save(DOC/'progress.json',{'completeOriginalFaces':len(tri),'facesProcessed':i,'exactIntercomponentCandidatePairs':pairs,'exactContacts':len(records),'geometryChanges':0})
  anchors=[k for k,p in enumerate(parts) if any(c.get('positiveContactCount') and c['originalTowerFaces']==p['faceIndices'] for c in d['completeTowerComponents'])];assert len(anchors)==1
  previous={k:None for k in anchors};todo=collections.deque(anchors)
  while todo:
   k=todo.popleft()
   for j in sorted(adj[k]):
    if j not in previous:previous[j]=k;todo.append(j)
  outcomes=[]
  for k,p in enumerate(parts):
   path=[k]
   while path[-1] in previous and previous[path[-1]] is not None:path.append(previous[path[-1]])
   outcomes.append({'component':k,'originalFaces':p['faceIndices'],'completeTopology':{a:b for a,b in p.items() if a!='faceIndices'},'exactPositiveContactPathToOriginalPodium':path[-1] in anchors,'componentPath':path,'originalBounds':[tri[p['faceIndices']].min(axis=(0,1)).tolist(),tri[p['faceIndices']].max(axis=(0,1)).tolist()]})
  result={'uid':'landsd/146396:0','sourceSHA256':d['sourceSHA256s'][0],'completeWorldSHA256':digest(tri.astype('<f8').tobytes()),'completeOriginalFaceCount':len(tri),'completeOriginalComponentCount':len(parts),'exactIntercomponentCandidatePairs':pairs,'completeExactOriginalInterfaces':records,'originalPodiumContactAnchors':anchors,'originalComponentOutcomes':outcomes,'collapsedOriginalFacesRetained':np.flatnonzero(~valid).tolist(),'evidenceRefs':[ref(p) for p in [Path(__file__),INPUT,SOURCE,HERE/'exact_packed_world_geometry_20261009.py',HERE/'source_closed_components.py',HERE/'exact_original_shell_intersections_20261009.py',HERE/'exact_original_component_contacts_20261009.py']],'sourceGeometryChanges':0,'identityAccepted':False,'physicalAccepted':False,'installationApproved':False,'publication':False,'qualification':'Complete original Tower8 cross-component interfaces recomputed from all original nondegenerate triangles with inclusive unpadded exact bounds and exact rational intersections. Point contacts remain zero bridge credit. Positive source-only paths to a currently absent original podium are not current support acceptance. Every current actor and full terrain/foundation/runtime gate remains independent.'}
  save(DOC/'diagnostic.json.gz',result);summary={'components':len(parts),'positivePathsToOriginalPodium':len(previous),'unattachedComponentCountsByFaceCount':dict(collections.Counter(len(r['originalFaces']) for r in outcomes if not r['exactPositiveContactPathToOriginalPodium'])),'exactCandidatePairs':pairs,'positiveContacts':sum(r['dimension']>0 for r in records),'pointContacts':sum(r['dimension']==0 for r in records),'physicalAccepted':False};save(DOC/'summary.json',summary);print(json.dumps(summary),flush=True)
 finally:assert reservations.release(claim['reservation'])['ok']
if __name__=='__main__':main()
