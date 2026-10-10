"""Complete original commercial/estate pair association, no source or role waiver."""
from pathlib import Path
import json,numpy as np,shapely
from run import ROOT,HERE,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_component_contacts_20261009 import exact_component_contacts
from source_closed_components import components
DOC=ROOT/'docs/astra-city/government-import/government-xl-tung-sing-commercial-original-assembly-20261010'
REC=DOC.parent/'government-xl-source-neighbour-recovery-leads-20261010/selection.json.gz'
PAIR=DOC.parent/'government-xl-tung-sing-interior-current-identity-inputs-v2-20261010/selection.json.gz'
def main():
 assert not DOC.exists();commercial=next(r for r in read(REC)['rows'] if r['uid']=='landsd/254604:0');pairs=read(PAIR)['rows'];rows=[commercial,*pairs];tri=[];paths=[]
 for r in rows:
  p=ROOT/r['candidate']['path'];raw=p.read_bytes();assert digest(raw)==r['sourceSHA256'];a=decode_original_world_triangles(raw);assert len(a)==r['native']['model']['triangles'];tri.append(a);paths.append(p)
 top=components(tri[0]);interfaces=[]
 for row,a in zip(pairs,tri[1:]):
  contact=exact_component_contacts(tri[0],range(len(tri[0])),a,range(len(a)),maximum_pairs=1000000);parts={i:ci for ci,c in enumerate(top['components']) for i in c['faceIndices']}
  for c in contact['contacts']:c['commercialComponent']=parts[c['sourceFaceA']]
  interfaces.append({'relatedUID':row['uid'],'completeRelatedFaces':len(a),'completeRelatedWorldSHA256':digest(a.astype('<f8').tobytes()),'completeOriginalContacts':contact})
 inputs=[Path(__file__),REC,PAIR,*paths,HERE/'exact_packed_world_geometry_20261009.py',HERE/'exact_original_component_contacts_20261009.py',HERE/'source_closed_components.py'];save(DOC/'diagnostic.json.gz',{'uid':commercial['uid'],'completeCurrentBuilding':commercial['source']['building'],'sourceSHA256':commercial['sourceSHA256'],'completeWorldSHA256':digest(tri[0].astype('<f8').tobytes()),'completeOriginalFaces':len(tri[0]),'completeOriginalTopology':top,'completeOriginalTriangles':tri[0].tolist(),'wholeOriginalRelatedInterfaces':interfaces,'inputHashes':{str(p.relative_to(ROOT)):digest(p.read_bytes()) for p in inputs},'identityAccepted':False,'physicalAccepted':False,'sourceGeometryChanges':0,'qualification':'Actual unchanged original commercial source and full estate original interfaces; no shared permit/legal ownership/load-bearing/terrain/collision credit.'});print(json.dumps({'uid':commercial['uid'],'faces':len(tri[0]),'parts':len(top['components']),'interfaces':[{'uid':r['relatedUID'],'positiveContacts':sum(c['dimension']>0 for c in r['completeOriginalContacts']['contacts']),'pointContacts':sum(c['dimension']==0 for c in r['completeOriginalContacts']['contacts'])} for r in interfaces]}),flush=True)
if __name__=='__main__':main()
