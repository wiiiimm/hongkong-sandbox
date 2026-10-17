from pathlib import Path
import sys,json,ast,subprocess
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT/'source-scripts/city/government-import'))
import upton_podium_standalone_tower_fallback_guard_v1_20261014 as a
P=a.PROPOSAL;assert not a.DOC.exists()and not a.LOCAL.exists()and not(P/'draft-pins.json').exists();refs=[];commands=[]
def run(cmd,name,cwd=ROOT):
 path=P/name;assert not path.exists();r=subprocess.run(cmd,cwd=cwd,capture_output=True,text=True);path.write_text(r.stdout+r.stderr);commands.append(dict(command=cmd,exitCode=r.returncode,log=a.ref(path)));assert r.returncode==0,(cmd,path)
# Parse exact production literal closure, do not construct BASIC geometry.
run(['node',str(a.RUNTIME),str((P/'literal-runtime-closure.json').relative_to(ROOT)),'--closure-only'],'literal-runtime-closure.log')
closure=a.read(P/'literal-runtime-closure.json');assert closure['computedImportsRejected']and closure['unsupportedDynamicImports']==0
run([sys.executable,'-m','unittest','-v','test_exact_distinct_evidence_refs_v1_20261014','test_upton_existing_guard_disposition_v1_20261014'],'existing-authentication-and-guard-fixtures.log',a.HERE)
folders=[a.HERE,a.HERE.parent/'shared-modelling',a.HERE.parent/'citywide-native',a.HERE.parent/'island-detail-integration',ROOT/'docs/astra-city/mui-wo-buildings/review',a.HERE.parent/'assembly-support-review'];todo=[Path(a.__file__)];seen=set();codes=[]
while todo:
 path=todo.pop().resolve()
 if path in seen:continue
 seen.add(path);codes.append(a.ref(path))
 for n in ast.walk(ast.parse(path.read_text())):
  mods=[n.module]if isinstance(n,ast.ImportFrom)and n.module else[q.name for q in n.names]if isinstance(n,ast.Import)else[]
  for mod in mods:
   for folder in folders:
    q=folder/(mod.replace('.','/')+'.py')
    if q.is_file():todo.append(q)
codes +=[a.ref(a.RUNTIME),a.ref(Path(__file__)),a.ref(a.HERE/'check-neighbours.mjs')]+[dict(path=k,sha256=v)for k,v in closure['inputHashes'].items()]
inputs=[];receipts=[]
for folder in [a.physical.DOC,a.physical.metadata.DOC,a.physical.metadata.capture.DOC,a.physical.finite.DOC]:
 result=a.read(folder/'result.json');v=a.read(folder/'ROOT-VERIFIED.json');assert result['jobId']==v['jobId']and v['exactNeonReadback']and v['allEvidenceHashesVerified']and v['leaseReleased'];receipts.append(dict(jobId=result['jobId'],result=a.ref(folder/'result.json')))
 inputs += result['evidenceRefs']+[a.ref(folder/'result.json'),a.ref(folder/'ROOT-VERIFIED.json')]
# Actual native and1911 BASIC old tuples already bound by these complete receipts.
replay=a.read(a.physical.metadata.capture.DOC/'actual-production-replay.json.gz')
def ground_hash(which):
 import numpy as np
 return a.physical.finite.sha(np.asarray(replay[which]['closedDomainDrawnTriplets'],dtype='<f8').reshape(-1,3,3))
pins=dict(caller=a.ref(Path(a.__file__)),actualBeforeGroundSHA256=ground_hash('before'),actualAfterGroundSHA256=ground_hash('after'),completedReceipts=receipts,codeRefs=a.distinct_refs(codes),inputRefs=a.distinct_refs(inputs),physicalAccepted=False,installationApproved=False)
for q in pins['codeRefs']+pins['inputRefs']:a.check(q)
a.save(P/'draft-pins.json',pins);run([sys.executable,str(Path(a.__file__)),'--schema-only'],'schema-only.log')
schema=json.loads((P/'schema-only.log').read_text());assert schema['passed'];refs=[a.ref(P/'METHOD.md'),a.ref(P/'draft-pins.json'),a.ref(P/'literal-runtime-closure.json')]+[q['log']for q in commands]
for q in pins['codeRefs']+pins['inputRefs']+refs:a.check(q)
a.save(P/'actual-readonly-preparation.json',dict(passed=True,caller=a.ref(Path(a.__file__)),commands=commands,schemaVerbatim=schema,evidenceRefs=refs,noConstructorSourceNumericalFiniteSamplerDBLeaseOrWorker=True))
print(json.dumps(dict(passed=True,codePins=len(pins['codeRefs']),inputPins=len(pins['inputRefs']),literalClosure=len(closure['inputHashes']))))
