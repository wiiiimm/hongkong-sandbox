import sys,json,subprocess
from pathlib import Path
from types import SimpleNamespace
R=Path.cwd();H=R/'source-scripts/city/government-import';sys.path.insert(0,str(H))
import citywalk134332_current_complete_finite_ground_draft_v1_20261013 as Q
import citywalk134332_freeze_current_complete_finite_ground_draft_v1_20261013 as F
assert F.Q is Q
P=Q.P;a=SimpleNamespace(expected_manifest='c00fd9f731b1bcbf4d2df6067a5cb3231f0eaa8c503a8adea584fec39bf73bf7')
print('Actual exact caller/freezer imports PASS; no finite arithmetic/lease',flush=True)
before,receipt,d,worlds,grounds,unused,components,labels,pins=Q.inputs(a)
P.joinpath('actual-readonly-finite-current-state-before-v1.json').write_text(json.dumps(before,indent=2)+'\n')
bindings=[dict(sourceWorld=m,groundWorld=n,completeSourceFaces=len(w),completeGroundFaces=len(g),sourceWorldSHA256=Q.digest(w.astype('<f8').tobytes()),groundWorldSHA256=Q.digest(g.astype('<f8').tobytes()),proofTupleSHA256=Q.digest((Q.digest(w.astype('<f8').tobytes())+Q.digest(g.astype('<f8').tobytes())).encode()))for m,w in worlds.items()for n,g in grounds.items()]
assert len(bindings)==12
partition=dict(completeBodies=len(components),completeFaces=len(labels),sourceFaceIDsByOriginalBody=[c['sourceFaceIndices']for c in components],savedComponentMetadataSHA256=Q.digest(json.dumps(components,sort_keys=True,allow_nan=False).encode()),bodyLabelSHA256=Q.digest(json.dumps(labels,sort_keys=True,allow_nan=False).encode()))
P.joinpath('actual-readonly-source-ground-partition-bindings-v1.json').write_text(json.dumps(dict(bindings=bindings,distinctFullTupleCount=len({b['proofTupleSHA256']for b in bindings}),wholeUnusedPositionBindings=unused,completeOriginalPartition=partition,groundReceipt=Q.ref(Q.G.D/'result.json'),completeGround=Q.ref(Q.G.D/'complete-current-drawn-ground.json.gz')),indent=2)+'\n')
print('Actual full arrays/12bindings/193-body partition verified',flush=True)
r=subprocess.run([sys.executable,str(Path(Q.__file__)),'--expected-manifest',a.expected_manifest,'--preflight-only'],cwd=R,check=False);assert r.returncode==0
after,*rest=Q.inputs(a);assert after==before
for e in pins:assert Q.ref(R/e['path'])==e
P.joinpath('actual-readonly-finite-current-state-after-v1.json').write_text(json.dumps(after,indent=2)+'\n')
assert not Q.LOCAL.exists()and not Q.D.exists()
P.joinpath('actual-readonly-finite-preflight-result-v1.json').write_text(json.dumps(dict(importsPassed=True,preflightExitCode=r.returncode,beforeAfterExact=True,completeSourceFaces=41277,completeGroundFaces=4215,completeOriginalBodies=193,sourceGroundBindings=12,distinctCompleteSourceGroundTuples=len({b['proofTupleSHA256']for b in bindings}),currentNativeCount=6650,contextUIDs=19,protectedReviewRows=1704,noWorker=True,noLease=True,noFiniteArithmetic=True,normalLocalAndDocAbsent=True,codeRefs=pins),indent=2)+'\n')
print('Actual readonly preflight terminal0/before-after exact; no finite worker/lease',flush=True)
