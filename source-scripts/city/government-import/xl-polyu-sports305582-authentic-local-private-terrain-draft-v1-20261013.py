"""UNEXECUTED private original-terrain proposal; no source replay or acceptance."""
import importlib.util,json,subprocess,sys,types,uuid,traceback,base64
from pathlib import Path
from fractions import Fraction as F
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
import polyu_sports_authentic_local_core_parent_draft_v1_20261013 as adapter
from southside_selective13_certified_width_parent_restoration_draft_v2_20261013 import nominate_current_natives,interface_runtime_probes
B=ROOT/'docs/astra-city/government-import';D=B/'government-xl-polyu-sports305582-authentic-local-private-terrain-draft-v1-20261013';FEAS=B/'government-xl-polyu-sports305582-authentic-terrain-feasibility-draft-v2-20261013/calculation-v1/feasibility.json.gz';CAP=B/'government-xl-polyu-sports305582-current-four-world-ground-capture-v1-20261013';NAM=B/'government-xl-complete-native-actual-position-post-nam-delta-v1-20261013'
BATCH='government-xl-polyu-sports305582-authentic-local-private-terrain-v1-20261013';DOC=B/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json';UID='landsd/305582:0';P='landsd/305793:0';CURRENT='c00fd9f731b1bcbf4d2df6067a5cb3231f0eaa8c503a8adea584fec39bf73bf7';SOURCE='ac9df2e1b9b66b9c120a8638881b5f44fb966f7463b8874c27b040b91d37df15'
sha=lambda p:digest(p.read_bytes())
def canonical(q):return digest(json.dumps(q,sort_keys=True,separators=(',',':')).encode())
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def preflight(require_basic=False,require_tests=False):
 assert not DOC.exists()and not(LOCAL/'private-terrain.json').exists();c=read(D/'input-contract.json');assert c['schema']=='polyu-original-local-terrain-input-v1'and c['sourceSHA256']==SOURCE and c['currentManifestSHA256']==CURRENT
 pins={r['path']:r['sha256']for r in c['filePins']};pins.update({str(p.relative_to(ROOT)):sha(p)for p in [Path(__file__),D/'input-contract.json',D/'METHOD.md',D/'review-file-pins.json']})
 for r in read(D/'review-file-pins.json')['filePins']:assert sha(ROOT/r['path'])==r['sha256'];pins[r['path']]=r['sha256']
 for p,h in pins.items():assert sha(ROOT/p)==h,p
 assert sha(ROOT/'3d-viewer/city/data/manifest.json')==CURRENT
 f=read(FEAS);data=read(CAP/'complete-sports-four-stream-current-ground-inputs.json.gz');cap=read(CAP/'complete-current-actual-source-and-ground-305582-0.json.gz');inputs=read(CAP/'capture-inputs.json.gz')
 assert f['uid']==data['uid']==UID and data['sourceSHA256']==SOURCE and f['currentAcceptance']is False
 assert len(data['completeWorldStreams'])==4 and all(len(q['completeWorldTriangles'])==q['completeFaces']==10536 for q in data['completeWorldStreams'].values())
 assert len(data['completeOriginalTopologyVerbatim']['sharedEdgeConnectedComponents'])==21 and len(data['completeOriginalTopologyVerbatim']['exactNonrenderingOriginalFaces'])==4
 bounds=[cap['completeOriginalPOSITIONProof']['originalWholeSourceBounds'],*cap['completeWholeUnusedVertexBounds']];core=adapter.bounds_core(bounds);assert list(map(float,core))==f['sourceCoreClosedAABBFromWholeUnusedFourViews'];assert cap['completeOriginalPOSITIONProof']['allOriginalPositionVerticesAccounted']is True
 parent=read(ROOT/'3d-viewer/city/data/terrain.json');cells,domain,parent_proof=adapter.captured_parent_grid(parent,f['allCurrent12GroundFacetsVerbatim']);assert list(map(float,domain))==f['provisionalParentRoutingEnvelope'];active=adapter.expanded(core);assert domain[0]<=active[0]<active[2]<=domain[2]and domain[1]<=active[1]<active[3]<=domain[3]
 selected=np.asarray(f['allNominatedAuthenticTerrainFacets'],dtype='<f8');ids=f['conservativeClosedNominationOriginalTerrainIds'];assert selected.shape==(7690,3,3)and ids==sorted(set(ids))and len(ids)==7690 and all(type(i)is int and 0<=i<181089 for i in ids);assert digest(selected.tobytes())==c['selectedTerrainFloat64SHA256']
 assert f['allSource181089FacetsSHA256']==c['completeOriginal181089ProducerWorldSHA256']and f['allSourceSlopesVerticalsAndZerosRetainedWithoutHeightLayerDeletion']is True
 forms=[q['form']for q in f['fullCurrentProtectedForms']];assert len(forms)==len({q['uid']for q in forms})==25 and set(q['uid']for q in inputs['completeCurrentForms'])<=set(q['uid']for q in forms)
 manifest=read(ROOT/'3d-viewer/city/data/manifest.json');entries={}
 for url in manifest['officialModelCatalogues']:
  for e in read(ROOT/'3d-viewer'/url)['models']:assert e['uid']not in entries;entries[e['uid']]=e
 assert len(entries)==6650 and UID not in entries and {q['uid']for q in forms}&set(entries)=={P}
 assert entries[P]==inputs['installedPodiumDependency']['entry']==f['installedPodiumDependencyVerbatim']['entry']and entries[P]['publicationApproved']is False and 'landsd/305600:0'in entries[P]['suppressesBuildingUids']
 comp=read(NAM/'composition.json.gz');inp=read(NAM/'input.json.gz');binding=read(ROOT/comp['exactBaselineCurrentBinding']['path']);baseline=read(ROOT/comp['baselineInventory']['path']);delta=read(ROOT/comp['actualNewDelta']['path']);native=baseline['rows']+delta['rows'];assert comp['currentManifest']['sha256']==CURRENT and len(native)==len({q['uid']for q in native})==6650 and len(binding['rows'])==6649 and binding['exactAllSourceFormEntryLoaderTuples']is True
 by={q['uid']:q for q in native};current_forms={}
 needed={q['uid']for q in forms}|set(inp['currentAllNativeSourceForms'])
 for tile in manifest['tiles']:
  for q in read(ROOT/'3d-viewer'/tile['url'])['buildings']:
   if q['uid']in needed:assert q['uid']not in current_forms;current_forms[q['uid']]=q
 for q in forms:assert current_forms[q['uid']]==q
 for z in binding['rows']:
  u=z['uid'];assert canonical(by[u])==z['unchangedActualBoundsSHA256']and current_forms[u]==inp['currentAllNativeSourceForms'][u]and canonical(current_forms[u])==z['currentViewerFormSHA256']and canonical(entries[u])==z['currentRawEntrySHA256']and sha(ROOT/z['source']['path'])==z['source']['sha256']
 assert current_forms[delta['rows'][0]['uid']]==inp['currentAllNativeSourceForms'][delta['rows'][0]['uid']]
 assert by[P]==inputs['installedPodiumDependency']['actualPositionRecord'];assert by[P]['wholeUnusedPositionVerticesIncluded']is True and by[P]['sourceFacesOmitted']==0
 for p,h in inp['requiredUnchangedProductionClosure'].items():assert sha(ROOT/p)==h,p;pins[p]=h
 intersections=[]
 for e in manifest['terrainPatches']:
  path=ROOT/'3d-viewer'/e['url'];patch=read(path);pins[str(path.relative_to(ROOT))]=sha(path);bb=adapter.old.terrain_bounds(patch)
  if adapter.old.closed_xz_touch(domain,bb):intersections.append(dict(entry=e,completeActualAndUnusedGridDomain=bb,fullExistingPatchObligation=True))
 assert not intersections,'current-parent-child-closed-touch-requires-explicit-retention-before-construction'
 if require_tests:
  v=read(D/'immutable-boundary-tests-v1/validation.json');assert v['tests']==22 and v['exitCode']==0 and v['passed']is True and sha(D/'immutable-boundary-tests-v1/tests.log')==v['testLogSHA256'];assert v['codePins']==[dict(path=p,sha256=pins[p])for p in c['orderedTestCodePaths']];pins[str((D/'immutable-boundary-tests-v1/validation.json').relative_to(ROOT))]=sha(D/'immutable-boundary-tests-v1/validation.json');pins[str((D/'immutable-boundary-tests-v1/tests.log').relative_to(ROOT))]=sha(D/'immutable-boundary-tests-v1/tests.log')
 proof=None
 if require_basic:
  path=D/'actual-basic-protection-proof.json.gz';proof=read(path);assert proof['schema']=='polyu25-complete-actual-basic-protection-v1'and proof['startAndEndInputsVerified']is True and proof['completeScannedForms']==25 and len(proof['rows'])==25 and {q['uid']for q in proof['rows']}=={q['uid']for q in forms}
  assert proof['inputSHA256']==sha(D/'actual-basic-protection-input.json.gz');assert len([q for q in proof['rows']if q['classification']=='actual-production-BASIC'])==24
  for q in proof['rows']:
   assert q['currentForm']==current_forms[q['uid']]
   if q['uid']==P:assert q['classification']=='installed-native-scalar-bounds-whole-terrain-regression-pending'and q['completeCurrentNativeBoundsVerbatim']==by[P]and q['wholeNativeBeforeAfterTerrainRegressionProved']is False
   else:
    assert q['classification']=='actual-production-BASIC'and q['wholeUnusedPositionVerticesIncluded']is True
    if q['completePositionVertices']:
     for mode,key in [('actualLiteral','actualLiteralSHA256'),('explicitLeftAssociatedF32ModelMatrix','explicitLeftAssociatedF32SHA256'),('explicitBalancedF32ModelMatrix','explicitBalancedF32SHA256')]:
      raw=base64.b64decode(q['completeStreamBytesBase64'][mode]);assert digest(raw)==q[key]and len(raw)==q['completePositionVertices']*3*8
  for p,h in proof['inputHashes'].items():assert sha(ROOT/p)==h,p;pins[p]=h
  for p in [path,D/'actual-basic-protection-input.json.gz']:pins[str(p.relative_to(ROOT))]=sha(p)
 for m in list(sys.modules.values()):
  if isinstance(m,types.ModuleType)and getattr(m,'__file__',None):
   p=Path(m.__file__).resolve()
   if p.is_relative_to(ROOT)and p.is_file():pins[str(p.relative_to(ROOT))]=sha(p)
 resources=sorted({'building:'+q['uid']for q in forms}|{'terrain-parent:city/data/terrain.json','terrain-patch:'+UID,'immutable-source-sheet:11-NW-25C'});assert len(resources)==28
 return dict(contract=c,pins=pins,f=f,data=data,inputs=inputs,core=core,active=active,parent=parent,parents=f['allCurrent12GroundFacetsVerbatim'],cells=cells,domain=domain,parentProof=parent_proof,selected=selected,ids=ids,forms=forms,native=native,manifest=manifest,proof=proof,resources=resources)
def unchanged(s):
 assert sha(ROOT/'3d-viewer/city/data/manifest.json')==CURRENT
 for p,h in s['pins'].items():assert sha(ROOT/p)==h,p

def prepare(s):
 path=D/'actual-basic-protection-input.json.gz';assert not path.exists();save(path,dict(schema='polyu25-complete-basic-protection-input-v1',forms=s['forms'],domainBounds=list(map(float,s['domain'])),inputHashes=s['pins'],installedPodiumDependency=s['inputs']['installedPodiumDependency'],currentNativeBoundsRecord=next(q for q in s['native']if q['uid']==P),currentAcceptance=False,physicalAccepted=False));unchanged(s)
def owned(s):
 lease=read(LEASE);assert lease['resources']==s['resources']and reservations.owns(lease);unchanged(s)
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY')
  for path in s['contract']['completeReceiptPaths']:
   q=read(ROOT/path);assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(q['jobId'],)).fetchone()==('complete',q)
 output,account=adapter.construct(s['selected'],s['ids'],s['core'],s['parents'],expected_sha256=s['contract']['selectedTerrainFloat64SHA256'],declared_source_faces=181089)
 step,w,h,nodes,raw,display,vegetation=adapter.old.refined_parent_grid(s['parent'],s['cells'],s['domain']);patch=dict(id='government-native-polyu-sports305582-authentic-private-v1',w=w,h=h,cell=float(step),elev=raw,renderedElev=display,vegetation=vegetation,coarseCells=s['cells'],meta=dict(georef=dict(aE=float(step),aN=-float(step),bE=float(s['domain'][0])+834500,bN=816500-float(s['domain'][1]),W=w,H=h),parentTerrain='city/data/terrain.json',parentSha256=sha(ROOT/'3d-viewer/city/data/terrain.json'),targetUids=[UID]),nativeMesh=dict(position=[v for t in output for p in t for v in p],index=list(range(3*len(output))),source=dict(verticalDatum='HKPD',verticalScale=1,policy='Immutable original layered core, explicitly changed analytic5m vertex-interpolated collar, captured packed parent exterior; every acceptance gate remains pending.')))
 candidate=LOCAL/'private-terrain.json';save(candidate,patch);actual=adapter.old.bbox([*output,*[[[adapter.old.f32(v)for v in p]]*3 for p in nodes]]);account['wholeAlteredActualAndUnusedGridBounds']=actual;account['capturedParentGridReconstructionProof']=s['parentProof'];account['native6650ClosedDomainNomination']=nominate_current_natives(actual,s['native']);account['all25CompleteProductionBasicAndExplicitNativeInputsVerbatim']=s['proof'];account['all752FourModeRawNegativesAnd21BodiesVerbatim']=s['f']['rows'];account['installedPodiumFalseHoldVerbatim']=s['inputs']['installedPodiumDependency'];account['sourceBuildingPoseAndGeometryUnchanged']=True
 nominated=[];excluded=[]
 for q in s['proof']['rows']:
  if q['uid']==P:nominated.append(dict(uid=P,fullNative59527FourStreamBeforeAfterTerrainQualificationPending=True));continue
  if q['completePositionVertices']==0:excluded.append(dict(uid=q['uid'],completeOriginalProductionGeometryEmpty=True,noSupportCredit=True));continue
  gaps=[];touch=[]
  for mode,b in q['boundsByArithmetic'].items():
   proof=None
   for axis in [0,2]:
    if F(actual[1][axis])<F(b[0][axis]):proof=dict(axis=axis,exactGapM=str(F(b[0][axis])-F(actual[1][axis])));break
    if F(b[1][axis])<F(actual[0][axis]):proof=dict(axis=axis,exactGapM=str(F(actual[0][axis])-F(b[1][axis])));break
   if proof is None:touch.append(mode)
   else:gaps.append(dict(arithmetic=mode,**proof))
  if touch:nominated.append(dict(uid=q['uid'],touchingModes=touch,wholeActualMeshObligationPending=True))
  else:excluded.append(dict(uid=q['uid'],all4StrictDisjointActualUnusedBounds=gaps))
 account['complete25AffectedActualMeshNomination']=dict(nominated=nominated,excluded=excluded,formsAccounted=25,touchRetained=True)
 save(DOC/'full-candidate-and-account-before-runtime.json.gz',dict(account=account,candidatePath=str(candidate.relative_to(ROOT)),candidateSHA256=sha(candidate),inputHashes=s['pins'],currentAcceptance=False,physicalAccepted=False))
 try:
  if not account['triangleBudgetPass']:account['runtimeSkippedBecauseRealBudgetFailure']=True
  else:
   edges={}
   for tri in output:
    for a,b in zip(tri,tri[1:]+tri[:1]):edges.setdefault(tuple(sorted((tuple(a),tuple(b)))),dict(actualPackedEdge=[a,b]))
   probes=interface_runtime_probes(np.asarray(output,dtype='<f8'),list(edges.values()));save(DOC/'complete-packed-edge-max-envelopes.json.gz',probes)
   save(DOC/'runtime-input.json.gz',dict(schema='polyu-authentic-local-private-runtime-v1',candidate=dict(path=str(candidate.relative_to(ROOT)),sha256=sha(candidate)),currentManifestSHA256=CURRENT,parentTerrainSHA256=patch['meta']['parentSha256'],currentTerrainEntries=s['manifest']['terrainPatches'],inputHashes={p:h for p,h in s['pins'].items()if p.startswith('3d-viewer/')or p.endswith('.mjs')or '/vendor/'in p},probes=probes['runtimeProbes'],currentAcceptance=False))
   runtime=subprocess.run(['node',str(HERE/'xl-polyu-sports305582-authentic-local-runtime-draft-v1-20261013.mjs'),str(DOC.relative_to(ROOT))+'/'],cwd=ROOT,capture_output=True,text=True);save(DOC/'actual-max-runtime-process.json',dict(exitCode=runtime.returncode,stdout=runtime.stdout,stderr=runtime.stderr));assert runtime.returncode==0,runtime.stderr;account['actualProductionSamplerMAXRayReport']=read(DOC/'actual-interface-max-ray-report.json')
   validator=module('reviewed_unchanged_polyu_validator',HERE/'resolve-pass-indexed-parent-clipping.py')
   try:validator.validate_patch(patch,s['parent']);account['unchangedRawPatchValidator']=dict(passed=True)
   except(AssertionError,ValueError)as e:account['unchangedRawPatchValidator']=dict(passed=False,errorType=type(e).__name__,message=str(e),noOverlapApprovalInserted=True)
   selection=dict(candidateIds=[UID],rows=[dict(building=q,existingNative=q['uid']==P,patchIndexes=[0])for q in s['forms']],patches=[dict(path=str(candidate.relative_to(ROOT)),sha256=sha(candidate),uids=[UID])],inputHashes={p:h for p,h in s['pins'].items()if p.startswith('3d-viewer/')});save(DOC/'neighbour-inputs.json.gz',selection)
   run=subprocess.run(['node',str(HERE/'check-neighbours.mjs'),str(DOC.relative_to(ROOT))+'/'],cwd=ROOT,capture_output=True,text=True);save(DOC/'actual25-neighbour-process.json',dict(exitCode=run.returncode,stdout=run.stdout,stderr=run.stderr));assert run.returncode==0,run.stderr;account['ordinary25NeighbourRawGuards']=read(DOC/'neighbour-checks.json');account['ordinary25NeighbourGuardsPass']=all(not q['reasons']for q in account['ordinary25NeighbourRawGuards']['rows'])
 except Exception as e:account['actualRuntimeFailure']=dict(errorType=type(e).__name__,message=str(e),traceback=traceback.format_exc(),candidateAndCompleteAccountPreserved=True,currentAcceptance=False)
 save(DOC/'full-computed-private-candidate-and-account.json.gz',dict(account=account,candidatePath=str(candidate.relative_to(ROOT)),candidateSHA256=sha(candidate),inputHashes=s['pins'],currentAcceptance=False,physicalAccepted=False,installationApproved=False));unchanged(s);assert reservations.owns(lease)
 refs=[ROOT/p for p in s['pins']]+[p for folder in [DOC,LOCAL]for p in folder.rglob('*')if p.is_file()and p.name!='reservation.json'];freezer=module('reviewed_polyu_original_context_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');q=freezer.freeze(BATCH,'polyu-original-authentic-private-terrain-proposal-no-acceptance',refs,dict(uids=[UID],sourceFaces=10536,completeOriginalTerrainInventoryFacets=181089,selectedOriginalTerrainFacets=7690,outputFacets=len(output),triangleBudget=25000,triangleBudgetPass=account['triangleBudgetPass'],currentNatives=6650,noSourceDecode=True,currentAcceptance=False,physicalAccepted=False,newlyInstalled=0));print(json.dumps(dict(jobId=q['jobId'],outputFacets=len(output),budgetPass=account['triangleBudgetPass'],currentAcceptance=False)),flush=True)
def main():
 prep='--preflight-only'in sys.argv or '--prepare-current-basic-input-only'in sys.argv;s=preflight(require_basic=not prep,require_tests=not prep)
 if '--preflight-only'in sys.argv:unchanged(s);print(json.dumps(dict(forms=25,actualBASIC=24,nativePodium=1,resources=s['resources'],sourceSelected=7690,completeOriginalTerrain=181089,sourceSlots=42144,parentProof=s['parentProof'],coarseCells=s['cells'],core=list(map(str,s['core'])),declaredChangedCollar5m=True,currentManifestSHA256=CURRENT,noDB=True,noLease=True,noClippingOrTerrainConstruction=True,currentAcceptance=False)),flush=True);return
 if '--prepare-current-basic-input-only'in sys.argv:return prepare(s)
 if '--owned'in sys.argv:return owned(s)
 assert not LOCAL.exists();q=reservations.claim('polyu-original-authentic-private-'+str(uuid.uuid4()),s['resources'],batch=BATCH,ttl=3600);assert q['ok'];save(LEASE,json.loads(json.dumps(q['reservation'],default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,str(Path(__file__)),'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
