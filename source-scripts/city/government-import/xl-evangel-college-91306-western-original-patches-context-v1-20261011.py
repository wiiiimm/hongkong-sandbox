"""Complete source-defined school-wing patches and finite interfaces, no role credit.

The observed extent witnesses nominate original patches only. Whole patches,
all original body incidences, and every other source primitive are retained.
No geometry, approximate welding, architectural function or support is inferred.
"""
import json,sys,uuid,subprocess
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_shared_edge_component_census_v2_20261011 import census
from exact_original_full_edge_coplanar_patch_census_v1_20261011 import verify
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts
BASE=ROOT/'docs/astra-city/government-import'
SOURCE=BASE/'government-xl-evangel-college-91306-untouched-original-recovery-v1-20261011'
CONTEXT=BASE/'government-xl-evangel-college-91306-complete-source-extent-context-v1-20261011'
CURRENT=BASE/'government-xl-evangel-college-91306-current-complete-identity-diagnostic-v1-20261011'
BATCH='government-xl-evangel-college-91306-western-original-patches-context-v1-20261011'
DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json';UID='landsd/91306:0'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def owned():
 assert not DOC.exists();lease=read(LEASE);assert reservations.owns(lease)
 row=read(SOURCE/'selection.json.gz')['rows'][0];prior=read(CONTEXT/'diagnostic.json.gz');asset=ROOT/row['candidate']['path'];raw=asset.read_bytes()
 assert row['uid']==UID and digest(raw)==row['sourceSHA256']==prior['sourceSHA256']
 world=decode_original_world_triangles(raw);assert world.shape==(13960,3,3)and digest(world.tobytes())==prior['completeOriginalWorldSHA256']
 topology=census(world,list(range(len(world))));assert topology==prior['completeOriginalTopology'];parts=topology['sharedEdgeConnectedComponents']
 assert [len(parts[k])for k in [13,20,142]]==[5185,14,56]
 witnesses=prior['farVertexWitnessFaces'];assert len(witnesses)==98 and all(f in set(parts[13]+parts[20]+parts[142]+topology['exactNonrenderingOriginalFaces'])for f in witnesses)
 patches=verify(world,parts[13]);selected=[]
 for index,patch in enumerate(patches['allSourceDefinedFullEdgeCoplanarPatches']):
  ids=patch['completeOriginalPatchFaces'];hits=sorted(set(ids)&set(witnesses))
  if hits:
   triangles=world[ids];selected.append(dict(patch=index,**patch,witnessFaces=hits,completeOriginalTriangles=triangles.tolist(),completeBounds=[triangles.min((0,1)).tolist(),triangles.max((0,1)).tolist()]))
 face_component={f:i for i,ids in enumerate(parts)for f in ids};contacts=[]
 for component in [20,142]:
  ids=parts[component];others=sorted(set(range(len(world)))-set(ids))
  result=exact_finite_contacts(world,ids,world,others,maximum_pairs=float('inf'))
  for contact in result['contacts']:contact['otherRealComponent']=face_component.get(contact['sourceFaceB'])
  contacts.append(dict(component=component,completeFaces=ids,completeOriginalTriangles=world[ids].tolist(),allOtherOriginalFacesExamined=len(others),completeFiniteContacts=result))
 import shapely
 current=read(CURRENT/'selection.json.gz')['rows'][0]['source']['building'];target=shapely.Polygon(current['rings'][0],current['rings'][1:]);assert target.is_valid
 nominated=sorted(set(f for p in selected for f in p['completeOriginalPatchFaces'])|set(parts[20]+parts[142]));remaining=sorted(set(range(len(world)))-set(nominated))
 distances=np.asarray([target.distance(shapely.Point(float(v[0]),float(v[2])))for v in world.reshape(-1,3)]).reshape(len(world),3)
 out=dict(uids=[UID],completeWorldSHA256=digest(world.tobytes()),sourceSHA256=row['sourceSHA256'],completeOriginalFaces=len(world),completeSourceTopology=topology,completeMainBodyPatchPartition=patches,nominatedSourceDefinedPatches=selected,completeDetachedOriginalContexts=contacts,nominatedCompleteFaceIDs=nominated,remainingCompleteFaceIDs=remaining,rawCurrentIdentity=read(CURRENT/'identity.json'),descriptiveNominatedVertexExtentM=float(distances[nominated].max()),descriptiveRemainingVertexExtentM=float(distances[remaining].max()),descriptiveFullVertexExtentM=float(distances.max()),originalFacesOmitted=0,sourceGeometryChanges=0,terrainGeometryChanges=0,currentAcceptance=False,installationApproved=False,sourceOwnedSchoolWingInterpretationAccepted=False,architecturalFunctionAccepted=False,precisePlanRegistration=False,structuralRootOrBridgeCredit=False)
 save(DOC/'diagnostic.json.gz',out)
 save(DOC/'provenance.json',dict(uids=[UID],evidenceRefs=[ref(Path(__file__)),ref(SOURCE/'selection.json.gz'),ref(SOURCE/'result.json'),ref(CONTEXT/'diagnostic.json.gz'),ref(CONTEXT/'provenance.json'),ref(CURRENT/'selection.json.gz'),ref(CURRENT/'identity.json'),ref(CURRENT/'result.json'),ref(asset),ref(HERE/'exact_packed_world_geometry_20261009.py'),ref(HERE/'exact_original_shared_edge_component_census_v2_20261011.py'),ref(HERE/'exact_original_full_edge_coplanar_patch_census_v1_20261011.py'),ref(HERE/'exact_original_finite_triangle_contacts_20261010.py')],sourceOnly=True,qualification='Exact source patch and contact census, descriptive vertex extents. No finite maximum-extent replacement, architectural function, support, grounding, current acceptance or installation credit.'))
 assert reservations.owns(lease)and asset.read_bytes()==raw
 print(json.dumps(dict(nominatedCompleteFaces=len(nominated),remainingCompleteFaces=len(remaining),patches=[dict(patch=p['patch'],faces=len(p['completeOriginalPatchFaces']),witnessFaces=len(p['witnessFaces']),bounds=p['completeBounds'],upward=p['allPatchFacesExactUpward'])for p in selected],contacts=[dict(component=c['component'],contacts=len(c['completeFiniteContacts']['contacts']),positiveReal=sum(r['dimension']>0 and r['sourcePrimitiveDimensionA']==r['sourcePrimitiveDimensionB']==2 for r in c['completeFiniteContacts']['contacts']),otherComponents=sorted({r['otherRealComponent']for r in c['completeFiniteContacts']['contacts']if r['otherRealComponent']is not None}))for c in contacts],remainingVertexExtentM=out['descriptiveRemainingVertexExtentM'])),flush=True)
def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists()and not LOCAL.exists();claim=reservations.claim('evangel-patches-'+str(uuid.uuid4()),['building:'+UID],batch=BATCH,ttl=3600);assert claim['ok'];save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
