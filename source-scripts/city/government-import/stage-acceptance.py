"""Stage a source-preserving mechanically accepted subset; never publish or write review credit."""
import gzip,hashlib,importlib.util,json,shutil,sys,uuid
from collections import Counter
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(HERE.parent/'shared-modelling'));from db import connect
import reservations
spec=importlib.util.spec_from_file_location('acceptance_policy',HERE/'acceptance-policy.py');policy=importlib.util.module_from_spec(spec);spec.loader.exec_module(policy)
read=lambda p:json.loads(gzip.decompress(p.read_bytes()) if str(p).endswith('.gz') else p.read_bytes())
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2)+'\n')
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
batch='government-200-20260911';base=ROOT/'docs/astra-city/government-import'/batch;out=base/'acceptance';local=HERE/'local'/batch
source=read(base/'selection.json.gz');prior=read(base/'results.json.gz');metrics=read(out/'metrics.json');by_metric={r['uid']:r for r in metrics['rows']};by_source={r['uid']:r for r in source['rows']}
for rel,h in metrics['inputHashes'].items():assert digest(ROOT/rel)==h,'Current model/terrain inputs changed'
rows=[r for r in prior['rows'] if r['state']=='runtime-validated-awaiting-acceptance'];ids=[r['uid'] for r in rows]
with connect() as c:
 c.execute('SET TRANSACTION READ ONLY')
 reviews=dict(c.execute('SELECT DISTINCT ON(uid) uid,review_state FROM astra_modelling.model_reviews WHERE uid=ANY(%s) ORDER BY uid,updated_at DESC',(ids,)).fetchall())
 native=dict(c.execute('SELECT r.cache_key,r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND r.cache_key=ANY(%s)',(source['nativeRun'],list({by_source[uid]['native']['cacheKey'] for uid in ids}))).fetchall())
landmarks={c['uid'] for r in read(ROOT/'docs/astra-city/landmark-registry/inventory-candidates.json')['rows'] for c in r['candidates']}
results=[];accepted=[]
for r in rows:
 uid=r['uid'];s=by_source[uid];reasons=policy.reasons(r,by_metric[uid],metrics['profiles']['mobile'])
 if native.get(s['native']['cacheKey'])!=s['native']['resultSha']:reasons.append('native-stage-proof-changed')
 if reviews.get(uid) in ('held','source-unavailable','identity-unresolved','installed-verified'):reasons.append('existing-review-requires-explicit-resolution')
 if uid in landmarks:reasons.append('landmark-component-scope')
 results.append({'uid':uid,'sourceSHA256':r['sourceSHA256'],'action':'retain-pending' if reasons else 'stage-original-import','reasons':reasons})
 if not reasons:accepted.append(s)
assert accepted,'No forms satisfy the conservative direct-import contract'
owned=reservations.claim('codex-government-acceptance-'+str(uuid.uuid4()),['building:'+uid for uid in ids],batch='government-200-acceptance')
assert owned['ok'],'Source reservation conflict'
save(local/'acceptance-reservation.json',json.loads(json.dumps(owned['reservation'],default=str)))
catalogue=read(local/'candidates/catalogue.json');catalogue['area']='Government direct imports · 11 September 2026';catalogue['models']=[]
stage=HERE/'accepted'/batch
for s in accepted:
 e=dict(s['candidate']['entry']);p=local/'candidates'/e['asset'];assert digest(p)==e['sha256'];target=stage/e['asset'];target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target)
 e.update(placementReviewed=True,sourceIdentityReviewed=True,identityReviewApproved=True,priority='detail',placementReview='Scripted original-government-import-v1: exact source identity/hash, original geometry, conservative drawn-terrain contact and runtime checks; no architectural reconstruction or whole-landmark sign-off.')
 catalogue['models'].append(e)
catalogue['counts']['packedModels']=len(accepted);save(stage/'catalogue.json',catalogue)
plan={'areas':[{'area':catalogue['area'],'catalogue':str((stage/'catalogue.json').relative_to(ROOT)),'destination':'city/data/official-models/government-20260911/catalogue.json'}]};save(stage/'plan.json',plan)
forms=[]
for s in accepted:
 b=dict(s['source']['building']);b['tile']=Path(s['source']['tile']).stem;forms.append(b)
save(stage/'source-forms.json',forms)
report={'policy':policy.POLICY,'inputHashes':metrics['inputHashes'],'metricsSHA256':digest(out/'metrics.json'),'policySHA256':digest(HERE/'acceptance-policy.py'),'catalogueSHA256':digest(stage/'catalogue.json'),'planSHA256':digest(stage/'plan.json'),'modelsChecked':len(rows),'staged':len(accepted),'retainedPending':len(rows)-len(accepted),'reasonCounts':dict(Counter(reason for r in results for reason in r['reasons'])),'rows':results,'aiCalls':0,'geometryChanges':0,'publication':False,'qualification':'Direct import of unchanged government source parts only. Source/terrain/runtime contract; no AI architectural review or whole-landmark completion.'};save(out/'decision.json',report);print(json.dumps({k:report[k] for k in ['modelsChecked','staged','retainedPending','reasonCounts']}))
