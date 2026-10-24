"""Record the isolated trial in Neon; never change the live review pointer."""
import argparse,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'source-scripts/city/model-review-ledger'));import ledger
read=lambda p:json.loads(p.read_bytes())
p=argparse.ArgumentParser();p.add_argument('--ship-receipt',required=True);p.add_argument('--other-receipt',required=True);a=p.parse_args()
folder=ROOT/'3d-viewer/city/data/whampoa-light-trial';manifest=read(folder/'manifest.json');data=read(folder/'basic.json');evidence=ROOT/'docs/astra-city/whampoa-light-trial/verification.json';proof=read(evidence);assert not proof['errors'] and len(proof['views'])==10
snapshot='light-trial-'+hashlib.sha256((folder/'manifest.json').read_bytes()).hexdigest()[:16]
models={m['uid']:m for r in manifest['references'].values()for m in r['light']};parts=[]
for b in data['buildings']:
 asset=folder/models[b['uid']]['asset'] if b['uid']in models else folder/'basic.json'
 parts.append({'uid':b['uid'],'name':b['name'],'landmarkIds':[g['id']for g in manifest['groups']if b['uid']in g['uids']],'sourceProgress':'lightweight-trial','candidate':{'sha256':hashlib.sha256(asset.read_bytes()).hexdigest()},'classification':['isolated-light-trial'],'knownHold':'Comparison only; high pass/terrain and city integration not accepted','objectId':int(b['uid'].split('/')[1].split(':')[0])})
report=ROOT/'docs/astra-city/whampoa-light-trial/source-review.json';report.write_text(json.dumps({'snapshotId':snapshot,'parts':parts},indent=2)+'\n');ledger.seed(report)
for b in data['buildings']:
 uid=b['uid'];receipt=a.ship_receipt if uid in manifest['groups'][0]['uids'] else a.other_receipt
 asset='3d-viewer/city/data/whampoa-light-trial/'+models[uid]['asset'] if uid in models else '3d-viewer/city/whampoa-comparison.js'
 ledger.record(snapshot,receipt,uid,'held',evidence,'HKS-225 lightweight comparison passed loading checks; remains trial-only. Existing city model and source-review pointer unchanged. Mesh simplification or illustrative facade generation is scripted; session reasoning setting is not inferred.',effort={'method':'lightweight','ai_model':None,'reasoning_effort':'not-applicable','issue':'HKS-225','run_id':snapshot,'output_ref':asset},request_id=snapshot+':'+uid)
result={'issue':'HKS-225','snapshotId':snapshot,'records':len(parts),'status':'held: comparison only','mainReviewPointerUnchanged':True,'effort':'script generation: no AI calls; reasoning not applicable','nextIssue':'HKS-226'}
(ROOT/'docs/astra-city/whampoa-light-trial/neon.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
