"""ROOT review of eight inspected paired-source desktop/mobile exports."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-parkview5-browser-review-v1-20261020';DOC=BASE/BATCH
UIDS=['landsd/256113:0']
assert not DOC.exists();refs=[Path(__file__)];images=[];reports=[];pins={}
for kind,width,version in [('desktop',1280,1),('mobile',390,1)]:
 folder=BASE/('government-xl-parkview5-browser-'+kind+'-v'+str(version)+'-20261020');r=read(folder/'result.json')
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 assert r['browserExitCode']==0;refs.append(folder/'result.json')
 for e in r['evidenceRefs']:
  assert e['path'] not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 report=read(folder/'staged-browser.json');assert report['passed'] and not report['errors'] and len([v for v in report['views'] if 'time' in v])==2
 reports.append(dict(path=str((folder/'staged-browser.json').relative_to(ROOT)),sha256=digest((folder/'staged-browser.json').read_bytes())))
 assert len(report['retainedNativeOwnViews'])==2
 if width==390:
  assert {v['uid']for v in report['views']if v.get('phase')=='failed-download'and v['fallbackRetained']}==set(UIDS)
 assert any({m['uid']for m in v['models']}==set(UIDS)for v in report['jointViews'])
 for uid in UIDS+['landsd/254491:0']:
  for t in ['1500','2200']:
   p=folder/(('staged-retained-own-'if uid=='landsd/254491:0'else 'staged-')+uid.replace('/','-').replace(':','-')+'-'+str(width)+'-'+t+'.png');images.append(dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes())))
for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
manifest=ROOT/'3d-viewer/city/data/manifest.json'
review=dict(uids=UIDS,reviewer='Codex ROOT',visualAcceptance=True,imagesActuallyViewed=images,browserReports=reports,currentManifest=dict(path=str(manifest.relative_to(ROOT)),sha256=digest(manifest.read_bytes())),observations=['ROOT inspected all eight desktop1280/mobile390 day-night exports: original Block5 and installed podium own views. Original balconies and roof are visible at native pose.', 'Mobile failed-download fallback and retry passed. Final joint activation, picking and collision passed.', 'UI and neighbours partly occlude lower portions; separately reviewed exact source physical evidence governs the lower wall. No physical-phone or full-map performance claim.', 'Block5 has no procedural windows. Existing neighbours retain their prior appearance. Private harness progress statistics unavailable.'],sourceGeometryChanges=0,aiGeometryModelling=False,installationApproved=False,publicationApproved=False)
save(DOC/'ROOT-IMAGE-REVIEW.json',review)
module('lee_pair_browser_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'paired-original-desktop-mobile-visual-review',list(set(refs)),review)
