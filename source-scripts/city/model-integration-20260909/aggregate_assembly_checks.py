"""Combine unchanged successful source checks with the final facade-picking rerun.
Original failed reports remain intact; only their completed per-model checks count.
"""
import json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];DOC=ROOT/'docs/astra-city/model-integration-20260909'
def read(path):return json.loads(path.read_text())
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
plan=read(ROOT/'source-scripts/city/model-integration-20260909/assemblies-plan.json');expected={m['uid'] for a in plan['areas'] for m in read(ROOT/a['catalogue'])['models']}
paths=[DOC/'assemblies-live/after/verification.json',DOC/'assemblies-final-two-live/after/verification.json'];reports=[read(p) for p in paths];assert reports[1]['result']=='passed'
rows={}
for report in reports:
 assert not report['errors']
 for area in report['areas']:
  for row in area['models']:
   assert row['active'] and row['pick']==row['uid'] and row['contact'] and abs(row['terrainHits'][0]-row['ground'])<.03
   rows[row['uid']]=row
assert set(rows)==expected and len(rows)==53
result={'result':'passed','models':len(rows),'uids':sorted(rows),'sourceReports':[{'path':str(p.relative_to(ROOT)),'sha256':digest(p),'overallResult':r['result'],'completedSourceChecks':sum(len(a['models']) for a in r['areas'])} for p,r in zip(paths,reports)],'resolution':'Original51 completed source checks passed. The next podium had no overhead picking ray; both remaining parts passed actual-camera facade and overhead picking, source-local collision, terrain and native streaming in the final rerun. Original failed report retained unchanged.','collisionFix':'ae138ef0','mobileScope':'Final two-part rerun verifies one mobile-layout podium plus walk/fly, failure fallback and retry. Other desktop source checks do not imply physical-phone or all-model mobile visual acceptance.','wholeLandmarkComplete':False}
(DOC/'assemblies-verification.json').write_text(json.dumps(result,indent=2)+'\n');print('53 source components verified')
