"""UNEXECUTED ROOT preparation: fixtures/import/schema/syntax/literal closures.

No actual production imports, native decode, capture, finite math, DB or lease.
"""
from pathlib import Path
import argparse,hashlib,importlib.util,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[4];HERE=ROOT/'source-scripts/city/government-import';PROPOSAL=Path(__file__).resolve().parent
CALLER=HERE/'polyu_parent_cell_actual_production_capture_v4_draft_20261014.py'
RUNTIME=HERE/'polyu_parent_cell_actual_production_runtime_v4_draft_20261014.mjs'
sys.path.insert(0,str(HERE))
from exact_distinct_evidence_refs_v1_20261014 import distinct_refs
TEST=HERE/'test_polyu_compact_runtime_mesh_projection_v1_draft_20261014.py';HELPER=HERE/'polyu_compact_runtime_mesh_projection_v1_draft_20261014.py';JSHELPER=HERE/'polyu_compact_runtime_mesh_projection_v1_draft_20261014.mjs'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def read(p):return json.loads(p.read_text())
def check(q):
 p=ROOT/q['path'];assert ref(p)==q;return p
def import_child():
 sys.path.insert(0,str(HERE));spec=importlib.util.spec_from_file_location('polyu_capture_v2_readonly_import',CALLER);m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
 files={}
 for mod in tuple(sys.modules.values()):
  path=getattr(mod,'__file__',None)
  if path:
   p=Path(path).resolve()
   if p.is_relative_to(ROOT)and p.is_file():files[str(p.relative_to(ROOT))]=ref(p)
 print(json.dumps(dict(importPassed=True,caller=ref(CALLER),transitiveLocalCodeRefs=[files[k]for k in sorted(files)]),sort_keys=True))
def prepare():
 output=PROPOSAL/'actual-readonly-preparation.json';assert not output.exists();logs=PROPOSAL/'closed-readonly-preparation';logs.mkdir(exist_ok=False)
 pins=read(PROPOSAL/'draft-pins.json');assert pins['caller']==ref(CALLER)and pins['runtime']==ref(RUNTIME)
 refs=distinct_refs(pins['codeRefs']+pins['inputRefs']);known={q['path']:q for q in refs};commands=[];closures=[];imports=[];schema=None;failure=None;end_errors=[]
 def command(label,args):
  log=logs/(label+'.log')
  with log.open('wb')as stream:r=subprocess.run(args,cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT)
  commands.append(dict(label=label,command=args,exitCode=r.returncode,logRef=ref(log)));assert r.returncode==0,label+' failed; preserve actual log'
  return log
 try:
  for q in refs:check(q)
  testlog=command('eight-projection-fixtures',[sys.executable,str(TEST)])
  text=testlog.read_text();assert 'Ran 8 tests'in text and text.rstrip().endswith('OK')
  validation=dict(passedTests=8,failedTests=0,exitCode=0,executedCodeRefs=[ref(HELPER),ref(JSHELPER),ref(TEST)],evidenceRefs=[ref(HELPER),ref(JSHELPER),ref(TEST),ref(testlog)])
  validation_path=PROPOSAL/'projection-validation.json';assert not validation_path.exists();validation_path.write_text(json.dumps(validation,sort_keys=True,indent=2)+'\n')
  imported=json.loads(command('isolated-import',[sys.executable,__file__,'--import-child']).read_text());assert imported['importPassed'];imports=imported['transitiveLocalCodeRefs']
  for q in imports:assert known.get(q['path'])==q,'Unexpected unpinned local import '+q['path'];check(q)
  schema=json.loads(command('schema-only',[sys.executable,str(CALLER),'--schema-only']).read_text());assert schema['passed']and schema['completeNewNativeFacets']==pins['completeNewNativeFacets']and schema['completeNewRawSHA256']==pins['completeNewRawSHA256']
  command('runtime-syntax',['node','--check',str(RUNTIME)])
  # This imports only the reviewed dependency auditor, never viewer modules.
  audit="""import {snapshotModuleClosure,verifyModuleClosure} from './source-scripts/city/government-import/exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs';import {pathToFileURL} from 'node:url';import assert from 'node:assert/strict';const root=pathToFileURL(process.cwd()+'/');const rows=process.argv.slice(1).map(p=>snapshotModuleClosure(new URL(p,root),root));for(const c of rows){assert.equal(c.schema,'exact-literal-static-dynamic-resource-closure-v1');assert(c.computedImportsRejected&&c.completeAuditedLiteralImportClosure&&c.opaqueResourcesAreNotParsedModules);assert.equal(c.unsupportedDynamicImports,0);assert.deepEqual(Object.keys(c.inputHashes).sort(),[...c.modules,...c.resources].sort());verifyModuleClosure(c,root);}console.log(JSON.stringify(rows));"""
  log=command('strict-literal-runtime-closures',['node','--input-type=module','-e',audit,str(RUNTIME.relative_to(ROOT))]);closures=json.loads(log.read_text())
  for c in closures:
   for p,h in c['inputHashes'].items():assert known.get(p)==dict(path=p,sha256=h),'Unpinned literal closure input '+p;check(dict(path=p,sha256=h))
 except BaseException as error:failure=dict(type=type(error).__name__,message=str(error))
 finally:
  for q in distinct_refs(refs+imports):
   try:check(q)
   except (AssertionError,OSError)as error:end_errors.append(dict(ref=q,error=str(error)))
 passed=failure is None and not end_errors;evidence={q['path']:q for q in imports+[c['logRef']for c in commands]+[ref(PROPOSAL/'draft-pins.json'),ref(Path(__file__).resolve())]}
 validation_path=PROPOSAL/'projection-validation.json'
 if validation_path.exists():evidence[str(validation_path.relative_to(ROOT))]=ref(validation_path)
 result=dict(passed=passed,caller=ref(CALLER),runtime=ref(RUNTIME),exactSourceActorInputsReusedFromJob=pins['previousCompleteCaptureJob'],commands=commands,schemaVerbatim=schema,completeStrictLiteralRuntimeClosures=closures,transitiveLocalCodeRefs=imports,declaredCodeRefs=len(pins['codeRefs']),declaredInputRefs=len(pins['inputRefs']),endPinFailures=end_errors,actualFailure=failure,beforeEndAllDeclaredPinsVerified=passed,noProductionRuntimeImportOrNativeDecodeOrFiniteDBLease=True,evidenceRefs=[evidence[k]for k in sorted(evidence)])
 if validation_path.exists():result['projectionValidationRef']=ref(validation_path)
 binding_path=ROOT/'docs/astra-city/government-import/government-xl-polyu-parent-cell-actual-production-capture-v3-20261014-proposal/binding-validation.json'
 binding=read(binding_path);assert binding['passedTests']==8 and binding['failedTests']==0 and binding['exitCode']==0
 for q in binding['evidenceRefs']:check(q)
 result['bindingValidationRef']=ref(binding_path);result['evidenceRefs']=distinct_refs(result['evidenceRefs']+[ref(binding_path)]+binding['evidenceRefs'])
 target=output if passed else PROPOSAL/'actual-readonly-preparation-failure.json';assert not target.exists();target.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
 print(json.dumps(dict(passed=passed,preparationRef=ref(target),actualFailure=failure,endPinFailures=len(end_errors),commands=commands),sort_keys=True));return 0 if passed else 2
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);m=p.add_mutually_exclusive_group(required=True);m.add_argument('--import-child',action='store_true');m.add_argument('--prepare-only',action='store_true');a=p.parse_args()
 if a.import_child:import_child()
 else:sys.exit(prepare())
