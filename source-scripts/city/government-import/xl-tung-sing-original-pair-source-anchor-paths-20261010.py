"""Every original pair component: exact paths to strict original-TIN anchors."""
import collections,json
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest
from exact_original_shell_intersections_20261009 import rational_face,intersection_points
from exact_original_component_contacts_20261009 import contact_measure
BATCH='government-xl-tung-sing-original-pair-source-anchor-paths-20261010';DOC=ROOT/'docs/astra-city/government-import'/BATCH
GROUND=DOC.parent/'government-xl-tung-sing-original-pair-exact-source-terrain-20261010'
def main():
 assert not DOC.exists();inputs=read(GROUND/'complete-original-podium-footing-inputs.json.gz');foot=read(GROUND/'complete-original-podium-ground-interfaces.json.gz');tri=[];parts=[];anchors=[];owners=[]
 for row,result in zip(inputs['rows'],foot['rows']):
  offset=len(tri);base=len(parts)
  for part in row['parts']:
   pts=np.asarray(part['position'],float).reshape(-1,3)[np.asarray(part['index']).reshape(-1,3)];indices=list(range(len(tri),len(tri)+len(pts)));tri.extend(pts);parts.append({'faceIndices':indices,'originalFaceIds':part['originalFaceIds'],'originalComponent':part['component'],'uid':row['uid']});owners.extend([row['uid']]*len(pts))
   if next(r for r in result['parts'] if r['component']==part['component'])['strictOriginalGroundAnchor']:anchors.append(len(parts)-1)
 tri=np.asarray(tri,float);normal=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);valid=np.linalg.norm(normal,axis=1)>0;lo,hi=tri.min(axis=1),tri.max(axis=1);byface=np.zeros(len(tri),int)
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
 save(DOC/'diagnostic.json.gz',{'completeOriginalPairFaces':len(tri),'completeOriginalPairComponents':len(parts),'strictOriginalSourceTINAnchors':[{'component':i,'uid':parts[i]['uid'],'originalComponent':parts[i]['originalComponent']} for i in anchors],'completeOriginalComponents':parts,'completeExactOriginalInterfaces':records,'completePositivePaths':{str(k):v for k,v in reached.items()},'componentsWithoutPositiveOriginalGroundPath':[i for i in range(len(parts)) if i not in reached],'exactPairs':pairs,'physicalAccepted':False,'sourceGeometryChanges':0,'terrainGeometryChanges':0,'inputHashes':{str((GROUND/name).relative_to(ROOT)):digest((GROUND/name).read_bytes()) for name in ['complete-original-podium-footing-inputs.json.gz','complete-original-podium-ground-interfaces.json.gz','exact-original-coverage.json.gz']},'qualification':'Complete original-source/TIN attachment diagnosis only. Every part and raw source face retained. Graph reachability supplies no inferred load-bearing role, current ground support, collision, neighbour or physical/runtime/install credit.'});print({'completePairComponents':len(parts),'positivePaths':len(reached),'anchors':anchors,'unattached':len(parts)-len(reached),'mainTowerComponent1':next((reached.get(i) for i,p in enumerate(parts) if p['uid']=='landsd/53800:0' and p['originalComponent']==1),None),'podiumPaths':[{**p,'faceIndices':len(p['faceIndices']),'originalFaceIds':len(p['originalFaceIds']),'path':reached.get(i)} for i,p in enumerate(parts) if p['uid']=='landsd/126434:0']},flush=True)
if __name__=='__main__':main()
