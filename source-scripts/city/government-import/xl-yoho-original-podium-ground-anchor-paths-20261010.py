"""Complete untouched podium exact component paths from strict original anchors."""
import collections
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_shell_intersections_20261009 import rational_face,intersection_points
from exact_original_component_contacts_20261009 import contact_measure
from yoho_eight_current_bound_identity_20261009 import DOC as INPUT
from yoho_eight_related_original_podium_identity_20261009 import UID,RELATED,ring_poly
BATCH='government-xl-yoho-original-podium-strict-anchor-paths-20261010';DOC=ROOT/'docs/astra-city/government-import'/BATCH
GROUND=DOC.parent/'government-xl-yoho-original-podium-current-ground-20261010'
def main():
 assert not DOC.exists();diagnostic=read(GROUND/'diagnostic.json.gz');foot=read(GROUND/'complete-original-podium-ground-interfaces.json.gz');source=ROOT/read(INPUT/'current-inputs.json.gz')['podiumOriginalPath'];tri=decode_original_world_triangles(source.read_bytes());parts=diagnostic['completeComponents'];anchors=[p['component'] for p in foot['rows'][0]['parts'] if p['strictOriginalGroundAnchor']];normal=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);valid=np.linalg.norm(normal,axis=1)>0;lo,hi=tri.min(axis=1),tri.max(axis=1);byface=np.zeros(len(tri),int)
 for i,p in enumerate(parts):byface[p['faceIndices']]=i
 tree=shapely.STRtree(shapely.box(lo[:,0],lo[:,2],hi[:,0],hi[:,2]));cached={};records=[];adj={i:set() for i in range(len(parts))};pairs=0
 def face(i):
  if i not in cached:cached[i]=rational_face(tri[i])
  return cached[i]
 for i in range(len(tri)):
  if not valid[i]:continue
  for j in tree.query(shapely.box(lo[i,0],lo[i,2],hi[i,0],hi[i,2])):
   j=int(j)
   if j<=i or not valid[j] or byface[i]==byface[j] or np.any(hi[i]<lo[j]) or np.any(hi[j]<lo[i]):continue
   pairs+=1;points=intersection_points(face(i),face(j))
   if not points:continue
   measure=contact_measure(points);a,b=int(byface[i]),int(byface[j]);records.append({'originalFaces':[i,j],'originalComponents':[a,b],**measure})
   if measure['dimension']>0:adj[a].add(b);adj[b].add(a)
  if i%1000==0:save(DOC/'progress.json',{'facesChecked':i,'completeOriginalFaces':len(tri),'exactPairs':pairs,'exactContacts':len(records)})
 reached={i:[i] for i in anchors};todo=collections.deque(anchors)
 while todo:
  i=todo.popleft()
  for j in sorted(adj[i]):
   if j not in reached:reached[j]=[j]+reached[i];todo.append(j)
 own=shapely.union_all([ring_poly(b['rings']) for b in diagnostic['allCurrentForms'] if b['uid'] in [UID,RELATED]]);projection=shapely.union_all(shapely.polygons(tri[:,:,[0,2]]));foreign=[]
 for b in diagnostic['allCurrentForms']:
  if b['uid'] in [UID,RELATED]:continue
  overlap=projection.difference(own).intersection(ring_poly(b['rings']))
  if overlap.area<=0:continue
  ids=[i for i,t in enumerate(tri) if shapely.Polygon(t[:,[0,2]]).intersection(overlap).area>0];foreign.append({'currentForm':b,'sourceExcessOverlapM2':overlap.area,'allOriginalFaceIds':ids,'allOriginalFaces':tri[ids].tolist(),'overlapGeoJSON':__import__('json').loads(shapely.to_geojson(overlap))})
 ids={f for q in records if q['dimension']>0 for f in q['originalFaces']};towercontacts=read(DOC.parent/'government-xl-yoho-eight-original-podium-contacts-20261009/diagnostic.json.gz');summary={'completeOriginalComponents':len(parts),'strictOriginalCurrentGroundAnchors':anchors,'positiveOriginalAnchorPaths':len(reached),'componentsWithoutPositiveAnchorPath':[i for i in range(len(parts)) if i not in reached],'exactPairs':pairs,'positiveInterfaces':sum(q['dimension']>0 for q in records),'pointInterfaces':sum(q['dimension']==0 for q in records),'foreignExcessActors':[{'uid':q['currentForm']['uid'],'areaM2':q['sourceExcessOverlapM2'],'sourceFaces':len(q['allOriginalFaceIds'])} for q in foreign],'physicalAccepted':False};save(DOC/'diagnostic.json.gz',{'summary':summary,'completeExactOriginalInterfaces':records,'completePositivePaths':{str(k):v for k,v in reached.items()},'completeOriginalComponents':parts,'exactOriginalForeignOverlaps':foreign,'inputHashes':{str(source.relative_to(ROOT)):digest(source.read_bytes()),str((GROUND/'diagnostic.json.gz').relative_to(ROOT)):digest((GROUND/'diagnostic.json.gz').read_bytes()),str((GROUND/'complete-original-podium-ground-interfaces.json.gz').relative_to(ROOT)):digest((GROUND/'complete-original-podium-ground-interfaces.json.gz').read_bytes())},'sourceGeometryChanges':0,'physicalAccepted':False,'qualification':'All original positive-dimensional interfaces and strict original component ground anchors retained. Contact/graph reachability alone does not assign load-bearing roles or accept the source pair; two buried upward faces, exact foreign overlap/extent,143 detached tower parts and complete current physical/runtime gates remain independent.'});save(DOC/'summary.json',summary);print(summary,flush=True)
if __name__=='__main__':main()
