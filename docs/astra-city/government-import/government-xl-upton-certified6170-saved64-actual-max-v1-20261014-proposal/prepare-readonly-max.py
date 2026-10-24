from pathlib import Path
import sys,json,subprocess,ast
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT/'source-scripts/city/government-import'))
import upton_certified6170_saved64_actual_max_v1_20261014 as a
P=Path(__file__).parent;codeonly='--code-only'in sys.argv;assert codeonly or '--bind-completed-capture-readonly'in sys.argv
assert not a.DOC.exists() and not a.LOCAL.exists();prefix='code-only-'if codeonly else 'actual-';commands=[]
def run(cmd,name,cwd=ROOT):
 path=P/(prefix+name);assert not path.exists();r=subprocess.run(cmd,cwd=cwd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT);path.write_bytes(r.stdout);commands.append(dict(command=cmd,exitCode=r.returncode,log=a.ref(path)));assert r.returncode==0
old=ROOT/'source-scripts/city/government-import/upton_scoped_subdivision_saved64_max_runtime_draft_v1_20261013.mjs'
assert a.RUNTIME.read_text()==old.read_text().replace('assert.equal(candidate.nativeMesh.index.length/3,11576)','assert.equal(candidate.nativeMesh.index.length/3,input.completeNewNativeFacets)').replace('completeCandidateFacets:11576','completeCandidateFacets:input.completeNewNativeFacets'), 'entire MAX/ray runtime unchanged except count binding'
run(['node','--check',str(a.RUNTIME)],'runtime-syntax.log');run([sys.executable,'-c',"import sys;sys.path.insert(0,'source-scripts/city/government-import');import "+Path(a.__file__).stem+";print('isolated import PASS; no arrays/numerical/production/DB/lease')"],'isolated-import.log')
closurepath=P/(prefix+'literal-runtime-closure-preflight.json')
script="import assert from 'node:assert/strict';import {writeFileSync} from 'node:fs';import {pathToFileURL} from 'node:url';import {snapshotModuleClosure,verifyModuleClosure} from './source-scripts/city/government-import/exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs';const root=pathToFileURL(process.cwd()+'/'),entry=new URL("+json.dumps(str(a.RUNTIME.relative_to(ROOT)))+",root),c=snapshotModuleClosure(entry,root);assert(c.computedImportsRejected&&c.completeAuditedLiteralImportClosure);assert.equal(c.unsupportedDynamicImports,0);assert(verifyModuleClosure(c,root));writeFileSync(new URL("+json.dumps(str(closurepath.relative_to(ROOT)))+",root),JSON.stringify(c,null,2)+'\\n',{flag:'wx'});console.log(JSON.stringify({passed:true,files:Object.keys(c.inputHashes).length,noProductionImport:true}));"
run(['node','--input-type=module','-e',script],'literal-runtime-closure.log');closure=a.read(closurepath);literal=[dict(path=k,sha256=v)for k,v in closure['inputHashes'].items()]
folders=[a.HERE,a.HERE.parent/'shared-modelling',a.HERE.parent/'citywide-native',a.HERE.parent/'island-detail-integration',ROOT/'docs/astra-city/mui-wo-buildings/review',a.HERE.parent/'assembly-support-review'];todo=[Path(a.__file__)];seen=set();transitive=[]
while todo:
 p=todo.pop().resolve()
 if p in seen:continue
 seen.add(p);transitive.append(a.ref(p))
 for n in ast.walk(ast.parse(p.read_text())):
  names=[n.module]if isinstance(n,ast.ImportFrom)and n.module else[q.name for q in n.names]if isinstance(n,ast.Import)else[]
  for name in names:
   for folder in folders:
    q=folder/(name.replace('.','/')+'.py')
    if q.is_file():todo.append(q)
refs=literal+transitive+[a.ref(Path(__file__)),a.ref(P/'METHOD.md'),a.ref(closurepath),a.ref(old)]+[q['log']for q in commands]
for q in refs:a.check(q)
if codeonly:
 assert not (P/'draft-pins.json').exists();a.save(P/'code-only-preparation.json',dict(passed=True,caller=a.ref(Path(a.__file__)),runtime=a.ref(a.RUNTIME),entireRuntimeUnchangedExceptDynamicCount=True,commands=commands,transitiveLocalPythonImports=transitive,strictLiteralDependencyRefs=literal,evidenceRefs=refs,finalActualCaptureCountHashReceiptUnbound=True,notReadyForWorker=True,noArraysNumericalProofProductionDBLease=True));print(json.dumps(dict(passed=True,codeOnly=True,pythonClosure=len(transitive),literalClosure=len(literal))));raise SystemExit
receipt=a.read(a.capture.DOC/'result.json');v=a.read(a.capture.DOC/'ROOT-VERIFIED.json');assert v['jobId']==receipt['jobId'] and v['exactNeonReadback'] and v['allEvidenceHashesVerified'] and v['leaseReleased']
cap=a.read(a.capture.PROPOSAL/'draft-pins.json');codes={q['path']:q for q in cap['codeRefs']};inputs={q['path']:q for q in cap['inputRefs']}
for q in transitive+literal+[a.ref(a.RUNTIME),a.ref(old)]:codes[q['path']]=q
for folder,names in [(a.capture.DOC,['result.json','ROOT-VERIFIED.json','actual-production-replay.json.gz','private-native-terrain-candidate.json.gz','new-scoped-geometry-measured-overlap.json.gz','real-validator-outcome.json']),(a.capture.PROPOSAL,['draft-pins.json','actual-readonly-preparation.json'])]:
 for name in names:q=a.ref(folder/name);inputs[q['path']]=q
m=a.read(a.capture.DOC/'new-scoped-geometry-measured-overlap.json.gz')['measured'];pins=dict(caller=a.ref(Path(a.__file__)),runtime=a.ref(a.RUNTIME),completedCaptureJob=receipt['jobId'],completeNewNativeFacets=m['completeCandidateFaces'],geometryCanonicalSHA256=m['candidateGeometryCanonicalSHA256'],actualMeasuredExcessM2=m['nativeProjectedExcessM2'],codeRefs=sorted(codes.values(),key=lambda q:q['path']),inputRefs=sorted(inputs.values(),key=lambda q:q['path']),sourceOnly=True,physicalAccepted=False)
assert not (P/'draft-pins.json').exists();a.save(P/'draft-pins.json',pins)
for q in pins['codeRefs']+pins['inputRefs']:a.check(q)
run([sys.executable,str(Path(a.__file__)),'--schema-only'],'schema-only.log');schema=json.loads((P/'actual-schema-only.log').read_text());assert schema['passed'] and schema['actualSavedSites']==64
for q in pins['codeRefs']+pins['inputRefs']+refs:a.check(q)
assert a.ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==a.capture.legacy.CURRENT and not a.DOC.exists() and not a.LOCAL.exists()
refs+=[a.ref(P/'draft-pins.json')]+[q['log']for q in commands];a.save(P/'actual-readonly-preparation.json',dict(passed=True,caller=a.ref(Path(a.__file__)),runtime=a.ref(a.RUNTIME),driver=a.ref(Path(__file__)),schemaVerbatim=schema,entireRuntimeUnchangedExceptDynamicCount=True,commands=commands,transitiveLocalPythonImports=transitive,strictLiteralDependencyRefs=literal,allCodeInputPinsVerifiedBeforeAndEnd=True,evidenceRefs=refs,noNumericalMAXRaySourceProofDBLeaseOrWorker=True));print(json.dumps(dict(passed=True,codePins=len(codes),inputPins=len(inputs),pythonClosure=len(transitive),literalClosure=len(literal))))
