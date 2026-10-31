"""Complete unchanged low-extension parts versus every other original primitive.

Finite geometry evidence only: no function, ownership, physical-root or identity
acceptance. All point/line/area records survive; zero-area faces supply no roots.
"""
import importlib.util,json
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_shared_edge_component_census_v2_20261011 import census
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts
BASE=ROOT/'docs/astra-city/government-import'
INPUT=BASE/'government-xl-king-cheung-95691-untouched-original-recovery-v1-20261011'
CONTEXT=BASE/'government-xl-king-cheung-95691-complete-original-extra-context-v1-20261011'
BATCH='government-xl-king-cheung-95691-complete-low-parts-contacts-v1-20261011';DOC=BASE/BATCH
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists()
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for p in [INPUT/'result.json',CONTEXT/'result.json']:
   receipt=read(p);assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 row=read(INPUT/'selection.json.gz')['rows'][0];prior=read(CONTEXT/'diagnostic.json.gz')
 assert row['uid']=='landsd/95691:0'and row['sourceSHA256']=='daad7e84a632e97cd7af9c354dd3d6c122e2e1afc0afdc751f752a0f909cd119'
 asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256']
 world=decode_original_world_triangles(asset.read_bytes());assert world.shape==(18742,3,3)and np.isfinite(world).all()and digest(world.tobytes())==prior['completeOriginalWorldSHA256']
 topology=census(world,list(range(len(world))));assert topology==prior['completeTopology']
 groups=topology['sharedEdgeConnectedComponents'];assert len(groups)==908 and [len(groups[i])for i in [39,43,44]]==[88,8,8]
 face_component={f:i for i,ids in enumerate(groups)for f in ids}
 records=[]
 for component in [39,43,44]:
  own=groups[component];others=sorted(set(range(len(world)))-set(own))
  contacts=exact_finite_contacts(world,own,world,others,maximum_pairs=1000000)
  for contact in contacts['contacts']:contact['otherRealComponent']=face_component.get(contact['sourceFaceB'])
  records.append(dict(component=component,completeOriginalFaceIds=own,completeOriginalTriangles=world[own].tolist(),completeComponentBounds=[world[own].min((0,1)).tolist(),world[own].max((0,1)).tolist()],allOtherOriginalFacesExamined=len(others),contacts=contacts))
 save(DOC/'diagnostic.json.gz',dict(uids=[row['uid']],source=ref(asset),sourceSHA256=row['sourceSHA256'],originalRootModelId=row['modelId'],completeWorldSHA256=digest(world.tobytes()),completeFaces=len(world),completeSourceTopology=topology,completeLowParts=records,currentFormHistoricalContext=prior['currentForm'],currentManifestHistoricalContext=prior['currentManifest'],allSourceFacesPreserved=True,sourceGeometryChanges=0,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,physicalSupportAccepted=False,appendageFunctionAccepted=False,sourceOwnershipAccepted=False,currentAcceptance=False,installationApproved=False))
 refs=[Path(__file__),INPUT/'result.json',INPUT/'selection.json.gz',CONTEXT/'result.json',CONTEXT/'diagnostic.json.gz',asset,HERE/'exact_packed_world_geometry_20261009.py',HERE/'exact_original_shared_edge_component_census_v2_20261011.py',HERE/'exact_original_finite_triangle_contacts_20261010.py',HERE/'exact_original_component_contacts_20261009.py',HERE/'exact_original_shell_intersections_20261009.py']
 s=importlib.util.spec_from_file_location('king_cheung_low_contacts_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
 m.freeze(BATCH,'complete-original-low-parts-all-primitives-attachment-source-evidence-no-role-credit',refs,dict(uids=[row['uid']],completeFaces=len(world),selectedParts=[39,43,44],contactCounts=[len(r['contacts']['contacts'])for r in records],sourceOnly=True,currentAcceptance=False,newlyInstalled=0))
 print(json.dumps([dict(component=r['component'],contacts=len(r['contacts']['contacts']),positiveRealFacetContacts=sum(c['dimension']>0 and c['sourcePrimitiveDimensionA']==c['sourcePrimitiveDimensionB']==2 for c in r['contacts']['contacts']),otherComponents=sorted({c['otherRealComponent']for c in r['contacts']['contacts']if c['otherRealComponent']is not None}))for r in records]),flush=True)
if __name__=='__main__':main()
