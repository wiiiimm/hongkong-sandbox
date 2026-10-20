"""Record actual inspected exports and framing limitation; no acceptance waiver."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-victoria-mall-four-original-image-review-v1-20261020';DOC=BASE/BATCH;SRC=BASE/'government-xl-victoria-mall-four-original-browser-v1-20261020'
assert not DOC.exists();receipt=read(SRC/'result.json');refs=[Path(__file__),SRC/'result.json'];pins={e['path']:e['sha256']for e in receipt['evidenceRefs']};images=[]
with connect() as c:
 c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
for width in [390,1280]:
 p=SRC/str(width)/'staged-browser.json';assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p);report=read(p);assert report['passed'] and not report['errors']
 for v in report['views']:
  if 'file'not in v:continue
  p=SRC/str(width)/v['file'];assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p);images.append(dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes())))
assert len(images)==16
review=dict(reviewer='Codex ROOT',uids=receipt['uids'],imagesActuallyViewed=images,scriptedRuntimePassed=True,visualAcceptance=False,installationApproved=False,sourceGeometryChanges=0,observations=['All16 exported PNGs were individually viewed through view_image. Original mall walls and terraces are visible; selected original towers show plain facades without procedural windows.','Tower tops are cropped in several exports and mobile controls obscure lower parts, despite fullyFramed=true. Do not use that flag as full visual acceptance.','Some mobile banners reflect deliberately induced download failures and background work; scripted recovery checks pass, but these images alone do not prove a quiet settled loading state.','The original source geometry is not implicated. A separate camera-framing retry keeps this completed runtime evidence immutable.'],nextAction='Increase private inspection-camera framing margin, disable residual camera damping before placement, and inspect new day/night exports. Keep all earlier raw support diagnostics.')
save(DOC/'ROOT-IMAGE-REVIEW.json',review)
module('victoria_four_image_review',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'root-inspected-runtime-exports-framing-limitation',refs,review)
print('16 exports reviewed; full visual acceptance remains pending',flush=True)
