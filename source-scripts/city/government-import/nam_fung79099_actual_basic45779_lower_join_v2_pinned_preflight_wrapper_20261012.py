"""Draft orchestration wrapper; no numerical changes or receipt substitution.
Read literal draft pins before actual v2 imports/DB/lease/numerical execution.
"""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
PROPOSAL=ROOT/'docs/astra-city/government-import/government-xl-nam-fung79099-actual-basic45779-carrier-route-proposal-v1-20261012'
PINS=PROPOSAL/'lower-join-v2-exact-draft-pins.json'
CALLER=ROOT/'source-scripts/city/government-import/nam_fung79099_actual_basic45779_lower_join_grade_cap_draft_v2_20261012.py'
CALLER_SHA='a7e08e2015949cd230c15cc35c5bf2a5ada5652cf5f97aa116c0d4161f03213c'
def ref(path):return dict(path=str(path.relative_to(ROOT)),sha256=hashlib.sha256(path.read_bytes()).hexdigest())
def verify():
 raw=PINS.read_bytes();d=json.loads(raw);assert d['caller']==ref(CALLER)and d['caller']['sha256']==CALLER_SHA
 assert any(e==ref(Path(__file__).resolve())for e in d['boundDraftInputs'])
 for e in d['boundDraftInputs']:
  p=(ROOT/e['path']).resolve();assert p.is_relative_to(ROOT)and ref(p)==e
 return raw,d
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--expected-capture-result-sha',required=True);p.add_argument('--preflight-only',action='store_true');a=p.parse_args();raw,d=verify();args=[sys.executable,str(CALLER),'--expected-capture-result-sha',a.expected_capture_result_sha]
 if a.preflight_only:args+=['--preflight-only']
 code=subprocess.run(args,cwd=ROOT).returncode;assert PINS.read_bytes()==raw and verify()[1]==d;sys.exit(code)
