"""Record ROOT review of actual desktop/mobile exports; ground closeups still pending."""
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from pathlib import Path
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-china-ferry-five-image-review-v1-20261020';DOC=BASE/BATCH
assert not DOC.exists();refs=[Path(__file__)];pins={};images=[];summaries=[]
for device,width in [('desktop',1280),('mobile',390)]:
 folder=BASE/('government-xl-china-ferry-five-browser-'+device+'-v1-20261020');r=read(folder/'result.json')
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 refs.append(folder/'result.json')
 for e in r['evidenceRefs']:
  assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 report=read(folder/'staged-browser.json');assert report['passed']and not report['errors'];screens=[v for v in report['views']if 'file'in v];assert len(screens)==10
 for v in screens:
  assert v['width']==width and v['active']and v['visible']and v['fullyFramed']and not v['overflow']and v['fallbackFaces']==0
  p=folder/v['file'];assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];images.append(dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()),uid=v['uid'],width=width,time=v['time']))
 failed=[v for v in report['views']if v.get('phase')=='failed-download'];assert len(failed)==(5 if width==390 else 0)
 summaries.append(dict(width=width,views=10,failedDownloadRecoveries=len(failed)))
for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
review=dict(uids=sorted({v['uid']for v in images}),imagesActuallyViewed=images,reviewer='Codex ROOT',ordinaryModelViewsAccepted=True,wholeSiteVisualAcceptance=False,installationApproved=False,views=summaries,findings='All five exact original model bodies are visible in day/night exports. Original roof edges, recesses and serrated hotel facade are retained. No procedural windows are added to the sources; neighbouring BASIC forms retain their own windows. Mobile intermediate error banners occur during intentional independent candidate failures; final candidate recovers. These elevated cameras do not resolve the two low terminal perimeter intersections.',remaining='Focused lower-perimeter views and collision/visible-ground interpretation, retained Gateway regression browser, and final private guarded-base staging remain separate requirements.')
save(DOC/'ROOT-IMAGE-REVIEW.json',review)
module('china_image_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'five-original-desktop-mobile-export-review',list(dict.fromkeys(refs)),dict(uids=review['uids'],imagesActuallyViewed=20,ordinaryModelViewsAccepted=True,installationApproved=False))
