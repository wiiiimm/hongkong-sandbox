"""Exact source-specific support review; canonical numeric output remains unchanged."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-star-house-pair-support-review-v1-20261020';DOC=BASE/BATCH;ACCOUNT=BASE/'government-xl-star-house-pair-four-world-contacts-v1-20261020';FOUND=BASE/'government-xl-star-parkview-four-mode-foundations-v1-20261020';VIEW=BASE/'government-xl-star-house-pair-support-views-v1-20261020';TVIEW=BASE/'government-xl-star-house-tower-source-views-v1-20261020';IDENT=BASE/'government-xl-star-house-podium-identity-review-v1-20261020';OLD=BASE/'government-xl-next-twenty-original-identity-v2-20261020'
assert not DOC.exists();refs=[Path(__file__)];pins={}
with connect() as c:
 c.execute('SET TRANSACTION READ ONLY')
 for folder in [ACCOUNT,FOUND,VIEW,TVIEW,IDENT]:
  r=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
  for e in r['evidenceRefs']:
   assert e['path'] not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
# Historical identity source proof is consumed only by exact immutable file hash.
towerPath=OLD/'33396:0/identity.json';assert digest(towerPath.read_bytes())==pins[str(towerPath.relative_to(ROOT))];tower=read(towerPath);podium=read(IDENT/'231484:0-review.json');assert tower['passed'] and not tower['reasons'] and podium['identityOnlyApproved']
for p,h in pins.items():
 # Older identity receipts include historical whole-map inputs; only the consumed
 # identity file is needed from that receipt. Current captured worlds bind the pair.
 if p in {e['path'] for e in read(TVIEW/'result.json')['evidenceRefs']} and p not in {str(towerPath.relative_to(ROOT)),str((TVIEW/'complete-source-four-views.png').relative_to(ROOT)),str((TVIEW/'summary.json').relative_to(ROOT)),str((TVIEW/'result.json').relative_to(ROOT))}:continue
 assert digest((ROOT/p).read_bytes())==h,p
rows=read(ACCOUNT/'contacts.json.gz')['rows'];assert {r['mode'] for r in rows}=={'original','literal','explicitLeftF32','explicitBalancedF32'};summaries=[]
for r in rows:
 assert (r['samples'],r['canonicalContacts'],r['canonicalResolvedWallContacts'],r['directOriginalFaceContacts'],r['stillUnresolved'])==(1105,1033,1,71,0)
 assert not r['rawInterface']['passed'];assert len(r['mapped'])==71 and all(p['supportFacesAtOriginalPoint'] and all(h['distanceM']<=.001 for h in p['supportFacesAtOriginalPoint']) for p in r['mapped'])
 for uid,field in [('landsd/33396:0','sourceWorldSHA256'),('landsd/231484:0','supportWorldSHA256')]:
  f=read(FOUND/(uid.split('/')[1]+'-'+r['mode']+'.json'));assert f['worldSHA256']==r[field] and f['strictFoundationAccepted'] and f['foundation']['fullyBuriedTriangles']==0
 summaries.append({k:v for k,v in r.items() if k not in ['rawInterface','mapped']})
images=[VIEW/'source-junctions.png',TVIEW/'complete-source-four-views.png'];decision=dict(uids=['landsd/33396:0','landsd/231484:0'],sourceSHA256ByUid={'landsd/33396:0':tower['sourceSHA256'],'landsd/231484:0':podium['sourceSHA256']},sourceSpecificSupportAccepted=True,requiredOriginalPodiumUid='landsd/231484:0',dependentUids=['landsd/33396:0'],sampleAccounts=summaries,rawCanonicalWarningsRetained=True,rawCanonicalInterfacePassed=False,sourceGeometryChanges=0,sourcePoseChanges=0,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,reviewer='Codex ROOT',imagesActuallyViewed=[dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes())) for p in images],basis='All1105 original tower rim samples accounted independently in four coordinate representations:1033 ordinary contacts,1 existing bounded same-wall contact,71 direct original finite podium face contacts within the existing1mm query tolerance. Direct contacts include vertical edge and lower-deck surfaces excluded or obscured by highest-surface sampling. ROOT inspected complete tower source views and opposite original junction views. Exact tower provider identity passes; podium identity independently reviewed. Both complete-source foundations pass every mode. This accepts only the exact supplied pair relationship, not a general support tolerance change or structural certification.',scope='Canonical strict interface stays failed and unchanged. Required podium dependency must be enforced in staged/live loader and failure recovery. Podium ground relationship, full current neighbour/runtime/browser and publication gates remain independent. No neighbouring UID suppression or model geometry edit.',fullAcceptance=False,publicationApproved=False,installationApproved=False)
save(DOC/'ROOT-SUPPORT-REVIEW.json',decision)
refs.extend([towerPath,ACCOUNT/'contacts.json.gz',VIEW/'source-junctions.png',TVIEW/'complete-source-four-views.png',IDENT/'231484:0-review.json']);refs.extend(FOUND/(uid+'-'+m+'.json') for uid in ['33396:0','231484:0'] for m in ['original','literal','explicitLeftF32','explicitBalancedF32'])
module('star_pair_support_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-original-pair-source-specific-support-review',list(dict.fromkeys(refs)),dict(uids=decision['uids'],sourceSpecificSupportAccepted=True,fullAcceptance=False,installationApproved=False))
