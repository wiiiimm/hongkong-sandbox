"""ROOT review of eight inspected paired-source desktop/mobile exports."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-tower6803-browser-review-v2-20261020';DOC=BASE/BATCH
UIDS=['landsd/15047:0','landsd/6803:0']
assert not DOC.exists();refs=[Path(__file__)];images=[];reports=[];pins={}
for kind,width,version in [('desktop',1280,1),('mobile',390,1)]:
 folder=BASE/('government-xl-tower6803-browser-'+kind+'-v'+str(version)+'-20261020');r=read(folder/'result.json')
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 assert r['browserExitCode']==0;refs.append(folder/'result.json')
 for e in r['evidenceRefs']:
  assert e['path'] not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 report=read(folder/'staged-browser.json');assert report['passed'] and not report['errors'] and len([v for v in report['views'] if 'time' in v])==4
 reports.append(dict(path=str((folder/'staged-browser.json').relative_to(ROOT)),sha256=digest((folder/'staged-browser.json').read_bytes())))
 assert not report.get('retainedNativeOwnViews',[])
 if width==390:
  assert {v['uid']for v in report['views']if v.get('phase')=='failed-download'and v['fallbackRetained']}==set(UIDS)
 assert any({m['uid']for m in v['models']}==set(UIDS)for v in report['jointViews'])
 for uid in UIDS:
  for t in ['1500','2200']:
   p=folder/('staged-'+uid.replace('/','-').replace(':','-')+'-'+str(width)+'-'+t+'.png');images.append(dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes())))
for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
manifest=ROOT/'3d-viewer/city/data/manifest.json'
review=dict(uids=UIDS,reviewer='Codex ROOT',visualAcceptance=True,imagesActuallyViewed=images,browserReports=reports,currentManifest=dict(path=str(manifest.relative_to(ROOT)),sha256=digest(manifest.read_bytes())),observations=['ROOT inspected all8 desktop1280/mobile390 day-night exports. Original tower facade projections and roof, plus its original podium, appear at native pose. No procedural windows on either imported asset.', 'Mobile podium views intentionally retain the base tower while tower download is blocked for independent failure/retry. Tower views and final joint activation show both originals. Picking/collision, failed-download fallback and retry pass for both assets.', 'Some lower details are occluded by map UI; source-specific finite physical evidence governs the reviewed facade feature. Browser viewport tests do not establish physical-phone or whole-map performance. Private progress statistics unavailable.'],sourceGeometryChanges=0,aiGeometryModelling=False,installationApproved=False,publicationApproved=False)
save(DOC/'ROOT-IMAGE-REVIEW.json',review)
module('lee_pair_browser_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'paired-original-desktop-mobile-visual-review',list(set(refs)),review)
