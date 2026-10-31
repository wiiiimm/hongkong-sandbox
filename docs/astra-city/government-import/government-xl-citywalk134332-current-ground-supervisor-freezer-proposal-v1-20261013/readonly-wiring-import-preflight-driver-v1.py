import sys,json
from pathlib import Path
from types import SimpleNamespace
R=Path.cwd();H=R/'source-scripts/city/government-import';sys.path.insert(0,str(H))
import citywalk134332_current_ground_only_supervised_draft_v1_20261013 as W
import citywalk134332_freeze_complete_current_ground_draft_v1_20261013 as F
assert F.W is W
P=W.P;a=SimpleNamespace(expected_manifest='c00fd9f731b1bcbf4d2df6067a5cb3231f0eaa8c503a8adea584fec39bf73bf7')
pins=W.Q.read(P/'executable-pins.json')['refs']
for e in pins:assert W.Q.ref(R/e['path'])==e
print('Actual exact supervisor/freezer imports PASS; no renderer import/lease',flush=True)
before=W.inputs(a);P.joinpath('actual-readonly-wiring-state-before-v1.json').write_text(json.dumps(before,indent=2)+'\n')
print('Actual inputs before PASS:21resources/19UID/1704rows/6650',flush=True)
import subprocess
r=subprocess.run([sys.executable,str(Path(W.__file__)),'--expected-manifest',a.expected_manifest,'--preflight-only'],cwd=R,check=False);assert r.returncode==0
after=W.inputs(a);assert after==before
for e in pins:assert W.Q.ref(R/e['path'])==e
P.joinpath('actual-readonly-wiring-state-after-v1.json').write_text(json.dumps(after,indent=2)+'\n')
assert not W.LOCAL.exists()and not W.D.exists()
P.joinpath('actual-readonly-wiring-preflight-result-v1.json').write_text(json.dumps({'importsPassed':True,'preflightExitCode':r.returncode,'beforeAfterInputsAndProtectedStateExact':True,'canonicalResources':21,'contextUIDs':19,'protectedReviewRows':1704,'currentNativeCount':6650,'noWorker':True,'noLease':True,'normalLocalAndDocAbsent':True,'codeRefs':pins},indent=2)+'\n')
print('Actual preflight exit0, all exact before/after inputs/state/pins; no worker/local/DOC',flush=True)
