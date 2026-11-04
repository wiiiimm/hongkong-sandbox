"""ROOT-only prefix/provenance preparation; no GEOS pairs/MAX/validator/DB."""
from pathlib import Path
import ast,json,sys,os,subprocess
import numpy as np
import polyu_whole_actor_current_ground_delta3_prepare_v1_draft_20261014 as shared
import polyu_refined_candidate_overlap_max_caller_v1_draft_20261014 as caller
ROOT,HERE,BASE=shared.ROOT,shared.HERE,shared.BASE;P=caller.PROPOSAL;CALLER=Path(caller.__file__);RUNTIME=caller.RUNTIME
read,ref,save,distinct=shared.read,shared.ref,shared.save,shared.distinct
SCHED=HERE/'polyu_appended_pair_schedule_v1_draft_20261014.py';TEST=HERE/'test_polyu_appended_pair_schedule_v1_draft_20261014.py'
def code_closure():
 todo=[CALLER,Path(__file__),SCHED,TEST];seen=set();roots=[HERE,HERE.parent/'shared-modelling',HERE.parent/'citywide-native',HERE.parent/'island-detail-integration',HERE.parent/'assembly-support-review',ROOT/'docs/astra-city/mui-wo-buildings/review']
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
 previous=read(caller.capture.PROPOSAL/'draft-pins.json');capture=caller.capture.DOC;old=caller.OLD;oldreceipt=read(old/'result.json');capreceipt=read(capture/'result.json')
 for folder,job in [(old,caller.OLD_JOB),(capture,caller.CAP_JOB)]:
  cert=read(folder/'ROOT-VERIFIED.json');assert read(folder/'result.json')['jobId']==cert['jobId']==job and cert['exactNeonReadback']and cert['allEvidenceHashesVerified']and cert['leaseReleased']
 chunks=sorted([q for q in oldreceipt['evidenceRefs']if '/complete-pair-chunks/'in q['path']],key=lambda q:q['path']);assert len(chunks)==1159
 candidate=read(capture/'private-native-terrain-candidate.json.gz');inp=read(capture/'input.json.gz');replay=read(capture/'actual-production-replay.json.gz');parent=dict(path='3d-viewer/city/data/terrain.json',sha256=replay['inputHashes']['3d-viewer/city/data/terrain.json'])
 inputs=distinct(previous['inputRefs']+chunks+[ref(capture/n)for n in ['result.json','ROOT-VERIFIED.json','input.json.gz','actual-production-replay.json.gz','private-native-terrain-candidate.json.gz','real-validator-outcome.json','guard-first-viability.json']]+[ref(old/n)for n in ['result.json','ROOT-VERIFIED.json','complete-overlap-summary.json','complete-source-plane-and-face-map.json.gz']]+[ref(caller.OLD_CAPTURE/'private-native-terrain-candidate.json.gz'),ref(caller.FIRST/'private-compatible-current-parent-append-nomination.json.gz'),inp['newNomination'],ref(caller.FEAS/'complete-nine-parent-restoration-feasibility.json.gz'),parent])
 code=distinct(previous['codeRefs']+code_closure()+[ref(RUNTIME),ref(P/'METHOD.md'),ref(HERE/'exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs'),ref(HERE/'dependency-closure-vendor/acorn-8.8.1/acorn.mjs')])
 for q in distinct(code+inputs):assert ref(ROOT/q['path'])==q
 save(P/'draft-pins.json',dict(caller=ref(CALLER),runtime=ref(RUNTIME),codeRefs=code,inputRefs=inputs,completeInheritedPairChunkRefs=chunks,actualBaseParent=parent,completeMeshBinding=caller.mesh_binding({k:candidate['nativeMesh'][k]for k in ['position','index']}),candidateCanonicalSHA256=caller.canonical(candidate)))
 print(json.dumps(dict(pins=ref(P/'draft-pins.json'),completeInheritedChunks=len(chunks),noUnionPairsMAXValidatorDBLease=True)))
def prepare():
 pins=read(P/'draft-pins.json');assert pins['caller']==ref(CALLER)and pins['runtime']==ref(RUNTIME);declared=distinct(pins['codeRefs']+pins['inputRefs'])
 def fence():
  for q in declared:assert ref(ROOT/q['path'])==q
 fence();commands=[];evidence=[];env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')
 def run(name,cmd):
  log=P/(name+'.log')
  with log.open('xb')as f:proc=subprocess.run(cmd,cwd=ROOT,env=env,stdout=f,stderr=subprocess.STDOUT)
  commands.append(dict(command=cmd,exitCode=proc.returncode,log=ref(log)));evidence.append(ref(log));fence();assert proc.returncode==0,(name,proc.returncode);return log
 log=run('actual-four-pair-scheduler-tests',[sys.executable,str(TEST),'-v']);assert 'Ran 4 tests'in log.read_text()and '\nOK\n'in log.read_text()
 validation=P/'schedule-validation.json';save(validation,dict(passedTests=4,failedTests=0,exitCode=0,executedCodeRefs=[ref(SCHED),ref(TEST)],evidenceRefs=[ref(SCHED),ref(TEST),ref(log)]));evidence.append(ref(validation))
 run('actual-new-overlap-import',[sys.executable,'-c',"import sys;sys.path.insert(0,"+repr(str(HERE))+");import "+CALLER.stem+";print('IMPORT PASS')"])
 run('actual-new-overlap-schema',[sys.executable,str(CALLER),'--schema-only'])
 closure=P/'literal-runtime-closure.json';js="import fs from 'node:fs';import assert from 'node:assert/strict';import {snapshotModuleClosure,verifyModuleClosure} from './source-scripts/city/government-import/exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs';const root=new URL('./',import.meta.url),c=snapshotModuleClosure(new URL("+json.dumps(str(RUNTIME.relative_to(ROOT)))+",root),root);assert.equal(c.schema,'exact-literal-static-dynamic-resource-closure-v1');assert(c.computedImportsRejected&&c.completeAuditedLiteralImportClosure&&c.opaqueResourcesAreNotParsedModules);assert.equal(c.unsupportedDynamicImports,0);verifyModuleClosure(c,root);fs.writeFileSync("+json.dumps(str(closure))+",JSON.stringify(c)+String.fromCharCode(10),{flag:'wx'});console.log(JSON.stringify({passed:true,files:Object.keys(c.inputHashes).length}));"
 run('actual-new-overlap-literal-closure',['node','--input-type=module','-e',js]);evidence.append(ref(closure))
 for path,h in read(closure)['inputHashes'].items():assert ref(ROOT/path)==dict(path=path,sha256=h);evidence.append(dict(path=path,sha256=h))
 fence();save(P/'actual-readonly-preparation.json',dict(passed=True,caller=ref(CALLER),runtime=ref(RUNTIME),scheduleValidationRef=ref(validation),literalClosureRef=ref(closure),commands=commands,beforeEndAllDeclaredPinsVerified=True,transitivePythonCodeRefs=pins['codeRefs'],evidenceRefs=distinct(evidence+[ref(Path(__file__)),ref(P/'draft-pins.json')]),noUnionPairMAXValidatorSourceDecodeDBLease=True));print(json.dumps(dict(preparation=ref(P/'actual-readonly-preparation.json'),passed=True)))
if __name__=='__main__':
 if '--build-pins-only'in sys.argv:build()
 else:assert '--prepare-only'in sys.argv;prepare()
