"""Append only the HKS-227 trial revisions; retain the main installation snapshot."""
import argparse,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'source-scripts/city/model-review-ledger'));import ledger
read=lambda p:json.loads(p.read_bytes())
p=argparse.ArgumentParser();p.add_argument('--receipt',required=True);p.add_argument('--commit');a=p.parse_args()
folder=ROOT/'3d-viewer/city/data/whampoa-light-trial';doc=ROOT/'docs/astra-city/ifc-hsbc-light';m=read(folder/'manifest.json');b=read(folder/'basic.json');evidence=doc/('final-verification.json' if (doc/'final-verification.json').exists() else 'verification.json');proof=read(evidence)
assert not proof['errors'] and len(proof['views'])==14
selected={x['uid']:x for name in ['ifc','hsbc']for x in m['references'][name]['light']};assert len(selected)==5
snapshot='light-ifc-hsbc-'+hashlib.sha256(json.dumps(selected,sort_keys=True).encode()).hexdigest()[:16];parts=[]
for row in b['buildings']:
 uid=row['uid']
 if uid not in selected:continue
 model=selected[uid];assert hashlib.sha256((folder/model['asset']).read_bytes()).hexdigest()==model['sha256']
 parts.append({'uid':uid,'name':row['name'],'objectId':int(uid.split('/')[1].split(':')[0]),'landmarkIds':['hsbc' if uid=='landsd/89275:0' else 'ifc'],'sourceProgress':'lightweight-trial','candidate':model,'classification':['isolated-light-trial'],'knownHold':'Comparison only; not approved for main-map replacement.'})
report=doc/'source-review.json';report.write_text(json.dumps({'snapshotId':snapshot,'parts':parts},indent=2)+'\n');ledger.seed(report)
entries=[(p['uid'],'held',evidence,'HKS-227 deterministic1m light mesh from existing exact source model; upper silhouette retained. Comparison-only; original detailed map geometry unchanged. Script generation uses no AI calls; unmeasured code-authoring token usage is not inferred.',a.commit)for p in parts]
ledger.record_many(snapshot,a.receipt,entries,effort={'method':'lightweight','ai_model':None,'reasoning_effort':'not-applicable','issue':'HKS-227','run_id':snapshot,'output_ref':'3d-viewer/city/data/whampoa-light-trial/manifest.json'},request_id=snapshot+(":"+a.commit if a.commit else ""))
(doc/'neon.json').write_text(json.dumps({'issue':'HKS-227','snapshotId':snapshot,'records':5,'state':'held: comparison only','mainReviewPointerUnchanged':True,'commit':a.commit},indent=2)+'\n')
print('Recorded five lightweight trial revisions; installed review snapshot unchanged.')
