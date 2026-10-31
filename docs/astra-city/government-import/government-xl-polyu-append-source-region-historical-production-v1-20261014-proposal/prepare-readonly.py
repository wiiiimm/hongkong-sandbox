"""UNEXECUTED six fixtures/import/schema/strict literal closure only."""
from pathlib import Path
import ast,hashlib,json,os,re,subprocess,sys
P=Path(__file__).resolve().parent;ROOT=P.parents[3];HERE=ROOT/'source-scripts/city/government-import';SHARED=HERE.parent/'shared-modelling';PY='/tmp/astra-city-venv/bin/python'
CALLER=HERE/'polyu_append_source_region_historical_production_caller_v1_draft_20261014.py';RUNTIME=HERE/'polyu_append_source_region_historical_production_runtime_v1_draft_20261014.mjs'
HELPER=HERE/'polyu_append_historical_capture_binding_v1_draft_20261014.py';TEST=HERE/'test_polyu_append_historical_capture_binding_v1_draft_20261014.py'
sys.path.insert(0,str(HERE))
from exact_distinct_evidence_refs_v1_20261014 import distinct_refs
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def write(p,v):
    with p.open('x')as f:json.dump(v,f,indent=2,sort_keys=True);f.write('\n')
def main():
    pins=json.loads((P/'draft-pins.json').read_text());assert pins['caller']==ref(CALLER)and pins['runtime']==ref(RUNTIME)
    def fence():
        for q in distinct_refs(pins['codeRefs']+pins['inputRefs']):assert ref(ROOT/q['path'])==q,q['path']
    fence();folder=P/'closed-readonly-preparation';folder.mkdir();commands=[];env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')
    def run(name,cmd):
        log=folder/(name+'.log')
        with log.open('xb')as f:r=subprocess.run(cmd,cwd=ROOT,env=env,stdout=f,stderr=subprocess.STDOUT)
        commands.append(dict(command=cmd,exitCode=r.returncode,log=ref(log)));fence();assert r.returncode==0,name;return log
    try:
        log=run('six-append-historical-binding-fixtures',[PY,str(TEST)]);assert re.search(r'Ran 6 tests\b',log.read_text())
        validation=P/'binding-validation.json';write(validation,dict(passedTests=6,failedTests=0,exitCode=0,executedCodeRefs=[ref(HELPER),ref(TEST)],evidenceRefs=[ref(HELPER),ref(TEST),ref(log)]))
        run('isolated-import',[PY,'-c',"import sys,importlib.util;sys.path.insert(0,sys.argv[1]);s=importlib.util.spec_from_file_location('append_historical_production',sys.argv[2]);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);print('isolated import PASS; no main/owned')",str(HERE),str(CALLER)])
        run('schema-only',[PY,str(CALLER),'--schema-only'])
        script="import assert from 'node:assert/strict';import {pathToFileURL} from 'node:url';import {snapshotModuleClosure,verifyModuleClosure} from './source-scripts/city/government-import/exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs';const root=pathToFileURL(process.argv[2]+'/'),closure=snapshotModuleClosure(pathToFileURL(process.argv[1]),root);assert(closure.computedImportsRejected&&closure.completeAuditedLiteralImportClosure);assert.equal(closure.unsupportedDynamicImports,0);verifyModuleClosure(closure,root);console.log(JSON.stringify({passed:true,closure,noProductionImport:true}));"
        closure_log=run('strict-literal-runtime-closure',['node','--input-type=module','-e',script,str(RUNTIME),str(ROOT)])
        value=json.loads(closure_log.read_text());assert value['passed']and value['noProductionImport'];closure=value['closure']
        closure_path=P/'strict-literal-runtime-closure.json';write(closure_path,value)
        closure_refs=distinct_refs([dict(path=p,sha256=h)for p,h in closure['inputHashes'].items()])
        for q in closure_refs:assert ref(ROOT/q['path'])==q
        declared={q['path']:q['sha256']for q in pins['codeRefs']};pending=[CALLER,HELPER,TEST,HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py'];seen=set();imports=[]
        while pending:
            p=pending.pop()
            if p in seen:continue
            seen.add(p);q=ref(p);assert declared[q['path']]==q['sha256'];imports.append(q)
            for n in ast.walk(ast.parse(p.read_text(),filename=str(p))):
                names=([a.name for a in n.names]if isinstance(n,ast.Import)else[n.module]if isinstance(n,ast.ImportFrom)and n.module else[])
                for name in names:
                    for parent in [HERE,SHARED]:
                        local=parent/(name.split('.')[0]+'.py')
                        if local.is_file():pending.append(local);break
        fence()
        for q in closure_refs:assert ref(ROOT/q['path'])==q
        write(P/'actual-readonly-preparation.json',dict(passed=True,caller=ref(CALLER),runtime=ref(RUNTIME),bindingValidationRef=ref(validation),commands=commands,
            transitiveLiteralPythonRefs=sorted(imports,key=lambda q:q['path']),strictLiteralClosureRef=ref(closure_path),historicalReplay=True,currentAcceptance=False,
            beforeEndAllDeclaredPinsVerified=True,noSourceDecodePackingFiniteCaptureDBLeaseOrProductionImport=True,evidenceRefs=distinct_refs([ref(Path(__file__)),ref(validation),ref(closure_path)]+[q['log']for q in commands]+imports+closure_refs)))
        print(json.dumps(dict(passed=True,preparation=ref(P/'actual-readonly-preparation.json'),fixturesPassed=6,commands=len(commands))))
    except BaseException as e:
        fence();write(P/'actual-preparation-failure.json',dict(passed=False,errorType=type(e).__name__,message=str(e),commands=commands,beforeEndAllDeclaredPinsVerified=True,noWorkerOrLease=True));raise
if __name__=='__main__':main()
