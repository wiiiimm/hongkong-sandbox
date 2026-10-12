"""UNEXECUTED exact existing guard-sample attribution + saved complete source columns."""
from pathlib import Path
import json,sys,time,uuid,subprocess,struct
import numpy as np
from run import ROOT,HERE,read,save,connect,reservations
import upton_six_basic_preserved_ground_feasibility_draft_v1_20261012 as inputs
from upton_geometry_bound_inherited_overlap_replay_draft_v1_20261012 import ref,check,module,CURRENT,UIDS,FOREIGN,FREEZER
from upton_parent_tin_regression_bookkeeping_v1_20261012 import sha
from upton_saved_guard_source_column_v1_20261012 import assess
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-upton-six-basic-existing-guard-samples-full-source-columns-v1-20261012';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;PROPOSAL=BASE/(BATCH+'-proposal');LEASE=LOCAL/'reservation.json';RUNTIME=HERE/'upton_six_basic_guard_sample_attribution_v1_20261012.mjs';JSHELPER=HERE/'upton_six_basic_guard_samples_v1_20261012.mjs'
FEAS=BASE/'government-xl-upton-six-basic-saved-current-ground-feasibility-v1-20261012';MAIN=BASE/'government-xl-upton-main12728-four-world-grade-cap-interfaces-v1-20261012';FOLDERS=inputs.FOLDERS+[FEAS,MAIN];IDS=['landsd/'+str(i)+':0'for i in inputs.BASIC]
def bits(v):return struct.pack('>d',float(v)).hex()
def ranges(ids):
 out=[]
 for i in map(int,ids):
  if out and i==out[-1][1]+1:out[-1][1]=i
  else:out.append([i,i])
 return out
def schema_only():
 p=read(PROPOSAL/'draft-pins.json');assert p['caller']==ref(Path(__file__))
 for q in p['codeRefs']+p['inputRefs']:check(q)
 c=read(PROPOSAL/'literal-runtime-closure-preflight.json');assert c['schema']=='exact-literal-static-dynamic-resource-closure-v1'and c['computedImportsRejected']and c['unsupportedDynamicImports']==0 and c['completeAuditedLiteralImportClosure']and c['entryPath']==str(RUNTIME.relative_to(ROOT))
 for name,h in c['inputHashes'].items():assert ref(ROOT/name)['sha256']==h
 raw=read(inputs.RAW/'neighbour-inputs.json.gz');findings=read(inputs.RAW/'neighbour-checks.json');rows=[next(q for q in raw['rows']if q['building']['uid']==u)for u in IDS];prior=[next(q for q in findings['rows']if q['uid']==u)for u in IDS]
 assert len({q['building']['parent']for q in rows})==6 and all(q['checks']>0 and 'increased-neighbour-ground-gap'in q['reasons']for q in prior)
 _,_,worlds,_,_=inputs.load_inputs();assert len(worlds)==12 and ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==CURRENT
 return dict(passed=True,caller=ref(Path(__file__)),completeSourceFaces=13704,worldRows=12,sixExactPriorSampleCounts={q['uid']:q['checks']for q in prior},actualLiteralClosure=ref(PROPOSAL/'literal-runtime-closure-preflight.json'),noSamplerColumnDBOrLeaseExecution=True)
def owned():
 lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists();last=time.monotonic();refs=[ref(p)for p in inputs.code_paths(Path(__file__))]+[ref(PROPOSAL/n)for n in ['METHOD.md','draft-pins.json','schema-preflight.json','helper-validation.json','literal-runtime-closure-preflight.json']]
 def pulse(force=False):
  nonlocal last
  if force or time.monotonic()-last>20:assert reservations.heartbeat(lease)['ok']and reservations.owns(lease);last=time.monotonic();print(json.dumps(dict(heartbeat=True)),flush=True)
 schema_only();validation=read(PROPOSAL/'helper-validation.json');assert validation['passedTests']==21 and validation['failedTests']==0 and validation['exitCode']==0
 required=[ref(p)for p in[JSHELPER,HERE/'test_upton_six_basic_guard_samples_v1_20261012.mjs',HERE/'upton_saved_guard_source_column_v1_20261012.py',HERE/'test_upton_saved_guard_source_column_v1_20261012.py']];assert validation['executedCodeRefs']==required
 for q in validation['executedCodeRefs']+validation['actualLogs']:check(q);refs.append(q)
 refs+=read(PROPOSAL/'draft-pins.json')['inputRefs']+read(PROPOSAL/'draft-pins.json')['codeRefs'];closure=read(PROPOSAL/'literal-runtime-closure-preflight.json');refs+=[dict(path=p,sha256=h)for p,h in closure['inputHashes'].items()]
 for folder in FOLDERS:
  receipt=read(folder/'result.json')
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
  for q in receipt['evidenceRefs']+[ref(folder/'result.json')]:check(q);refs.append(q);pulse()
 def fence():
  for q in refs:check(q);pulse()
  assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==CURRENT;pulse(True)
 fence();DOC.mkdir(parents=True);save(DOC/'exact-sample-replay-inputs.json',dict(currentManifestSHA256=CURRENT,basicUIDs=IDS,savedNeighbourInputs=ref(inputs.RAW/'neighbour-inputs.json.gz'),savedNeighbourChecks=ref(inputs.RAW/'neighbour-checks.json'),inputRefs=refs));sampleInput=DOC/'exact-sample-replay-inputs.json';sampleOutput=DOC/'actual-six-guard-samples-and-boundaries.json';args=['node',str(RUNTIME),str(sampleInput.relative_to(ROOT)),str(sampleOutput.relative_to(ROOT))];p=subprocess.run(args,cwd=ROOT,capture_output=True,text=True);save(DOC/'actual-sample-replay-log.json',dict(command=args,exitCode=p.returncode,stdout=p.stdout,stderr=p.stderr));assert p.returncode==0,p.stderr
 replay=read(sampleOutput);assert replay['startEndAllInputsVerified']and replay['samplerAndGuardAttributionOnly'];actualClosure=replay['completeLiteralDynamicResourceClosure'];assert actualClosure==closure
 refs +=[dict(path=path,sha256=h)for path,h in replay['inputHashes'].items()]+[ref(sampleInput),ref(sampleOutput),ref(DOC/'actual-sample-replay-log.json')];fence();_,_,worlds,_,_=inputs.load_inputs();cache={};out=[]
 for uid,mode,w,census,prior in worlds:
  xz=w[:,:,[0,2]];lo=xz.min(1);hi=xz.max(1);body={i:k for k,g in enumerate(census['sharedEdgeConnectedComponents'])for i in g};basic=[]
  for actor in replay['rows']:
   threshold=actor['boundary']['minimumAcceptedBinary64HeightM'];assert bits(threshold)==actor['boundary']['minimumHeightBitsHex'];columns=[]
   for sample in actor['rows']:
    point=sample['point'];assert [bits(v)for v in point]==sample['pointBitsHex'];selected=np.flatnonzero(np.all(lo<=point,1)&np.all(hi>=point,1));rows=[]
    for i in selected:
     key=(sha(w[i]),tuple(sample['pointBitsHex']),actor['boundary']['minimumHeightBitsHex'])
     if key not in cache:cache[key]=assess(w[i],point,threshold)
     rows.append(dict(sourceFace=int(i),originalBody=body.get(int(i)),proof=cache[key]));pulse()
    columns.append(dict(actualSample=sample,allClosedPointBoundsCandidates=selected.tolist(),strictOutsideSourceFaceClosedIntegerRanges=ranges(np.setdiff1d(np.arange(len(w)),selected)),completeSourceFaceCount=len(w),outsideRangeEncoding='inclusive integers; exact sorted complement of allClosedPointBoundsCandidates',allFiniteSourceColumns=rows,existingOrdinaryConflictAtGuardMinimum=any(q['proof']['ordinaryConflictAtSmallestAcceptedHeight']for q in rows),sampleOnlyNotContinuousCoverageOrTerrainConstruction=True))
   basic.append(dict(basicUID=actor['uid'],exactBinary64GuardBoundary=actor['boundary'],completeSamples=columns));save(LOCAL/(uid.replace('/','-').replace(':','-')+'-'+mode+'-progress.json.gz'),dict(completedBasicRows=basic,complete=False,wholeWorldSHA256=sha(w)));pulse(True)
  out.append(dict(uid=uid,mode=mode,wholeWorldSHA256=sha(w),completeOwnedFaces=len(w),originalBodyAndZeroProvenance=census,rows=basic,noAutomaticRoleSupportOrAcceptance=True));print(json.dumps(dict(uid=uid,mode=mode,conflictingSamples=sum(q['existingOrdinaryConflictAtGuardMinimum']for b in basic for q in b['completeSamples']))),flush=True)
 save(DOC/'diagnostic.json.gz',dict(rows=out,exactOriginalSamplerAndSampleContract=ref(sampleOutput),full749Body17Zero23CrossingObligationsRemain=True,geometryChanges=0,terrainConstructed=False,physicalAccepted=False,newlyInstalled=0));refs+=[ref(p)for p in DOC.rglob('*')if p.is_file()]+[ref(p)for p in LOCAL.glob('*progress.json.gz')];fence();module(FREEZER,'upton_exact_guard_column_freezer').freeze(BATCH,'existing-six-guard-exact-binary64-boundary-and-full-saved-source-columns',[check(q)for q in{(q['path'],q['sha256']):q for q in refs}.values()],dict(uids=UIDS[:3],sourceOnly=True,newlyInstalled=0,physicalAccepted=False,currentManifestSHA256=CURRENT))
def main():
 if '--schema-only'in sys.argv:print(json.dumps(schema_only(),sort_keys=True));return
 if '--owned'in sys.argv:return owned()
 assert '--attribute-existing-gap-samples-only'in sys.argv and not DOC.exists()and not LOCAL.exists();resources=['building:'+u for u in UIDS+[FOREIGN]]+['terrain-patch:'+u for u in UIDS+[FOREIGN]]+['immutable-source-proof:'+BATCH];claim=reservations.claim('upton-existing-guard-columns-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'];save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
