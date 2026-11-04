from pathlib import Path
import sys,json,subprocess,ast
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT/'source-scripts/city/government-import'))
import upton_full22_original_current_restoration_feasibility_v1_20261014 as a
P=Path(__file__).parent;pins=a.read(P/'draft-pins.json');refs=pins['codeRefs']+pins['inputRefs']+[a.ref(P/'draft-pins.json'),a.ref(Path(__file__))]
assert len(pins['codeRefs'])>=59 and len(pins['inputRefs'])>=139
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
closure=a.read(a.finite.capture.PROPOSAL/'literal-runtime-closure-preflight.json');assert closure['computedImportsRejected']and closure['completeAuditedLiteralImportClosure']and closure['unsupportedDynamicImports']==0
literal=[dict(path=k,sha256=v)for k,v in closure['inputHashes'].items()];refs+=[a.ref(a.finite.capture.PROPOSAL/'literal-runtime-closure-preflight.json')]+literal
for q in refs:a.check(q)
assert not a.DOC.exists()and not a.LOCAL.exists();commands=[]
def run(cmd,name,cwd=ROOT):
 path=P/name;assert not path.exists();r=subprocess.run(cmd,cwd=cwd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT);path.write_bytes(r.stdout)
 commands.append(dict(command=cmd,exitCode=r.returncode,log=a.ref(path)));assert r.returncode==0,(cmd,r.returncode,path)
run([sys.executable,'-c',"import sys;sys.path.insert(0,'source-scripts/city/government-import');import upton_full22_original_current_restoration_feasibility_v1_20261014;print('isolated import PASS; no numerical proof/source decode/DB/lease')"],'actual-isolated-import.log')
run([sys.executable,'-m','unittest','-v',a.TEST,'test_upton_six_basic_preserved_ground_feasibility_v1_20261012'],'actual-existing-coverage-fixtures.log',a.HERE)
run([sys.executable,str(Path(a.__file__)),'--schema-only'],'actual-schema-only.log')
schema=json.loads((P/'actual-schema-only.log').read_text());assert schema['passed']and schema['wholeResidualPolygons']==22 and schema['wholeResidualBoundaryEdges']==80 and schema['savedAllFourWorldRows']==12 and schema['completeCurrentFacets']==9214 and schema['completeOriginalTINFacets']==122721 and schema['completeNativeActorScope']==6650 and schema['completeOwnedFacesPerMode']==13312 and schema['completeBasicRows']==1911 and schema['affectedBasicActors']==52 and schema['affectedBasicSelectedFacets']==2114 and schema['protectedLiteralCurrentFacets']==68
for q in refs:a.check(q)
for q in transitive:assert q==a.ref(a.check(q))
assert a.ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==a.baseline.CURRENT
assert not a.DOC.exists()and not a.LOCAL.exists()
summary=dict(passed=True,caller=a.ref(Path(a.__file__)),method=a.ref(P/'METHOD.md'),driver=a.ref(Path(__file__)),commands=commands,schemaVerbatim=schema,allCodeInputPinsVerifiedBeforeAndEnd=True,codePinCount=len(pins['codeRefs']),inputPinCount=len(pins['inputRefs']),transitiveLocalPythonImports=sorted(transitive,key=lambda q:q['path']),currentManifestSHA256=a.baseline.CURRENT,strictLiteralDependencyRefs=literal,noCoverageFiniteConstructorRaySourceDecodeDBOrLeaseExecuted=True,fullResidualAndClosedBoundaryAndMaskedPairOriginalKernelsUnchanged=True,evidenceRefs=[a.ref(Path(__file__)),a.ref(P/'draft-pins.json')]+[r['log']for r in commands]+transitive)
a.save(P/'actual-readonly-preparation.json',summary);print(json.dumps(summary,sort_keys=True))
