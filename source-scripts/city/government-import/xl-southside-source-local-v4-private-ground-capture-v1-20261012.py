"""UNEXECUTED candidate-ground capture + unchanged ordinary neighbour guards.
No terrain construction, source decode, role approval or live mutation.
"""
import importlib.util,json,subprocess,sys,traceback,uuid,types
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
import southside_actual_basic_extent_gate_v2_20261012 as extent
BASE=ROOT/'docs/astra-city/government-import'
DRAFT=BASE/'government-xl-southside-private-authentic-terrain-draft-v2-20261012/candidate-ground-qualification-draft-v1'
INPUT=BASE/'government-xl-southside-315025-300867-current-actual-ground-capture-v1-20261012'
PROPOSAL=BASE/'government-xl-southside-315025-300867-source-local-private-terrain-diagnostic-v4-20261012'
EXTENT=DRAFT.parent;NATIVE=BASE/'government-xl-complete-current-native-actual-position-matrix-bounds-v4-20261012'
BATCH='government-xl-southside-source-local-v4-private-ground-capture-v1-20261012';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
JS=HERE/'xl-southside-source-local-v4-private-ground-capture-v1-20261012.mjs';UIDS=['landsd/315025:0','landsd/300867:0'];CURRENT='2dde0cfc3c0869963c185c3398e48a1928c76802b2efa6c2d9713183a6ad5540'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def module(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def preflight():
 manifest=ROOT/'3d-viewer/city/data/manifest.json';before=manifest.read_bytes();assert digest(before)==CURRENT
 receipts=[read(PROPOSAL/'result.json'),read(INPUT/'result.json'),read(NATIVE/'result.json')]
 assert receipts[0]['jobId']=='4e1c5edcc40e59f857f762719b3a6a2561a822099b71bd05e0e0a276ab444edd'and len(receipts[0]['evidenceRefs'])==8164
 assert receipts[1]['jobId']=='3aa11a60f740759f78677d151fa2f9c34f494d935b7a208958164e23273f84d9'
 refs=[Path(__file__),JS,DRAFT/'METHOD.md',HERE/'southside_actual_basic_extent_gate_v2_20261012.py',HERE/'test_southside_actual_basic_extent_gate_v2_20261012.py',HERE/'check-neighbours.mjs',HERE/'check-native-neighbours.mjs',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py']
 refs.extend(HERE.parent/'shared-modelling'/n for n in ['db.py','jobs.py','reservations.py']);refs.extend([PROPOSAL/'result.json',INPUT/'result.json',NATIVE/'result.json'])
 for q in receipts:
  assert not q.get('currentAcceptance',False)and not q.get('physicalAccepted',False)
  for p in q['evidenceRefs']:assert ref(ROOT/p['path'])==p;refs.append(ROOT/p['path'])
 saved=read(PROPOSAL/'saved-source-local-construction-account.json.gz');account=saved['account'];candidate=ROOT/saved['privateCandidatePath'];assert ref(candidate)['sha256']=='d493c3bb9e60a076fc5c1df2a1f801dc695bcb48696f8a08d56e7be466448642'
 assert account['outputFacets']==24580 and account['triangleBudget']==25000 and account['triangleBudgetPass']is True and account['ordinaryPatchValidatorDiagnostic']['passed']is True
 assert account['realOutputFacetsCollapsedByFloat32']==[17783]and account['whole6649NativeDomainNomination']['nominated']==[]
 source=read(INPUT/'capture-inputs.json.gz');worlds=read(INPUT/'complete-two-actor-four-stream-ground-inputs.json.gz')['rows'];assert set(worlds)==set(UIDS)and len(source['completeCurrentForms'])==46 and source['manifestSHA256']==CURRENT
 captures={u:read(INPUT/('complete-current-actual-source-and-ground-'+u.split('/')[1].replace(':','-')+'.json.gz'))for u in UIDS}
 construction=module('southside_capture_existing_position_binding',HERE/'southside_saved_local_core_parent_adapter_v3_20261012.py');assert construction.bind_positions(worlds,captures)
 loader=captures[UIDS[0]]['completeRecursiveLoaderModuleClosure'];terrain=captures[UIDS[0]]['completeRecursiveTerrainModuleClosure']
 for c in captures.values():assert c['completeRecursiveLoaderModuleClosure']==loader and c['completeRecursiveTerrainModuleClosure']==terrain and c['completeCurrentCatalogueRefs']==source['completeCurrentCatalogueRefs']and c['completeCurrentForms']==source['completeCurrentForms']
 for q in source['rows']:
  assert q['candidate']['entry']==captures[q['uid']]['entry']and q['sourceSHA256']==captures[q['uid']]['sourceSHA256']==digest((ROOT/q['candidate']['path']).read_bytes())
  assert q['source']['building']==next(f for f in source['completeCurrentForms']if f['uid']==q['uid'])
 ei=read(EXTENT/'actual-basic-extent-input.json.gz');ep=read(EXTENT/'actual-basic-extent-proof.json.gz');ea=read(EXTENT/'actual-basic-extent-account.json.gz');forms={f['uid']:f for f in ei['forms']};assert len(forms)==1238
 rechecked=extent.validate(ep,forms,ei['complete6649NativeNomination'],ei['domainBounds'],digest((EXTENT/'actual-basic-extent-input.json.gz').read_bytes()));assert rechecked==ea['account']and len(rechecked['affectedUIDs'])==117
 resources=ea['actualResources'];assert len(resources)==124 and len(set(resources))==124 and set(source['canonicalResources'])<=set(resources)
 for raw in [source,ep,ei,*captures.values()]:
  for p,h in raw['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 for cl in [loader,terrain,ep['recursiveProductionModuleClosure']]:
  assert cl['schema']=='exact-literal-static-dynamic-resource-closure-v1'and cl['computedImportsRejected']and cl['unsupportedDynamicImports']==0
  for p,h in cl['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 prior=read(BASE/'government-xl-southside-315025-300867-private-authentic-terrain-diagnostic-v3-20261012/source-terrain-inventory-and-proposal-account.json.gz');assert prior['parentChildIntersections']==[]
 ownbounds=[c['completeOriginalPOSITIONProof']['originalWholeSourceBounds']for c in captures.values()]
 ownbounds.extend(b for c in captures.values()for b in c['completeWholeUnusedVertexBounds']);affected=[forms[u]for u in rechecked['affectedUIDs']]
 boxes=ownbounds+[b for q in ep['rows']if q['uid']in rechecked['affectedUIDs']and q['classification']=='actual-production-BASIC'for b in(q['boundsByArithmetic']or{}).values()]+[account['wholeAlteredDomainAllPackedAndUnusedGridBounds']]
 region=[min(b[0][0]for b in boxes)-2,min(b[0][2]for b in boxes)-2,max(b[1][0]for b in boxes)+2,max(b[1][2]for b in boxes)+2]
 refs.extend([EXTENT/'actual-basic-extent-input.json.gz',EXTENT/'actual-basic-extent-proof.json.gz',EXTENT/'actual-basic-extent-account.json.gz',PROPOSAL/'saved-source-local-construction-account.json.gz',candidate])
 freezer=module('southside_candidate_ground_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py')
 # Full transitive local modules, including imported constructor/guard helpers.
 for m in list(sys.modules.values())+[freezer,construction]:
  p=Path(getattr(m,'__file__','')or'/').resolve()
  if ROOT in p.parents and p.is_file():refs.append(p)
 pins={str(p.relative_to(ROOT)):digest(p.read_bytes())for p in sorted(set(refs))}
 assert manifest.read_bytes()==before
 return dict(receipts=receipts,refs=sorted(set(refs)),pins=pins,before=before,source=source,captures=captures,worlds=worlds,ep=ep,ei=ei,ea=ea,affected=affected,resources=resources,region=region,candidate=candidate,account=account,loader=loader,terrain=terrain,parentIntersections=prior['parentChildIntersections'])

def owned(s):
 lease=read(LEASE);assert lease['resources']==s['resources']and reservations.owns(lease)and not DOC.exists()
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for q in s['receipts']:assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(q['jobId'],)).fetchone()==('complete',q)
 DOC.mkdir();save(DOC/'input.json.gz',dict(schema='southside-source-local-v4-two-scene-ground-input-v1',currentManifestSHA256=CURRENT,parentTerrainSHA256=digest((ROOT/'3d-viewer/city/data/terrain.json').read_bytes()),candidate=ref(s['candidate']),affectedCurrentForms=s['affected'],protectedOriginalForms=s['source']['completeCurrentForms'],completeCurrentCatalogueRefs=s['source']['completeCurrentCatalogueRefs'],completeGroundCaptureRegion=s['region'],exactPriorLoaderModuleClosure=s['loader'],exactPriorTerrainModuleClosure=s['terrain'],exactPriorBASICModuleClosure=s['ep']['recursiveProductionModuleClosure'],parentChildIntersections=s['parentIntersections'],inputHashes=s['pins'],currentAcceptance=False))
 def call(args,name):
  p=subprocess.run(args,cwd=ROOT,capture_output=True,text=True);save(DOC/(name+'.json'),dict(exitCode=p.returncode,stdout=p.stdout,stderr=p.stderr));assert p.returncode==0,(name,p.stderr);assert reservations.owns(lease)
  for path,h in s['pins'].items():assert digest((ROOT/path).read_bytes())==h
 try:
  call(['node',str(JS)],'actual-ground-export-log')
  actual=read(DOC/'production-two-scene-ground.json.gz');assert actual['startAndEndInputsVerified']and actual['allCandidateFacetsRetainedIncluding17783']and actual['currentNativeActors']==6649
  for label in ['baseline','privateCandidate']:
   q=actual[label];a=np.asarray(q['completeRegionalPosition'],dtype='<f8').reshape(-1,3,3);assert len(a)==q['completeRegionalFaces']and len(q['completeRegionalFacetOrigins'])==len(a)and digest(a.tobytes())==q['worldTriangleSHA256']and np.isfinite(a).all()
  forms={f['uid']:f for f in s['affected']+s['source']['completeCurrentForms']};native=set(q['uid']for url in read(ROOT/'3d-viewer/city/data/manifest.json')['officialModelCatalogues']for q in read(ROOT/'3d-viewer'/url)['models']);assert len(native)==6649
  patch=dict(**ref(s['candidate']),uids=UIDS,triangles=24580,bounds=s['region'])
  save(DOC/'neighbour-inputs.json.gz',dict(rows=[dict(building=f,patchIndexes=[0],existingNative=u in native)for u,f in sorted(forms.items())],inputHashes=s['pins'],candidateIds=UIDS,patches=[patch]))
  call(['node',str(HERE/'check-neighbours.mjs'),str(DOC.relative_to(ROOT))+'/'],'unchanged-neighbour-guard-log')
  neighbours=read(DOC/'neighbour-checks.json');assert {q['uid']for q in neighbours['rows']}==set(forms)
  save(DOC/'capture-and-neighbour-summary.json',dict(uids=UIDS,currentManifestSHA256=CURRENT,proposalReceipt=s['receipts'][0]['jobId'],currentSourceCaptureReceipt=s['receipts'][1]['jobId'],wholeCurrentNativeReceipt=s['receipts'][2]['jobId'],ownedCompleteFaceModeSlots=51560,all117AffectedFormsRetained=True,all46ProtectedOriginalFormsRetained=True,all1238ExactExtentAccountVerbatim=s['ea'],complete6649NativeAlteredDomainNominationVerbatim=s['account']['whole6649NativeDomainNomination'],rawNeighbourReasons=[q for q in neighbours['rows']if q['reasons']],collapse17783Verbatim=s['account']['completeOutputFacetLineage'][17783],stationForeignOverlapAnd34FacesVerbatim=read(INPUT/'historical-obligations-verbatim.json'),all19SourceRolesRemainUnqualified=True,actualFourStreamCandidateFiniteAndSupportPending=True,noSourceGeometryChanges=True,noLiveTerrainChanges=True,privateTerrainProposalChanged=True,currentAcceptance=False,physicalAccepted=False,installationApproved=False))
 except BaseException as e:
  save(DOC/'failure.json',dict(error=str(e),traceback=traceback.format_exc(),currentAcceptance=False,physicalAccepted=False));raise
 assert reservations.owns(lease)and(ROOT/'3d-viewer/city/data/manifest.json').read_bytes()==s['before']
 for path,h in s['pins'].items():assert digest((ROOT/path).read_bytes())==h
 refs=s['refs']+[p for p in DOC.rglob('*')if p.is_file()]+[p for p in LOCAL.rglob('*')if p.is_file()and p.name!='reservation.json']
 freezer=module('southside_private_ground_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');out=freezer.freeze(BATCH,'southside-source-local-v4-actual-candidate-ground-ordinary-neighbour-no-acceptance',refs,dict(uids=UIDS,sourceFaces=12890,ownedFourStreamFaceSlots=51560,affectedForms=117,protectedOriginalForms=46,currentAcceptance=False,physicalAccepted=False))
 print(json.dumps(dict(jobId=out['jobId'],currentAcceptance=False)),flush=True)
def main():
 s=preflight()
 if '--preflight-only'in sys.argv:print(json.dumps(dict(noDB=True,noLease=True,noConstruction=True,noProductionJSImported=True,canonicalResources=len(s['resources']),affectedForms=117,protectedForms=46,completeScannedForms=1238,groundRegion=s['region'],currentAcceptance=False)));return
 if '--owned'in sys.argv:return owned(s)
 assert not DOC.exists()and not LOCAL.exists();claim=reservations.claim('southside-private-ground-v4-'+str(uuid.uuid4()),s['resources'],batch=BATCH,ttl=3600);assert claim['ok'];save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)))
 subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,str(Path(__file__)),'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
