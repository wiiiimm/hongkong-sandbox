from pathlib import Path
import sys,json,subprocess,ast
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT/'source-scripts/city/government-import'))
import upton_three_own_layer_saved_actual_union_delta_draft_v1_20261013 as a
P=Path(__file__).parent;pins=a.read(P/'draft-pins.json');refs=pins['codeRefs']+pins['inputRefs']+[a.ref(P/'draft-pins.json'),a.ref(Path(__file__))]
assert len(pins['codeRefs'])>=57 and len(pins['inputRefs'])>=124
folders=[a.HERE,a.HERE.parent/'shared-modelling',a.HERE.parent/'citywide-native',a.HERE.parent/'island-detail-integration',ROOT/'docs/astra-city/mui-wo-buildings/review',a.HERE.parent/'assembly-support-review']
todo=[Path(a.__file__)];seen=set();transitive=[];declared={q['path']:q for q in pins['codeRefs']}
while todo:
 p=todo.pop().resolve()
 if p in seen:continue
 seen.add(p);r=a.ref(p);assert r==declared[r['path']];transitive.append(r)
 for n in ast.walk(ast.parse(p.read_text())):
  names=[n.module]if isinstance(n,ast.ImportFrom)and n.module else[x.name for x in n.names]if isinstance(n,ast.Import)else[]
  for name in names:
   for folder in folders:
    q=folder/(name.replace('.','/')+'.py')
    if q.is_file():todo.append(q)
def assess_ast(path):
 tree=ast.parse(path.read_text());owned=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='owned');return ast.dump(next(n for n in owned.body if isinstance(n,ast.FunctionDef)and n.name=='assess'),include_attributes=False)
assert assess_ast(Path(a.__file__))==assess_ast(Path(a.previous_delta.__file__))
closure=a.read(a.capture.PROPOSAL/'literal-runtime-closure-preflight.json');assert closure['schema']=='exact-literal-static-dynamic-resource-closure-v1'and closure['computedImportsRejected']and closure['completeAuditedLiteralImportClosure']and closure['unsupportedDynamicImports']==0 and closure['entryPath']==str(a.capture.RUNTIME.relative_to(ROOT))
literal=[dict(path=k,sha256=v)for k,v in closure['inputHashes'].items()];refs+=[a.ref(a.capture.PROPOSAL/'literal-runtime-closure-preflight.json')]+literal
for q in refs:a.check(q)
assert not a.DOC.exists()and not a.LOCAL.exists();commands=[]
def run(cmd,name):
 path=P/name;assert not path.exists();r=subprocess.run(cmd,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT);path.write_bytes(r.stdout)
 commands.append(dict(command=cmd,exitCode=r.returncode,log=a.ref(path)));assert r.returncode==0,(cmd,r.returncode,path)
run([sys.executable,'-c',"import sys;sys.path.insert(0,'source-scripts/city/government-import');import upton_three_own_layer_saved_actual_union_delta_draft_v1_20261013;print('isolated import PASS; no kernel/selection/worker/lease')"],'actual-isolated-import.log')
run([sys.executable,str(Path(a.__file__)),'--schema-only'],'actual-schema-only.log')
schema=json.loads((P/'actual-schema-only.log').read_text());assert schema['passed']and schema['newDrawnFaces']==11608 and schema['oldDrawnFaces']==11605 and schema['newGroundSHA256']==a.GROUND_SHA and schema['oldGroundSHA256']==a.previous_delta.GROUND_SHA and schema['completeNativeActorScope']==6650 and schema['affectedBasicActors']==52 and schema['completeOwnedFaces']==13312 and schema['native79882Faces']==616 and schema['secondaryForeignFaces']==392
for q in refs:a.check(q)
for q in transitive:assert q==a.ref(a.check(q))
assert a.ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==a.baseline.CURRENT
assert not a.DOC.exists()and not a.LOCAL.exists()
summary=dict(passed=True,caller=a.ref(Path(a.__file__)),method=a.ref(P/'METHOD.md'),driver=a.ref(Path(__file__)),commands=commands,schemaVerbatim=schema,allFrozenCodeInputPinsVerifiedBeforeAndEnd=True,codePinCount=len(pins['codeRefs']),inputPinCount=len(pins['inputRefs']),transitiveLocalPythonImports=sorted(transitive,key=lambda q:q['path']),strictLiteralRuntimeClosureReusedVerbatim=a.ref(a.capture.PROPOSAL/'literal-runtime-closure-preflight.json'),strictLiteralDependencyRefs=literal,currentManifestSHA256=a.baseline.CURRENT,completeAssessASTExactlyEqualToLatestRing12=True,noFiniteKernelSelectionDBLeaseWorkerOrSourceDecode=True,evidenceRefs=[a.ref(Path(__file__)),a.ref(P/'draft-pins.json'),a.ref(a.capture.PROPOSAL/'literal-runtime-closure-preflight.json')]+[r['log']for r in commands]+literal+transitive)
a.save(P/'actual-readonly-preparation.json',summary);print(json.dumps(summary,sort_keys=True))
