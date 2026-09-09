"""Append verified HKS-226 high-pass results using the existing fenced Neon ledger."""
import argparse, hashlib, json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'source-scripts/city/model-review-ledger'))
import ledger
read=lambda p:json.loads(p.read_bytes())
p=argparse.ArgumentParser();p.add_argument('--receipt',required=True);p.add_argument('--commit');a=p.parse_args()
doc=ROOT/'docs/astra-city/whampoa-high';proof=read(doc/'live/after/verification.json');comparison=read(doc/'comparison/verification.json')
assert proof['result']=='passed' and not proof['errors']
assert len(comparison['views'])==10 and not comparison['errors'] and all(not v['highPending'] for v in comparison['views'])
cat=read(ROOT/'3d-viewer/city/data/official-models/whampoa-estates-high/catalogue.json')
assert {m['uid']for m in cat['models']}=={m['uid']for area in proof['areas']for m in area['models']}
for m in cat['models']:
 assert m['placementReviewed'] and m['publicationApproved']
 asset=ROOT/'3d-viewer/city/data/official-models/whampoa-estates-high'/m['asset']
 assert hashlib.sha256(asset.read_bytes()).hexdigest()==m['sha256']
pointer=read(ROOT/'docs/astra-city/model-integration-20260909/current-source-review.json')
entries=[(m['uid'],'installed-verified',doc/'README.md',m['architectureReview']+' HKS-226 installed source mesh verified in feature-branch browser; neutral comparison preserves original light assets. Not production deployment or complete neighbourhood certification.',a.commit)for m in cat['models']]
result=ledger.record_many(pointer['snapshotId'],a.receipt,entries,effort={'method':'detailed','ai_model':'gpt-6-astra','reasoning_effort':'high','issue':'HKS-226','run_id':'whampoa-estates-high-20260909','output_ref':'3d-viewer/city/data/official-models/whampoa-estates-high/catalogue.json'},request_id='HKS-226:installed:'+pointer['snapshotId'])
output={'issue':'HKS-226','snapshotId':pointer['snapshotId'],'records':len(result),'state':'installed-verified','productionPublished':False,'commit':a.commit}
(doc/'neon.json').write_text(json.dumps(output,indent=2)+'\n');print(json.dumps(output))
