"""Unexecuted saved-candidate runtime continuation; no reconstruction/acceptance."""
import importlib.util,json,sys,subprocess,uuid,traceback,types
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from polyu_sports_saved_candidate_actual_edge_incidents_draft_v1_20261013 import actual_complete_edge_incidents
from southside_selective13_certified_width_parent_restoration_draft_v2_20261013 import interface_runtime_probes
B=ROOT/'docs/astra-city/government-import';PRIOR=B/'government-xl-polyu-sports305582-authentic-local-private-terrain-v2-20261013';D=B/'government-xl-polyu-sports305582-authentic-local-private-terrain-draft-v1-20261013/saved-candidate-runtime-only-draft-v1';BATCH='government-xl-polyu-sports305582-saved-private-candidate-runtime-only-v1-20261013';DOC=B/BATCH;LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json';CURRENT='c00fd9f731b1bcbf4d2df6067a5cb3231f0eaa8c503a8adea584fec39bf73bf7';UID='landsd/305582:0';P='landsd/305793:0'
sha=lambda p:digest(p.read_bytes())
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def preflight(require_tests):
 assert not DOC.exists()and not LOCAL.exists()or '--owned'in sys.argv and LOCAL.exists()and not DOC.exists()
 pins={r['path']:r['sha256']for r in read(D/'input-pins.json')['filePins']}
 for p,h in pins.items():assert sha(ROOT/p)==h,p
 q=read(PRIOR/'result.json');a=read(PRIOR/'full-computed-private-candidate-and-account.json.gz');assert q['jobId']=='f27f496a7877e8eda20dcab082a0c8dbd08eb67e7c6051ca90f908578748ccdf'and len(q['evidenceRefs'])==8804
 for r in q['evidenceRefs']:assert sha(ROOT/r['path'])==r['sha256'],r['path'];pins[r['path']]=r['sha256']
 for p,h in a['inputHashes'].items():assert sha(ROOT/p)==h,p;pins[p]=h
 candidate=ROOT/a['candidatePath'];assert sha(candidate)==a['candidateSHA256'];patch=read(candidate);assert a['account']['triangleBudgetPass']is True and a['account']['outputFacets']==3214 and a['account']['realFloat32CollapsedOutputFacets']==[]
 assert a['account']['actualRuntimeFailure']['errorType']=='KeyError'and a['account']['actualRuntimeFailure']['message']=="'allIncidentRecords'"
 assert q['currentAcceptance']is q['physicalAccepted']is False and sha(ROOT/'3d-viewer/city/data/manifest.json')==CURRENT
 manifest=read(ROOT/'3d-viewer/city/data/manifest.json');proof=a['account']['all25CompleteProductionBasicAndExplicitNativeInputsVerbatim'];forms=[r['currentForm']for r in proof['rows']];assert len(forms)==len({r['uid']for r in forms})==25
 lease=read(HERE/'local'/q['batch']/'reservation.json');resources=lease['resources'];assert len(resources)==28 and {r for r in resources if r.startswith('building:')}=={'building:'+f['uid']for f in forms}
 if require_tests:
  v=read(D/'immutable-tests-v1/validation.json');assert v['tests']==8 and v['exitCode']==0 and v['passed']is True;assert sha(D/'immutable-tests-v1/tests.log')==v['testLogSHA256']
  assert v['codePins']==[dict(path=p,sha256=sha(ROOT/p))for p in read(D/'input-pins.json')['testCodePaths']]
  for p in [D/'immutable-tests-v1/validation.json',D/'immutable-tests-v1/tests.log']:pins[str(p.relative_to(ROOT))]=sha(p)
 for m in list(sys.modules.values()):
  if isinstance(m,types.ModuleType)and getattr(m,'__file__',None):
   p=Path(m.__file__).resolve()
   if p.is_relative_to(ROOT)and p.is_file():pins[str(p.relative_to(ROOT))]=sha(p)
 for p in [D/'input-pins.json',Path(__file__)]:pins[str(p.relative_to(ROOT))]=sha(p)
 return dict(pins=pins,q=q,a=a,patch=patch,candidate=candidate,resources=resources,forms=forms,manifest=manifest)
def unchanged(s):
 assert sha(ROOT/'3d-viewer/city/data/manifest.json')==CURRENT
 for p,h in s['pins'].items():assert sha(ROOT/p)==h,p
def owned(s):
 lease=read(LEASE);assert lease['resources']==s['resources']and reservations.owns(lease);unchanged(s)
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(s['q']['jobId'],)).fetchone()==('complete',s['q'])
 account=dict(savedSourceOnlyCandidateJob=s['q']['jobId'],candidatePath=str(s['candidate'].relative_to(ROOT)),candidateSHA256=sha(s['candidate']),noConstructionOrDecodeOrPointCheckReplay=True,currentAcceptance=False,physicalAccepted=False)
 try:
  edge=actual_complete_edge_incidents(s['patch'],s['a']['account']);save(DOC/'complete-actual-edge-incidents.json.gz',edge);probes=interface_runtime_probes(np.asarray(edge['completeActualTriangles'],dtype='<f8'),edge['completeActualPackedEdgeInventory']);save(DOC/'complete-packed-edge-max-envelopes.json.gz',probes)
  save(DOC/'runtime-input.json.gz',dict(schema='polyu-authentic-local-private-runtime-v1',candidate=dict(path=str(s['candidate'].relative_to(ROOT)),sha256=sha(s['candidate'])),currentManifestSHA256=CURRENT,parentTerrainSHA256=s['patch']['meta']['parentSha256'],currentTerrainEntries=s['manifest']['terrainPatches'],inputHashes={p:h for p,h in s['pins'].items()if p.startswith('3d-viewer/')or p.endswith('.mjs')or '/vendor/'in p},probes=probes['runtimeProbes'],currentAcceptance=False))
  runtime=subprocess.run(['node',str(HERE/'xl-polyu-sports305582-authentic-local-runtime-draft-v1-20261013.mjs'),str(DOC.relative_to(ROOT))+'/'],cwd=ROOT,capture_output=True,text=True);save(DOC/'actual-max-runtime-process.json',dict(exitCode=runtime.returncode,stdout=runtime.stdout,stderr=runtime.stderr));assert runtime.returncode==0,runtime.stderr;account['actualProductionSamplerMAXRayReport']=read(DOC/'actual-interface-max-ray-report.json')
  validator=module('reviewed_unchanged_polyu_saved_validator',HERE/'resolve-pass-indexed-parent-clipping.py')
  try:validator.validate_patch(s['patch'],read(ROOT/'3d-viewer/city/data/terrain.json'));account['unchangedRawPatchValidator']=dict(passed=True)
  except(AssertionError,ValueError)as e:account['unchangedRawPatchValidator']=dict(passed=False,errorType=type(e).__name__,message=str(e),noOverlapApprovalInserted=True)
  selection=dict(candidateIds=[UID],rows=[dict(building=q,existingNative=q['uid']==P,patchIndexes=[0])for q in s['forms']],patches=[dict(path=str(s['candidate'].relative_to(ROOT)),sha256=sha(s['candidate']),uids=[UID])],inputHashes={p:h for p,h in s['pins'].items()if p.startswith('3d-viewer/')});save(DOC/'neighbour-inputs.json.gz',selection)
  run=subprocess.run(['node',str(HERE/'check-neighbours.mjs'),str(DOC.relative_to(ROOT))+'/'],cwd=ROOT,capture_output=True,text=True);save(DOC/'actual25-neighbour-process.json',dict(exitCode=run.returncode,stdout=run.stdout,stderr=run.stderr));assert run.returncode==0,run.stderr;account['ordinary25NeighbourRawGuards']=read(DOC/'neighbour-checks.json');account['ordinary25NeighbourGuardsPass']=all(not q['reasons']for q in account['ordinary25NeighbourRawGuards']['rows'])
 except Exception as e:account['actualRuntimeFailure']=dict(errorType=type(e).__name__,message=str(e),traceback=traceback.format_exc(),originalCandidateAndLineagePreserved=True,currentAcceptance=False)
 save(DOC/'saved-candidate-runtime-only-account.json.gz',dict(account=account,inputHashes=s['pins'],allOriginal3214LineagesAndParentSourceBindingsVerbatim=s['a']['account'],currentAcceptance=False,physicalAccepted=False));unchanged(s);assert reservations.owns(lease)
 refs=[ROOT/p for p in s['pins']]+[p for folder in [DOC,LOCAL]for p in folder.rglob('*')if p.is_file()and p.name!='reservation.json'];freezer=module('reviewed_polyu_saved_runtime_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');q=freezer.freeze(BATCH,'polyu-saved-original-terrain-runtime-only-no-acceptance',refs,dict(uids=[UID],candidateFacets=3214,noTerrainReconstruction=True,currentAcceptance=False,physicalAccepted=False,newlyInstalled=0));print(json.dumps(dict(jobId=q['jobId'],runtimeFailure=account.get('actualRuntimeFailure'),currentAcceptance=False)),flush=True)
def main():
 prep='--preflight-only'in sys.argv;s=preflight(require_tests=not prep)
 if prep:unchanged(s);print(json.dumps(dict(forms=25,resources=len(s['resources']),candidateFacets=3214,currentManifestSHA256=CURRENT,noDB=True,noLease=True,noRuntimeOrConstruction=True,currentAcceptance=False)),flush=True);return
 if '--owned'in sys.argv:return owned(s)
 q=reservations.claim('polyu-saved-candidate-runtime-'+str(uuid.uuid4()),s['resources'],batch=BATCH,ttl=3600);assert q['ok'];save(LEASE,json.loads(json.dumps(q['reservation'],default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,str(Path(__file__)),'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
