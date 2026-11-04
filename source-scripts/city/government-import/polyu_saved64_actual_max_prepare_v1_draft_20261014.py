"""ROOT-only read-only preparation; no rays/validator/DB/leases/source decode."""
from pathlib import Path
import json,sys,subprocess,os,hashlib
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-polyu-saved64-actual-max-reviewed-validator-v1-20261014'
P=BASE/(BATCH+'-proposal');CALLER=HERE/'polyu_saved64_actual_max_validator_caller_v1_draft_20261014.py';RUNTIME=HERE/'polyu_saved64_actual_max_full_ray_runtime_v1_draft_20261014.mjs'
def ref(p):return dict(path=str(p.resolve().relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def save(p,v):p.write_text(json.dumps(v,sort_keys=True,separators=(',',':'))+'\n')
def main():
 pins=json.loads((P/'draft-pins.json').read_bytes());allpins={q['path']:q for q in pins['codeRefs']+pins['inputRefs']}
 def fence():
  for q in allpins.values():assert ref(ROOT/q['path'])==q,q
 fence();assert not(P/'actual-readonly-preparation.json').exists();commands=[];env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1');outputs=[]
 def run(name,cmd):
  path=P/(name+'.log')
  with path.open('xb')as log:proc=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT)
  commands.append(dict(command=cmd,exitCode=proc.returncode,log=ref(path)));outputs.append(ref(path));fence()
  assert proc.returncode==0,(name,proc.returncode)
  return path
 test=HERE/'test_polyu_saved64_site_selection_v1_draft_20261014.py';helper=HERE/'polyu_saved64_site_selection_v1_draft_20261014.py'
 log=run('actual-selection-tests',[sys.executable,str(test),'-v']);text=log.read_text();assert 'Ran 3 tests'in text and '\nOK\n'in text
 validation=P/'helper-validation.json';save(validation,dict(passedTests=3,failedTests=0,exitCode=0,executedCodeRefs=[ref(helper),ref(test)],evidenceRefs=[ref(helper),ref(test),ref(log)]));outputs.append(ref(validation))
 run('actual-import',[sys.executable,'-c',"import sys;sys.path.insert(0,"+repr(str(HERE))+");import "+CALLER.stem+";print('IMPORT PASS')"])
 run('actual-schema',[sys.executable,str(CALLER),'--schema-only'])
 closure=P/'literal-runtime-closure.json'
 code="import fs from 'node:fs';import assert from 'node:assert/strict';import {snapshotModuleClosure,verifyModuleClosure} from './source-scripts/city/government-import/exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs';const root=new URL('./',import.meta.url);const c=snapshotModuleClosure(new URL("+json.dumps(str(RUNTIME.relative_to(ROOT)))+",root),root);assert.equal(c.schema,'exact-literal-static-dynamic-resource-closure-v1');assert(c.computedImportsRejected&&c.completeAuditedLiteralImportClosure&&c.opaqueResourcesAreNotParsedModules);assert.equal(c.unsupportedDynamicImports,0);verifyModuleClosure(c,root);fs.writeFileSync("+json.dumps(str(closure))+",JSON.stringify(c)+'\\n',{flag:'wx'});console.log(JSON.stringify({files:Object.keys(c.inputHashes).length,passed:true}));"
 run('actual-literal-closure',['node','--input-type=module','-e',code]);c=json.loads(closure.read_bytes());outputs.append(ref(closure))
 for path,h in c['inputHashes'].items():assert ref(ROOT/path)==dict(path=path,sha256=h);outputs.append(dict(path=path,sha256=h))
 fence();evidence={q['path']:q for q in outputs+[ref(Path(__file__)),ref(P/'draft-pins.json')]}
 save(P/'actual-readonly-preparation.json',dict(passed=True,caller=ref(CALLER),runtime=ref(RUNTIME),helperValidationRef=ref(validation),literalClosureRef=ref(closure),commands=commands,
  beforeEndAllDeclaredPinsVerified=True,literalTransitivePythonCodeRefs=pins['codeRefs'],evidenceRefs=[evidence[p]for p in sorted(evidence)],noMAXRayValidatorSourceDecodeDBLease=True))
 print(json.dumps(dict(preparation=ref(P/'actual-readonly-preparation.json'),passed=True,commands=len(commands))))
if __name__=='__main__':main()
