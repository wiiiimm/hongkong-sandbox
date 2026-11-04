"""Bind Parkview's exact bounded lower-wall paths, without publication approval."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-parkview-two-support-review-v1-20261020';DOC=BASE/BATCH
UIDS=['landsd/255917:0','landsd/255646:0'];POD='landsd/254491:0'
def folder(n):return BASE/('government-xl-'+n+'-20261020')
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
assert not DOC.exists()
refs=[Path(__file__)];receipts={}
with connect()as c:
 c.execute('SET TRANSACTION READ ONLY')
 for name in ['parkview-low-contact-paths-v1','parkview-three-four-world-contacts-v2','star-parkview-four-mode-foundations-v1','parkview-three-support-views-v1','parkview-two-current-runtime-v2']:
  d=folder(name);r=read(d/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  receipts[name]={e['path']:e['sha256']for e in r['evidenceRefs']};refs.append(d/'result.json')
def consume(name,file):
 p=folder(name)/file;assert digest(p.read_bytes())==receipts[name][str(p.relative_to(ROOT))];refs.append(p);return read(p)
binding=consume('parkview-two-current-runtime-v2','current-binding.json');current={r['uid']:r for r in binding['rows']}
assert set(current)==set(UIDS+[POD]) and all(r['sameCompleteWorld']and r['sameCompleteDrawnGround']for r in current.values())
contacts=consume('parkview-three-four-world-contacts-v2','contacts.json.gz')['rows'];accounts=[];sources={}
for mode in ['original','literal','explicitLeftF32','explicitBalancedF32']:
 verified=consume('parkview-low-contact-paths-v1',mode+'-verified.json.gz')['rows']
 graph=consume('parkview-low-contact-paths-v1',mode+'-graph.json.gz')['rows']
 for uid in UIDS:
  v=next(r for r in verified if r['uid']==uid);g=next(r for r in graph if r['uid']==uid);raw=next(r for r in contacts if r['uid']==uid and r['mode']==mode)
  f=consume('star-parkview-four-mode-foundations-v1',uid.split('/')[1]+'-'+mode+'.json')
  assert f['strictFoundationAccepted']and f['foundation']['fullyBuriedTriangles']==0
  assert f['worldSHA256']==v['worldSHA256']==raw['sourceWorldSHA256'];sources[uid]=f['sourceSHA256']
  assert v['unresolved']==0 and v['boundedPaths']==v['failures']==len(v['details'])==g['failedSamples']
  assert g['strictSamples']+g['failedSamples']==raw['samples'] and g['strictSamples']==raw['canonicalContacts']
  assert not raw['rawInterface']['passed']
  for d in v['details']:
   assert d['verified'] and d['maximumFaceResidualM']<=.001 and -.1<=d['root']['gap']<=1
   assert d['maximumPathHeightM']<=d['endpointHeightCeilingM']+1e-9
  if mode in ['original','literal']:assert v['worldSHA256']==current[uid]['completeWorldSHA256'] and raw['supportWorldSHA256']==current[POD]['completeWorldSHA256']
  accounts.append(dict(uid=uid,mode=mode,sourceWorldSHA256=v['worldSHA256'],supportWorldSHA256=raw['supportWorldSHA256'],samples=raw['samples'],strictContacts=g['strictSamples'],boundedOriginalWallPaths=v['boundedPaths'],unresolved=0,completeFoundationAccepted=True))
images=[]
for uid in UIDS:
 p=folder('parkview-three-support-views-v1')/(uid.split('/')[1]+'-junctions.png');assert digest(p.read_bytes())==receipts['parkview-three-support-views-v1'][str(p.relative_to(ROOT))];images.append(ref(p));refs.append(p)
review=dict(uids=UIDS,requiredInstalledSupportUid=POD,sourceSHA256ByUid=sources,sampleAccounts=accounts,sourceSpecificSupportAccepted=True,rawCanonicalInterfacePassed=False,rawWarningsRetained=True,sourceGeometryChanges=0,sourcePoseChanges=0,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,reviewer='Codex ROOT',imagesActuallyViewed=images,basis='Exact lower-wall surface continuity resolves the terrain-only rim interpretation for these two source revisions. Every raw failed rim sample follows finite original wall/upward faces through exact shared edges to an existing strict podium contact; no path rises above its own endpoint-height ceiling. All complete-source foundations pass in all four coordinate representations. Opposite cropped junction views show lower wall outlines among the original podium levels. They provide context only and do not prove hiddenness or structural engineering roles. No tolerance or geometry changes.',scope='Support interpretation only. The installed podium publication flag still requires explicit evidence reconciliation. Current full-browser appearance, picking/collision, dependency failure recovery, neighbours and guarded publication remain independent required gates. This is not full installation or optimisation approval.',fullAcceptance=False,installationApproved=False,publicationApproved=False)
save(DOC/'ROOT-SUPPORT-REVIEW.json',review)
module('parkview_two_support_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'two-originals-bounded-lower-wall-support-review',list(dict.fromkeys(refs)),dict(uids=UIDS,sourceSpecificSupportAccepted=True,fullAcceptance=False,installationApproved=False))
