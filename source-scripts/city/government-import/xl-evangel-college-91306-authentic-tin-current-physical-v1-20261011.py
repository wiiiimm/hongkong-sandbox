"""Bounded original-TIN candidate with all seventeen current actors retained.

Distinct post-Elements inputs and named identity must already be frozen. This
calls the unchanged routed terrain constructor and ordinary physical checks;
no foundation, source-component, foreign or runtime exception is granted.
"""
from pathlib import Path
from types import SimpleNamespace
import importlib.util,json,subprocess,sys,uuid,traceback
from run import ROOT,HERE,read,save,digest,connect,reservations,NATIVE_RUN
from evangel_college_post_elements_current_bound_wing_extension_identity_v2_20261011 import verify_files,POLICY,UID,SOURCE_SHA,source_proposal_pin_path
BASE=ROOT/'docs/astra-city/government-import';INPUT=BASE/'government-xl-evangel-college-91306-authentic-tin-candidate-input-v1-20261011'
TIN=BASE/'government-xl-evangel-college-91306-authentic-tin-source-context-v1-20261011'
BATCH='government-xl-evangel-college-91306-authentic-tin-current-physical-v1-20261011';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def module(name,file):
 s=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def owned():
 lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists()
 receipts=[read(p/'result.json')for p in [INPUT,TIN]];refs=[Path(__file__)]
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for receipt in receipts:assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for receipt in receipts:
  for pin in receipt['evidenceRefs']:
   # Only the immutable source-TIN receipt may contain the old de8 manifest.
   p=source_proposal_pin_path(pin)if receipt is receipts[1]else ROOT/pin['path'];assert digest(p.read_bytes())==pin['sha256'];refs.append(p)
 for name in ['check-selection.json.gz','context.json.gz','proposal-input.json','complete-protected-current-forms.json.gz']:assert ref(INPUT/name)in receipts[0]['evidenceRefs']
 selected=read(INPUT/'check-selection.json.gz');assert len(selected['rows'])==1;row=selected['rows'][0];assert row['uid']==UID and row['sourceSHA256']==SOURCE_SHA and row['triangles']==13960 and row['currentReview']is None
 context=read(INPUT/'context.json.gz')['rows'];assert len(context)==1
 proposal=read(INPUT/'proposal-input.json');assert proposal['completeProtectedCurrentForms']==17
 manifest=ROOT/'3d-viewer/city/data/manifest.json';start=ref(manifest);assert start==proposal['currentManifest']and start['sha256']==selected['manifestSHA256']
 catalogue_refs=proposal['completeCurrentCatalogueRefs'];assert [p['path']for p in catalogue_refs]==['3d-viewer/'+p for p in read(manifest)['officialModelCatalogues']]
 for pin in catalogue_refs:assert ref(ROOT/pin['path'])==pin
 forms=module('evangel_authentic_all_current_forms','xl-final-script-pass.py').load_forms(proposal['proposedRegion']);saved=read(INPUT/'complete-protected-current-forms.json.gz')
 assert {b['uid']:b for b,_,_ in forms}=={r['building']['uid']:r['building']for r in saved['rows']}and len(forms)==17
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert not c.execute('SELECT uid FROM astra_modelling.model_reviews WHERE uid=%s',(UID,)).fetchone()
  assert c.execute('SELECT r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=%s',(NATIVE_RUN,row['native']['cacheKey'])).fetchall()==[(row['native']['resultSha'],)]
 assert digest((ROOT/row['candidate']['path']).read_bytes())==SOURCE_SHA
 identity=verify_files(row,context[0],LOCAL/'current-named-identity');assert identity==read(INPUT/'owned-source-identity.json')and identity['passed']and identity['reasons']==[]
 save(DOC/'owned-source-identity.json',identity);(DOC/'captured-manifest.json').write_bytes(manifest.read_bytes())
 source=read(TIN/'complete-authentic-source-tin-ground.json.gz');assert source['sourceTerrainReceipt']['sheet']=='12-NW-21C'
 folder=ROOT/source['sourceTerrainReceipt']['cache'];index=module('evangel_verified_authentic_TIN','xl-owned-indexed-terrain-continuation.py');verified=index.verified_terrain(folder);assert verified and verified[0]['directorySHA256']==source['sourceTerrainReceipt']['directorySHA256']
 pipeline=module('evangel_authentic_current_pipeline','xl-routed-cell-contact-resolution.py');pipeline.BATCH=BATCH;pipeline.BASE=INPUT;pipeline.DOC=DOC;pipeline.LOCAL=LOCAL;pipeline.UIDS=[UID];pipeline.SOURCE=folder;pipeline.ADJACENT_SOURCES=[]
 def exact_own_identity(r,ctx,local):
  assert r==row and ctx==context[0]and r['uid']==UID
  return verify_files(r,ctx,local)
 def fenced_call(args,allowed=(0,)):
  process=subprocess.Popen(args,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
  while True:
   try:stdout,stderr=process.communicate(timeout=30);break
   except subprocess.TimeoutExpired:
    assert process.poll()is None and reservations.owns(lease)and reservations.heartbeat(lease,ttl=3600)['ok'];print(json.dumps(dict(activeCommand=args[1],reservationHeartbeat=True)),flush=True)
  save(DOC/('command-'+str(len(list(DOC.glob('command-*.json'))))+'.json'),dict(args=args,exitCode=process.returncode,stdout=stdout,stderr=stderr));assert process.returncode in allowed,(args,process.returncode,stderr)
  assert ref(manifest)==start and reservations.owns(lease)
  for pin in catalogue_refs:assert ref(ROOT/pin['path'])==pin
 pipeline.call=fenced_call
 prior=sys.modules.get('routed_original_cell_identity');sys.modules['routed_original_cell_identity']=SimpleNamespace(POLICY=POLICY,verify_files=exact_own_identity)
 raw_guard_failure=None
 try:
  try:pipeline.owned()
  except AssertionError as error:
   raw_guard_failure=dict(error=str(error),traceback=traceback.format_exc(),attemptCompleted=False,currentAcceptance=False);save(DOC/'raw-guard-failure.json',raw_guard_failure)
 finally:
  if prior is None:sys.modules.pop('routed_original_cell_identity',None)
  else:sys.modules['routed_original_cell_identity']=prior
 reasons=[]
 if raw_guard_failure is None:
  actual=read(DOC/'neighbour-inputs.json.gz');assert {r['building']['uid']:r['building']for r in actual['rows']}=={r['building']['uid']:r['building']for r in saved['rows']}and len(actual['rows'])==17
  assert actual['inputHashes']==saved['inputHashes']and all(r['existingNative']==s['existingNative']for r,s in zip(sorted(actual['rows'],key=lambda r:r['building']['uid']),sorted(saved['rows'],key=lambda r:r['building']['uid'])))
  metrics=read(DOC/'metrics.json');found=read(DOC/'foundation.json');validation=read(DOC/'validation.json');policy=module('evangel_raw_candidate_policy','acceptance-policy.py')
  reasons=policy.reasons(dict(state='runtime-validated-awaiting-acceptance',sourceSHA256=SOURCE_SHA,identityProof=identity['proof']),metrics['rows'][0],metrics['profiles']['mobile'])
  if not found['rows'][0]['strictFoundationAccepted']:reasons.append('whole-source-foundation')
  reasons.extend(validation['results'][0].get('concerns',[]));native=read(DOC/'native-neighbour-checks.json');resolved=set(native['resolved']);reasons.extend('native-neighbour-regression:'+u for u in set(native['blocked'])-resolved);reasons.extend('terrain-regresses-neighbour:'+r['uid']for r in read(DOC/'neighbour-checks.json')['rows']if r['reasons']and r['uid']not in resolved)
 assert reservations.owns(lease)and ref(manifest)==start
 for pin in catalogue_refs:assert ref(ROOT/pin['path'])==pin
 for p,h in saved['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h
 save(DOC/'diagnostic.json.gz',dict(uids=[UID],sourceSHA256=SOURCE_SHA,currentManifest=start,completeCurrentCatalogueRefs=catalogue_refs,completeProtectedCurrentForms=17,completeFourWorldUnusedPOSITIONBounds=proposal['completeFourWorldUnusedPOSITIONBounds'],rawOrdinaryReasons=sorted(set(reasons)),rawGuardFailure=raw_guard_failure,sourceGeometryChanges=0,terrainProposalCreated=(DOC/'terrain-candidates.json').exists(),terrainProposalIsNotInstalled=True,namedIdentityGrantsNoPhysicalExemption=True,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,currentAcceptance=False,physicalAccepted=False,installationApproved=False,newlyInstalled=0))
 refs+=[INPUT/'result.json',TIN/'result.json',manifest,*[ROOT/p['path']for p in catalogue_refs],HERE/'evangel_college_post_elements_current_bound_wing_extension_identity_v2_20261011.py',HERE/'xl-routed-cell-contact-resolution.py',HERE/'xl-owned-indexed-terrain-continuation.py',HERE/'acceptance-policy.py',HERE/'xl-final-script-pass.py',HERE/'native_patch_resolution.py',HERE/'xl-second-pass.py']
 refs.extend(p for p in DOC.rglob('*')if p.is_file());refs.extend(p for p in LOCAL.rglob('*')if p.is_file()and p.name!='reservation.json')
 receipt=module('evangel_physical_candidate_freeze','xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'authentic-school-TIN-candidate-complete-current-17-actor-ordinary-physical-diagnostic-no-waiver',refs,dict(uids=[UID],rawOrdinaryReasons=sorted(set(reasons)),attemptCompleted=raw_guard_failure is None,currentAcceptance=False,newlyInstalled=0));print(json.dumps(dict(jobId=receipt['jobId'],rawReasons=reasons,rawGuardFailure=raw_guard_failure)),flush=True)
def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists()and not LOCAL.exists();saved=read(INPUT/'complete-protected-current-forms.json.gz');assert len(saved['rows'])==17
 resources=[('building:'if r['building']['uid'].startswith('landsd/')else'foreign-form:')+r['building']['uid']for r in saved['rows']]+['terrain-patch:'+UID]
 claim=reservations.claim('evangel-authentic-current-physical-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'];save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)))
 subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
