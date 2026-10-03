"""Inventory original connected source parts for the ten held forms; no acceptance."""
import importlib.util,shutil
from collections import Counter
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
spec=importlib.util.spec_from_file_location('continuation',HERE/'sol-continuation-20261003.py');c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
final=c.module('component_final','xl-final-script-pass.py')
def run():
 c.owns();packet=read(c.BASE/'sol-pilot-20261002/packet.json');available={}
 for name in ('government-xl-remaining-20260923','government-xl-remaining-held-20260923','government-xl-source-revision-20260924','government-xl-source-http-retry-20260924'):
  folder=HERE/'local'/name/'recovered'
  for e in read(folder/'catalogue.json')['models']:available[e['uid']]={'entry':e,'path':folder/e['asset']}
 rows=[]
 for frozen in packet['rows']:
  uid=frozen['uid'];source=available[uid];entry=source['entry'];assert entry['sha256']==frozen['sourceSHA256']==digest(source['path'].read_bytes())
  final.s.LOCAL=c.LOCAL/'components';asset=final.s.LOCAL/'assets'/(entry['sha256']+'.glb.gz');asset.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source['path'],asset)
  triangles=final.s.glb_triangles({'sourceSHA256':entry['sha256'],'modelId':entry['modelId'],'triangles':entry['triangles'],'native':{'model':{'worldBounds':entry['worldBounds']}}})
  components=[]
  for indices in final.connected_components(triangles,np.ones(len(triangles),dtype=bool)):
   faces=triangles[indices];cross=np.cross(faces[:,1]-faces[:,0],faces[:,2]-faces[:,0]);area=np.linalg.norm(cross,axis=1)/2
   edges=Counter()
   for face in np.round(faces,4):
    vertices=[tuple(p) for p in face]
    for a,b in zip(vertices,vertices[1:]+vertices[:1]):edges[tuple(sorted([a,b]))]+=1
   components.append({'sourceFaceIndices':indices.tolist(),'triangles':len(indices),'worldBounds':[faces.min(axis=(0,1)).tolist(),faces.max(axis=(0,1)).tolist()],'surfaceAreaM2':float(area.sum()),'upwardTriangles':int((cross[:,1]>.25*np.linalg.norm(cross,axis=1)).sum()),'boundaryEdges':sum(n==1 for n in edges.values()),'nonManifoldEdges':sum(n>2 for n in edges.values())})
  components.sort(key=lambda r:-r['triangles']);detail=c.DOC/'components'/(uid.split('/')[1].replace(':','-')+'.json.gz');save(detail,{'uid':uid,'sourceSHA256':entry['sha256'],'components':components,'aiCalls':0,'modelGeometryChanges':0,'publication':False})
  row={'uid':uid,'name':frozen['name'],'sourceSHA256':entry['sha256'],'componentCount':len(components),'largestComponentTriangles':components[0]['triangles'],'largestComponentBoundaryEdges':components[0]['boundaryEdges'],'sourceTriangles':len(triangles),'componentEvidence':c.ref(detail),'humanStatus':'held-unknown','installationApproved':False};rows.append(row);print({k:row[k] for k in ('uid','componentCount','sourceTriangles')},flush=True)
 save(c.DOC/'source-components.json',{'rows':rows,'qualification':'Vertex adjacency rounded to 0.1mm only for diagnostics, with original source face indices retained. Connectivity or a closed mesh alone does not establish semantic component membership, support, below-grade intent or installation approval.','aiCalls':0,'modelGeometryChanges':0,'publication':False})
if __name__=='__main__':run()
