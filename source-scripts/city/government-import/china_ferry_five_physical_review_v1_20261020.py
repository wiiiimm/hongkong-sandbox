"""Exact unchanged compound physical interpretation; private staging only."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-china-ferry-five-physical-review-v1-20261020';DOC=BASE/BATCH
names=['five-private-terrain-v1','five-four-mode-foundations-v1','four-mode-support-v1','podium-rim-verification-v2','buried-face-verification-v2','lower-perimeter-review-v1','perimeter-browser-v1','estimated-base-proposal-v1','current-neighbours-v1'];folders={n:BASE/('government-xl-china-ferry-'+n+'-20261020')for n in names};pins={};refs=[Path(__file__)]
assert not DOC.exists()
with connect()as c:
 c.execute('SET TRANSACTION READ ONLY')
 for f in folders.values():
  r=read(f/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(f/'result.json')
  for e in r['evidenceRefs']:
   assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
rows=read(folders['five-private-terrain-v1']/'selection.json.gz')['rows'];sources={r['uid']:r['sourceSHA256']for r in rows};POD='landsd/285642:0';assert len(sources)==5
context=read(folders['lower-perimeter-review-v1']/'ROOT-LOWER-PERIMETER-REVIEW.json');assert context['sourceRoleContextResolved']and context['sourceSHA256']==sources[POD]
browser=read(folders['perimeter-browser-v1']/'staged-browser.json');assert browser['passed']and not browser['errors']and len(browser['perimeterViews'])==2
for r in browser['perimeterViews']:
 assert r['sourceSHA256']==sources[POD]and r['active']and r['drawnGroundHits']and abs(r['drawnGroundHits'][0]-r['sampler'])<.004
support=read(folders['four-mode-support-v1']/'summary.json')['rows'];assert len(support)==16 and all(r['passed']and r['strictContacts']==r['samples']and r['unresolved']==0 for r in support)
accounts=[]
for mode in ['original','literal','explicitLeftF32','explicitBalancedF32']:
 rim=read(folders['podium-rim-verification-v2']/(mode+'.json'));faces=read(folders['buried-face-verification-v2']/(mode+'.json'))
 assert len(rim['rows'])==61 and len(faces['rows'])==79 and all(x['finitePathVerified']and x['withinEndpointHeight']for x in rim['rows']+faces['rows'])
 for r in rows:
  uid=r['uid'];f=read(folders['five-four-mode-foundations-v1']/(uid.split('/')[1]+'-'+mode+'.json'));assert f['foundation']['completeTerrainTriangles']==r['candidate']['entry']['triangles']
  if uid==POD:
   assert f['worldSHA256']==rim['sourceWorldSHA256']==faces['sourceWorldSHA256'] and f['foundation']['fullyBuriedTriangles']==79 and f['foundation']['fullyBuriedUpwardTriangles']==8
   accounts.append(dict(uid=uid,mode=mode,worldSHA256=f['worldSHA256'],rawBuriedFaces=79,rawUpwardBuriedFaces=8,canonicalRimFiniteRoutes=61,faceCentreFiniteRoutes=79,interpretation='Exact lower exterior source/ground intersections accepted; not a claim of whole-face clearance.'))
  else:
   assert f['strictFoundationAccepted'];a=next(x for x in support if x['uid']==uid and x['mode']==mode);accounts.append(dict(uid=uid,mode=mode,worldSHA256=f['worldSHA256'],strictContacts=a['strictContacts'],rawBuriedFaces=0))
review=dict(uids=sorted(sources),sourceSHA256ByUid=sources,sourceSpecificPhysicalInterpretationAccepted=True,rawStrictFailuresRetained=True,reviewer='Codex ROOT',accounts=accounts,installationApproved=False,sourceGeometryChanges=0,sourcePoseChanges=0,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,basis='The exact 79 lower source facets lie in two narrow exterior perimeter regions, including eight sloping edge facets below3.32m. The complete source has20,464faces and rises above20m; its principal body and four supported companions are not buried. Actual source/ground closeups show the exposed boundary and adjoining ground; raycast and production sampler agree at both views. All61canonical low-rim samples and79affected-face centres have independently verified finite original-face routes to positive-dimensional ground contacts within endpoint heights in four representations. This is not a proof that every affected point clears terrain: these exact original lower intersections are accepted as embedded perimeter geometry. Official podium/two-basement record is supporting context, not an independent waiver. Mixed underside routes and interior terrain contacts remain recorded; no engineering/watertightness claim. Four elevated companions pass full strict foundation and support. No generic threshold change, source movement, clipping, simplification or suppression is approved. Final identity, retained-neighbour, visual, publisher and live checks remain required.',reviewedPerimeterImages=[dict(path=str((folders['perimeter-browser-v1']/r['file']).relative_to(ROOT)),sha256=digest((folders['perimeter-browser-v1']/r['file']).read_bytes()))for r in browser['perimeterViews']])
save(DOC/'ROOT-PHYSICAL-REVIEW.json',review)
for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
module('china_physical_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-five-original-source-specific-physical-interpretation',list(dict.fromkeys(refs)),dict(uids=sorted(sources),sourceSpecificPhysicalInterpretationAccepted=True,installationApproved=False))
