"""Current byte rebind + saved294 point/source-layer attribution; no full source reload."""
from pathlib import Path
import json,sys,time,uuid,subprocess,importlib.util
import numpy as np
from run import ROOT,HERE,read,save,connect,reservations
from exact_distinct_evidence_refs_v1_20261014 import distinct_refs
from upton_parent_tin_regression_bookkeeping_v1_20261012 import sha
import polyu_four_parent_current_capture_binding_v3_draft_20261014 as delta
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-citywalk-saved294-source-layer-attribution-v1-20261014'
DOC=BASE/BATCH;P=BASE/(BATCH+'-proposal');LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
CAP=BASE/'government-xl-citywalk134332-surviving-native-interface-context-v1-20261013';GLOBAL=BASE/'government-xl-complete-current-native-actual-position-matrix-bounds-v4-20261012'
OLD=BASE/'government-xl-remaining-20260923/sol-hold-resolution-20261004/citywalk-contact-rescue'
COMP=BASE/'government-xl-remaining-20260923/sol-continuation-20261003/components/134332-0.json.gz'
PROFILE=BASE/'government-xl-citywalk134332-current-ground-only-proposal-v2-20261013/ground-capture-plan.json'
PRIOR_SCOPE=HERE/'local/government-xl-citywalk134332-current-complete-finite-ground-v1-20261013/protected-state-before.json'
RUNTIME=HERE/'citywalk_saved294_source_layers_runtime_v1_draft_20261014.mjs';FREEZER=HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py'
TOWERS=['landsd/215992:0','landsd/216991:0','landsd/218019:0','landsd/218095:0','landsd/218258:0'];UID='landsd/134332:0'
def ref(p):
 import hashlib
 return dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def check(q):p=ROOT/q['path'];assert ref(p)==q;return p
def load():
 pins=read(P/'draft-pins.json');assert pins['caller']==ref(Path(__file__))and pins['runtime']==ref(RUNTIME)
 for q in distinct_refs(pins['codeRefs']+pins['inputRefs']):check(q)
 manifest_ref=ref(ROOT/'3d-viewer/city/data/manifest.json');assert manifest_ref['sha256']==delta.CURRENT
 manifest=read(ROOT/manifest_ref['path']);historical=read(ROOT/pins['actualC00Archive']['path']);assert pins['actualC00Archive']['sha256']==delta.OLD
 scene=delta.scene_delta(historical,manifest);current=[e for url in manifest['officialModelCatalogues']for e in read(ROOT/'3d-viewer'/url)['models']]
 assert len(current)==len({e['uid']for e in current})==6653;lookup={e['uid']:e for e in current};assert UID not in lookup
 native=read(GLOBAL/'input.json.gz');inventory=read(GLOBAL/'inventory.json.gz');baseline={r['uid']:r for r in native['rows']};bounds={r['uid']:r for r in inventory['rows']}
 forms={};uids=read(PRIOR_SCOPE)['currentState']['uids'];assert len(uids)==len(set(uids))==19 and set(TOWERS)|{UID}<=set(uids)
 for t in manifest['tiles']:
  for f in read(ROOT/'3d-viewer'/t['url'])['buildings']:
   if f['uid']in uids:assert f['uid']not in forms or forms[f['uid']]==f;forms[f['uid']]=f
 assert set(forms)==set(uids);tower_tuples=[]
 old_entries=[e for url in historical['officialModelCatalogues']for e in read(ROOT/'3d-viewer'/url)['models']]
 suppression=lambda entries:{u:sorted(e['uid']for e in entries if u in e.get('suppressesBuildingUids',[]))for u in uids}
 current_suppression=suppression(current);assert current_suppression==suppression(old_entries),'Relevant suppression changed'
 for uid in TOWERS:
  row=baseline[uid];assert lookup[uid]==row['rawCurrentEntry']and forms[uid]==row['currentBuilding']and ref(ROOT/row['source']['path'])==row['source']
  proof=bounds[uid];assert proof['sourceSHA256']==row['source']['sha256']and proof['sourceFacesOmitted']==0 and proof['wholeUnusedPositionVerticesIncluded']
  assert all(m['wholePositionVerticesIncludingUnused']for m in proof['actualRenderMeshes'])
  tower_tuples.append(dict(uid=uid,rawCurrentEntry=lookup[uid],currentForm=forms[uid],actualUnusedPOSITIONMatrixBoundsProof=proof,actualTowerModelGeometryNotRecaptured=True,noCurrentSupportAcceptance=True))
 attrs=read(CAP/'actual-attributes.json.gz');captured=read(CAP/'current-interface-input.json.gz');assert attrs['startEndAllInputsVerified']and attrs['sourceGeometryChanges']==0
 declared={(q['path'],q['sha256'])for q in pins['inputRefs']+pins['codeRefs']}
 for q in pins['relevantCapturedSourceAndCodeRefs']:assert(q['path'],q['sha256'])in declared
 for path,h in attrs['completeRecursiveProductionModuleClosure']['inputHashes'].items():assert(path,h)in declared
 for path,h in inventory['completeRecursiveProductionModuleClosure']['inputHashes'].items():assert(path,h)in declared
 assert all(lookup[r['uid']]==r['rawInstalledEntry']for r in attrs['nativeContextRows'])
 own=attrs['rows'][0];assert own['uid']==UID and own['sourceSHA256']=='b2d26e9f7a3b033877cd8c2aa6e6c363fec2cdcc2c09af8b06a1e3f583ad17df'and own['loadedGroupScale']==[1,1,1]
 assert all(forms[f['uid']]==f for f in captured['completeCurrentForms'])
 old=read(OLD/'tower-support.json');assert [r['uid']for r in old['rows']]==TOWERS;saved=[]
 for row in old['rows']:
  assert row['sourceSHA256']==lookup[row['uid']]['sha256']and row['supportUid']==UID and row['supportSHA256']==own['sourceSHA256']and not row['passed']
  for ordinal,failure in enumerate(row['interfaceProof']['unresolved']):
   assert failure['reason']=='support-above-rim'and np.isfinite(failure['position']).all()and np.isfinite(failure['gap'])
   saved.append(dict(uid=row['uid'],ordinal=ordinal,failure=failure,originalTowerSourceSHA256=row['sourceSHA256']))
 assert len(saved)==294 and sum(f['failure']['gap']<-.5 for f in saved)==288
 labels=[None]*41277;components=read(COMP)['components'];assert len(components)==193
 for body,c in enumerate(components):
  for i in c['sourceFaceIndices']:assert type(i)is int and 0<=i<41277 and labels[i]is None;labels[i]=body
 assert all(i is not None for i in labels)
 profile=read(PROFILE)
 with np.load(ROOT/profile['providerOriginalNPZ']['path'],allow_pickle=False)as z:provider=np.array(z[profile['providerOriginalNPZKey']],dtype='<f8',copy=True)
 assert provider.shape==(41277,3,3)and sha(provider)==profile['providerOriginalWorldSHA256']=='e4f766dcd25463e7bbef605068852b893059df268eff9cc3b5f73d2b1b3cdb21'
 index=np.asarray(own['completeOriginalIndex'],dtype=np.int64).reshape(-1,3);assert index.shape==(41277,3)
 worlds=[dict(label='providerOriginal',array=provider)]
 for label,field in [('actualLiteral','completeLiteralWorldPosition'),('explicitLeftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('explicitBalancedF32','completeExplicitBalancedFloat32WorldPosition')]:
  positions=np.asarray(own[field],dtype='<f8').reshape(-1,3);assert np.isfinite(positions).all()and np.all(index>=0)and np.all(index<len(positions));worlds.append(dict(label=label,array=positions[index]))
 for w in worlds:assert w['array'].shape==(41277,3,3)and np.isfinite(w['array']).all()
 source_key=read(PRIOR_SCOPE)['currentState']['sourceKey'];resources=sorted(['building:'+u for u in uids]+['native-model:'+source_key,'source-context:'+BATCH+'-compute']);assert reservations.normalise(resources)==resources
 return pins,saved,labels,worlds,dict(currentManifest=manifest_ref,currentModels=6653,sourceReviewPointer=ref(ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json'),sceneDelta=scene,completeRelevantSuppressionInventory=current_suppression,oldManifestNotAliasedOrRestored=True,towerTuples=tower_tuples,relevantCodeSourceFormAndPoseBytesUnchanged=True,currentIdentityPhysicalSupportNotAccepted=True),resources,uids
def reviews(uids):
 with connect()as db:db.execute('SET TRANSACTION READ ONLY');return json.loads(json.dumps(db.execute('SELECT row_to_json(t) FROM astra_modelling.model_reviews t WHERE uid=ANY(%s) ORDER BY uid,snapshot_id',(uids,)).fetchall(),default=str))
def schema_only():
 p,s,l,w,rebind,res,u=load();return dict(passed=True,savedPoints=len(s),sourceFacets=41277,sourceBodies=193,worlds=[dict(label=x['label'],sha256=sha(x['array']))for x in w],currentManifest=rebind['currentManifest'],resources=res,noPointPredicateSourceDecodeDBLease=True)
def owned():
 lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists();last=time.monotonic()
 def pulse():
  nonlocal last
  if time.monotonic()-last>20:assert reservations.heartbeat(lease)['ok']and reservations.owns(lease);last=time.monotonic()
 pins,points,labels,worlds,rebind,resources,uids=load();assert lease['resources']==resources;before=reviews(uids)
 prep=read(P/'actual-readonly-preparation.json');assert prep['passed']and prep['caller']==ref(Path(__file__))and prep['runtime']==ref(RUNTIME)
 refs=distinct_refs(pins['codeRefs']+pins['inputRefs']+prep['evidenceRefs']+[ref(P/'draft-pins.json'),ref(P/'actual-readonly-preparation.json')])
 for folder,job in [(CAP,'ca2a6024037ef04c57b0f6ffbf9220f2abd27f824b554595c2d4db7be516a67e'),(GLOBAL,pins['nativeBoundsJob'])]:
  result=read(folder/'result.json');assert result['jobId']==job
  with connect()as db:db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(job,)).fetchone()==('complete',result)
 def fence():
  for q in refs:check(q);pulse()
  assert reservations.owns(lease)and ref(ROOT/'3d-viewer/city/data/manifest.json')==rebind['currentManifest']and reviews(uids)==before
 fence();DOC.mkdir();save(DOC/'current-relevant-source-tuple-rebind.json',rebind);save(DOC/'raw294-historical-failures-verbatim.json.gz',points)
 closure=read(ROOT/prep['literalClosureRef']['path']);runtime_refs=distinct_refs([dict(path=p,sha256=h)for p,h in closure['inputHashes'].items()]+[ref(CAP/'actual-attributes.json.gz'),ref(OLD/'tower-support.json'),ref(COMP)])
 save(DOC/'input.json.gz',dict(savedPoints=points,bodyLabels=labels,originalSourceFaces=41277,sourceWorlds=[dict(label=w['label'],worldSHA256=sha(w['array']),position=w['array'].reshape(-1).tolist())for w in worlds],currentRelevantTupleRebind=rebind,runtimeInputRefs=runtime_refs,fullSourceAndUnusedAttributeCapture=ref(CAP/'actual-attributes.json.gz'),providerOriginalBodiesAreOrdinalProvenanceOnly=True))
 with(DOC/'actual-saved-point-runtime.log').open('xb')as log:proc=subprocess.run(['node',str(RUNTIME),str(DOC.relative_to(ROOT))],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
 save(DOC/'actual-runtime-command.json',dict(exitCode=proc.returncode,completeAttributionProduced=proc.returncode==0))
 refs=distinct_refs(refs+[ref(p)for p in DOC.rglob('*')if p.is_file()]);fence()
 spec=importlib.util.spec_from_file_location('citywalk_saved_point_freezer',FREEZER);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 result=module.freeze(BATCH,'saved294-source-layer-attribution-current-byte-tuple-rebind-no-acceptance',[check(q)for q in refs],dict(uids=uids,sourceOnly=True,currentAcceptance=False,physicalAccepted=False,installationApproved=False,newlyInstalled=0,savedPoints=294,completeSourceFaces=41277,runtimeExitCode=proc.returncode,completeAttributionProduced=proc.returncode==0));fence();print(json.dumps(dict(jobId=result['jobId'],result=ref(DOC/'result.json'))),flush=True)
def main():
 if '--schema-only'in sys.argv:print(json.dumps(schema_only()));return
 if '--owned'in sys.argv:return owned()
 assert '--attribute-saved294-source-layers-only'in sys.argv and not DOC.exists()and not LOCAL.exists();*_,resources,uids=load()
 claim=reservations.claim('citywalk-saved-layers-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  save(LEASE,json.loads(json.dumps(lease,default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
