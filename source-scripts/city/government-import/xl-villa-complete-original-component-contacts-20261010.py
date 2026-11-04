"""All58 source parts and all exact mutual contacts, no support credit."""
import importlib.util
import json
from pathlib import Path
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_mesh_components import face_components
from exact_original_component_contacts_20261009 import exact_component_contacts

BATCH='government-xl-villa-complete-original-component-contacts-20261010'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
PHYSICAL=DOC.parent/'government-xl-villa-complete-original-current-physical-v1-20261010'
INPUT=DOC.parent/'government-xl-villa-current-bound-courtyard-edge-inputs-v1-20261010'
UID='landsd/89917:0'

def main():
 assert not DOC.exists();DOC.mkdir(parents=True)
 row=read(INPUT/'selection.json.gz')['rows'][0];assert row['uid']==UID
 path=ROOT/row['candidate']['path'];raw=path.read_bytes();assert digest(raw)==row['sourceSHA256']
 triangles=decode_original_world_triangles(raw);parts=face_components(triangles)
 assert len(triangles)==16669 and len(parts)==58
 counts=[]
 for i,ids in enumerate(parts):
  t=triangles[ids];normal=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);projection=shapely.union_all(shapely.polygons(t[:,:,[0,2]]))
  counts.append(dict(part=i,completeFaces=len(ids),allFaceIds=ids.tolist(),bounds=[t.min((0,1)).tolist(),t.max((0,1)).tolist()],projectionAreaM2=projection.area,projection=shapely.to_geojson(projection),upwardFaces=int((normal[:,1]>0).sum()),downwardFaces=int((normal[:,1]<0).sum()),exactVerticalFaces=int((normal[:,1]==0).sum())))
 interfaces=[];tested=0;examined=0
 for i,a in enumerate(parts):
  aa=triangles[a];lo,hi=aa.min((0,1)),aa.max((0,1))
  for j,b in enumerate(parts[i+1:],i+1):
   bb=triangles[b]
   examined+=1
   if np.any(bb.max((0,1))<lo)or np.any(bb.min((0,1))>hi):continue
   c=exact_component_contacts(triangles,a,triangles,b)
   assert c['allPairsExamined'];tested+=c['trianglePairsTested']
   if c['contacts']:interfaces.append(dict(partA=i,partB=j,completeContacts=c))
 reachable={0}
 while True:
  old=set(reachable)
  for x in interfaces:
   if not any(c['dimension']>0 for c in x['completeContacts']['contacts']):continue
   if x['partA']in reachable:reachable.add(x['partB'])
   if x['partB']in reachable:reachable.add(x['partA'])
  if old==reachable:break
 out=dict(uids=[UID],sourceSHA256=row['sourceSHA256'],decodedWorldSHA256=digest(triangles.tobytes()),completeOriginalFaces=len(triangles),completeOriginalParts=len(parts),parts=counts,all1653ComponentPairsExamined=examined==1653,exactTrianglePairsTested=tested,allMutualInterfaces=interfaces,positiveContactReachableFromMainbody=sorted(reachable),partsWithoutPositiveMainbodyPath=sorted(set(range(58))-reachable),structuralSupportAccepted=False,identityAccepted=False,physicalAccepted=False,installationApproved=False,sourceGeometryChanges=0,qualification='Complete unchanged original graph only. Exact positive-dimensional source interfaces establish authored attachment, not a terrain-supported root or load bearing. All detached parts remain visible and unclassified; full actual current ground/foreign/footing/finite-surface gates remain mandatory.')
 save(DOC/'diagnostic.json.gz',out)
 spec=importlib.util.spec_from_file_location('villa_all_component_fence',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 refs=[Path(__file__),INPUT/'selection.json.gz',INPUT/'result.json',PHYSICAL/'result.json',path,HERE/'exact_packed_world_geometry_20261009.py',HERE/'exact_mesh_components.py',HERE/'exact_original_component_contacts_20261009.py']
 result=m.freeze(BATCH,'all58-original-component-mutual-contact-diagnostic-v1',refs,out)
 print(json.dumps(dict(jobId=result['jobId'],parts=58,interfaces=len(interfaces),positiveReachable=len(reachable),unattached=out['partsWithoutPositiveMainbodyPath'])),flush=True)

if __name__=='__main__':main()
