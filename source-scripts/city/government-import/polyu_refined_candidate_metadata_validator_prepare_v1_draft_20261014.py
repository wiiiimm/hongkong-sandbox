"""ROOT preparation only after exact new overlap result/certificate; no numerical replay."""
from pathlib import Path
import ast,json,sys,os,subprocess
import polyu_whole_actor_current_ground_delta3_prepare_v1_draft_20261014 as shared
import polyu_refined_candidate_metadata_validator_v1_draft_20261014 as caller
ROOT,HERE=shared.ROOT,shared.HERE;P=caller.PROPOSAL;CALLER=Path(caller.__file__)
read,ref,save,distinct=shared.read,shared.ref,shared.save,shared.distinct
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
 prior=caller.prior;previous=read(prior.PROPOSAL/'draft-pins.json');r=read(prior.DOC/'result.json');c=read(prior.DOC/'ROOT-VERIFIED.json')
 assert r['jobId']==c['jobId']and c['exactNeonReadback']and c['allEvidenceHashesVerified']and c['leaseReleased']
 names=['result.json','ROOT-VERIFIED.json','complete-new-overlap-summary.json','complete-old-and-new-pair-evidence-manifest.json','complete-new-source-plane-and-face-map.json.gz','complete-new-base-parent-edge-inventory.json.gz','actual-saved64-full-candidate-native-max-ray-findings.json.gz','unchanged-validator-outcome.json']
 inputs=distinct(previous['inputRefs']+r['evidenceRefs']+[ref(prior.DOC/n)for n in names]+[ref(prior.PROPOSAL/'draft-pins.json')])
 code=distinct(previous['codeRefs']+closure()+[ref(P/'METHOD.md')])
 for q in distinct(code+inputs):caller.check(q)
 summary=read(prior.DOC/'complete-new-overlap-summary.json')
 save(P/'draft-pins.json',dict(caller=ref(CALLER),codeRefs=code,inputRefs=inputs,completedOverlapJob=r['jobId'],candidateCanonicalSHA256=previous['candidateCanonicalSHA256'],completeMeshBinding=previous['completeMeshBinding'],measuredProjectedExcessM2=summary['measurement']['nativeProjectedExcessM2'],actualBaseParent=previous['actualBaseParent']))
 print(json.dumps(dict(pins=ref(P/'draft-pins.json'),completedOverlapJob=r['jobId'],noNumericalReplayDBLease=True)))
def prepare():
 p=read(P/'draft-pins.json');assert p['caller']==ref(CALLER);declared=distinct(p['codeRefs']+p['inputRefs']);commands=[];evidence=[]
 def fence():
  for q in declared:caller.check(q)
 fence();env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')
 for name,cmd in [('actual-metadata-import',[sys.executable,'-c',"import sys;sys.path.insert(0,"+repr(str(HERE))+");import "+CALLER.stem+";print('IMPORT PASS')"]),('actual-metadata-schema',[sys.executable,str(CALLER),'--schema-only'])]:
  log=P/(name+'.log')
  with log.open('xb')as f:proc=subprocess.run(cmd,cwd=ROOT,env=env,stdout=f,stderr=subprocess.STDOUT)
  commands.append(dict(command=cmd,exitCode=proc.returncode,log=ref(log)));evidence.append(ref(log));fence();assert proc.returncode==0,(name,proc.returncode)
 fence();save(P/'actual-readonly-preparation.json',dict(passed=True,caller=ref(CALLER),commands=commands,beforeEndAllDeclaredPinsVerified=True,transitivePythonCodeRefs=closure(),evidenceRefs=distinct(evidence+[ref(Path(__file__)),ref(P/'draft-pins.json')]),noPairsRaysActorsFiniteValidatorDBLease=True))
 print(json.dumps(dict(preparation=ref(P/'actual-readonly-preparation.json'),passed=True)))
if __name__=='__main__':
 if '--build-pins-only'in sys.argv:build()
 else:assert '--prepare-only'in sys.argv;prepare()
