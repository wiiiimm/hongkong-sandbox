"""UNEXECUTED complete provider-original census; no current/physical approval."""
import importlib.util,json,subprocess,sys,uuid
from pathlib import Path
from collections import deque
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_shared_edge_component_census_v2_20261011 import census
from exact_original_body_boundary_group_census_v1_20261011 import census as boundary_census
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts,primitive_census
from exact_finite_contact_crossing_classification_20261011 import classify
from xl_source_stream_binding_20261009 import source_stream_binding
BASE=ROOT/'docs/astra-city/government-import'
DRAFT=BASE/'government-xl-victoria-mall-complete-source-census-draft-v1-20261012'
CONTRACT=DRAFT/'input-contract.json';CONTRACT_SHA='a6a356ea8c88e3dc637de54d4fe44aaf9a6d84b4c0074d5d676fe4880e075488'
OLD=BASE/'government-xl-victoria-three-original-checked-20261009';SEAMS=BASE/'government-xl-victoria-three-original-shared-edges-20261009'
RECEIPTS=[(OLD,'d924ceab4de75d96405ab0b59d9e65df902ed87b86963d418e94729201133024','ac025bdf2a78b6b924d6842cb2fea7b5cdc682c343a37abc2a6fb0d04bca8251'),(SEAMS,'666717cdea16578f3ea2c2da1b7bc550331c22e7bdc3c69057d8f116e7ad9cc6','cf925db795b26396a535541be2260e9b7039a912cfeb0d714e74d1416c3dfd62')]
P,T,T2,T1='landsd/227593:0','landsd/251609:0','landsd/251614:0','landsd/251615:0';ACTIVE=[P,T]
MANIFEST='2dde0cfc3c0869963c185c3398e48a1928c76802b2efa6c2d9713183a6ad5540'
BATCH='government-xl-victoria-mall-retained-tower3-complete-source-census-v1-20261012';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
def preflight():
 assert not DOC.exists();assert digest(CONTRACT.read_bytes())==CONTRACT_SHA;contract=read(CONTRACT)
 refs=[Path(__file__),CONTRACT,DRAFT/'METHOD.md'];receipts=[];alias=contract['historicalRuntimeResolution'];alias_used=0
 for folder,jid,sha in RECEIPTS:
  path=folder/'result.json';assert digest(path.read_bytes())==sha;r=read(path);assert r['jobId']==jid and r['newlyInstalled']==0 and r['publication']is False;receipts.append(r);refs.append(path)
  for pin in r['evidenceRefs']:
   path=ROOT/pin['path']
   if pin==dict(path=alias['originalPath'],sha256=alias['sha256']):path=ROOT/alias['archivePath'];alias_used+=1
   assert digest(path.read_bytes())==pin['sha256'];refs.append(path)
 assert alias_used==1,'Only exact named historical runtime reference may resolve to archived bytes'
 for pin in contract['ordinaryPins']:
  path=ROOT/pin['path'];assert digest(path.read_bytes())==pin['sha256'];refs.append(path)
 manifest=read(ROOT/'3d-viewer/city/data/manifest.json');assert digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes())==MANIFEST and manifest['officialModelCatalogues']==contract['completeCurrentCataloguePaths'];refs.append(ROOT/'3d-viewer/city/data/manifest.json')
 entries=[]
 for name in manifest['officialModelCatalogues']:
  catalogue=read(ROOT/'3d-viewer'/name);entries.extend(catalogue['models'])
 assert len(entries)==6649;retained=[r for r in entries if r['uid']==T];assert len(retained)==1 and retained[0]['sha256']==contract['expectedOriginalSources'][T]['sourceSHA256']
 assert retained[0]['supportDependencies']==[dict(csuid='3540818204P20050523',distance=0.22064590454101562,state='surveyed-footprint-fallback',uid=P)]
 assert all(not any(r['uid']==uid for r in entries)for uid in [P,T1,T2])
 source_data=read(OLD/'support-inputs.json');rows={uid:[r for r in source_data['sources']if r['uid']==uid]for uid in contract['expectedOriginalSources']};assert all(len(v)==1 for v in rows.values())and len(source_data['sources'])==4
 for uid,expected in contract['expectedOriginalSources'].items():
  r=rows[uid][0];assert r['modelId']==expected['modelId']and r['source']['building']['buildingCSUID']==expected['csuid']and r['sourceSHA256']==expected['sourceSHA256']and r['candidate']['entry']['sha256']==expected['sourceSHA256']and r['candidate']['entry']['triangles']==expected['faces']and r['candidate']['path']==expected['assetPath'];asset=ROOT/expected['assetPath'];assert digest(asset.read_bytes())==expected['sourceSHA256'];refs.append(asset)
 old=read(OLD/'support-checks.json.gz');seams=read(SEAMS/'checks.json');assert len(old['rows'])==len(seams['rows'])==3
 for uid,count in [(T,5),(T2,0),(T1,4)]:
  a=[r for r in old['rows']if r['uid']==uid];b=[r for r in seams['rows']if r['uid']==uid];assert len(a)==len(b)==1 and a[0]['supportUid']==b[0]['supportUid']==P and len(a[0]['interface']['unresolved'])==len(b[0]['interface']['unresolved'])==count and a[0]['interface']['unresolved']==b[0]['interface']['unresolved']
  assert not b[0]['newlyPasses']
 pins={str(p.relative_to(ROOT)):digest(p.read_bytes())for p in refs};return contract,receipts,rows,retained[0],old,seams,refs,pins

def complete(a,ids_a,b,ids_b):
 out=exact_finite_contacts(a,ids_a,b,ids_b,maximum_pairs=len(ids_a)*len(ids_b));assert out['allPairsExamined']and out['sourceFacesOmitted']==0;return out

def positive(result):return [r for r in result['contacts']if r['dimension']>0 and r['sourcePrimitiveDimensionA']==r['sourcePrimitiveDimensionB']==2]

def owned(state):
 contract,receipts,rows,retained,old,seams,refs,pins=state;lease=read(LEASE);resources=['building:'+u for u in sorted([P,T,T1,T2])];assert lease['resources']==resources and reservations.owns(lease)
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for r in receipts:assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 worlds={};actors={};groups={};mapping={}
 for uid,e in contract['expectedOriginalSources'].items():
  raw=(ROOT/e['assetPath']).read_bytes();world=decode_original_world_triangles(raw);assert world.shape==(e['faces'],3,3)and np.isfinite(world).all();worlds[uid]=world
  topology=census(world,list(range(len(world))));parts=topology['sharedEdgeConnectedComponents'];groups[uid]=parts;mapping[uid]={f:i for i,ids in enumerate(parts)for f in ids};assert sorted(list(mapping[uid])+topology['exactNonrenderingOriginalFaces'])==list(range(len(world)))
  actors[uid]=dict(sourceTupleVerbatim=e,completeWorldSHA256=digest(world.astype('<f8').tobytes()),completeOriginalProviderStreamBinding=source_stream_binding(raw),completePrimitiveCensus=primitive_census(world),completeOriginalTopology=topology,completeFaceToComponent={str(f):i for f,i in mapping[uid].items()},componentFullBounds=[dict(component=i,completeOriginalFaceIDs=ids,bounds=[world[ids].min((0,1)).tolist(),world[ids].max((0,1)).tolist()])for i,ids in enumerate(parts)],completeBoundaryCensus=[boundary_census(world,ids)for ids in parts]if uid in ACTIVE else None,contextOnly=uid not in ACTIVE,noCurrentPoseOrRuntimeAcceptance=True)
  save(LOCAL/('completed-source-'+uid.split('/')[1].replace(':','-')+'.json.gz'),actors[uid])
 pair_rows=[];graph={(uid,i):set()for uid in ACTIVE for i in range(len(groups[uid]))};excluded={};nonrender_contacts=[]
 for uid in ACTIVE:
  w=worlds[uid];parts=groups[uid];bounds=[(w[ids].min((0,1)),w[ids].max((0,1)))for ids in parts];nominated=0
  for i,ids_a in enumerate(parts):
   for j in range(i+1,len(parts)):
    if not(np.all(bounds[i][1]>=bounds[j][0])and np.all(bounds[j][1]>=bounds[i][0])):continue
    nominated+=1;contact=complete(w,ids_a,w,parts[j]);real=positive(contact);row=dict(uid=uid,componentA=i,componentB=j,completeFiniteContactInventory=contact,positiveRealFacetInterfaces=len(real));pair_rows.append(row)
    if real:graph[(uid,i)].add((uid,j));graph[(uid,j)].add((uid,i))
    save(LOCAL/('within-'+uid.split('/')[1].replace(':','-')+'-'+str(i)+'-'+str(j)+'.json.gz'),row)
   print(json.dumps(dict(uid=uid,component=i,total=len(parts))),flush=True)
  excluded[uid]=dict(completeComponentPairUniverse=len(parts)*(len(parts)-1)//2,inclusiveBoundsNominatedPairs=nominated,strictCompleteBoundsDisjointExcludedPairs=len(parts)*(len(parts)-1)//2-nominated,completeComponentBoundsRecorded=True)
  for z in actors[uid]['completeOriginalTopology']['exactNonrenderingOriginalFaces']:
   other=[f for f in range(len(w))if f!=z];nonrender_contacts.append(dict(uid=uid,originalNonrenderingFace=z,completeFiniteContacts=complete(w,[z],w,other),rootOrBridgeCredit=False))
 cross=complete(worlds[P],list(range(len(worlds[P]))),worlds[T],list(range(len(worlds[T]))));classified=[dict(contactVerbatim=r,**classify(worlds[P][r['sourceFaceA']],worlds[T][r['sourceFaceB']],r))for r in cross['contacts']]
 for r in positive(cross):
  a=(P,mapping[P][r['sourceFaceA']]);b=(T,mapping[T][r['sourceFaceB']]);graph[a].add(b);graph[b].add(a)
 families=[];remaining=set(graph)
 while remaining:
  first=min(remaining);seen={first};todo=deque([first])
  while todo:
   for node in sorted(graph[todo.popleft()]):
    if node not in seen:seen.add(node);todo.append(node)
  remaining-=seen;families.append(sorted(seen))
 contexts=[]
 for uid,count in [(T,5),(T1,4)]:
  raw_row=next(r for r in old['rows']if r['uid']==uid);assert len(raw_row['unresolved'])==count
  for witness in raw_row['unresolved']:
   supplied=witness['originalSourceFaces'];ids=sorted({r['faceIndex']for r in supplied});assert ids and all(0<=i<len(worlds[uid])for i in ids);incident=sorted({i for i,face in enumerate(worlds[uid])if any(np.array_equal(v,np.asarray(witness['position']))for v in face)})
   component_ids=sorted({mapping[uid][f]for f in ids if f in mapping[uid]});contexts.append(dict(uid=uid,rawFailedWitnessVerbatim=witness,oldAnnotatedSourceFaceIDs=ids,decodedOriginalFaceCoordinates=[dict(face=i,vertices=worlds[uid][i].tolist())for i in ids],annotatedFaceCoordinatesExactlyMatchSaved=all(np.array_equal(worlds[uid][r['faceIndex']],np.asarray(r['vertices']))for r in supplied),completeExactVertexIncidencesOfOldPoint=incident,affectedSourceComponentIDs=component_ids,completeAffectedComponentFaceIDs=[groups[uid][i]for i in component_ids],noOldWitnessRoleOrPointBridgeCredit=True))
 assert len(contexts)==9
 out=dict(uids=[P,T,T2,T1],originalSources=actors,installedTower3EntryVerbatim=retained,installedTower3AlreadyPresentNotNewImport=True,intentionalSurveyedFootprintFallbackUnchanged=True,completeMallAndRetainedTower3WithinComponentPairs=pair_rows,withinActorBroadphaseCensus=excluded,completeNonrenderingContactsUncredited=nonrender_contacts,completeMallToRetainedTower3Contacts=cross,completeContactClassifications=classified,completePositiveRealFacetGeometricFamilies=families,noFamilyGroundOrEngineeringRootClaim=True,allNineOldFailedLowerWitnessContexts=contexts,threeOldOriginalSupportRowsVerbatim=old['rows'],threeOldSharedRoofEdgeRowsVerbatim=seams['rows'],oldSampleAndSharedEdgeFailuresNotRerun=True,historicalRuntimeResolutionVerbatim=contract['historicalRuntimeResolution'],historicalProofNotTransferredToCurrentViewer=True,absentTower1And2OriginalsContextOnly=True,allOriginalFacesAndZeroPrimitivesPreserved=True,sourceOnly=True,sourceGeometryChanges=0,terrainGeometryChanges=0,identityAccepted=False,architecturalRoleAccepted=False,groundRootsAccepted=False,structuralSupportAccepted=False,physicalAccepted=False,currentAcceptance=False,installationApproved=False,newlyInstalled=0)
 save(DOC/'diagnostic.json.gz',out);refs.append(DOC/'diagnostic.json.gz');refs.extend(p for p in LOCAL.rglob('*')if p.is_file()and p.name!='reservation.json')
 assert reservations.owns(lease)and digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes())==MANIFEST
 for p,sha in pins.items():assert digest((ROOT/p).read_bytes())==sha
 spec=importlib.util.spec_from_file_location('victoria_source_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 result=m.freeze(BATCH,'complete-original-mall-retained-tower3-source-census-nine-old-failures-no-role',refs,dict(uids=[P,T,T2,T1],sourceOnly=True,completeOriginalMallFaces=21310,completeRetainedTower3Faces=4456,oldFailedWitnessesPreserved=9,installedTower3AlreadyPresentNotNewImport=True,currentAcceptance=False,physicalAccepted=False,installationApproved=False,newlyInstalled=0));assert reservations.owns(lease)and digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes())==MANIFEST
 for p,sha in pins.items():assert digest((ROOT/p).read_bytes())==sha
 print(json.dumps(dict(jobId=result['jobId'],newlyInstalled=0)),flush=True)
def main():
 state=preflight()
 if '--owned'in sys.argv:return owned(state)
 assert not LOCAL.exists();resources=['building:'+u for u in sorted([P,T,T1,T2])];claim=reservations.claim('victoria-complete-source-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'],claim;save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)))
 subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,str(Path(__file__)),'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
