"""Bind the reviewed exact-source physical evidence and twelve inspected browser exports."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from skytower_original_catalogue_scope_v1_20261024 import UID,PARENT,SOURCES,RETAINED,RETAINED_SHA,RETAINED_FACES
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-skytower-original-source-review-v1-20261024';BROWSER='government-xl-skytower-elements-suntower-private-browser-v1-20261024'
def main():
 out=BASE/BATCH;assert not out.exists();refs=[Path(__file__),HERE/'skytower_original_catalogue_scope_v1_20261024.py'];pins={}
 def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
 def take(n,f):
  if n not in pins:pins[n]=authenticate(BASE/n)[1];refs.append(BASE/n/'result.json')
  p=BASE/n/f;assert ref(p)['sha256']==pins[n][ref(p)['path']];refs.append(p);return read(p)
 review=take('government-xl-skytower-original-physical-review-v1-20261024','ROOT-PHYSICAL-REVIEW.json');assert review['sourceSHA256ByUid']==SOURCES and review['sourceSpecificPhysicalInterpretationAccepted']and review['identityAccepted']and review['completeNeighbourInterpretationAccepted']and review['completeFourWorldFoundations']
 n='government-xl-skytower-actual-ground-four-world-foundations-v1-20261024';foundation=take(n,'summary.json');assert len(foundation['rows'])==4
 for r in foundation['rows']:assert r['completeTerrainTriangles']==r['triangles']==10887 and r['fullyBuriedTriangles']==r['fullyBuriedUpwardTriangles']==0
 browser,pins[BROWSER]=authenticate(BASE/BROWSER);refs.append(BASE/BROWSER/'result.json');assert not browser['installationApproved']
 reports=[];expected={}
 for width in [1280,390]:
  path=BASE/BROWSER/str(width)/'staged-browser.json';r=take(BROWSER,str(width)+'/staged-browser.json');assert r['passed']and not r['errors'];reports.append(ref(path))
  own=[v for v in r['views']if'time'in v];assert len(own)==2
  for v in own:
   assert v['uid']==UID and v['sourceSHA256']==SOURCES[UID]and v['fullyFramed']and v['solidAppearance']and v['pick']==v['collision']==UID and not v['fallbackFaces']
  retained=r['retainedNativeOwnViews'];assert len(retained)==2*len(RETAINED)and{v['uid']for v in retained}==RETAINED
  for v in retained:assert v['sourceSHA256']==RETAINED_SHA[v['uid']]and v['originalTriangles']==RETAINED_FACES[v['uid']]and v['active']and v['visible']and v['fullyFramed']and not v['overflow']and not v['fallbackFaces']and all(v['meshVisibility'])and not any(v['wireframeFlags'])
  assert r['jointViews']and all({m['uid']:m['sourceSHA256']for m in j['models']}==SOURCES and all(m['active']and m['visible']and not m['fallbackFaces']for m in j['models'])for j in r['jointViews'])
  if width==390:
   failures=[v for v in r['views']if v.get('phase')=='failed-download'];assert len(failures)==1 and failures[0]['uid']==UID and failures[0]['fallbackRetained']
  for v in own+retained:
   p=BASE/BROWSER/str(width)/v['file'];assert ref(p)['sha256']==pins[BROWSER][ref(p)['path']];refs.append(p);key=(v['uid'],width,v['time']);assert key not in expected;expected[key]=dict(**ref(p),uid=v['uid'],width=width,time=v['time'])
 binding=BASE/'government-xl-skytower-private-browser-inspection-v1-20261024/panel-bindings.json';sheets=read(binding);refs.append(binding);images=[];previews=[]
 for row in sheets['rows']:
  p=ROOT/row['path'];assert ref(p)['sha256']==row['sha256'];refs.append(p);previews.append(ref(p))
  for i in row['panels']:
   key=(i['uid'],i['width'],i['time']);assert i==expected[key];images.append(i)
 assert len(images)==len({i['path']for i in images})==12 and len(expected)==12 and len(previews)==3
 manifest=ROOT/'3d-viewer/city/data/manifest.json';assert ref(manifest)==review['currentManifest'];refs.append(manifest)
 result={**review,'originalSourceReviewAccepted':True,'visualAcceptance':True,'completeActualGroundFourWorldFoundationReceipt':ref(BASE/n/'result.json'),'browserReports':reports,'imagesActuallyViewed':[i for i in images if i['uid']==UID],'retainedImagesActuallyViewed':[i for i in images if i['uid']in RETAINED],'inspectionPreviewsActuallyViewed':previews,'rawClearancePassed':False,'rawStrictSupportPassed':False,'qualifiedFourWorldSourceClearance':True,'observations':[
 'ROOT inspected all12exact full-frame source/retained desktop/mobile day/night exports via3hash-bound sheets, plus the scientific source/podium/ground two-angle wall plot and complete source/footprint plots. The new tall original is solid, framed and recognisable; all3actors remain visible in their own views. Lower neighbouring volumes naturally occlude some facades. Original Skytower/Suntower are dark at night; nearby ordinary lit skins remain. This is a faithful source-port and runtime review, not photographic architectural completeness.',
 'Allfour complete actual-ground foundation reports independently confirm zero whole/upward burial; all10strict unresolved probes have finite original paths to Elements. Six exact lower wall faces cross the original podium top with exposed upper vertices and clear-cap paths in every coordinate stream. Both retained original assets and their existing dependencies are unchanged. No new procedural window skin, terrain edit, native metadata migration or geometry simplification.',
 'Mobile deliberately denied only the new source asset, retained its fallback and recovered the original by retry. Picking/collision, all original body triangle counts, full framing, final joint activation and both retained own-source day/night views pass. No missing native view is defaulted. The exact3-source identity context and existing numerical limits are bound in the physical review. Publication still requires fenced complete-source guards and a fresh installed browser/readback.' ],'installationApproved':False,'publication':False}
 save(out/'ROOT-SOURCE-REVIEW.json',result);save(out/'ROOT-PHYSICAL-REVIEW.json',result)
 module('skytower_source_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-original-skytower-supported-source-and-inspected-preview-review',refs,dict(uids=[UID],sourceSHA256ByUid=SOURCES,originalSourceReviewAccepted=True,identityAccepted=True,sourceSpecificPhysicalInterpretationAccepted=True,visualAcceptance=True,installationApproved=False,sourceGeometryChanges=0))
if __name__=='__main__':main()
