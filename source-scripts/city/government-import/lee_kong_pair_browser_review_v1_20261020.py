"""ROOT review of eight inspected paired-source desktop/mobile exports."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-lee-kong-pair-browser-review-v1-20261020';DOC=BASE/BATCH
UIDS=['landsd/72296:0','landsd/253697:0']
assert not DOC.exists();refs=[Path(__file__)];images=[];reports=[];pins={}
for kind,width,version in [('desktop',1280,2),('mobile',390,3)]:
 folder=BASE/('government-xl-lee-kong-pair-browser-'+kind+'-v'+str(version)+'-20261020');r=read(folder/'result.json')
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 assert r['browserExitCode']==0;refs.append(folder/'result.json')
 for e in r['evidenceRefs']:
  assert e['path'] not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 report=read(folder/'staged-browser.json');assert report['passed'] and not report['errors'] and len([v for v in report['views'] if 'time' in v])==4
 reports.append(dict(path=str((folder/'staged-browser.json').relative_to(ROOT)),sha256=digest((folder/'staged-browser.json').read_bytes())))
 for uid in UIDS:
  for t in ['1500','2200']:
   p=folder/('staged-'+uid.replace('/','-').replace(':','-')+'-'+str(width)+'-'+t+'.png');images.append(dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes())))
for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
manifest=ROOT/'3d-viewer/city/data/manifest.json'
review=dict(uids=UIDS,reviewer='Codex ROOT',visualAcceptance=True,imagesActuallyViewed=images,browserReports=reports,currentManifest=dict(path=str(manifest.relative_to(ROOT)),sha256=digest(manifest.read_bytes())),observations=['ROOT inspected all eight exports: desktop1280 and mobile390 day/night for the original podium and tower. The high oblique view exposes the stepped tower roof and lower assembly amid neighbouring buildings.', 'Neighbouring buildings obscure portions of the lower facades. Complete isolated source views were inspected separately; these captures do not prove every facade visible or physical phone performance.', 'The original pair uses no procedural window overlay. Original geometry, picking/collision and solid material checks pass. The tower explicitly depends on the original podium; joint activation passes.', 'Desktopv1 had an obstructed camera. Mobilev2 simultaneously blocked both dependent sources and timed out after tower-only retry. Neither grants acceptance. Mobilev3 tests tower failed-download fallback/retry with the supporting original available. Raw failed-run evidence is retained.', 'Background neighbourhood loading and unavailable progress statistics remain visible during captures. This is not certification of full-map load completion or performance.'],sourceGeometryChanges=0,aiGeometryModelling=False,installationApproved=False,publicationApproved=False)
save(DOC/'ROOT-IMAGE-REVIEW.json',review)
module('lee_pair_browser_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'paired-original-desktop-mobile-visual-review',list(set(refs)),review)
