from pathlib import Path
import sys,json,subprocess,ast
import numpy as np
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT/'source-scripts/city/government-import'))
import upton_certified6170_saved_actual_union_delta_v1_20261014 as finite
import upton_certified6170_saved_area_pair_ancestor_v1_20261014 as pairs
assert ('--finite-only'in sys.argv)!=('--area-pairs-only'in sys.argv)
a=finite if '--finite-only'in sys.argv else pairs;isfinite=a is finite
P=a.PROPOSAL;codeonly='--code-only'in sys.argv;assert codeonly or '--bind-completed-capture-readonly'in sys.argv
assert not a.DOC.exists() and not a.LOCAL.exists();commands=[];prefix='code-only-'if codeonly else 'actual-'
def run(cmd,name,cwd=ROOT):
 path=P/(prefix+name);assert not path.exists();r=subprocess.run(cmd,cwd=cwd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT);path.write_bytes(r.stdout)
 commands.append(dict(command=cmd,exitCode=r.returncode,log=a.ref(path)));assert r.returncode==0,(cmd,r.returncode,path)
if isfinite:
 def assess_ast(path):
  owned=next(n for n in ast.parse(path.read_text()).body if isinstance(n,ast.FunctionDef)and n.name=='owned');return ast.dump(next(n for n in owned.body if isinstance(n,ast.FunctionDef)and n.name=='assess'),include_attributes=False)
 assert assess_ast(Path(a.__file__))==assess_ast(Path(a.previous_delta.__file__))
else:run([sys.executable,'-m','unittest','-v']+[p.removesuffix('.py')for p in a.TESTS],'existing-helper-fixtures.log',a.HERE)
run([sys.executable,'-c',"import sys;sys.path.insert(0,'source-scripts/city/government-import');import "+Path(a.__file__).stem+";print('isolated import PASS; no arrays/proof/production/DB/lease')"],'isolated-import.log')
closure_name=('code-only-'if codeonly else 'actual-')+'literal-runtime-closure-preflight.json'
closure_path=a.capture.PROPOSAL/'actual-literal-runtime-closure-preflight.json';closure=a.read(closure_path);assert closure['computedImportsRejected'] and closure['completeAuditedLiteralImportClosure'] and closure['unsupportedDynamicImports']==0 and closure['entryPath']==str(a.capture.RUNTIME.relative_to(ROOT))
literal=[dict(path=k,sha256=v)for k,v in closure['inputHashes'].items()];assert len(literal)==24
folders=[a.HERE,a.HERE.parent/'shared-modelling',a.HERE.parent/'citywide-native',a.HERE.parent/'island-detail-integration',ROOT/'docs/astra-city/mui-wo-buildings/review',a.HERE.parent/'assembly-support-review']
todo=[Path(a.__file__)];seen=set();transitive=[]
while todo:
 path=todo.pop().resolve()
 if path in seen:continue
 seen.add(path);transitive.append(a.ref(path))
 for n in ast.walk(ast.parse(path.read_text())):
  names=[n.module]if isinstance(n,ast.ImportFrom)and n.module else[q.name for q in n.names]if isinstance(n,ast.Import)else[]
  for name in names:
   for folder in folders:
    q=folder/(name.replace('.','/')+'.py')
    if q.is_file():todo.append(q)
refs=literal+transitive+[a.ref(Path(__file__)),a.ref(P/'METHOD.md'),a.ref(closure_path)]+[q['log']for q in commands]
for q in refs:a.check(q)
if codeonly:
 assert not (P/'draft-pins.json').exists() and not (P/'actual-readonly-preparation.json').exists()
 a.save(P/'code-only-preparation.json',dict(passed=True,caller=a.ref(Path(a.__file__)),commands=commands,transitiveLocalPythonImports=transitive,strictLiteralDependencyRefs=literal,fullAssessASTExactlyUnchanged=isfinite,evidenceRefs=refs,finalActualCaptureCountHashReceiptUnbound=True,notReadyForWorker=True,noArraysNumericalProofProductionDBLease=True))
 print(json.dumps(dict(passed=True,codeOnly=True,finite=isfinite,pythonClosure=len(transitive),literalClosure=len(literal),finalActualCaptureUnbound=True)));raise SystemExit
receipt=a.read(a.capture.DOC/'result.json');verification=a.read(a.capture.DOC/'ROOT-VERIFIED.json');assert verification['jobId']==receipt['jobId'] and verification['exactNeonReadback'] and verification['allEvidenceHashesVerified'] and verification['leaseReleased']
old=a.read((a.previous_delta if isfinite else a.previous_pairs).PROPOSAL/'draft-pins.json');codes={q['path']:q for q in old['codeRefs']};inputs={q['path']:q for q in old['inputRefs']}
cap=a.read(a.capture.PROPOSAL/'draft-pins.json')
for q in cap['codeRefs']+transitive+literal:codes[q['path']]=q
for q in cap['inputRefs']:inputs[q['path']]=q
for folder,names in [(a.capture.DOC,['result.json','ROOT-VERIFIED.json','actual-production-replay.json.gz','private-native-terrain-candidate.json.gz','new-scoped-geometry-measured-overlap.json.gz','six-existing-production-protection-guards.json.gz','real-validator-outcome.json']),(a.capture.PROPOSAL,['draft-pins.json','actual-readonly-preparation.json'])]:
 for name in names:q=a.ref(folder/name);inputs[q['path']]=q
if isfinite:
 for name in ['result.json','complete-actual-union-finite-delta.json.gz']:
  q=a.ref(a.previous_delta.DOC/name);inputs[q['path']]=q
 replay=a.read(a.capture.DOC/'actual-production-replay.json.gz');ground=a.triangles(np.asarray(replay['after']['closedDomainDrawnTriplets'],dtype='<f8').reshape(-1,3,3))
 bindings=dict(completeNewDrawnFaces=len(ground),completeNewGroundSHA256=a.sha(ground))
else:
 for name in ['result.json','complete-saved-area-pair-source-ancestor-continuation.json.gz']:
  q=a.ref(a.previous_pairs.DOC/name);inputs[q['path']]=q
 measured=a.read(a.capture.DOC/'new-scoped-geometry-measured-overlap.json.gz')['measured'];area=[r for r in measured['allProjectedIntersectingPairs']if r['projectedDimension']=='area']
 bindings=dict(candidateGeometryCanonicalSHA256=measured['candidateGeometryCanonicalSHA256'],completeNewNativeFacets=measured['completeCandidateFaces'],completeSavedAreaPairs=len(area),freshChangedAreaPairs=sum(r['rightFace']>=11606 for r in area))
pins=dict(caller=a.ref(Path(a.__file__)),completedCaptureJob=receipt['jobId'],**bindings,codeRefs=sorted(codes.values(),key=lambda q:q['path']),inputRefs=sorted(inputs.values(),key=lambda q:q['path']),sourceOnly=True,physicalAccepted=False)
assert not (P/'draft-pins.json').exists();a.save(P/'draft-pins.json',pins)
for q in pins['codeRefs']+pins['inputRefs']:a.check(q)
run([sys.executable,str(Path(a.__file__)),'--schema-only'],'schema-only.log');schema=json.loads((P/'actual-schema-only.log').read_text());assert schema['passed']
if isfinite:assert schema['oldDrawnFaces']==11634 and schema['completeNativeActorScope']==6650 and schema['completeBasicActors']==1911 and schema['affectedBasicActors']==52 and schema['completeOwnedFaces']==13312 and schema['secondaryForeignFaces']==392 and schema['native79882Faces']==616
else:assert schema['eligibleExactCompletePairAncestorReuse']==2168 and schema['allOld2168AndHistoricalNegativesRetained'] and schema['completeSourceFacets']==122721 and schema['completeCurrentFacets']==9214
for q in pins['codeRefs']+pins['inputRefs']+refs:a.check(q)
assert a.ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==a.capture.legacy.CURRENT and not a.DOC.exists() and not a.LOCAL.exists()
refs+=[a.ref(P/'draft-pins.json')]+[q['log']for q in commands]
a.save(P/'actual-readonly-preparation.json',dict(passed=True,caller=a.ref(Path(a.__file__)),driver=a.ref(Path(__file__)),method=a.ref(P/'METHOD.md'),commands=commands,schemaVerbatim=schema,fullAssessASTExactlyUnchanged=isfinite,transitiveLocalPythonImports=transitive,strictLiteralDependencyRefs=literal,allCodeInputPinsVerifiedBeforeAndEnd=True,evidenceRefs=refs,noNumericalFinitePairSourceProofDBLeaseOrWorker=True))
print(json.dumps(dict(passed=True,finite=isfinite,codePins=len(codes),inputPins=len(inputs),pythonClosure=len(transitive),literalClosure=len(literal),bindings=bindings)))
