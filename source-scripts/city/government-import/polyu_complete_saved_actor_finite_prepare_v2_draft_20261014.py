"""Post-terminal ROOT preparation: immutable exact prefix snapshot, no finite replay."""
from pathlib import Path
import ast,json,sys,os,subprocess
import polyu_complete_saved_actor_finite_v2_draft_20261014 as caller
import polyu_complete_saved_actor_finite_v1_draft_20261014 as prior
ROOT,HERE=caller.ROOT,caller.HERE;P=caller.PROPOSAL;CALLER=Path(caller.__file__)
read,save,ref,check=caller.read,caller.save,caller.ref,caller.check
distinct=caller.distinct_refs
COMBINED=caller.BASE/'government-xl-polyu-exact-finite-combined-cache-v1-20261014-proposal'
def closure():
 todo=[CALLER,Path(__file__)];seen=set();roots=[HERE,HERE.parent/'shared-modelling',HERE.parent/'citywide-native',HERE.parent/'island-detail-integration',HERE.parent/'assembly-support-review',ROOT/'docs/astra-city/mui-wo-buildings/review']
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
def build():
 stop=caller.lifecycle();previous,receipt,actors,before,after=prior.load();entries=[];chunkrefs=[];before_sha,after_sha=caller.sha(before),caller.sha(after)
 for i,actor in enumerate(actors['rows']):
  for mode,stream in actor['worlds'].items():
   folder=caller.PRIOR_DOC/'chunks'/str(i).zfill(2)/mode;paths=sorted(folder.glob('[0-9][0-9][0-9][0-9][0-9].json.gz'))
   assert [p.name for p in paths]==[f'{j:05}.json.gz'for j in range(len(paths))]
   refs=[ref(p)for p in paths];count=sum(len(read(p)['rows'])for p in paths);chunkrefs+=refs
   entries.append(dict(actorIndex=i,uid=actor['uid'],role=actor['role'],mode=mode,wholeWorldSHA256=stream['worldSHA256'],completeFaces=len(stream['completeWorldTriangles']),beforeGroundSHA256=before_sha,afterGroundSHA256=after_sha,chunks=refs,closedRows=count))
 prefix=P/'closed-prior-prefix-manifest.json';assert not prefix.exists()
 save(prefix,dict(priorTerminalRelease=ref(P/'prior-terminal-release.json'),entries=entries,partialPriorEvidenceNotCompleteReceipt=True,noPrefixArithmeticReplayed=True,temporaryChunksUncredited=True))
 comparison=COMBINED/'actual-saved-completed-comparison.json';assert ref(comparison)['sha256']=='82ea1664902f94ea7fba3511def8400cf054ab6d7b468b604d0016451fd1be53'
 compared=read(COMBINED/'saved-comparison-pins.json')
 code=distinct(previous['codeRefs']+closure()+[ref(P/'METHOD.md')]+compared['codeRefs'])
 inputs=distinct(previous['inputRefs']+chunkrefs+stop['evidenceRefs']+[ref(P/'prior-terminal-release.json'),ref(caller.PRIOR_LEASE),ref(prefix),ref(comparison),ref(COMBINED/'saved-comparison-pins.json'),ref(prior.PROPOSAL/'draft-pins.json')])
 for q in distinct(code+inputs):check(q)
 save(P/'draft-pins.json',dict(caller=ref(CALLER),codeRefs=code,inputRefs=inputs,completedGroundCaptureJob=previous['completedGroundCaptureJob'],beforeGroundSHA256=previous['beforeGroundSHA256'],afterGroundSHA256=previous['afterGroundSHA256'],prefixManifest=ref(prefix),verifiedExecutorComparison=ref(comparison)))
 print(json.dumps(dict(pins=ref(P/'draft-pins.json'),prefixManifest=ref(prefix),closedRows=sum(e['closedRows']for e in entries),chunks=len(chunkrefs),noFiniteDBLease=True)))
def prepare():
 pins=read(P/'draft-pins.json');assert pins['caller']==ref(CALLER);declared=distinct(pins['codeRefs']+pins['inputRefs'])
 def fence():
  for q in declared:check(q)
 fence();commands=[];evidence=[];env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')
 for name,cmd in [('actual-finite-v2-import',[sys.executable,'-c',"import sys;sys.path.insert(0,"+repr(str(HERE))+");import "+CALLER.stem+";print('IMPORT PASS')"]),('actual-finite-v2-prefix-schema',[sys.executable,str(CALLER),'--schema-only'])]:
  log=P/(name+'.log')
  with log.open('xb')as f:proc=subprocess.run(cmd,cwd=ROOT,env=env,stdout=f,stderr=subprocess.STDOUT)
  commands.append(dict(command=cmd,exitCode=proc.returncode,log=ref(log)));evidence.append(ref(log));fence();assert proc.returncode==0,(name,proc.returncode)
 fence();save(P/'actual-readonly-preparation.json',dict(passed=True,caller=ref(CALLER),commands=commands,beforeEndAllPinsVerified=True,closedPrefixMetadataAndSourceHashesVerified=True,noFiniteOrSelectorReplay=True,transitivePythonCodeRefs=pins['codeRefs'],evidenceRefs=distinct(evidence+[ref(Path(__file__)),ref(P/'draft-pins.json')]),noDBLeaseSourceDecode=True))
 print(json.dumps(dict(preparation=ref(P/'actual-readonly-preparation.json'),passed=True)))
if __name__=='__main__':
 if '--build-pins-only'in sys.argv:build()
 else:assert '--prepare-only'in sys.argv;prepare()
