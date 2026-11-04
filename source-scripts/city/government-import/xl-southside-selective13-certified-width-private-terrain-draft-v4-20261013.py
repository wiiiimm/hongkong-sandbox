"""UNEXECUTED private acquisition proposal; no source decode/live/acceptance."""
import importlib.util,json,subprocess,sys,uuid,traceback
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect,reservations
import southside_selective13_certified_width_parent_restoration_draft_v2_20261013 as adapter
import native_patch_resolution as overlap
B=ROOT/'docs/astra-city/government-import';D=B/'government-xl-southside-private-authentic-terrain-draft-v2-20261012';P=D/'selective13-parent-restoration-draft-v1';PLAN=P/'certified-width-constructor-draft-v1'
BATCH='government-xl-southside-selective13-certified-width-private-terrain-v4-20261013';DOC=B/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json';CURRENT='c00fd9f731b1bcbf4d2df6067a5cb3231f0eaa8c503a8adea584fec39bf73bf7';OLD='2dde0cfc3c0869963c185c3398e48a1928c76802b2efa6c2d9713183a6ad5540'
BASE=B/'government-xl-southside-315025-300867-source-local-private-terrain-diagnostic-v4-20261012';MASK=P/'exact-half-distance-closed-mask-certificate-v1/certificate.json.gz';NAM=B/'government-xl-complete-native-actual-position-post-nam-delta-v1-20261013';OLD_CAPTURE=B/'government-xl-southside-315025-300867-current-actual-ground-capture-v1-20261012'
UIDS=['landsd/315025:0','landsd/300867:0'];EXPECTED_TESTS=26
sha=lambda p:digest(p.read_bytes())
def module(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def codes():return [Path(__file__),HERE/'southside_selective13_certified_width_parent_restoration_draft_v2_20261013.py',HERE/'test_southside_selective13_certified_width_parent_restoration_draft_v2_20261013.py',HERE/'xl-southside-selective13-certified-width-runtime-draft-v1-20261013.mjs',PLAN/'METHOD-v4.md',PLAN/'input-contract-v4.json']
def preflight(require_validation=True):
 assert not DOC.exists()and not(LOCAL/'private-terrain.json').exists()
 c=read(PLAN/'input-contract-v4.json');assert c['schema']=='southside-certified-width-private-constructor-input-v1'and c['currentManifestSHA256']==CURRENT
 refs=codes();pins={}
 for r in c['filePins']:
  p=ROOT/r['path'];assert p.resolve().is_relative_to(ROOT.resolve())and sha(p)==r['sha256'],r['path'];refs.append(p);pins[r['path']]=r['sha256']
 assert sha(ROOT/'3d-viewer/city/data/manifest.json')==CURRENT
 mask=read(MASK);assert sha(MASK)=='71fabd75966c74d67414e37ba95deff1d958ea7b2dc5092fed0122f998cdfb35'and mask['currentAcceptance']is False
 assert mask['sourceBoundMaskCertificate']['all4784ClosedRegionsSeparatedFromPackedMask']and len(mask['sourceBoundMaskCertificate']['completeClosedCoreMinkowskiMaskPrimitives'])==831
 saved=read(BASE/'saved-source-local-construction-account.json.gz');basepatch=read(ROOT/saved['privateCandidatePath']);assert sha(ROOT/saved['privateCandidatePath'])==saved['privateCandidateSHA256']and saved['account']['outputFacets']==24580
 assert saved['account']['completeInputFacets']==774477 and saved['account']['triangleBudget']==25000 and saved['all19RoleAndWholeModelQualificationPending']and saved['face3009Unqualified']and saved['facet11034Unqualified']
 extent=read(D/'actual-basic-extent-account.json.gz');resources=extent['actualResources'];assert len(resources)==len(set(resources))==124 and extent['account']['completeScannedForms']==1238 and len(extent['account']['affectedUIDs'])==117 and extent['all46OriginalProtectiveResourcesRetained']
 proof=read(D/'actual-basic-extent-proof.json.gz');assert len(proof['rows'])==len({r['uid']for r in proof['rows']})==1238
 assert {r['classification']for r in proof['rows']}=={'actual-production-BASIC','installed-native-already-exactly-bound'}
 basic_rows=[r for r in proof['rows']if r['classification']=='actual-production-BASIC'];saved_native_rows=[r for r in proof['rows']if r['classification']=='installed-native-already-exactly-bound']
 assert len(basic_rows)==1231 and len(saved_native_rows)==7 and all(r['wholeUnusedPositionVerticesIncluded']is True for r in basic_rows)
 assert all(set(r)=={'uid','currentForm','classification'}for r in saved_native_rows)
 inp=read(NAM/'input.json.gz');composition=read(NAM/'composition.json.gz');delta=read(NAM/'inventory.json.gz');binding=read(ROOT/composition['exactBaselineCurrentBinding']['path']);baseline=read(ROOT/composition['baselineInventory']['path'])
 assert composition['completeCurrentNativeActors']==6650 and composition['completeOldActorsExactlyRebound']==6649 and composition['newUID']=='landsd/79099:0' and composition['currentManifest']['sha256']==CURRENT
 assert delta['completeNativeActors']==6650 and delta['successfullyCapturedActors']==1 and not delta['errors']and delta['startAndEndInputHashesVerified'];assert len(baseline['rows'])==6649 and len(binding['rows'])==6649 and binding['exactAllSourceFormEntryLoaderTuples']
 native=baseline['rows']+delta['rows'];assert len(native)==len({r['uid']for r in native})==6650
 assert inp['requiredUnchangedProductionClosure']==delta['completeRecursiveProductionModuleClosure']['inputHashes']
 manifest=read(ROOT/'3d-viewer/city/data/manifest.json');assert [r['path']for r in inp['currentCatalogueRefs']]==['3d-viewer/'+url for url in manifest['officialModelCatalogues']]
 entries={}
 for r in inp['currentCatalogueRefs']:
  assert r['path']==r['originalPath'];assert sha(ROOT/r['path'])==r['sha256']
  for entry in read(ROOT/r['path'])['models']:assert entry['uid']not in entries;entries[entry['uid']]=entry
 assert len(entries)==6650 and all(u not in entries for u in UIDS)
 actual_by_uid={r['uid']:r for r in native};binding_by_uid={r['uid']:r for r in binding['rows']}
 assert {r['uid']for r in saved_native_rows}=={'landsd/32681:0','landsd/34759:0','landsd/125385:0','landsd/136832:0','landsd/282761:0','landsd/283473:0','landsd/295518:0'}
 for r in saved_native_rows:
  u=r['uid'];assert u in entries and u in actual_by_uid and u in binding_by_uid
  a,b=actual_by_uid[u],binding_by_uid[u];assert a['wholeUnusedPositionVerticesIncluded']is True and a['sourceFacesOmitted']==0 and a['completeOriginalPOSITIONProof']['allOriginalPositionVerticesAccounted']is True
  assert a['actualRenderMeshes']and all(m['wholePositionVerticesIncludingUnused']is True for m in a['actualRenderMeshes'])
  assert sum(m['completePositionVertices']for m in a['actualRenderMeshes'])==a['completePositionVertices']and sum(m['completeIndexedFaces']for m in a['actualRenderMeshes'])==a['completeFaces']
  assert a['sourceSHA256']==a['completeOriginalPOSITIONProof']['sourceSHA256']==b['source']['sha256']and sha(ROOT/b['source']['path'])==b['source']['sha256']
  assert digest(json.dumps(a,sort_keys=True,separators=(',',':')).encode())==b['unchangedActualBoundsSHA256']
  assert r['currentForm']==inp['currentAllNativeSourceForms'][u]and digest(json.dumps(inp['currentAllNativeSourceForms'][u],sort_keys=True,separators=(',',':')).encode())==b['currentViewerFormSHA256']
  assert digest(json.dumps(entries[u],sort_keys=True,separators=(',',':')).encode())==b['currentRawEntrySHA256']
 forms={};wanted_source_ids={r['uid']for r in proof['rows']}
 for tile in manifest['tiles']:
  for f in read(ROOT/('3d-viewer/'+tile['url']))['buildings']:
   if f['uid']in wanted_source_ids or f['uid']in inp['currentAllNativeSourceForms']:
    assert f['uid']not in forms;forms[f['uid']]=f
 for r in proof['rows']:assert forms[r['uid']]==r['currentForm']
 for r in binding['rows']:
  u=r['uid'];assert forms[u]==inp['currentAllNativeSourceForms'][u];assert sha(ROOT/r['source']['path'])==r['source']['sha256'];assert digest(json.dumps(entries[u],sort_keys=True,separators=(',',':')).encode())==r['currentRawEntrySHA256']
 current_forms=read(OLD_CAPTURE/'capture-inputs.json.gz')['completeCurrentForms'];assert len(current_forms)==46 and saved['all46FormsVerbatim']==current_forms
 for f in current_forms:assert forms[f['uid']]==f
 neighbour=read(B/'government-xl-southside-source-local-v4-private-ground-capture-v1-20261012/neighbour-inputs.json.gz');assert len(neighbour['rows'])==117
 for r in neighbour['rows']:assert forms[r['building']['uid']]==r['building']and r['existingNative']==(r['building']['uid']in entries)
 parent=read(ROOT/'3d-viewer/city/data/terrain.json');assert sha(ROOT/'3d-viewer/city/data/terrain.json')==basepatch['meta']['parentSha256']
 if require_validation:
  path=PLAN/'immutable-focused-tests-v2/validation.json';v=read(path);assert v['tests']==EXPECTED_TESTS and v['passed']and v['exitCode']==0 and sha(PLAN/'immutable-focused-tests-v2/tests.log')==v['testLogSHA256'];legacy_codes=[HERE/'xl-southside-selective13-certified-width-private-terrain-draft-v2-20261013.py',HERE/'southside_selective13_certified_width_parent_restoration_draft_v2_20261013.py',HERE/'test_southside_selective13_certified_width_parent_restoration_draft_v2_20261013.py',HERE/'xl-southside-selective13-certified-width-runtime-draft-v1-20261013.mjs',PLAN/'METHOD-v2.md',PLAN/'input-contract-v2.json']
  assert v['codePins']==[dict(path=str(p.relative_to(ROOT)),sha256=sha(p))for p in legacy_codes]
  envelope_path=PLAN/'caller-only-v4-binding-envelope.json';envelope=read(envelope_path);assert envelope['schema']=='southside-preflight-form-representation-caller-only-v4'and envelope['unchanged26NumericFixturesReused']is True
  assert envelope['originalValidationSHA256']==sha(path)and envelope['originalTestLogSHA256']==sha(PLAN/'immutable-focused-tests-v2/tests.log')and envelope['currentCodePins']==[dict(path=str(p.relative_to(ROOT)),sha256=sha(p))for p in codes()]
  assert sha(PLAN/'caller-v3-v4-current-form-representation-only.diff')==envelope['exactCallerDiffSHA256'];refs.extend([path,PLAN/'immutable-focused-tests-v2/tests.log',envelope_path,PLAN/'caller-v3-v4-current-form-representation-only.diff',*legacy_codes])
 for p in refs:pins[str(p.relative_to(ROOT))]=sha(p)
 return dict(refs=sorted(set(refs)),pins=pins,resources=resources,mask=mask,saved=saved,basepatch=basepatch,parent=parent,native=native,manifest=manifest,neighbour=neighbour,entries=entries,forms=forms,contract=c)
def unchanged(s):
 assert sha(ROOT/'3d-viewer/city/data/manifest.json')==CURRENT
 for p,h in s['pins'].items():assert sha(ROOT/p)==h,p

def owned(s):
 lease=read(LEASE);assert reservations.owns(lease)and lease['resources']==s['resources'];unchanged(s)
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for r in s['contract']['completeReceiptPaths']:
   q=read(ROOT/r);assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(q['jobId'],)).fetchone()==('complete',q)
 patch,account=adapter.construct(s['basepatch'],s['saved']['account'],s['parent'],s['mask']);actual=account['wholeAlteredDomainAllActualAndUnusedBounds'];oldbounds=s['saved']['account']['wholeAlteredDomainAllPackedAndUnusedGridBounds']
 assert all(actual[0][k]>=oldbounds[0][k]and actual[1][k]<=oldbounds[1][k]for k in [0,2]),'new extent requires complete affected-form census'
 account['whole6650ActualNativeDomainNomination']=adapter.nominate_current_natives(actual,s['native']);account['all1238FormsAnd117AffectedVerbatim']=read(D/'actual-basic-extent-account.json.gz');account['all19RolesAndStation34ForeignObligationsVerbatim']=s['saved']['stationForeignAnd34FacetsVerbatim'];account['all46FormsVerbatim']=s['saved']['all46FormsVerbatim'];account['threeUnsafeFormRestorationsNotProposed']=True
 candidate=LOCAL/'private-terrain.json';save(candidate,patch);save(LOCAL/'private-terrain-before-runtime.json',patch)
 save(DOC/'full-account-before-runtime.json.gz',dict(account=account,fullOriginalInventoryVerbatim=s['saved']['fullOriginalInventoryVerbatim'],inputHashes=s['pins'],candidatePath=str(candidate.relative_to(ROOT)),candidateSHA256=sha(candidate),runtimeCompleted=False,currentAcceptance=False,physicalAccepted=False))
 try:
  if account['triangleBudgetPass']:
   account['completeClosedMaskPackedCoverageDiagnostic']=adapter.projection_coverage_context(patch,account,s['mask']);envelopes=adapter.interface_runtime_probes(np_triangles(patch),account['completeNewInterfaceEdgeInventory']);save(DOC/'complete-interface-max-envelopes.json.gz',envelopes)
   runtime=dict(schema='southside-certified-width-private-runtime-v1',candidate=dict(path=str((LOCAL/'private-terrain-before-runtime.json').relative_to(ROOT)),sha256=sha(LOCAL/'private-terrain-before-runtime.json')),currentManifestSHA256=CURRENT,parentTerrainSHA256=sha(ROOT/'3d-viewer/city/data/terrain.json'),currentTerrainEntries=s['manifest']['terrainPatches'],inputHashes={p:h for p,h in s['pins'].items()if p.startswith('3d-viewer/')or p.endswith('.mjs')or '/vendor/'in p},probes=envelopes['runtimeProbes'],currentAcceptance=False);save(DOC/'runtime-input.json.gz',runtime)
   call_runtime([str(HERE/'xl-southside-selective13-certified-width-runtime-draft-v1-20261013.mjs'),str(DOC.relative_to(ROOT))+'/'],DOC/'actual-interface-max-runtime.log');account['actualProductionMAXRayReport']=read(DOC/'actual-interface-max-ray-report.json')
   bounds=[actual[0][0],actual[0][2],actual[1][0],actual[1][2]];_,_,_,excess=overlap.projected_context(patch,bounds);account['floatingProjectedExcessMeasurementM2']=excess
   account['projectedOverlapMeasurementIsNotApproval']=True
   account['overlapMetadataRequiresSeparateROOTReviewOfActualGeometry']=True
   account['completeMeasuredGeometryPath']=str((LOCAL/'private-terrain-before-runtime.json').relative_to(ROOT));account['completeMeasuredGeometrySHA256']=sha(LOCAL/'private-terrain-before-runtime.json')
   assert 'sourceOverlap'not in patch['nativeMesh']
   validator=module('reviewed_unchanged_terrain_validator',HERE/'resolve-pass-indexed-parent-clipping.py')
   try:validator.validate_patch(patch,s['parent']);account['ordinaryPatchValidatorDiagnostic']=dict(passed=True)
   except(AssertionError,ValueError)as e:account['ordinaryPatchValidatorDiagnostic']=dict(passed=False,errorType=type(e).__name__,message=str(e),originalGuardUnchanged=True)
   wanted={r['building']['uid']:r['building']for r in s['neighbour']['rows']};wanted.update({f['uid']:f for f in s['saved']['all46FormsVerbatim']});rows=[dict(building=f,existingNative=u in s['entries'],patchIndexes=[0])for u,f in sorted(wanted.items())];selection=dict(candidateIds=UIDS,rows=rows,patches=[dict(path=str(candidate.relative_to(ROOT)),sha256=sha(candidate),uids=UIDS)],inputHashes={p:h for p,h in s['pins'].items()if p.startswith('3d-viewer/')});save(DOC/'neighbour-inputs.json.gz',selection);call_runtime([str(HERE/'check-neighbours.mjs'),str(DOC.relative_to(ROOT))+'/'],DOC/'actual-neighbour-guard.log');account['whole117And46OrdinaryNeighbourGuards']=read(DOC/'neighbour-checks.json');account['neighbourGuardsPass']=all(not r['reasons']for r in account['whole117And46OrdinaryNeighbourGuards']['rows'])
  else:account['expensiveRuntimeSkippedBecauseRealBudgetFailure']=True
 except Exception as e:
  save(DOC/'actual-runtime-failure.json',dict(errorType=type(e).__name__,message=str(e),traceback=traceback.format_exc(),actualExitCode=e.returncode if isinstance(e,subprocess.CalledProcessError)else None,completedAccountPreserved=True,currentAcceptance=False));account['actualRuntimeFailure']=read(DOC/'actual-runtime-failure.json')
 save(DOC/'full-computed-candidate-and-account.json.gz',dict(account=account,fullOriginalInventoryVerbatim=s['saved']['fullOriginalInventoryVerbatim'],all19SourceRoleAndWholeModelQualificationPending=True,face3009Unqualified=True,facet11034Unqualified=True,all3484PriorFiveMetreFailuresVerbatim=s['mask']['all3484PriorFiveMetreNegativesVerbatim'],inputHashes=s['pins'],candidatePath=str(candidate.relative_to(ROOT)),candidateSHA256=sha(candidate),currentAcceptance=False,physicalAccepted=False,installationApproved=False));unchanged(s);assert reservations.owns(lease)
 refs=s['refs']+[p for folder in [DOC,LOCAL]for p in folder.rglob('*')if p.is_file()and p.name!='reservation.json'];freezer=module('reviewed_source_context_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');q=freezer.freeze(BATCH,'private-selective13-certified-width-parent-restoration-proposal',refs,dict(uids=UIDS,completeOriginalInventoryFacets=774477,allSourceFaceSlots=51560,originalRestorationForms=13,outputFacets=account['outputFacets'],triangleBudget=25000,triangleBudgetPass=account['triangleBudgetPass'],exactWidthM=str(account['exactCertifiedUniformWidthM']),nativeActors=6650,noSourceDecode=True,noBuildingGeometryChanges=True,currentAcceptance=False,physicalAccepted=False,newlyInstalled=0));print(json.dumps(dict(jobId=q['jobId'],outputFacets=account['outputFacets'],triangleBudgetPass=account['triangleBudgetPass'],currentAcceptance=False)),flush=True)
def np_triangles(patch):
 import numpy as np
 p=np.asarray(patch['nativeMesh']['position'],dtype='<f4').astype('<f8').reshape(-1,3);return p[np.asarray(patch['nativeMesh']['index'],dtype=np.int64).reshape(-1,3)]
def call_runtime(args,log):
 q=subprocess.run(['node',*args],cwd=ROOT,capture_output=True,text=True);log.write_text(q.stdout+q.stderr)
 if q.returncode:raise subprocess.CalledProcessError(q.returncode,q.args,output=q.stdout,stderr=q.stderr)
def main():
 s=preflight()
 if '--preflight-only'in sys.argv:print(json.dumps(dict(resources=124,affectedForms=117,protectedForms=46,allScannedForms=1238,currentNatives=6650,sourceInventoryFacets=774477,savedCandidateFacets=24580,maskOnlyPriorProof=True,noDB=True,noLease=True,noConstruction=True,currentAcceptance=False)),flush=True);return
 if '--owned'in sys.argv:return owned(s)
 assert not LOCAL.exists();q=reservations.claim('southside-certified-width-private-'+str(uuid.uuid4()),s['resources'],batch=BATCH,ttl=3600);assert q['ok'];save(LEASE,json.loads(json.dumps(q['reservation'],default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,str(Path(__file__)),'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
