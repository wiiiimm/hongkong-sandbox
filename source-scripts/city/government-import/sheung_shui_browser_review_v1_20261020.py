from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-sheung-shui-browser-review-v1-20261020';DOC=BASE/BATCH
assert not DOC.exists();refs=[Path(__file__)];images=[];reports=[];pins={}
for kind,width in [('desktop',1280),('mobile',390)]:
 folder=BASE/('government-xl-sheung-shui-browser-'+kind+'-v2-20261020');r=read(folder/'result.json')
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 assert r['browserExitCode']==0;refs.append(folder/'result.json')
 for e in r['evidenceRefs']:
  assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 report=read(folder/'staged-browser.json');assert report['passed']and not report['errors']and len([v for v in report['views']if 'time'in v])==2
 reports.append(dict(path=str((folder/'staged-browser.json').relative_to(ROOT)),sha256=digest((folder/'staged-browser.json').read_bytes())))
 for t in ['1500','2200']:
  p=folder/('staged-landsd-56054-0-'+str(width)+'-'+t+'.png');images.append(dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes())))
for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
manifest=ROOT/'3d-viewer/city/data/manifest.json'
review=dict(uids=['landsd/56054:0'],reviewer='Codex ROOT',visualAcceptance=True,imagesActuallyViewed=images,browserReports=reports,currentManifest=dict(path=str(manifest.relative_to(ROOT)),sha256=digest(manifest.read_bytes())),observations=['All four corrected-v2 exports actually inspected: desktop1280 and mobile390, day15:00 and night22:00. Entire original complex renders at native pose with stepped roof blocks, long wings and end roof detail visible.','Neighbour basic structures remain present; this review authorises no suppression of the five overlapping records. No procedural facade-window overlay on the detailed source.','Mobile panels and minimap obscure part of the foreground in the screenshot; visible source geometry is coherent. Desktop view provides fuller composition coverage. These are model acceptance views, not a mobile performance certification.','V1 desktop run used incorrect terrain resolution metadata and is excluded. V2 uses cell5 from the candidate. Loading HUD was still progressing for surrounding map tiles at capture; browser model/fallback checks passed, but this is not an all-city loading-complete claim.'],sourceGeometryChanges=0,aiGeometryModelling=False,installationApproved=False,publicationApproved=False)
save(DOC/'ROOT-IMAGE-REVIEW.json',review)
module('sheung_shui_browser_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'sheung-shui-corrected-private-desktop-mobile-visual-review',list(set(refs)),review)
