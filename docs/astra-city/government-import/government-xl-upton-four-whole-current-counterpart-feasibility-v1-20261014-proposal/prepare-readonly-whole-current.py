from pathlib import Path
import sys,json,subprocess,ast
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT/'source-scripts/city/government-import'))
import upton_four_whole_current_counterpart_feasibility_v1_20261014 as a
P=Path(__file__).parent;pins=a.read(P/'draft-pins.json');refs=pins['codeRefs']+pins['inputRefs']+[a.ref(Path(__file__)),a.ref(P/'draft-pins.json')]
folders=[a.HERE,a.HERE.parent/'shared-modelling',a.HERE.parent/'citywide-native',a.HERE.parent/'island-detail-integration',ROOT/'docs/astra-city/mui-wo-buildings/review',a.HERE.parent/'assembly-support-review']
todo=[Path(a.__file__)];seen=set();transitive=[];declared={q['path']:q for q in pins['codeRefs']}
while todo:
 path=todo.pop().resolve()
 if path in seen:continue
 seen.add(path);q=a.ref(path);assert q==declared[q['path']];transitive.append(q)
 for n in ast.walk(ast.parse(path.read_text())):
  names=[n.module]if isinstance(n,ast.ImportFrom)and n.module else[q.name for q in n.names]if isinstance(n,ast.Import)else[]
  for name in names:
   for folder in folders:
    q=folder/(name.replace('.','/')+'.py')
    if q.is_file():todo.append(q)
closure=a.read(a.capture.PROPOSAL/'actual-literal-runtime-closure-preflight.json');assert closure['computedImportsRejected'] and closure['completeAuditedLiteralImportClosure'] and closure['unsupportedDynamicImports']==0
literal=[dict(path=k,sha256=v)for k,v in closure['inputHashes'].items()];assert len(literal)==24
refs+=[a.ref(a.capture.PROPOSAL/'actual-literal-runtime-closure-preflight.json')]+literal
for q in refs:a.check(q)
assert not a.DOC.exists() and not a.LOCAL.exists();commands=[]
def run(cmd,name,cwd=ROOT):
 path=P/name;assert not path.exists();r=subprocess.run(cmd,cwd=cwd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT);path.write_bytes(r.stdout);commands.append(dict(command=cmd,exitCode=r.returncode,log=a.ref(path)));assert r.returncode==0,(cmd,r.returncode,path)
run([sys.executable,'-m','unittest','-v']+a.TESTS,'actual-byte-prefix-and-existing-pair-fixtures.log',a.HERE)
run([sys.executable,str(Path(a.__file__)),'--schema-only'],'actual-schema-only.log');schema=json.loads((P/'actual-schema-only.log').read_text());assert schema['passed'] and schema['completeCurrentCounterpartIDs']==a.IDS and schema['actualFreshForeignFailureRows']==12 and schema['oldCandidateFacets']==11606 and schema['completeCurrentGroundDrawnFacets']==11634 and schema['wholeActorScope']==6650 and schema['completeBasicRecords']==1911 and schema['wholeAffectedBasicActors']==52
for q in refs:a.check(q)
assert a.ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==a.baseline.CURRENT and not a.DOC.exists() and not a.LOCAL.exists()
a.save(P/'actual-readonly-preparation.json',dict(passed=True,caller=a.ref(Path(a.__file__)),driver=a.ref(Path(__file__)),method=a.ref(P/'METHOD.md'),fallbackPlan=a.ref(P/'PACKED-ENCLOSURE-FALLBACK.md'),commands=commands,schemaVerbatim=schema,allCodeInputHashesVerifiedBeforeAndEnd=True,transitiveLocalPythonImports=transitive,strictLiteralDependencyRefs=literal,evidenceRefs=[a.ref(Path(__file__)),a.ref(P/'draft-pins.json'),a.ref(a.capture.PROPOSAL/'actual-literal-runtime-closure-preflight.json')]+[q['log']for q in commands]+literal+transitive,noPairFinitePackingNominationSourceCalculationDBLeaseOrWorker=True))
print(json.dumps(dict(passed=True,codePins=len(pins['codeRefs']),inputPins=len(pins['inputRefs']),pythonClosure=len(transitive),literalClosure=len(literal),wholeCurrentIDs=a.IDS,freshRows=12)))
