from pathlib import Path
import sys,ast,json,subprocess
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT/'source-scripts/city/government-import'))
import upton_tower41_main_source_attribution_v1_20261014 as a
P=a.PROPOSAL;assert not a.DOC.exists()and not a.LOCAL.exists()and not(P/'draft-pins.json').exists();commands=[]
def run(cmd,name,cwd=ROOT):
 path=P/name;assert not path.exists();r=subprocess.run(cmd,cwd=cwd,capture_output=True,text=True);path.write_text(r.stdout+r.stderr);commands.append(dict(command=cmd,exitCode=r.returncode,log=a.ref(path)));assert r.returncode==0,(cmd,path)
run([sys.executable,'-m','unittest','-v','test_exact_closed_ground_aabb_pruning_v1_20261011','test_exact_distinct_evidence_refs_v1_20261014'],'unchanged-ground-ref-fixtures.log',a.HERE)
run(['node','--check',str(a.RUNTIME)],'runtime-syntax.log')
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
for f in [a.RUNTIME,a.HERE/'support-contact.mjs',Path(__file__)]:codes.append(a.ref(f))
inputs=[]
for folder in [a.physical.DOC,a.physical.finite.DOC,a.physical.metadata.capture.DOC]:
 result=a.read(folder/'result.json');v=a.read(folder/'ROOT-VERIFIED.json');assert result['jobId']==v['jobId']and v['exactNeonReadback']and v['allEvidenceHashesVerified']and v['leaseReleased'];inputs+=result['evidenceRefs']+[a.ref(folder/'result.json'),a.ref(folder/'ROOT-VERIFIED.json')]
# Old source-only packets are explicit actual-byte inputs; no oldground approval
# or oldreceipt paths are rewritten. Exact ownedNeonreadback is ROOTworker only.
for folder in [a.MAIN,a.ROLE]:
 for name in ['result.json','diagnostic.json.gz']:inputs.append(a.ref(folder/name))
replay=a.read(a.physical.metadata.capture.DOC/'actual-production-replay.json.gz')
import numpy as np
sha=a.physical.finite.sha(np.asarray(replay['after']['closedDomainDrawnTriplets'],dtype='<f8').reshape(-1,3,3))
pins=dict(caller=a.ref(Path(a.__file__)),actualGroundSHA256=sha,codeRefs=a.distinct_refs(codes),inputRefs=a.distinct_refs(inputs),physicalAccepted=False)
for q in pins['codeRefs']+pins['inputRefs']:a.check(q)
a.save(P/'draft-pins.json',pins);run([sys.executable,str(Path(a.__file__)),'--schema-only'],'schema-only.log');schema=json.loads((P/'schema-only.log').read_text());assert schema['passed'];refs=[a.ref(P/'METHOD.md'),a.ref(P/'draft-pins.json')]+[q['log']for q in commands]
for q in pins['codeRefs']+pins['inputRefs']+refs:a.check(q)
a.save(P/'actual-readonly-preparation.json',dict(passed=True,caller=a.ref(Path(a.__file__)),commands=commands,schemaVerbatim=schema,evidenceRefs=refs,noSourceLayerMathSegmentsDBLeaseOrWorker=True));print(json.dumps(dict(passed=True,codePins=len(pins['codeRefs']),inputPins=len(pins['inputRefs']))))
