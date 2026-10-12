"""UNEXECUTED acquisition-only local terrain proposal from saved exact lineage."""
import importlib.util,json,subprocess,sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect,reservations
import southside_saved_local_core_parent_adapter_v1_20261012 as adapter
import native_patch_resolution as overlap
BASE=ROOT/'docs/astra-city/government-import'
DRAFT=BASE/'government-xl-southside-private-authentic-terrain-draft-v2-20261012'
PLAN=DRAFT/'source-local-acquisition-repair-draft-v1'
BATCH='government-xl-southside-315025-300867-source-local-private-terrain-diagnostic-v1-20261012'
DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
PRIOR=BASE/'government-xl-southside-315025-300867-private-authentic-terrain-diagnostic-v3-20261012'
INPUT=BASE/'government-xl-southside-315025-300867-current-actual-ground-capture-v1-20261012'
AUTH=BASE/'government-xl-southside-315025-300867-unfiltered-original-sheets-comparison-v2-20261012'
NATIVE=BASE/'government-xl-complete-current-native-actual-position-matrix-bounds-v4-20261012'
CURRENT='2dde0cfc3c0869963c185c3398e48a1928c76802b2efa6c2d9713183a6ad5540'
UIDS=['landsd/315025:0','landsd/300867:0']
def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def code_files():
 return [Path(__file__),HERE/'southside_saved_local_core_parent_adapter_v1_20261012.py',HERE/'test_southside_saved_local_core_parent_adapter_v1_20261012.py',HERE/'southside_exact_private_terrain_adapter_v1_20261012.py',HERE/'native_patch_resolution.py',HERE/'native_overlap_actual_ray_readonly_20261010.mjs',PLAN/'METHOD.md',PLAN/'input-contract.json']
def preflight():
 assert not DOC.exists()and not(LOCAL/'private-terrain.json').exists()
 contract=read(PLAN/'input-contract.json');refs=code_files();receipts=[]
 assert contract['schema']=='southside-saved-local-core-acquisition-input-v1'and contract['currentManifestSHA256']==CURRENT
 for pin in contract['pins']:
  p=ROOT/pin['path'];assert digest(p.read_bytes())==pin['sha256'];refs.append(p)
 for pin in contract['completeReceipts']:
  p=ROOT/pin['path'];assert digest(p.read_bytes())==pin['sha256'];q=read(p);assert q['jobId']==pin['jobId'];refs.append(p);receipts.append(q)
  for r in q['evidenceRefs']:
   f=ROOT/r['path'];assert digest(f.read_bytes())==r['sha256'];refs.append(f)
 prior=read(PRIOR/'result.json');assert prior['jobId']=='1be4acb6a5e52787ecc57dd7806df25dc4d5281fa6e94b6858a5ea2c14b2cfae'
 saved=read(PRIOR/'source-terrain-inventory-and-proposal-account.json.gz');account=saved['account']
 assert account['completeInputFacets']==774477 and account['triangleBudget']==25000 and account['triangleBudgetPass']is False
 assert len(account['completeOutputFacetLineage'])==78016 and [q['outputFacet']for q in account['completeOutputFacetLineage']]==list(range(78016))
 assert len(account['allOutsideAlteredDomainOriginalFacetIds'])+len(account['completeSelectedOriginalFacetAccounts'])==774477
 assert set(account['allOutsideAlteredDomainOriginalFacetIds'])|{q['globalOriginalFacetId']for q in account['completeSelectedOriginalFacetAccounts']}==set(range(774477))
 old=read(ROOT/account['privateCandidatePath']);assert digest((ROOT/account['privateCandidatePath']).read_bytes())==account['privateCandidateSHA256']
 worlds=read(INPUT/'complete-two-actor-four-stream-ground-inputs.json.gz');assert set(worlds)==set(UIDS)
 captures={u:read(INPUT/('complete-current-actual-source-and-ground-'+u.split('/')[1].replace(':','-')+'.json.gz'))for u in UIDS}
 assert adapter.bind_positions(worlds,captures)and sum(c['completeFaces']for c in captures.values())*4==51560
 source_inputs=read(INPUT/'capture-inputs.json.gz');assert source_inputs['manifestSHA256']==CURRENT and len(source_inputs['completeCurrentForms'])==46
 assert saved['all46FormsVerbatim']==source_inputs['completeCurrentForms']and saved['stationForeignOverlapAnd34FacetsVerbatim']==read(INPUT/'historical-obligations-verbatim.json')
 extent=read(DRAFT/'actual-basic-extent-account.json.gz');resources=extent['actualResources'];assert len(resources)==124 and len(set(resources))==124 and extent['all46OriginalProtectiveResourcesRetained']is True
 assert extent['all1238FormsRetained']is True and extent['account']['completeScannedForms']==1238 and len(extent['account']['affectedUIDs'])==117 and len(extent['account']['completeExclusionRecords'])==1121
 assert set(source_inputs['canonicalResources'])<=set(resources)
 assert saved['parentChildIntersections']==[]and saved['complete6649NativeNomination']['nominated']==[]
 parent=read(ROOT/'3d-viewer/city/data/terrain.json');assert digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes())==CURRENT
 native=read(NATIVE/'inventory.json.gz');assert native['completeNativeActors']==native['successfullyCapturedActors']==6649 and not native['errors']
 assert all(not Path('/proc',str(pid)).exists()for pid in [4139705,4146273,4146343,119538,119531])
 refs.extend([DRAFT/'immutable-source-local-tests-v1/validation.json',DRAFT/'immutable-source-local-tests-v1/tests.log'])
 v=read(refs[-2]);assert v['tests']==22 and v['passed']is True and v['exitCode']==0 and digest(refs[-1].read_bytes())==v['testLogSHA256']
 assert v['codePins']==[dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))for p in code_files()]
 pins={str(p.relative_to(ROOT)):digest(p.read_bytes())for p in sorted(set(refs))}
 return dict(receipts=receipts,refs=sorted(set(refs)),pins=pins,saved=saved,account=account,old=old,worlds=worlds,captures=captures,parent=parent,native=native,resources=resources,contract=contract)
def owned(s):
 lease=read(LEASE);assert reservations.owns(lease)and lease['resources']==s['resources']
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for q in s['receipts']:assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(q['jobId'],)).fetchone()==('complete',q)
  old=c.execute('SELECT released_at,resources FROM astra_modelling.reservation_groups WHERE token=%s',('b0b13f7b-914b-4690-a923-3c7b6f84956c',)).fetchone();assert old[0]is not None and sorted(old[1])==s['resources']
 patch,account=adapter.construction(s['account'],s['parent'],s['old'],s['worlds'],s['captures'])
 assert account['mask']['completeSourceFaceSlots']==51560 and account['triangleBudget']==25000
 patch['meta'].update(parentTerrain='city/data/terrain.json',parentSha256=digest((ROOT/'3d-viewer/city/data/terrain.json').read_bytes()))
 patch['meta']['source']=dict(originalInventoryVerbatim=s['saved']['fullOriginalInventoryVerbatim'],sourceInventoryFacets=774477,sourceInventorySHA256=s['account']['completeInputSHA256'],verticalDatum='HKPD',policy='Saved exact original terrain fragments, source-local closed-cell core and changed collar, parent exterior; no source-building geometry changes.')
 actual=account['wholeAlteredDomainAllPackedAndUnusedGridBounds'];previous=s['saved']['wholeAlteredDomainProposedPackedBounds']
 assert actual[0][0]>=previous[0][0]and actual[0][2]>=previous[0][2]and actual[1][0]<=previous[1][0]and actual[1][2]<=previous[1][2]
 account['whole6649NativeDomainNomination']=adapter.old.nominate_natives(actual,s['native']);assert not account['whole6649NativeDomainNomination']['nominated']
 account['all1238OriginalFormsAnd117ActualAffectedRetainedVerbatim']=read(DRAFT/'actual-basic-extent-account.json.gz')
 candidate=LOCAL/'private-terrain.json';save(candidate,patch)
 # Existing explicit highest-native-surface evidence. Retain every layer;
 # its bounded representative samples do not claim whole-domain agreement.
 bounds=[actual[0][0],actual[0][2],actual[1][0],actual[1][2]]
 _,_,_,excess=overlap.projected_context(patch,bounds);account['floatingProjectedExcessMeasurementM2']=excess
 if excess>0:
  audit_path=DOC/'highest-native-surface-evidence.json'
  sources=[dict(path=str((PRIOR/'source-terrain-inventory-and-proposal-account.json.gz').relative_to(ROOT)),sha256=digest((PRIOR/'source-terrain-inventory-and-proposal-account.json.gz').read_bytes()))]
  sources.extend(dict(path=q['sourceGltfPath'],sha256=q['sourceGltfSHA256'])for q in s['saved']['fullOriginalInventoryVerbatim'])
  audit=overlap.approve_original_overlap(patch,candidate,audit_path,sources);patch['nativeMesh']['sourceOverlap']['evidencePath']=str(audit_path.relative_to(ROOT))
  save(candidate,patch)
  ray=subprocess.run(['node',str(HERE/'native_overlap_actual_ray_readonly_20261010.mjs'),str(candidate),str(audit_path)],cwd=ROOT,capture_output=True,text=True)
  (DOC/'actual-highest-surface-ray.log').write_text(ray.stdout+ray.stderr);assert ray.returncode==0
  audit['actualProductionFloat32SamplerAndDoubleSideRay']=json.loads(ray.stdout);audit['wholeFiniteSeamAndCoverageProof']=False;audit['currentAcceptance']=False;audit_path.write_text(json.dumps(audit,sort_keys=True,separators=(',',':'))+'\n')
  overlap.finalize_overlap_evidence(patch,audit_path);save(candidate,patch)
  account['explicitHighestNativeSurfaceEvidence']=dict(path=str(audit_path.relative_to(ROOT)),sha256=digest(audit_path.read_bytes()),samples=audit['float32HighestRayAgreement']['samples'],wholeDomainAgreementClaim=False,sourceLayersRemoved=0)
 validator=module('southside_source_local_unchanged_validator',HERE/'resolve-pass-indexed-parent-clipping.py')
 try:validator.validate_patch(patch,s['parent']);account['ordinaryPatchValidatorDiagnostic']=dict(passed=True,physicalAccepted=False)
 except(AssertionError,ValueError)as e:account['ordinaryPatchValidatorDiagnostic']=dict(passed=False,errorType=type(e).__name__,message=str(e),originalGuardUnchanged=True,physicalAccepted=False)
 save(DOC/'saved-source-local-construction-account.json.gz',dict(account=account,fullOriginalInventoryVerbatim=s['saved']['fullOriginalInventoryVerbatim'],prior78016OutputLineageBound=True,stationForeignAnd34FacetsVerbatim=s['saved']['stationForeignOverlapAnd34FacetsVerbatim'],all46FormsVerbatim=s['saved']['all46FormsVerbatim'],all19RoleAndWholeModelQualificationPending=True,face3009Unqualified=True,facet11034Unqualified=True,currentAcceptance=False,physicalAccepted=False,installationApproved=False,privateCandidatePath=str(candidate.relative_to(ROOT)),privateCandidateSHA256=digest(candidate.read_bytes())))
 assert reservations.owns(lease)and digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes())==CURRENT
 for path,sha in s['pins'].items():assert digest((ROOT/path).read_bytes())==sha
 refs=s['refs']+[p for folder in [DOC,LOCAL]for p in folder.rglob('*')if p.is_file()and p.name!='reservation.json']
 previous=module('southside_existing_source_module_inventory',HERE/'xl-southside-315025-300867-source-role-reconciliation-v1-20261012.py')
 freezer=module('southside_existing_source_local_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');refs.extend(previous.local_modules(freezer));refs.extend([Path(validator.__file__),Path(previous.__file__)])
 q=freezer.freeze(BATCH,'source-local-original-layer-parent-terrain-proposal-not-accepted',refs,dict(uids=UIDS,completeInputFacets=774477,completeSourceFaceSlots=51560,outputFacets=account['outputFacets'],triangleBudget=25000,triangleBudgetPass=account['triangleBudgetPass'],privateTerrainProposalExplicitlyChanged=True,liveTerrainChanges=0,currentAcceptance=False,physicalAccepted=False,newlyInstalled=0));print(json.dumps(dict(jobId=q['jobId'],outputFacets=account['outputFacets'],triangleBudgetPass=account['triangleBudgetPass'],currentAcceptance=False)),flush=True)
def main():
 s=preflight()
 if '--preflight-only'in sys.argv:print(json.dumps(dict(resources=len(s['resources']),sourceSlots=51560,savedLineage=78016,fullSourceInventory=774477,noSourceDecode=True,noDB=True,noLease=True,noTerrainConstruction=True,currentAcceptance=False)),flush=True);return
 if '--owned'in sys.argv:return owned(s)
 assert not LOCAL.exists();claim=reservations.claim('southside-source-local-private-'+str(uuid.uuid4()),s['resources'],batch=BATCH,ttl=3600);assert claim['ok'];save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)))
 subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,str(Path(__file__)),'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
