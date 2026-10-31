import sys,json,hashlib
from pathlib import Path
from types import SimpleNamespace
R=Path.cwd();H=R/'source-scripts/city/government-import';sys.path.insert(0,str(H))
import citywalk134332_current_ground_only_preflight_draft_v2_20261013 as Q
P=Q.P;a=SimpleNamespace(expected_manifest='c00fd9f731b1bcbf4d2df6067a5cb3231f0eaa8c503a8adea584fec39bf73bf7')
print('Imported actual reviewed v2 caller and orchestration; no renderer import',flush=True)
before=Q.W.inputs(a);P.joinpath('actual-readonly-current-state-before-v1.json').write_text(json.dumps(before,indent=2)+'\n')
print('Current before state saved:19UID/1704rows',flush=True)
r=Q.inputs(a);print(json.dumps(r),flush=True)
after=Q.W.inputs(a);assert before==after
P.joinpath('actual-readonly-current-state-after-v1.json').write_text(json.dumps(after,indent=2)+'\n')
for e in json.loads(P.joinpath('actual-preparation-start-code-input-pins-v1.json').read_text())['refs']:assert Q.ref(R/e['path'])==e
P.joinpath('actual-readonly-preflight-result-v1.json').write_text(json.dumps(r,indent=2)+'\n')
print('Read-only before/after state and all start pins exact; no lease or exporter',flush=True)
