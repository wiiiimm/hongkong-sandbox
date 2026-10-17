"""UNEXECUTED exact two-face source-interface question; no new ground proof/role.
Preserves all306 body obligations, full component0 and prior99 false finite facts.
"""
import gzip,importlib.util,json,struct,subprocess,sys,uuid
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts
from exact_finite_contact_crossing_classification_20261011 import classify,triangle,normal,dot,sub
BASE=ROOT/'docs/astra-city/government-import'
CAPTURE=BASE/'government-xl-ocean-walk-current-actual-ground-capture-v1-20261012'
GRADE=BASE/'government-xl-ocean-walk-complete-four-stream-current-grade-paths-v1-20261012'
CONTEXT=BASE/'government-xl-ocean-walk-failed99-original-ground-context-v2-20261012'
METHOD=BASE/'government-xl-ocean-walk-two-nonsteep-counterparts-draft-v1-20261012/METHOD.md'
BATCH='government-xl-ocean-walk-two-nonsteep-original-counterparts-v1-20261012';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
UID='landsd/81743:0';SOURCE='52e0d6b6341f664cc18ee8a894e1c4c5e5dbc1b05729bb43deb8c109e0fac8cb';MANIFEST='2dde0cfc3c0869963c185c3398e48a1928c76802b2efa6c2d9713183a6ad5540';TARGET=[6034,6035]
MODES=['providerOriginal','actualLiteral','explicitLeftAssociatedF32ModelMatrix','explicitBalancedF32ModelMatrix']
HELPERS=['run.py','exact_original_finite_triangle_contacts_20261010.py','exact_original_component_contacts_20261009.py','exact_original_shell_intersections_20261009.py','exact_finite_contact_crossing_classification_20261011.py','test_exact_finite_contact_crossing_classification_20261011.py','xl-popcorn-source-investigations-checkpoints-20261009.py']
def edges(face):
 vertices=[tuple(float(x)for x in v)for v in face]
 return {tuple(sorted((a,b)))for a,b in zip(vertices,vertices[1:]+vertices[:1])if a!=b}
def plane(face):
 t=triangle(face);n=normal(t);return dict(exactUnnormalisedWindingNormalXYZ=[str(x)for x in n],exactPlaneConstant=str(-dot(n,t[0])),normalSignNotArchitecturalFunction=True,windingNotSolidOrientationCertificate=True)
def preflight():
 assert not DOC.exists();folders=[CAPTURE,GRADE,CONTEXT];receipts=[read(p/'result.json')for p in folders]
 assert [r['jobId']for r in receipts]==['736c7affd6c59099c7b7ef45515094d1319959dcb065db613a776f5bce1b3e65','4f3a1119bc56218d3e629f49928f6a80f22134e64ad0006ed643a15049567455','a3bdd133888af4b0b7bf8c2f4d7e79c8021b742d65fabc98051fa0518396d93e']
 refs=[Path(__file__),METHOD]+[p/'result.json'for p in folders]+[HERE/p for p in HELPERS]+[HERE.parent/'shared-modelling'/p for p in ['db.py','jobs.py','reservations.py']]
 for receipt in receipts:
  for pin in receipt['evidenceRefs']:
   p=ROOT/pin['path'];assert digest(p.read_bytes())==pin['sha256'];refs.append(p)
 assert digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes())==MANIFEST
 data=read(CAPTURE/'complete-four-stream-ground-inputs.json.gz');assert data['uid']==UID and data['sourceSHA256']==SOURCE and set(data['completeWorldStreams'])==set(MODES)
 selection=read(CAPTURE/'selection.json.gz');assert len(selection['rows'])==1;source_row=selection['rows'][0];assert source_row['uid']==UID and source_row['sourceSHA256']==SOURCE
 asset=ROOT/source_row['candidate']['path'];assert digest(asset.read_bytes())==SOURCE;refs.append(asset)
 grade=read(GRADE/'diagnostic.json.gz');context=read(CONTEXT/'context.json.gz');assert len(grade['rows'])==4 and len(context['fourStreamCompleteFailureBreakdownVerbatim']['rows'])==4
 pins={str(p.relative_to(ROOT)):digest(p.read_bytes())for p in refs};return receipts,refs,pins,data,source_row,grade,context,read(CAPTURE/'capture-inputs.json.gz')['canonicalResources']
def owned(state):
 receipts,refs,pins,data,source_row,grade,context,resources=state;lease=read(LEASE);assert lease['resources']==resources and len(resources)==30 and reservations.owns(lease)
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for r in receipts:assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 raw=gzip.decompress((ROOT/source_row['candidate']['path']).read_bytes());magic,version,total=struct.unpack_from('<III',raw);size,kind=struct.unpack_from('<II',raw,12);assert magic==0x46546c67 and version==2 and total==len(raw)and kind==0x4e4f534a
 meta=json.loads(raw[20:20+size]);assert meta['scenes'][meta.get('scene',0)]['nodes']==[0]and meta['nodes'][0]['children']==[1]and meta['nodes'][1]['mesh']==0 and len(meta['nodes'])==2 and len(meta['meshes'])==1 and len(meta['meshes'][0]['primitives'])==1
 primitive=meta['meshes'][0]['primitives'][0];assert primitive.get('mode',4)==4 and meta['accessors'][primitive['indices']]['count']==15484*3
 metadata=dict(assetVerbatim=meta['asset'],allSceneNodesVerbatim=meta['nodes'],meshVerbatim=meta['meshes'][0],materialsVerbatim=meta.get('materials',[]),sceneVerbatim=meta['scenes'],rootExtrasVerbatim=meta.get('extras'),fullOriginalFaceIDsOfSolePrimitive=list(range(15484)),architecturalRoleAccepted=False,materialNameNotFunction=True)
 rows=[]
 for mode in MODES:
  prior=next(r for r in grade['rows']if r['arithmetic']==mode);world=np.asarray(data['completeWorldStreams'][mode]['completeWorldTriangles'],dtype='<f8');assert world.shape==(15484,3,3)and np.isfinite(world).all()and digest(world.tobytes())==prior['completeWorldSHA256']
  groups=prior['completeOriginalTopology']['sharedEdgeConnectedComponents'];assert len(groups)==306 and sorted(i for ids in groups for i in ids)==list(range(15484));assert not prior['allZeroFacesUncredited']and len(groups[0])==10425 and set(TARGET)<=set(groups[0]);component={f:c for c,ids in enumerate(groups)for f in ids}
  all_edges={}
  for i,face in enumerate(world):
   for edge in edges(face):all_edges.setdefault(edge,[]).append(i)
  shared=[]
  for i in TARGET:
   for edge in sorted(edges(world[i])):
    neighbours=sorted(set(all_edges[edge])-{i});shared.append(dict(originalSourceFace=i,completeExactNonzeroOriginalEdge=[list(v)for v in edge],allOtherOriginalFaceIDsWithIdenticalWholeEdge=neighbours,otherComponentIDs=[component[j]for j in neighbours],contactOrRootCredit=False))
  others=sorted(set(range(15484))-set(TARGET));contacts=exact_finite_contacts(world,TARGET,world,others,maximum_pairs=len(TARGET)*len(others));mutual=exact_finite_contacts(world,[6034],world,[6035],maximum_pairs=1)
  assert all(c['allPairsExamined']and c['sourceFacesOmitted']==0 for c in [contacts,mutual]);classified=[]
  for contact in contacts['contacts']+mutual['contacts']:
   a,b=contact['sourceFaceA'],contact['sourceFaceB'];classified.append(dict(contactVerbatim=contact,sourceComponentA=component[a],sourceComponentB=component[b],**classify(world[a],world[b],contact)))
  counterpart_ids=sorted({c['sourceFaceB']for c in contacts['contacts']}|{j for r in shared for j in r['allOtherOriginalFaceIDsWithIdenticalWholeEdge']});planes=[]
  for i in sorted(set(TARGET)|set(counterpart_ids)):
   face=triangle(world[i]);relations={str(j):[str(dot(normal(face),sub(v,face[0])))for v in triangle(world[j])]for j in TARGET}
   planes.append(dict(originalSourceFace=i,sourceComponent=component[i],completeOriginalTriangle=world[i].tolist(),exactWindingPlane=plane(world[i]),exactSignedPlaneValueAtTargetVertices=relations,priorFiniteRecordVerbatim=prior['all15484FiniteRecords'][i],noNewGroundProof=True,noExposedTopOrUndersideRoleAccepted=True))
  affected=[0,117,227,228,268,269];assert [len(groups[i])for i in affected]==[10425,8,2,2,2,2]
  record=dict(arithmetic=mode,completeWorldSHA256=prior['completeWorldSHA256'],all15484OriginalFacesPreserved=True,complete306OriginalBodyFaceIDsVerbatim=groups,completeComponent0FaceIDsVerbatim=groups[0],sourceOriginalTargetFaceIDs=TARGET,allWholeNonzeroSharedEdgeIncidences=shared,completeTargetAgainstOther15482SourcePrimitivesContacts=contacts,completeTargetMutualContact=mutual,allContactClassifications=classified,completeTargetAndCounterpartPlanesAndPriorFiniteFacts=planes,sixAffectedOriginalComponentsMetadataContext=[dict(component=i,completeOriginalFaceIDs=groups[i],solePrimitiveId=0,materialIndex=primitive.get('material'),architecturalRoleUnknown=True)for i in affected],prior99RawFailureIDsVerbatim=prior['allRawFailedFaces'],priorNonsteepExcludedWallPathIDsVerbatim=prior['failedNonsteepFacesUncredited'],priorWholeGradeAndPathFactsVerbatim=context['fourStreamCompleteFailureBreakdownVerbatim']['rows'][MODES.index(mode)],properCrossingsNotSolidOrEngineeringCredit=True,pointContactsNeverBridge=True,sourceRoleAccepted=False,currentAcceptance=False)
  rows.append(record);save(LOCAL/('completed-'+mode+'.json.gz'),record);print(json.dumps(dict(arithmetic=mode,sourceContactRecords=len(classified),sharedEdgeRecords=len(shared),architecturalRoleAccepted=False)),flush=True)
 save(DOC/'diagnostic.json.gz',dict(uids=[UID],sourceSHA256=SOURCE,originalSourceEntryVerbatim=source_row['candidate']['entry'],completeOriginalSceneMetadata=metadata,rows=rows,sixPriorBasicRegressionsRetainedVerbatim=grade['sixPriorBasicRegressionsRetainedVerbatim'],elevenPriorUnresolvedInterfacesRetainedVerbatim=grade['elevenPriorUnresolvedInterfacesRetainedVerbatim'],all17OriginalSupplierInterfaceRowsRetainedVerbatim=grade['all17PriorInterfaceRowsRetainedVerbatim'],sourceOnly=True,noNewGroundClearanceOrGradeOrRootComputed=True,normalNotArchitecturalFunction=True,underGradeNotFoundation=True,sourceGeometryChanges=0,terrainGeometryChanges=0,identityAccepted=False,physicalAccepted=False,currentAcceptance=False,installationApproved=False))
 assert reservations.owns(lease)and digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes())==MANIFEST
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h
 refs.append(DOC/'diagnostic.json.gz');refs.extend(p for p in LOCAL.rglob('*')if p.is_file()and p.name!='reservation.json')
 spec=importlib.util.spec_from_file_location('ocean_counterparts_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.freeze(BATCH,'two-original-nonsteep-source-counterparts-and-complete306-obligations-no-role',refs,dict(uids=[UID],sourceOnly=True,all306OriginalBodiesPreserved=True,all99RawFailuresRetained=True,currentAcceptance=False,newlyInstalled=0))
def main():
 state=preflight()
 if '--owned'in sys.argv:return owned(state)
 assert not LOCAL.exists();claim=reservations.claim('ocean-two-nonsteep-counterparts-'+str(uuid.uuid4()),state[-1],batch=BATCH,ttl=3600);assert claim['ok'],claim;save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)))
 subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,str(Path(__file__)),'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
