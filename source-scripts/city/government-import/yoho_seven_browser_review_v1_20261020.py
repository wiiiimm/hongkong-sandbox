"""ROOT-reviewed exported desktop assembly and desktop/mobile individual views."""
from pathlib import Path
import shutil
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-yoho-seven-browser-review-v1-20261020';DOC=BASE/BATCH
UIDS=['landsd/300857:0','landsd/301636:0','landsd/300895:0','landsd/300896:0','landsd/300897:0','landsd/301638:0','landsd/301659:0'];POD='landsd/301636:0'
assert not DOC.exists();refs=[Path(__file__)];images=[];reports=[];pins={}
for name,width,group in [('government-xl-yoho-seven-browser-desktop-v3-20261020',1280,True),('government-xl-yoho-seven-browser-own-desktop-v2-20261020',1280,False),('government-xl-yoho-seven-browser-own-mobile-v2-20261020',390,False)]:
 folder=BASE/name;r=read(folder/'result.json')
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 assert r['browserExitCode']==0;refs.append(folder/'result.json')
 for e in r['evidenceRefs']:assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 report=read(folder/'staged-browser.json');views=[v for v in report['views']if 'time'in v];assert report['passed']and not report['errors']and len(views)==14 and {v['uid']for v in views}==set(UIDS)
 assert all(v['fullyFramed']and v['solidAppearance']and not v['fallbackFaces']and v['active']and v['visible']and v['pick']==v['collision']==v['uid']for v in views)
 reports.append(dict(path=str((folder/'staged-browser.json').relative_to(ROOT)),sha256=digest((folder/'staged-browser.json').read_bytes())))
 if width==390:assert {v['uid']for v in report['views']if v.get('phase')=='failed-download'and v['fallbackRetained']}==set(UIDS)
 assert len(report['jointViews'])==(1 if width==390 else 7)
 for joint in report['jointViews']:
  expected=set(UIDS)if group else {joint['selectedUid'],POD};assert {m['uid']for m in joint['models']}==expected and all(m['active']and m['visible']and not m['fallbackFaces']for m in joint['models'])
 for uid in UIDS:
  for t in ['1500','2200']:
   p=folder/('staged-'+uid.replace('/','-').replace(':','-')+'-'+str(width)+'-'+t+'.png');images.append(dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes())))
for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
DOC.mkdir();sheets=[]
for name in ['yoho-desktop-group-contact-sheet.jpg','yoho-mobile-own-contact-sheet.jpg','yoho-desktop-own-contact-sheet.jpg']:
 p=DOC/name;shutil.copyfile(Path('/tmp')/name,p);sheets.append(dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes())))
manifest=ROOT/'3d-viewer/city/data/manifest.json';refs.append(manifest)
review=dict(uids=UIDS,reviewer='Codex ROOT',visualAcceptance=True,imagesActuallyViewed=images,viewedContactSheets=sheets,reviewMethod='All42 exported images reviewed through labelled contact sheets, with full-size clubhouse export additionally inspected. Assembly views establish collective context; individual views establish small-part visibility.',browserReports=reports,currentManifest=dict(path=str(manifest.relative_to(ROOT)),sha256=digest(manifest.read_bytes())),observations=['Four detailed original towers, long podium, rounded clubhouse and small attached source component remain unchanged at source pose. Close-up silhouettes and roof/facade geometry are visible; procedural windows are disabled.', 'Desktop wide views show all7 originals together. Close-up views verify each selected source with its podium dependency; small components need not stay detailed at a distant mobile assembly view under the existing pixel budget.', 'All7 independent mobile failures retain fallback and recover after retry. Some screenshots intentionally show failure banners for not-yet-retried other candidates. UI overlays obscure portions of lower geometry; full geometric support/placement evidence remains separate.', 'Headless desktop/mobile viewport checks do not certify physical-phone FPS. No model geometry generated or edited.'],sourceGeometryChanges=0,aiGeometryModelling=False,installationApproved=False,publicationApproved=False)
save(DOC/'ROOT-IMAGE-REVIEW.json',review)
module('yoho_seven_browser_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'seven-original-exported-desktop-mobile-visual-review',list(dict.fromkeys(refs)),review)
