"""Prepare a bounded review of native candidates without sampled terrain flags."""
import json,sys,shutil,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
r=json.loads((ROOT/'docs/astra-city/landmark-preflight/report.json').read_text());pin=ROOT/'source-scripts/city/landmark-preflight/snapshots'/r['snapshotId']
c=json.loads((pin/'catalogue.json').read_text());exclude={168596,205817,279530,310908,283788,186982,226248}
parts=[p for p in r['parts'] if 'cpu-clear-awaiting-visual-review'in p['classification'] and p['objectId'] not in exclude]
uids={p['uid']for p in parts};out=HERE/'candidates';out.mkdir(exist_ok=True)
c['models']=[m for m in c['models'] if m['uid']in uids]
c['counts']['packedModels']=len(c['models'])
for m in c['models']:
 src=pin/'assets'/m['asset'];assert hashlib.sha256(src.read_bytes()).hexdigest()==m['sha256'];shutil.copyfile(src,out/m['asset'])
(out/'catalogue.json').write_text(json.dumps(c,indent=2)+'\n');(out/'catalogue-index.json').write_text(json.dumps({'models':len(c['models']),'catalogues':['catalogue.json']})+'\n')
plan={'areas':[{'area':'grounded-native-landmarks','catalogue':str((out/'catalogue.json').relative_to(ROOT)),'destination':'city/data/official-models/grounded-review-20260909/catalogue.json'}]}
(HERE/'plan.json').write_text(json.dumps(plan,indent=2)+'\n')
views={}
for m in c['models']:
 a,b=m['worldBounds'];mid=[(x+y)/2 for x,y in zip(a,b)];span=max(b[0]-a[0],b[2]-a[2]);height=b[1]-a[1];dist=max(30,height*.95,span*1.8)
 views[m['uid']]={'camera':[mid[0]+dist*.55,mid[1]+max(10,height*.22),mid[2]+dist]}
config={'plan':str((HERE/'plan.json').relative_to(ROOT)),'out':'docs/astra-city/grounded-model-review/browser','groups':[{'area':'grounded-landmarks','place':'central','uids':sorted(uids)}],'views':views}
(HERE/'browser-config.json').write_text(json.dumps(config,indent=2)+'\n')
(HERE/'selection.json').write_text(json.dumps({'snapshot':r['snapshotId'],'parts':[{'uid':p['uid'],'name':p['name'],'landmarks':p['landmarkIds'],'proposedIdentity':bool(p['identityProposalGroups'])}for p in parts]},indent=2)+'\n')
sys.path.insert(0,str(ROOT/'source-scripts/city/shared-modelling'));import reservations
receipt=Path('/tmp/astra-grounded-model-review-lease.json')
if receipt.exists():
 old=json.loads(receipt.read_text())
 if reservations.owns(old):print('Existing live reservation');sys.exit(0)
 receipt.unlink()
claim=reservations.claim('astra-root-grounded-model-review-20260909',['building:'+u for u in sorted(uids)],batch='HKS-214-grounded-review')
assert claim['ok'],claim
receipt.write_text(json.dumps(claim['reservation'],default=str,indent=2)+'\n')
print(json.dumps({'selected':len(uids),'retainedIdentity':sum(not p['identityProposalGroups']for p in parts),'receipt':str(receipt)}))
