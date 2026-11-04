"""ROOT-only hard-bounded comparisons against CLOSED saved canonical records.
No slow canonical replay, DB, lease, source decode, active-chunk read or resume.
"""
from pathlib import Path
import ast,gzip,hashlib,json,sys,time,multiprocessing as mp,queue
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
BASE=ROOT/'docs/astra-city/government-import';P=BASE/'government-xl-polyu-exact-finite-combined-cache-v1-20261014-proposal'
CAP=BASE/'government-xl-polyu-whole-actor-current-ground-delta3-v1-20261014'
FIN=BASE/'government-xl-polyu-complete-saved-actor-finite-v1-20261014'
CHUNKS=[FIN/'chunks/00/actualLiteral/00526.json.gz',FIN/'chunks/00/actualLiteral/00538.json.gz']
def read(p):
 with gzip.open(p,'rt')if str(p).endswith('.gz')else open(p)as f:return json.load(f)
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def check(q):assert ref(ROOT/q['path'])==q
def write(p,a):
 with p.open('x')as f:json.dump(a,f,sort_keys=True,indent=2,allow_nan=False);f.write('\n')
def code_refs():
 todo=[Path(__file__),HERE/'exact_finite_combined_coverage_cache_v1_draft_20261014.py',HERE/'test_exact_finite_combined_coverage_cache_v1_draft_20261014.py'];seen=set()
 roots=[HERE,HERE.parent/'shared-modelling',HERE.parent/'citywide-native',HERE.parent/'island-detail-integration',HERE.parent/'assembly-support-review']
 while todo:
  p=todo.pop().resolve()
  if p in seen:continue
  seen.add(p)
  for n in ast.walk(ast.parse(p.read_text())):
   names=[n.module]if isinstance(n,ast.ImportFrom)and n.module else[x.name for x in n.names]if isinstance(n,ast.Import)else[]
   for name in names:
    for root in roots:
     q=root/(name.replace('.','/')+'.py')
     if q.is_file():todo.append(q)
 return [ref(p)for p in sorted(seen)]
def saved_cases():
 a,b=map(read,CHUNKS);assert a['uid']==b['uid']=='landsd/305793:0'and a['mode']==b['mode']=='actualLiteral'
 assert a['wholeWorldSHA256']==b['wholeWorldSHA256']and a['beforeGroundSHA256']==b['beforeGroundSHA256']and a['afterGroundSHA256']==b['afterGroundSHA256']
 assert [r['sourceFace']for r in a['rows']]==list(range(33664,33728))and [r['sourceFace']for r in b['rows']]==list(range(34432,34496))
 paired=next(r for r in b['rows']if r['candidate']['paired']is not None)
 cases=[]
 for row,which in [(a['rows'][0],'current'),(a['rows'][0],'candidate'),(paired,'current'),(paired,'candidate'),(next(r for r in a['rows']if r['sourceFace']==33712),'candidate'),(a['rows'][-1],'candidate')]:
  cases.append(dict(sourceFace=row['sourceFace'],which=which,sourceFaceSHA256=row['sourceFaceSHA256'],selection=row[which+'CompleteSelectedGround'],expected=row[which]))
 return a,cases
def build():
 cert=read(CAP/'ROOT-VERIFIED.json');result=read(CAP/'result.json')
 assert result['jobId']==cert['jobId']=='0d3f5c3eb6569ab431cdc719057068ef4883c71ea3a5279f47677451637eaa24'and cert['exactNeonReadback']and cert['allEvidenceHashesVerified']and cert['leaseReleased']
 meta,cases=saved_cases();inputs=[ref(p)for p in CHUNKS]+[ref(CAP/n)for n in ['result.json','ROOT-VERIFIED.json','complete-saved-actor-worlds.json.gz','complete-whole-actor-current-before-ground.json.gz','complete-whole-actor-current-candidate-ground.json.gz']]
 receipt={(q['path'],q['sha256'])for q in result['evidenceRefs']};assert all((q['path'],q['sha256'])in receipt for q in inputs if q['path'].endswith('.gz')and'/chunks/'not in q['path'])
 pins=dict(caller=ref(Path(__file__)),codeRefs=code_refs()+[ref(P/'METHOD.md')],inputRefs=inputs,expectedCases=[dict(sourceFace=c['sourceFace'],which=c['which'],selected=c['selection']['selectedFacetCount'])for c in cases],closedExpectedChunkWorldSHA256=meta['wholeWorldSHA256'],maxCaseSeconds=90,maxTotalSeconds=240,noActiveChunkRead=True)
 for q in pins['codeRefs']+pins['inputRefs']:check(q)
 write(P/'saved-comparison-pins.json',pins);print(json.dumps(dict(pins=ref(P/'saved-comparison-pins.json'),cases=pins['expectedCases'],noNumericalCall=True)))
def schema():
 pins=read(P/'saved-comparison-pins.json');assert pins['caller']==ref(Path(__file__))
 for q in pins['codeRefs']+pins['inputRefs']:check(q)
 _,cases=saved_cases();assert pins['expectedCases']==[dict(sourceFace=c['sourceFace'],which=c['which'],selected=c['selection']['selectedFacetCount'])for c in cases]
 for c in cases:
  ids=c['selection']['selectedOriginalGroundFaces'];assert len(ids)==c['selection']['selectedFacetCount']and ids==sorted(set(ids))
  assert c['expected']['sourceFaceSHA256']==c['sourceFaceSHA256']and c['expected']['coarse']is not None
 return pins,cases
def child(output,face,ground,case):
 import numpy as np
 import exact_finite_combined_coverage_cache_v1_draft_20261014 as combined
 start=time.perf_counter();run,memo=combined.executor();actual=run(face,ground)
 assert actual==case['expected'],'Full canonical saved-result mismatch'
 assert actual['sourceFaceSHA256']==case['sourceFaceSHA256']
 output.put(dict(passed=True,sourceFace=case['sourceFace'],which=case['which'],selectedGroundFaces=len(ground),elapsedKernelSeconds=time.perf_counter()-start,fullResultSHA256=hashlib.sha256(json.dumps(actual,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest(),coverageHits=memo.hits,coverageMisses=memo.misses,boundsCounters=memo.bounds_totals,noCanonicalReplay=True))
def compare():
 import numpy as np
 pins,cases=schema();start=time.monotonic();actors=read(CAP/'complete-saved-actor-worlds.json.gz');actor=actors['rows'][0]
 assert actor['uid']=='landsd/305793:0'and actor['role']=='retained-native'
 stream=actor['worlds']['actualLiteral'];world=np.asarray(stream['completeWorldTriangles'],dtype='<f8');assert world.shape==(59527,3,3)and np.isfinite(world).all()
 sha=lambda a:hashlib.sha256(np.asarray(a,dtype='<f8').tobytes()).hexdigest()
 assert sha(world)==stream['worldSHA256']==pins['closedExpectedChunkWorldSHA256'];ground={}
 for which,name in [('current','complete-whole-actor-current-before-ground.json.gz'),('candidate','complete-whole-actor-current-candidate-ground.json.gz')]:
  ground[which]=np.asarray(read(CAP/name)['completeRelevantDrawnTriplets'],dtype='<f8').reshape(-1,3,3);assert np.isfinite(ground[which]).all()
  expected=next(c['selection']['completeGroundSHA256']for c in cases if c['which']==which);assert sha(ground[which])==expected
 rows=[];ctx=mp.get_context('fork')
 for ordinal,c in enumerate(cases):
  face=world[c['sourceFace']];assert sha(face)==c['sourceFaceSHA256'];selected=ground[c['which']][c['selection']['selectedOriginalGroundFaces']]
  assert sha(selected)==c['expected']['completeGroundSHA256']and np.isfinite(face).all();face.flags.writeable=False;selected.flags.writeable=False
  remaining=pins['maxTotalSeconds']-(time.monotonic()-start)
  if remaining<=0:rows.append(dict(notStarted=True,totalBudgetExhausted=True,sourceFace=c['sourceFace'],which=c['which']));break
  output=ctx.Queue();proc=ctx.Process(target=child,args=(output,face,selected,c));proc.start();print(json.dumps(dict(case=ordinal,pid=proc.pid,sourceFace=c['sourceFace'],which=c['which'],selected=len(selected))),flush=True)
  proc.join(min(pins['maxCaseSeconds'],remaining))
  if proc.is_alive():
   proc.kill();proc.join(5);assert not proc.is_alive(),'Owned comparison child did not reap after kill'
   rows.append(dict(timedOut=True,sourceFace=c['sourceFace'],which=c['which'],ownChildKilledAndReaped=True));output.close();break
  if proc.exitcode!=0:
   rows.append(dict(childFailure=True,exitCode=proc.exitcode,sourceFace=c['sourceFace'],which=c['which']));output.close();break
  try:rows.append(output.get(timeout=2))
  except queue.Empty:rows.append(dict(childResultMissing=True,sourceFace=c['sourceFace'],which=c['which']))
  output.close();print(json.dumps(rows[-1]),flush=True)
  if not rows[-1].get('passed'):break
 for q in pins['codeRefs']+pins['inputRefs']:check(q)
 passed=len(rows)==len(cases)and all(r.get('passed')for r in rows)
 write(P/'actual-saved-completed-comparison.json',dict(passed=passed,rows=rows,completeExpectedCases=len(cases),allBeforeEndPinsVerified=True,elapsedTotalSeconds=time.monotonic()-start,noSlowCanonicalReplay=True,noDBLeaseSourceDecodeOrWorkerModification=True,sourceOnlyNoAcceptance=True))
 print(json.dumps(dict(passed=passed,proof=ref(P/'actual-saved-completed-comparison.json'))),flush=True)
 if not passed:raise SystemExit(2)
if __name__=='__main__':
 if '--build-pins-only'in sys.argv:build()
 elif '--schema-only'in sys.argv:print(json.dumps(dict(passed=True,cases=len(schema()[1]),noNumericalCall=True)))
 else:assert '--compare-saved-completed-only'in sys.argv;compare()
