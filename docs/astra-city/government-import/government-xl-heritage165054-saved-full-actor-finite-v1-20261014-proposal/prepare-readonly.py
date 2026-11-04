"""Actual receipt/schema/hash binding only, after ROOT verifies production capture."""
from pathlib import Path
import sys,ast,json,subprocess
ROOT=Path(__file__).resolve().parents[4];HERE=ROOT/'source-scripts/city/government-import';sys.path.insert(0,str(HERE))
import heritage165054_saved_full_actor_finite_v1_20261014 as a
P=a.PROPOSAL;job=sys.argv[sys.argv.index('--capture-job')+1];assert len(job)==64 and all(c in '0123456789abcdef'for c in job)
assert not a.DOC.exists()and not a.LOCAL.exists()and not(P/'draft-pins.json').exists()
seen=set()
def local_closure(path):
    if path in seen:return
    seen.add(path);tree=ast.parse(path.read_text())
    for n in ast.walk(tree):
        names=[q.name for q in n.names]if isinstance(n,ast.Import)else[n.module]if isinstance(n,ast.ImportFrom)and n.level==0 else[]
        for name in names:
            if not name:continue
            q=HERE/(name.split('.')[0]+'.py')
            if q.is_file():local_closure(q)
for f in [Path(a.__file__),Path(__file__)]:local_closure(f)
data,actors,receipt,report,basic,review,refs=a.inputs(job)
for q in refs:a.check(q)
prior=a.read(a.capture.PROPOSAL/'draft-pins.json');codes=a.distinct_refs(prior['codeRefs']+[a.ref(f)for f in sorted(seen)]+[a.ref(P/'METHOD.md')])
a.save(P/'draft-pins.json',dict(caller=a.ref(Path(a.__file__)),codeRefs=codes,inputRefs=refs,captureJob=job,canonicalResources=a.resources(actors),currentManifestSHA256=a.CURRENT,currentSnapshot=a.SNAPSHOT,completeOwnedOriginalFaces=15140,completeOwnedWorldModes=4,currentBASICActorsIncludingOwnedContext=23,otherBASICActors=22,exactActorUIDs=actors,rawReasonResolved=False,conditional18Review=a.ref(a.capture.bounds.REVIEW)))
cmd=[sys.executable,str(Path(a.__file__)),'--capture-job',job,'--schema-only'];r=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True);log=P/'schema-only.log';assert not log.exists();log.write_text(r.stdout+r.stderr);assert r.returncode==0,log;schema=json.loads(r.stdout);assert schema['passed']and len(schema['canonicalResources'])==47
outs=[a.ref(P/p)for p in ['draft-pins.json','METHOD.md','schema-only.log']]
for q in codes+refs+outs:a.check(q)
a.save(P/'actual-readonly-preparation.json',dict(passed=True,caller=a.ref(Path(a.__file__)),captureJob=job,evidenceRefs=outs,commands=[dict(command=cmd,exitCode=0)],schemaVerbatim=schema,unchangedExistingExactKernelsAndSelectorsNoMirroredFixtures=True,noSourceWorldCalculationsRendererFiniteDBLeaseWorker=True));print(json.dumps(dict(passed=True,codePins=len(codes),inputPins=len(refs),captureJob=job,resources=len(a.resources(actors)))))
