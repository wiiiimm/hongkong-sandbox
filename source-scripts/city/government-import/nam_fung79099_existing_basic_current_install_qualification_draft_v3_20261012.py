"""DRAFT concrete existing-route current qualification; no publication/review writes.
Reuse complete Nam source proofs; run only missing ordinary identity/runtime guards.
"""
import argparse,copy,json,subprocess,sys,uuid
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect,reservations
import nam_fung79099_source_bound_basic_mainbody_interbody_role_draft_v1_20261012 as Q
from exact_original_georef_cell_identity_20261009 import verify_files as raw_identity
from government_owned_identity import verify_files as owned_identity
from exact_packed_world_bounds_v3_20261010 import packed_world_bounds
from complete_actual_native_position_bounds_separation_20261011 import verify as native_separation
B=ROOT/'docs/astra-city/government-import';BATCH='government-xl-nam-fung79099-existing-basic-current-install-qualification-v3-20261012';DOC=B/BATCH;LOCAL=HERE/'local'/BATCH
ROOT_NOTE=B/'government-xl-original-installation-followup-20261011/root-nam-source-context-verified-20261012.json';NATIVE=B/'government-xl-complete-current-native-actual-position-matrix-bounds-v4-20261012';PROPOSAL=B/'government-xl-nam-fung79099-existing-basic-current-install-qualification-proposal-v3-20261012';BUDGET=HERE/'nam_fung79099_current_basic_support_availability_budget_draft_v3_20261012.mjs'
UID=Q.UIDS[0];CARRIER=Q.PROTECTED;DEPENDENCY=dict(uid=CARRIER,csuid='3777116537P20060312',state='surveyed-footprint-fallback')

FAILED=B/'government-xl-nam-fung79099-existing-basic-current-install-qualification-v1-20261012';FAILED_PROPOSAL=B/'government-xl-nam-fung79099-existing-basic-current-install-qualification-proposal-v1-20261012'

COMPLETED=B/'government-xl-nam-fung79099-existing-basic-current-install-qualification-v2-20261012';COMPLETED_PROPOSAL=B/'government-xl-nam-fung79099-existing-basic-current-install-qualification-proposal-v2-20261012'

def pinned_inputs():
 pins=read(PROPOSAL/'executable-pins.json');assert Q.ref(Path(__file__))==pins['caller']
 for e in pins['inputs']:assert Q.ref(ROOT/e['path'])==e,e
 recovered=read(COMPLETED_PROPOSAL/'actual-v2-failure-release-current-state-audit.json');assert recovered['actualTerminalExitCode']==1 and recovered['releasedAtVerified']and recovered['ownsFalse']and recovered['protected207ReviewRowsUnchanged']and recovered['currentInputsUnchanged']
 for e in recovered['savedOutputs']+[recovered['executedCaller'],recovered['terminalLog'],recovered['lease']]:assert Q.ref(ROOT/e['path'])==e,e
 audit=read(FAILED_PROPOSAL/'actual-v1-failure-release-current-state-audit.json');assert audit['actualTerminalExitCode']==1 and audit['releasedAtVerified']and audit['ownsFalse']and audit['rawIdentityPassed']and audit['ownedIdentityPassed']
 for e in audit['savedOutputs']+[audit['executedCaller'],audit['terminalLog'],audit['lease']]:assert Q.ref(ROOT/e['path'])==e,e
 bound,capture,join,finite_receipt,scope,before,selections,prior,finite=Q.inputs();gr=read(Q.DOC/'result.json');assert Q.ref(Q.DOC/'result.json')['sha256']=='e115dc76bf126e2053c541f92c92f94cfd616e85b386e07badbbb8d73b3f9b7e';graph=read(Q.DOC/'diagnostic.json.gz');note=read(ROOT_NOTE)
 assert note['currentManifest']==scope['currentManifest']and note['originalGeometryChanges']==note['liveTerrainChanges']==0 and not note['physicalAccepted']and not note['installationApproved']
 findings=note['findings'];terminal=findings['descriptiveTerminalSourceReview'];assert terminal['sourceGeometryUnchanged']and not terminal['engineeringFunctionOrWeldCertified']and not terminal['physicalInstallationApproved']
 assert findings['completeFaces']==13061 and findings['originalBodies']==569 and findings['authoredZeroFaces']==75 and len(terminal['originalBodyIDs'])==112 and len(findings['rootActuallyViewedImages'])==5
 for e in findings['rootActuallyViewedImages']+[findings['sourceContext'],findings['actualExportValidation']]:assert Q.ref(ROOT/e['path'])==e
 assert graph['mainbodySavedCarrierFacts']==Q.mainbody_saved_facts(prior,finite)
 for sh,g in graph['distinctInterbodyRoleContexts'].items():
  assert g['typedGraph']['conditionalGraph']['unreachedNonvisualBodies']==terminal['originalBodyIDs'];assert len(g['typedGraph']['conditionalGraph']['conditionalPositiveDimensionalContactPaths'])==457
  assert set(map(int,g['typedGraph']['conditionalGraph']['conditionalPositiveDimensionalContactPaths']))|set(terminal['originalBodyIDs'])==set(range(569))
 nr=read(NATIVE/'result.json');ni=read(NATIVE/'input.json.gz');nv=read(NATIVE/'inventory.json.gz');assert nr['jobId']=='8614ecb76819b66f4dc97e0a840fc17532f25896d54e971d3c060332d644085e'and nr['currentManifest']==scope['currentManifest']and nr['freshEveryActorActualLoad']and not nr['oldActualRuntimeRowsReused']
 assert ni['currentManifest']==scope['currentManifest']and nv['completeNativeActors']==nv['successfullyCapturedActors']==len(nv['rows'])==6649 and not nv['errors']and nv['startAndEndInputHashesVerified']
 receipts=[capture,join,finite_receipt,gr,nr]
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for r in receipts:assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for r in receipts:
  for e in r['evidenceRefs']:assert Q.ref(ROOT/e['path'])==e,e
 for p,h in nv['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h,p
 entries={}
 manifest=read(ROOT/scope['currentManifest']['path']);assert ni['currentCatalogueRefs']==[dict(**Q.ref(ROOT/'3d-viewer'/p),originalPath='3d-viewer/'+p)for p in manifest['officialModelCatalogues']]
 for pin in ni['currentCatalogueRefs']:
  for e in read(ROOT/pin['path'])['models']:assert e['uid']not in entries;entries[e['uid']]=e
 assert len(entries)==6649 and UID not in entries and CARRIER not in entries and CARRIER not in {u for e in entries.values()for u in e.get('suppressesBuildingUids',[])}
 forms={}
 for p,h in ni['currentNativeViewerTileHashes'].items():
  assert digest((ROOT/p).read_bytes())==h
  for f in read(ROOT/p)['buildings']:
   if f['uid']in ni['currentAllNativeSourceForms']:assert f['uid']not in forms;forms[f['uid']]=f
 assert forms==ni['currentAllNativeSourceForms']
 by={r['uid']:r for r in nv['rows']};assert set(by)==set(entries)
 for r in ni['rows']:
  assert r['rawCurrentEntry']==entries[r['uid']]and r['currentBuilding']==forms[r['uid']]and Q.ref(ROOT/r['source']['path'])==r['source']and r['source']['sha256']==by[r['uid']]['sourceSHA256']
 return pins,bound,capture,join,finite_receipt,scope,before,selections,prior,finite,gr,graph,note,nr,ni,nv

def main():
 p=argparse.ArgumentParser();p.add_argument('--preflight-only',action='store_true');p.add_argument('--owned',action='store_true');a=p.parse_args();data=pinned_inputs();pins,bound,capture,join,fr,scope,before,selections,prior,finite,gr,graph,note,nr,ni,nv=data
 if a.preflight_only:print(json.dumps(dict(exactCurrentPriorNeonSourceRoleNativeTuplePreflightPassed=True,noWorker=True)));return
 if not a.owned:
  assert not DOC.exists()and not LOCAL.exists();claim=reservations.claim('nam-existing-basic-install-qualification-'+str(uuid.uuid4()),['building:'+u for u in before['uids']],batch=BATCH,ttl=3600);assert claim['ok'],claim;save(LOCAL/'reservation.json',json.loads(json.dumps(claim['reservation'],default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LOCAL/'reservation.json'),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True);return
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease)and not DOC.exists();DOC.mkdir(parents=True)
 def fence():
  assert reservations.owns(lease);Q.inputs()
  for e in [pins['caller']]+pins['inputs']:assert Q.ref(ROOT/e['path'])==e
  for p,h in nv['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h,p
 def call(cmd,allowed=(0,)):
  fence();assert reservations.heartbeat(lease)['ok'];r=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True);save(DOC/('command-'+str(len(list(DOC.glob('command-*.json'))))+'.json'),dict(args=cmd,exitCode=r.returncode,stdout=r.stdout,stderr=r.stderr));print(r.stdout,flush=True);assert r.returncode in allowed,r.stderr
  if str(HERE.parent/'building-batch/validate_candidates.mjs')in cmd:
   assert (DOC/'validation.json').is_file(),'Ordinary validator produced no actual report; terminal/stdout/stderr preserved'
   actual_report=read(DOC/'validation.json');assert set(['loaderAccepted','checksPassed','exceptions','results'])<=set(actual_report)and isinstance(actual_report['results'],list);assert all(isinstance(v.get('concerns',[]),list)for v in actual_report['results'])
  fence()
 row=copy.deepcopy(read(Q.CAP/'selection.json.gz')['rows'][0]);attrs=read(Q.CAP/'actual-render-geometry.json.gz');actual=attrs['rows'][0];world=np.asarray(read(Q.CAP/'original-full-source-root-context.json.gz')['rows'][0]['completeOriginalBinary64WorldTriangles'],dtype='<f8');assert world.shape==(13061,3,3)and digest(world.tobytes())=='5a3726aafe64e1410482327fd681f49ede03b47718d4180e0e24b5cd27078c38'
 final=Q.module(HERE/'xl-final-script-pass.py','nam_current_install_final');lo=world.min((0,1));hi=world.max((0,1));forms=final.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2]);current=next(f for f,_,_ in forms if f['uid']==UID);assert current==row['source']['building'];context=read(FAILED/'identity-context.json.gz');assert context['uid']==UID and context['sourceSHA256']==Q.SOURCE;assert context['neighbourTileHashes']=={t:digest((ROOT/'3d-viewer'/t).read_bytes())for _,_,t in forms};assert row['source']==read(FAILED/'selection.json.gz')['rows'][0]['source']
 saved_context=read(FAILED/'identity-context.json.gz');assert saved_context==context;raw=read(FAILED/'raw-current-identity.json');owned=read(FAILED/'owned-current-identity.json');assert raw['passed']and owned['passed'];save(DOC/'raw-current-identity.json',raw);save(DOC/'owned-current-identity.json',owned);save(DOC/'identity-context.json.gz',context);save(DOC/'saved-identity-exact-reuse.json',dict(actualCompletedV1IdentityArithmeticReused=True,identityArithmeticRerun=False,refs=[Q.ref(FAILED/f)for f in ['identity-context.json.gz','raw-current-identity.json','owned-current-identity.json']]))
 # Ordinary checks are diagnostic even when identity is held; no hidden exceptions.
 source=(ROOT/row['candidate']['path']).read_bytes();assert digest(source)==Q.SOURCE;dest=LOCAL/row['candidate']['entry']['asset'];dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(source);row['candidate']['path']=str(dest.relative_to(ROOT));save(DOC/'selection.json.gz',dict(rows=[row]));save(DOC/'terrain-candidates.json',[])
 catalogue=read(HERE/'local'/Q.CAP.name/'catalogue.json');assert len(catalogue['models'])==1;catalogue.update(area=BATCH,kind='staged-official-model-catalogue',counts=dict(packedModels=1),models=[row['candidate']['entry']]);save(LOCAL/'catalogue.json',catalogue);save(LOCAL/'catalogue-index.json',dict(models=1,catalogues=['catalogue.json']));save(LOCAL/'source-forms.json',{UID:row['source']})
 formrows=read(Q.CAP/'complete-current-forms.json.gz')['rows'];assert len(formrows)==len({r['building']['uid']for r in formrows})==len(before['uids'])==15 and {r['building']['uid']for r in formrows}==set(before['uids'])
 save(DOC/'neighbour-inputs.json.gz',dict(rows=[dict(building=r['building'],existingNative=r['installedNative'],patchIndexes=[])for r in formrows],inputHashes={str((ROOT/'3d-viewer'/r['tile']).relative_to(ROOT)):digest((ROOT/'3d-viewer'/r['tile']).read_bytes())for r in formrows},candidateIds=[UID],patches=[]))
 # Metrics already current-byte-bound; only execute missing production validator.
 (DOC/'metrics.json').write_bytes((Q.CAP/'metrics.json').read_bytes());call(['node',str(HERE.parent/'building-batch/validate_candidates.mjs'),'--candidates',str(LOCAL.relative_to(ROOT)),'--source-forms',str((LOCAL/'source-forms.json').relative_to(ROOT)),'--terrain-candidates',str((DOC/'terrain-candidates.json').relative_to(ROOT)),'--out',str((DOC/'validation.json').relative_to(ROOT))],(0,1))
 # Reuse the exact completed current v2 ordinary gates; all tuples freshly fenced.
 for name in ['neighbour-inputs.json.gz','neighbour-checks.json','native-neighbour-checks.json','foundation.json','native-separation.json.gz']:(DOC/name).write_bytes((COMPLETED/name).read_bytes())
 foundation=read(DOC/'foundation.json');foundation_ok=foundation['strictFoundationAccepted'];native_saved=read(DOC/'native-separation.json.gz');assert native_saved['currentManifest']==scope['currentManifest']and native_saved['currentFreshNativeReceipt']==Q.ref(NATIVE/'result.json');separation=native_saved['certificate'];separation_ok=separation['allFourOwnedByThreeActualNativeWorldBoundsStrictlyDisjoint'];assert separation['completeForeignNativeActors']==6649
 for name in ['neighbour-checks.json','native-neighbour-checks.json']:
  for path,h in read(DOC/name)['inputHashes'].items():assert digest((ROOT/path).read_bytes())==h,path
 save(DOC/'saved-v2-ordinary-gates-exact-reuse.json',dict(ordinaryGateArithmeticRerun=False,refs=[Q.ref(COMPLETED/name)for name in ['neighbour-inputs.json.gz','neighbour-checks.json','native-neighbour-checks.json','foundation.json','native-separation.json.gz']],failureAudit=Q.ref(COMPLETED_PROPOSAL/'actual-v2-failure-release-current-state-audit.json')))

 validation=read(DOC/'validation.json');metrics=read(DOC/'metrics.json');policy=Q.module(HERE/'acceptance-policy.py','nam_current_install_policy');numeric=policy.reasons(dict(state='runtime-validated-awaiting-acceptance',sourceSHA256=Q.SOURCE,identityProof=owned.get('proof',{})),metrics['rows'][0],metrics['profiles']['mobile']);neighbours=read(DOC/'neighbour-checks.json');nativechecks=read(DOC/'native-neighbour-checks.json');runtimeconcerns=validation['results'];allowed_runtime=all(r['uid']==UID and r.get('concerns',[])in [[],['sampled-ground-gap-below-model-bottom']]for r in runtimeconcerns)
 ordinary_clear=all(not p['ordinaryFailingFaces']and not p['coverageFailingFaces']for p in finite['distinctCompleteFiniteProofs'].values());source_ready=all(r['mainbodyGeometricCarrierCandidateReady']and len(r['positiveMainbodyQualifiedCapContactRecordIndices'])==41 for r in graph['mainbodySavedCarrierFacts']['qualifiedMainbodyFactsByExactWorld'].values())
 ready=bool(raw['passed']and owned['passed']and foundation_ok and ordinary_clear and source_ready and separation_ok and numeric in [[],['ground-contact-unresolved']]and validation['loaderAccepted']==validation['checksPassed']==1 and validation['exceptions']==0 and allowed_runtime and not any(r['reasons']for r in neighbours['rows'])and not nativechecks['blocked'])
 entry=copy.deepcopy(row['candidate']['entry']);entry.update(priority='detail',proceduralWindows=False,placementReviewed=True,identityReviewApproved=True,sourceIdentityReviewed=True,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,publicationApproved=ready,supportDependencies=[DEPENDENCY]);assert entry['sha256']==Q.SOURCE and entry['rootTranslation']==row['candidate']['entry']['rootTranslation']and entry['worldBounds']==row['candidate']['entry']['worldBounds'];save(DOC/'proposed-staged-entry.json',entry)
 source_roles=dict(uid=UID,sourceSHA256=Q.SOURCE,completeFaces=13061,completeOriginalBodies=569,authoredZeroFaces=75,mainbody0Faces=1601,sourceConnectedBodies=457,nonbridgingTerminalBodyIDs=note['findings']['descriptiveTerminalSourceReview']['originalBodyIDs'],rootSourceRoleReview=Q.ref(ROOT_NOTE),completeSourceGraph=Q.ref(Q.DOC/'diagnostic.json.gz'),savedMainbody41Interfaces=graph['mainbodySavedCarrierFacts'],interiorFlagsPreserved=True,allFourWorldBindings=finite['allFourStreamBindings'],wholeBASICReaccepted=False,originalGovernmentPodiumInstalled=False,perWindowIndependentGroundRootRequired=False)
 save(DOC/'source-bound-complete-assembly.json.gz',source_roles)
 if ready:
  lit=read(Q.CAP/'literal-source-inputs.json.gz');save(DOC/'runtime-support-input.json.gz',dict(rows=[row],currentManifest=scope['currentManifest'],currentCatalogueRefs=lit['currentCatalogueRefs'],currentAllSourceForms={r['building']['uid']:r['building']for r in formrows}));save(DOC/'runtime-support-geometry.json.gz',dict(row=actual,completeCurrentBasicGeometry=attrs['basicContextRows'],inputHashes=scope['inputHashes']));call(['node',str(BUDGET),str(DOC/'proposed-staged-entry.json'),str(DOC/'production-support-budget-loader.json')]);support=read(DOC/'production-support-budget-loader.json');assert support['checksPassed']==19 and support['startAndEndInputHashesVerified']and support['ordinaryBudgetLimitsUnchanged']
 blockers=[]
 for ok,reason in [(raw['passed'],'raw-current-identity'),(owned['passed'],'owned-current-identity'),(foundation_ok,'whole-foundation'),(separation_ok,'complete-native-separation-or-finite-actor-context'),(numeric in [[],['ground-contact-unresolved']],'other-ordinary-numeric-reasons'),(validation['loaderAccepted']==validation['checksPassed']==1 and validation['exceptions']==0 and allowed_runtime,'runtime-loader-picking-collision'),(not any(r['reasons']for r in neighbours['rows'])and not nativechecks['blocked'],'foreign-neighbour-regressions')]:
  if not ok:blockers.append(reason)
 outcome=dict(uid=UID,sourceSHA256=Q.SOURCE,currentManifest=scope['currentManifest'],currentNativeCount=6649,sourceAssembly=Q.ref(DOC/'source-bound-complete-assembly.json.gz'),rawIdentity=raw,ownedIdentity=owned,rawOrdinaryNumericReasons=numeric,rawRuntimeConcerns=runtimeconcerns,remainingActualBlockers=blockers,scriptChecksPassed=ready,acceptanceReadyForStaging=ready,physicalAccepted=ready,installationApproved=False,sourceGeometryChanges=0,terrainGeometryChanges=0,wholeBASICReaccepted=False,originalGovernmentPodiumUsedAsSupport=False,currentBasicCarrierDependency=DEPENDENCY,stageAndLiveBrowserRequired=True,newlyInstalled=0)
 save(DOC/'qualification.json',outcome);fence();walker=Q.module(HERE/'parkview_block17_freeze_current_source_evidence_20261011.py','nam_qualification_closure');paths=set();walker.local_imports(Path(__file__),paths);walker.declared_refs(outcome,paths);paths.update(q for folder in [DOC,LOCAL,PROPOSAL]for q in folder.rglob('*')if q.is_file());paths.update(ROOT/e['path']for r in [capture,join,fr,gr,nr]for e in r['evidenceRefs']);paths.update([ROOT_NOTE,BUDGET,Path(__file__)]);paths.update(q for folder in [FAILED,FAILED_PROPOSAL,HERE/'local'/FAILED.name,COMPLETED,COMPLETED_PROPOSAL,HERE/'local'/COMPLETED.name]for q in folder.rglob('*')if q.is_file())
 for folder in [DOC]:
  for file in folder.glob('*.json'):
   obj=read(file)
   for path in obj.get('inputHashes',{}):paths.add(ROOT/path)
 result=walker.F.freeze(BATCH,'nam-unchanged-original-current-basic-complete-qualification-no-publication',sorted(paths),dict(uids=[UID,CARRIER],sourceOnly=not ready,completeFaces=13061,completeOriginalBodies=569,authoredZeroFaces=75,scriptChecksPassed=ready,acceptanceReadyForStaging=ready,physicalAccepted=ready,installationApproved=False,newlyInstalled=0,sourceGeometryChanges=0,terrainGeometryChanges=0,wholeBASICReaccepted=False,modelReviewWrites=0))
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(result['jobId'],)).fetchone()==('complete',result)
 for e in result['evidenceRefs']:assert Q.ref(ROOT/e['path'])==e
 fence();print(json.dumps(dict(jobId=result['jobId'],allRefs=len(result['evidenceRefs']),acceptanceReadyForStaging=ready,remainingActualBlockers=blockers,installationApproved=False)))
if __name__=='__main__':main()
