"""Complete source/rendered tower vs actual nearby BASIC/native finite contacts.
No contact, footprint or identity relationship exempts any physical collision.
"""
from pathlib import Path
import importlib.util,json
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts,primitive_census
from exact_original_shell_intersections_20261009 import rational_face,cross,sub,dot
BATCH='government-xl-lippo-tower-only-complete-current-foreign-finite-contacts-v1-20261011';DOC=ROOT/'docs/astra-city/government-import'/BATCH
INPUT=DOC.parent/'government-xl-lippo-tower-only-current-complete-inputs-v3-20261011'
INVENTORY=DOC.parent/'xl-terrain-recovery-20261011-complete-current-native-position-inventory-v6'
def arrays(row):
 idx=np.array(row['completeOriginalIndex'],dtype=np.int64).reshape(-1,3)
 return [('actualLiteral',np.array(row['completeLiteralWorldPosition'],dtype='<f8').reshape(-1,3)[idx]),('explicitLeftAssociatedF32ModelMatrix',np.array(row['completeExplicitLeftAssociatedFloat32WorldPosition'],dtype='<f8').reshape(-1,3)[idx]),('explicitBalancedF32ModelMatrix',np.array(row['completeExplicitBalancedFloat32WorldPosition'],dtype='<f8').reshape(-1,3)[idx])]
def main():
 assert not DOC.exists();inp=read(INPUT/'input.json.gz');manifestpath=ROOT/inp['currentManifest']['path'];before=manifestpath.read_bytes();assert digest(before)==inp['currentManifest']['sha256']
 for folder in [INPUT,INVENTORY]:
  receipt=read(folder/'result.json')
  with connect() as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 geometry=read(INPUT/'complete-current-geometry.json.gz')
 for path,sha in geometry['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha,path
 row=inp['rows'][0];asset=ROOT/row['candidate']['path'];assert row['uid']=='landsd/239465:0' and digest(asset.read_bytes())==row['sourceSHA256']
 original=decode_original_world_triangles(asset.read_bytes());owned=[('providerOriginal',original),*arrays(geometry['row'])];assert all(w.shape==(3597,3,3) and np.isfinite(w).all() for _,w in owned)
 foreigners=[]
 for r in geometry['completeCurrentBasicGeometry']:
  world=np.array(r['position'],dtype='<f8').reshape(-1,3)[np.array(r['index'],dtype=np.int64).reshape(-1,3)];assert np.isfinite(world).all()
  foreigners.append(dict(uid=r['uid'],kind='actualCurrentBasic',streams=[('actualLiteralIdentityModelMatrixAllF32OrdersExact',world)],completeCurrentForm=r['currentForm']))
 for r in geometry['completeNearbyNativeGeometry']:
  n=next(n for n in inp['nearbyCurrentNativeActors'] if n['uid']==r['uid']);nasset=ROOT/n['path'];assert digest(nasset.read_bytes())==r['sourceSHA256'];noriginal=decode_original_world_triangles(nasset.read_bytes())
  foreigners.append(dict(uid=r['uid'],kind='actualCurrentInstalledNative',sourceSHA256=r['sourceSHA256'],streams=[('providerOriginal',noriginal),*arrays(r)]))
 assert len(foreigners)==20 and len({r['uid'] for r in foreigners})==20 and {'landsd/231645:0','landsd/237843:0','landsd/233997:0','landsd/21915:0'}.issubset({r['uid'] for r in foreigners})
 all_results=[];cache={}
 for actor in foreigners:
  trials=[]
  for ownmode,ownworld in owned:
   for foreignmode,foreignworld in actor['streams']:
    key=(digest(ownworld.tobytes()),digest(foreignworld.tobytes()))
    if key in cache:result=cache[key]
    else:
     contact=exact_finite_contacts(ownworld,list(range(len(ownworld))),foreignworld,list(range(len(foreignworld))))
     classified=[]
     for c in contact['contacts']:
      a,b=rational_face(ownworld[c['sourceFaceA']]),rational_face(foreignworld[c['sourceFaceB']]);na=cross(sub(a[1],a[0]),sub(a[2],a[0]));nb=cross(sub(b[1],b[0]),sub(b[2],b[0]));coplanar=bool(any(na) and any(nb) and not any(cross(na,nb)) and dot(na,sub(b[0],a[0]))==0)
      classified.append(dict(**c,exactTwoNonzeroFacetPlanesCoplanar=coplanar,positiveFiniteContact=c['dimension']>0,physicalCollisionExemption=False))
     result=dict(completeOwnedFaces=len(ownworld),completeForeignFaces=len(foreignworld),completeOwnedPrimitiveCensus=primitive_census(ownworld),completeForeignPrimitiveCensus=primitive_census(foreignworld),trianglePairsTested=contact['trianglePairsTested'],allPairsExamined=contact['allPairsExamined'],completeContacts=classified,positiveFiniteContacts=sum(c['dimension']>0 for c in classified),noncoplanarPositiveContacts=sum(c['dimension']>0 and not c['exactTwoNonzeroFacetPlanesCoplanar'] for c in classified),sourceFacesOmitted=0,foreignFacesOmitted=0,collisionCleared=False)
     cache[key]=result
    trials.append(dict(ownedMode=ownmode,foreignMode=foreignmode,ownedWorldSHA256=key[0],foreignWorldSHA256=key[1],**result))
  actor_result=dict(uid=actor['uid'],kind=actor['kind'],completeCurrentForm=actor.get('completeCurrentForm'),sourceSHA256=actor.get('sourceSHA256'),trials=trials)
  all_results.append(actor_result);save(DOC/'progress.json.gz',dict(actors=all_results))
  print(json.dumps(dict(uid=actor['uid'],kind=actor['kind'],maxPositive=max(t['positiveFiniteContacts'] for t in trials),maxNoncoplanar=max(t['noncoplanarPositiveContacts'] for t in trials),completeForeignFaces=trials[0]['completeForeignFaces'])),flush=True)
 assert manifestpath.read_bytes()==before
 for path,sha in geometry['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha,path
 result=dict(uid=row['uid'],currentManifest=inp['currentManifest'],completeOriginalTowerFaces=3597,completeNearbyForeignActors=20,actors=all_results,completeAll6637NativeOriginalPOSITIONCensusRef=str((INVENTORY/'inventory.json.gz').relative_to(ROOT)),geographicNativeCaptureSelectionIsNotActualGPUFarActorSeparationProof=True,allCurrentFormsCaptured=True,sourceGeometryChanges=0,terrainGeometryChanges=0,physicalAccepted=False,installationApproved=False,qualification='All original/literal/left-associated/balanced owned streams versus every captured full current BASIC and nearby installed native stream. Positive or point contacts remain raw diagnostics, never structural support or physical/collision exemptions. Whole original-POSITION census is retained, but far-actor actual-render separation and complete strict interior/collision classification remain independently required before acceptance.')
 save(DOC/'diagnostic.json.gz',result)
 refs=[Path(__file__),INPUT/'input.json.gz',INPUT/'complete-current-geometry.json.gz',INPUT/'result.json',INVENTORY/'result.json',INVENTORY/'inventory.json.gz',asset,*[ROOT/path for path in geometry['inputHashes']]]
 refs += [HERE/n for n in ['exact_packed_world_geometry_20261009.py','exact_original_finite_triangle_contacts_20261010.py','exact_original_shell_intersections_20261009.py','exact_original_component_contacts_20261009.py','test_exact_original_finite_triangle_contacts_20261010.py']]
 spec=importlib.util.spec_from_file_location('lippo_current_foreign_contact_fence',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 receipt=m.freeze(BATCH,'tower-only-complete-current-actual-basic-nearby-native-finite-contact-diagnostic-v1',refs,dict(uids=[row['uid']],completeOwnedFaces=3597,completeCapturedForeignActors=20,sourceFacesOmitted=0,physicalAccepted=False,installationApproved=False))
 print(json.dumps(dict(jobId=receipt['jobId'],foreignActors=20)),flush=True)
if __name__=='__main__':main()
