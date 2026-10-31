from pathlib import Path
import sys,json,subprocess,ast
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT/'source-scripts/city/government-import'))
import upton_full22_parent_edge_contract_diagnostic_v1_20261014 as a
P=Path(__file__).parent;pins=a.read(P/'draft-pins.json');refs=pins['codeRefs']+pins['inputRefs']+[a.ref(Path(__file__)),a.ref(P/'draft-pins.json')]
folders=[a.HERE,a.HERE.parent/'shared-modelling',a.HERE.parent/'citywide-native',a.HERE.parent/'island-detail-integration',ROOT/'docs/astra-city/mui-wo-buildings/review',a.HERE.parent/'assembly-support-review']
todo=[Path(a.__file__)];seen=set();transitive=[];declared={q['path']:q for q in pins['codeRefs']}
while todo:
 path=todo.pop().resolve()
 if path in seen:continue
 seen.add(path);q=a.ref(path);assert q==declared[q['path']];transitive.append(q)
 for n in ast.walk(ast.parse(path.read_text())):
  names=[n.module]if isinstance(n,ast.ImportFrom)and n.module else[x.name for x in n.names]if isinstance(n,ast.Import)else[]
  for name in names:
   for folder in folders:
    q=folder/(name.replace('.','/')+'.py')
    if q.is_file():todo.append(q)
helper=a.HERE/'upton_parent_edge_validator_sample_v1_20261014.py'
sample_ast=lambda path:ast.dump(next(n for n in ast.walk(ast.parse(path.read_text()))if isinstance(n,ast.FunctionDef)and n.name=='sample'),include_attributes=False)
assert sample_ast(helper)==sample_ast(a.capture.VALIDATOR)
for q in refs:a.check(q)
assert not a.DOC.exists() and not a.LOCAL.exists();commands=[]
def run(cmd,name,cwd=ROOT):
 path=P/name;assert not path.exists();r=subprocess.run(cmd,cwd=cwd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT);path.write_bytes(r.stdout);commands.append(dict(command=cmd,exitCode=r.returncode,log=a.ref(path)));assert r.returncode==0,(cmd,r.returncode,path)
run(['node','--check',str(a.RUNTIME)],'actual-runtime-syntax.log')
run([sys.executable,'-m','unittest','-v',a.TEST],'actual-existing-contract-fixtures.log',a.HERE)
script="import assert from 'node:assert/strict';import {writeFileSync} from 'node:fs';import {pathToFileURL} from 'node:url';import {snapshotModuleClosure,verifyModuleClosure} from './source-scripts/city/government-import/exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs';const root=pathToFileURL(process.cwd()+'/'),entry=new URL('source-scripts/city/government-import/upton_full22_parent_edge_sampler_context_v1_20261014.mjs',root),c=snapshotModuleClosure(entry,root);assert(c.computedImportsRejected&&c.completeAuditedLiteralImportClosure);assert.equal(c.unsupportedDynamicImports,0);assert(verifyModuleClosure(c,root));writeFileSync(new URL("+json.dumps(str((P/'literal-runtime-closure-preflight.json').relative_to(ROOT)))+",root),JSON.stringify(c,null,2)+'\\n',{flag:'wx'});console.log(JSON.stringify({passed:true,files:Object.keys(c.inputHashes).length,noProductionImport:true}));"
run(['node','--input-type=module','-e',script],'actual-literal-runtime-closure.log')
closure=a.read(P/'literal-runtime-closure-preflight.json');literal=[dict(path=k,sha256=v)for k,v in closure['inputHashes'].items()]
run([sys.executable,str(Path(a.__file__)),'--schema-only'],'actual-schema-only.log');schema=json.loads((P/'actual-schema-only.log').read_text());assert schema['passed'] and schema['savedMeasuredEdgeOccurrences']==860 and schema['savedOldParentGridFailedOccurrences']==13 and schema['savedFailedUniqueXYZ']==5 and schema['completeValidatorPositionVerticesIncludingUnused']==34818
for q in refs+literal:a.check(q)
assert a.ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==a.capture.legacy.CURRENT and not a.DOC.exists() and not a.LOCAL.exists()
a.save(P/'actual-readonly-preparation.json',dict(passed=True,caller=a.ref(Path(a.__file__)),runtime=a.ref(a.RUNTIME),driver=a.ref(Path(__file__)),method=a.ref(P/'METHOD.md'),commands=commands,schemaVerbatim=schema,literalValidatorSampleASTExactlyUnchanged=True,allCodeInputHashesVerifiedBeforeAndEnd=True,transitiveLocalPythonImports=transitive,strictLiteralDependencyRefs=literal,evidenceRefs=[a.ref(Path(__file__)),a.ref(P/'draft-pins.json'),a.ref(P/'literal-runtime-closure-preflight.json')]+[q['log']for q in commands]+literal+transitive,noParentHeightSamplerPredicateProductionSourceCalculationDBLeaseOrWorker=True))
print(json.dumps(dict(passed=True,codePins=len(pins['codeRefs']),inputPins=len(pins['inputRefs']),pythonClosure=len(transitive),literalClosure=len(literal),tests=5,savedEdgeOccurrences=860)))
