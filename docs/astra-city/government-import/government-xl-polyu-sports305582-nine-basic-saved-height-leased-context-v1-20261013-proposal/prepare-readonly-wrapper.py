from pathlib import Path
import sys,json,subprocess,ast
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT/'source-scripts/city/government-import'))
import polyu_nine_basic_saved_height_leased_wrapper_v1_20261013 as a
P=Path(__file__).parent;pins=a.read(P/'draft-pins.json');refs=pins['codeRefs']+pins['inputRefs']+[a.ref(P/'draft-pins.json'),a.ref(Path(__file__))]
folders=[a.HERE,a.HERE.parent/'shared-modelling',a.HERE.parent/'citywide-native',a.HERE.parent/'island-detail-integration',ROOT/'docs/astra-city/mui-wo-buildings/review',a.HERE.parent/'assembly-support-review']
todo=[Path(a.__file__),a.PRODUCER,a.FREEZER];seen=set();transitive=[];declared={q['path']:q for q in pins['codeRefs']}
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
for q in refs:a.check(q)
assert not a.DOC.exists()and not a.LOCAL.exists();commands=[]
def run(cmd,name):
 path=P/name;assert not path.exists();r=subprocess.run(cmd,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT);path.write_bytes(r.stdout);commands.append(dict(command=cmd,exitCode=r.returncode,log=a.ref(path)));assert r.returncode==0,(cmd,r.returncode,path)
run([sys.executable,str(Path(a.__file__)),'--schema-only'],'actual-schema-only-v2.log')
schema=json.loads((P/'actual-schema-only-v2.log').read_text());assert schema['passed']and schema['completeAffectedActors']==25 and len(schema['canonicalResources'])==51 and schema['nineSelectedDiagnosticActors']==9 and schema['fullInputPins']>=8830 and schema['completeSourceBodies']==21 and schema['originalNegativesPerMode']==752 and schema['retainedNative59527BeforeAfterPending']
for q in refs:a.check(q)
for q in transitive:assert q==a.ref(a.check(q))
assert not a.DOC.exists()and not a.LOCAL.exists()
summary=dict(passed=True,caller=a.ref(Path(a.__file__)),producer=a.ref(a.PRODUCER),driver=a.ref(Path(__file__)),commands=commands,schemaVerbatim=schema,codePinCount=len(pins['codeRefs']),inputPinCount=len(pins['inputRefs']),transitiveLocalPythonImports=sorted(transitive,key=lambda q:q['path']),existingHelperFiveTestReceiptReusedUnchanged=True,noNumericalContextDBLeaseWorkerOrAcceptance=True,evidenceRefs=[a.ref(Path(__file__)),a.ref(P/'draft-pins.json')]+[r['log']for r in commands]+transitive)
a.save(P/'actual-readonly-preparation.json',summary);print(json.dumps(summary,sort_keys=True))
