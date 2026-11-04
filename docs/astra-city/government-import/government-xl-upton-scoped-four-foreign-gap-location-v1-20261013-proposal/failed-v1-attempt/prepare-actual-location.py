from pathlib import Path
import sys,json,subprocess,ast
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT/'source-scripts/city/government-import'))
import upton_scoped_four_foreign_gap_location_draft_v1_20261013 as a
P=Path(__file__).parent;pins=a.read(P/'draft-pins.json');refs=pins['codeRefs']+pins['inputRefs']+[a.ref(P/'draft-pins.json'),a.ref(Path(__file__))]
assert len(pins['codeRefs'])==58 and len(pins['inputRefs'])==128
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
for q in refs:a.check(q)
assert not a.DOC.exists()and not a.LOCAL.exists();commands=[]
def run(cmd,name):
 path=P/name;assert not path.exists();r=subprocess.run(cmd,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT);path.write_bytes(r.stdout)
 commands.append(dict(command=cmd,exitCode=r.returncode,log=a.ref(path)));assert r.returncode==0,(cmd,r.returncode,path)
run([sys.executable,'-c',"import sys;sys.path.insert(0,'source-scripts/city/government-import');import upton_scoped_four_foreign_gap_location_draft_v1_20261013;print('isolated import PASS; no numerical proof/source decode/DB/lease')"],'actual-isolated-import.log')
run([sys.executable,str(Path(a.__file__)),'--schema-only'],'actual-schema-only.log')
schema=json.loads((P/'actual-schema-only.log').read_text());assert schema['passed']and schema['savedRows']==13 and schema['uniqueForeignFacets']==4 and schema['actualGroundFaces']==11604 and schema['sourceFacets']==122721 and schema['currentFacets']==9214 and schema['completeNativeFacets']==11576
packet=a.read(a.PACKET);assert len(packet['rows'])==13
for r in packet['rows']:
 assert r['exactSavedAreaCoverage']['method']=='closed-facet-area-union'and r['exactSavedAreaCoverage']['remainingPositiveAreaPieces']>0
for q in refs:a.check(q)
for q in transitive:assert q==a.ref(a.check(q))
assert a.ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==a.prior.baseline.CURRENT
assert not a.DOC.exists()and not a.LOCAL.exists()
summary=dict(passed=True,caller=a.ref(Path(a.__file__)),method=a.ref(P/'METHOD.md'),driver=a.ref(Path(__file__)),commands=commands,schemaVerbatim=schema,all58Code128InputPinsVerifiedBeforeAndEnd=True,transitiveLocalPythonImports=sorted(transitive,key=lambda q:q['path']),currentManifestSHA256=a.prior.baseline.CURRENT,noCoverageFiniteConstructorRaySourceDecodeDBOrLeaseExecuted=True,coverageMethodUnchanged='closed-facet-area-union with orientation reversal only for negative signed area as existing helper',evidenceRefs=[a.ref(Path(__file__)),a.ref(P/'draft-pins.json')]+[r['log']for r in commands]+transitive)
a.save(P/'actual-readonly-preparation.json',summary);print(json.dumps(summary,sort_keys=True))
