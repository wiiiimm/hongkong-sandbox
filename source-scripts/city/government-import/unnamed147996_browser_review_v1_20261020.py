from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-unnamed147996-browser-review-v1-20261020';DOC=BASE/BATCH
assert not DOC.exists();refs=[Path(__file__)];images=[];reports=[];pins={}
for kind,width in [('desktop',1280),('mobile',390)]:
 folder=BASE/('government-xl-unnamed147996-browser-'+kind+'-v3-20261020');r=read(folder/'result.json')
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 assert r['browserExitCode']==0;refs.append(folder/'result.json')
 for e in r['evidenceRefs']:
  assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 report=read(folder/'staged-browser.json');assert report['passed']and not report['errors']and len([v for v in report['views']if 'time'in v])==2
 reports.append(dict(path=str((folder/'staged-browser.json').relative_to(ROOT)),sha256=digest((folder/'staged-browser.json').read_bytes())))
 for t in ['1500','2200']:
  p=folder/('staged-landsd-147996-0-'+str(width)+'-'+t+'.png');images.append(dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes())))
for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
manifest=ROOT/'3d-viewer/city/data/manifest.json'
review=dict(uids=['landsd/147996:0'],reviewer='Codex ROOT',visualAcceptance=True,imagesActuallyViewed=images,browserReports=reports,currentManifest=dict(path=str(manifest.relative_to(ROOT)),sha256=digest(manifest.read_bytes())),observations=['All four v3 exports actually inspected: desktop1280 and mobile390 day15:00/night22:00. Higher oblique camera exposes the narrow original roof, raised projections and stepped outline.', 'Adjacent buildings obscure portions of the facades; no claim of complete facade visibility. Complete isolated source views were reviewed separately for identity. Neighbouring buildings remain rendered.', 'The detailed source has no procedural window overlay. Day/night geometry is coherent with no visible new separation at the exposed roof. Model picking/collision and failed-load/retry assertions pass.', 'Desktop v1 was obstructed; v2 runner rejected a multi-viewport configuration before rendering. Neither grants visual acceptance. Surrounding tile loading and unavailable progress stats remain visible in exports; this is not a whole-city loading or mobile performance certification.'],sourceGeometryChanges=0,aiGeometryModelling=False,installationApproved=False,publicationApproved=False)
save(DOC/'ROOT-IMAGE-REVIEW.json',review)
module('unnamed_browser_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'unnamed147996-corrected-private-desktop-mobile-visual-review',list(set(refs)),review)
