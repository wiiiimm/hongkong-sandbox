from pathlib import Path
import sys,json,subprocess,ast
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT/'source-scripts/city/government-import'))
import upton_certified6170_source_bound_overlap_edge_validator_v2_20261014 as meta
import upton_certified6170_two_original_current_physical_v3_20261014 as physical
assert '--physical-only'in sys.argv;a=physical;ismeta=False
P=a.PROPOSAL;codeonly='--code-only'in sys.argv;assert codeonly or '--bind-completed-inputs-readonly'in sys.argv;assert not a.DOC.exists() and not a.LOCAL.exists();prefix='code-only-'if codeonly else 'actual-';commands=[]
def run(cmd,name,cwd=ROOT):
 path=P/(prefix+name);assert not path.exists();r=subprocess.run(cmd,cwd=cwd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT);path.write_bytes(r.stdout);commands.append(dict(command=cmd,exitCode=r.returncode,log=a.ref(path)));assert r.returncode==0,(cmd,path)
helper=a.HERE/'upton_parent_edge_validator_sample_v1_20261014.py'
sample=lambda p:ast.dump(next(n for n in ast.walk(ast.parse(p.read_text()))if isinstance(n,ast.FunctionDef)and n.name=='sample'),include_attributes=False)
assert sample(helper)==sample(meta.capture.VALIDATOR)
run([sys.executable,'-m','unittest','-v','test_upton_parent_edge_validator_sample_v1_20261014','test_verified_installed_support_acceptance','test_exact_distinct_evidence_refs_v1_20261014','test_upton_certified6170_acceptance_draft_symbols_v1_20261014','test_upton_current_nam_form_setup_v1_20261014'],'existing-canonical-and-support-contract-fixtures.log',a.HERE)
run([sys.executable,'-c',"import sys;sys.path.insert(0,'source-scripts/city/government-import');import "+Path(a.__file__).stem+";print('isolated import PASS; no source/geometry/edge/pair/MAX/physical/DB/lease')"],'isolated-import.log')
folders=[a.HERE,a.HERE.parent/'shared-modelling',a.HERE.parent/'citywide-native',a.HERE.parent/'island-detail-integration',ROOT/'docs/astra-city/mui-wo-buildings/review',a.HERE.parent/'assembly-support-review'];todo=[Path(a.__file__),meta.capture.VALIDATOR];seen=set();transitive=[]
while todo:
 path=todo.pop().resolve()
 if path in seen:continue
 seen.add(path);transitive.append(a.ref(path))
 for n in ast.walk(ast.parse(path.read_text())):
  mods=[n.module]if isinstance(n,ast.ImportFrom)and n.module else[q.name for q in n.names]if isinstance(n,ast.Import)else[]
  for mod in mods:
   for folder in folders:
    q=folder/(mod.replace('.','/')+'.py')
    if q.is_file():todo.append(q)
closure=meta.read(meta.capture.PROPOSAL/'actual-literal-runtime-closure-preflight.json');literal=[dict(path=k,sha256=v)for k,v in closure['inputHashes'].items()];assert len(literal)==24 and closure['computedImportsRejected'] and closure['unsupportedDynamicImports']==0
refs=transitive+literal+[a.ref(Path(__file__)),a.ref(P/'METHOD.md')]+[q['log']for q in commands]
for q in refs:a.check(q)
if codeonly:
 assert not (P/'draft-pins.json').exists();a.save(P/'code-only-preparation.json',dict(passed=True,caller=a.ref(Path(a.__file__)),commands=commands,literalValidatorSampleASTExactlyUnchanged=True,transitiveLocalPythonImports=transitive,strictLiteralDependencyRefs=literal,evidenceRefs=refs,dependentActualReceiptsNotYetBound=True,notReadyForWorker=True,noNumericalEdgeOverlapMAXRootSupportPhysicalDBLeaseWorker=True));print(json.dumps(dict(passed=True,codeOnly=True,metadata=ismeta,pythonClosure=len(transitive),literalClosure=len(literal))));raise SystemExit
folders_to_bind=meta.FOLDERS if ismeta else [meta.DOC,meta.capture.DOC,meta.finite.DOC];receipts=[]
cap=meta.read(meta.capture.PROPOSAL/'draft-pins.json');codes={q['path']:q for q in cap['codeRefs']};inputs={q['path']:q for q in cap['inputRefs']}
for q in transitive+literal:codes[q['path']]=q
for folder in folders_to_bind:
 result=meta.read(folder/'result.json');v=meta.read(folder/'ROOT-VERIFIED.json');assert v['jobId']==result['jobId'] and v['exactNeonReadback'] and v['allEvidenceHashesVerified'] and v['leaseReleased'];receipts.append(dict(jobId=result['jobId'],result=meta.ref(folder/'result.json')))
 for q in result['evidenceRefs']+[meta.ref(folder/'result.json'),meta.ref(folder/'ROOT-VERIFIED.json')]:
  actual=meta.ref(meta.check(q));inputs[actual['path']]=actual
if not ismeta:
 bindings=dict(completedMetadataJob=meta.read(meta.DOC/'result.json')['jobId'])
 for name in ['input.json.gz','inventory.json.gz','composition.json.gz','result.json','independent-completed-readback-summary.json']:
  q=meta.ref(physical.NAM_PACKET/name);inputs[q['path']]=q
 nam=meta.read(physical.NAM_PACKET/'input.json.gz')
 for q in nam['currentCatalogueRefs']+[nam['rows'][0]['source']]:inputs[q['path']]=q
 for path,digest in nam['currentNativeViewerTileHashes'].items():inputs[path]=dict(path=path,sha256=digest)
 for folder,names in [(physical.RUNTIME,['selection.json.gz']),(physical.CAP,['input.json.gz']),(physical.IDENTITY,['source-identification-only.json','identities.json']),(physical.TOWER_IDENTITY,['result.json','identities.json','context.json.gz','captured-manifest.json']),(physical.ROOT_BODY,['diagnostic.json.gz'])]:
  for name in names:q=meta.ref(folder/name);inputs[q['path']]=q
 for row in meta.read(physical.RUNTIME/'selection.json.gz')['rows']:
  if row['uid']in physical.OWNED:q=meta.ref(ROOT/row['candidate']['path']);inputs[q['path']]=q
 for q in physical.TOOLS:ref=meta.ref(q);codes[ref['path']]=ref
 for b in physical.old_physical.history_bindings()+physical.tower_history_bindings():q=b['actualVerifiedFile'];inputs[q['path']]=q
pins=dict(caller=meta.ref(Path(a.__file__)),**bindings,codeRefs=sorted(codes.values(),key=lambda q:q['path']),inputRefs=sorted(inputs.values(),key=lambda q:q['path']),sourceOnly=True,physicalAccepted=False);assert not (P/'draft-pins.json').exists();meta.save(P/'draft-pins.json',pins)
for q in pins['codeRefs']+pins['inputRefs']:meta.check(q)
run([sys.executable,str(Path(a.__file__)),'--schema-only'],'schema-only.log');schema=json.loads((P/'actual-schema-only.log').read_text());assert schema['passed']
for q in pins['codeRefs']+pins['inputRefs']+refs:meta.check(q)
assert meta.ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==meta.capture.legacy.CURRENT and not a.DOC.exists() and not a.LOCAL.exists();refs+=[meta.ref(P/'draft-pins.json')]+[q['log']for q in commands];meta.save(P/'actual-readonly-preparation.json',dict(passed=True,caller=meta.ref(Path(a.__file__)),driver=meta.ref(Path(__file__)),schemaVerbatim=schema,commands=commands,literalValidatorSampleASTExactlyUnchanged=True,transitiveLocalPythonImports=transitive,strictLiteralDependencyRefs=literal,evidenceRefs=refs,noNumericalEdgeMetadataValidatorSupportRootPhysicalDBLeaseOrWorker=True));print(json.dumps(dict(passed=True,metadata=ismeta,codePins=len(codes),inputPins=len(inputs))))
