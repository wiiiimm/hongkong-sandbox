from pathlib import Path
import json,hashlib,subprocess,time,traceback
R=Path('/home/williamli/projects/wiiiimm/hongkong-sandbox/.claude/worktrees/astra-hong-kong-city');H=R/'source-scripts/city/government-import';P=R/'docs/astra-city/government-import/government-xl-upton-v6-saved-actual-union-finite-regression-v1-20261013-proposal'
def ref(p):return dict(path=str(p.relative_to(R)),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def read(p):return json.loads(p.read_bytes())
def save(p,v):assert not p.exists(),p;p.write_text(json.dumps(v,sort_keys=True,indent=2)+'\n')
pins=read(P/'draft-pins.json');assert pins['caller']['sha256']=='b46d289ed331231a9826889f0feb0ad12c32fdb70d400c5381401321f61cfb31';declared=pins['codeRefs']+pins['inputRefs']+[ref(P/'draft-pins.json')]
def fence():
 for q in declared:assert ref(R/q['path'])==q,q
 assert ref(R/'3d-viewer/city/data/manifest.json')['sha256']=='c00fd9f731b1bcbf4d2df6067a5cb3231f0eaa8c503a8adea584fec39bf73bf7'
fence();start=time.time();results=[];failure=None;schema=None;closure=None
print('declared-before PASS',len(declared),flush=True)
def command(name,args,cwd):
 p=P/name;assert not p.exists()
 with p.open('wb')as log:code=subprocess.run(args,cwd=cwd,stdout=log,stderr=subprocess.STDOUT).returncode
 row=dict(command=args,cwd=str(cwd),exitCode=code,log=ref(p));results.append(row);print(json.dumps(row),flush=True);return code,p
try:
 py='/tmp/astra-city-venv/bin/python';caller=R/pins['caller']['path']
 ic,log=command('actual-caller-import-smoke.log',[py,'-c','import '+caller.stem+'; print("actual import PASS")'],H);assert ic==0,log.read_text()
 sc,log=command('actual-schema-only.log',[py,str(caller),'--schema-only'],R);assert sc==0,log.read_text()
 schema=read(log);assert schema['passed']and schema['caller']==pins['caller'];save(P/'schema-preflight.json',schema)
 helper=H/'exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs';acorn=H/'dependency-closure-vendor/acorn-8.8.1/acorn.mjs'
 assert ref(helper)['sha256']=='c91ebfa352d1f610c832f882ff1e156ab0c3a4e1c04a9d4d44937e0234238579'and ref(acorn)['sha256']=='a8524d1734aecc543068d3c801aba2b6ad8f68dd7d751bace79d783f8ecd9e55'
 js="""import {snapshotModuleClosure,verifyModuleClosure} from './source-scripts/city/government-import/exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs';import {writeFileSync} from 'node:fs';import assert from 'node:assert/strict';const root=new URL('./',import.meta.url),entry=new URL('source-scripts/city/government-import/upton_v6_saved64_actual_max_full_ray_runtime_draft_v1_20261013.mjs',root);const c=snapshotModuleClosure(entry,root);assert.equal(c.schema,'exact-literal-static-dynamic-resource-closure-v1');assert(c.computedImportsRejected&&c.completeAuditedLiteralImportClosure&&c.opaqueResourcesAreNotParsedModules);assert.equal(c.unsupportedDynamicImports,0);verifyModuleClosure(c,root);writeFileSync(new URL('docs/astra-city/government-import/government-xl-upton-v6-saved-actual-union-finite-regression-v1-20261013-proposal/literal-completed-runtime-closure-preflight.json',root),JSON.stringify(c,null,2)+'\\n');console.log(JSON.stringify({passed:true,entryPath:c.entryPath,computedImportsRejected:c.computedImportsRejected,unsupportedDynamicImports:c.unsupportedDynamicImports,inputFiles:Object.keys(c.inputHashes).length,noProductionImportOrNumericalRuntime:true}));"""
 cc,log=command('actual-strict-literal-closure.log',['node','--input-type=module','-e',js],R);assert cc==0,log.read_text();closure=read(P/'literal-completed-runtime-closure-preflight.json')
 for path,h in closure['inputHashes'].items():assert ref(R/path)['sha256']==h
except BaseException as e:
 failure=dict(type=type(e).__name__,message=str(e),traceback=traceback.format_exc());print('PREPARATION FAILED '+repr(e),flush=True)
fence();print('declared-after PASS',len(declared),flush=True)
out=P/('actual-readonly-preparation.json'if failure is None else'actual-failed-readonly-preparation.json')
summary=dict(passed=failure is None,elapsedSeconds=time.time()-start,caller=pins['caller'],method=pins['method'],draftPins=ref(P/'draft-pins.json'),preparationWrapper=ref(Path(__file__)),declaredPinsVerifiedBeforeAndAfter=True,declaredPinCount=len(declared),declaredPins=declared,actualCommands=results,failure=failure,schema=ref(P/'schema-preflight.json')if schema is not None else None,literalClosure=ref(P/'literal-completed-runtime-closure-preflight.json')if closure is not None else None,literalClosureRefs=[dict(path=k,sha256=v)for k,v in closure['inputHashes'].items()]if closure else[],currentManifest=ref(R/'3d-viewer/city/data/manifest.json'),noLeaseDBOrFiniteWorker=True)
save(out,summary);print(json.dumps(dict(result=ref(out),passed=summary['passed']),indent=2),flush=True)
raise SystemExit(0 if failure is None else 1)
