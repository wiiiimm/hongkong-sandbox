"""Final source review requires exact completed desktop/mobile exports actually inspected."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-ronsdale-source-review-v1-20261022';DOC=BASE/BATCH
UIDS={'landsd/256898:0','landsd/256702:0','landsd/233771:0'}
def main():
 assert not DOC.exists();refs=[Path(__file__)];cache={}
 def take(n,p):
  if n not in cache:cache[n]=authenticate(BASE/n)[1];refs.append(BASE/n/'result.json')
  assert digest(p.read_bytes())==cache[n][str(p.relative_to(ROOT))];refs.append(p);return read(p)
 def doc(n,f):return take(n,BASE/n/f)
 physical=doc('government-xl-ronsdale-three-source-acceptance-v1-20261022','ROOT-PHYSICAL-REVIEW.json');assert all(physical[k]for k in ['identityAccepted','sourceSpecificPhysicalInterpretationAccepted','completeNeighbourInterpretationAccepted']);sources=physical['sourceSHA256ByUid'];assert set(sources)==UIDS
 loader=doc('government-xl-ronsdale-loader-v1-20261022','summary.json');assert loader['models']==loader['loaderAccepted']==loader['checksPassed']==3 and loader['exceptions']==0
 browser='government-xl-ronsdale-three-staged-browser-v2-20261022';reports=[];expected=set()
 for width in [1280,390]:
  p=BASE/browser/str(width)/'staged-browser.json';r=take(browser,p);assert r['passed']and not r['errors'];views=[v for v in r['views']if 'time'in v];assert len(views)==6
  for v in views:assert v['active']and v['visible']and v['fullyFramed']and v['solidAppearance']and not v['fallbackFaces']and v['pick']==v['collision']==v['uid']and v['sourceSHA256']==sources[v['uid']]
  assert r['jointViews']and all({m['uid']for m in j['models']}==UIDS and all(m['active']and m['visible']and not m['fallbackFaces']and m['sourceSHA256']==sources[m['uid']]for m in j['models'])for j in r['jointViews'])
  if width==390:assert {v['uid']for v in r['views']if v.get('phase')=='failed-download'and v['fallbackRetained']}==UIDS
  expected.update(str((p.parent/v['file']).relative_to(ROOT))for v in views);reports.append(dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes())))
 inspected=HERE/'local/government-xl-ronsdale-root-image-inspection-20261022/ROOT-INSPECTED-EXPORTS.json';viewed=read(inspected);assert viewed['reviewer']=='ROOT'and viewed['visualAcceptance']is True;images=viewed['imagesActuallyViewed'];assert len(images)==len({q['path']for q in images})==12 and {q['path']for q in images}==expected;refs.append(inspected)
 for q in images:assert digest((ROOT/q['path']).read_bytes())==q['sha256']==cache[browser][q['path']];refs.append(ROOT/q['path'])
 manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==physical['currentManifest']['sha256'];refs.append(manifest)
 result=dict(uids=sorted(UIDS),sourceSHA256ByUid=sources,currentManifest=physical['currentManifest'],identityAccepted=True,sourceSpecificPhysicalInterpretationAccepted=True,completeNeighbourInterpretationAccepted=True,visualAcceptance=True,imagesActuallyViewed=images,browserReports=reports,requiredOriginalAssembly=sorted(UIDS),requiredEstimatedBaseUpdates=physical['requiredEstimatedBaseUpdates'],sourceGeometryChanges=0,sourcePoseChanges=0,aiGeometryModelling=False,sourceEvidenceInterpretationUsedAI=True,installationApproved=False,qualification='Exact original two-tower/podium assembly at unchanged1x/source pose. All four complete world-coordinate arrays identical; complete source foundations, strict/finite tower contacts and all22ordinary-form obligations bound. Unsurveyed canopy estimate remains separately guarded; surveyed fields, footprint and estimated height unchanged. Corrected dependency-first desktop/mobile staged browser passed all3failure/recovery,picking/collision,solid visibility and joint activation checks. ROOT inspected all12unobstructedday/nightexports. Cold basemap startup is infrastructure context, not a performance guarantee. Guarded publication and live verification remain required.')
 save(DOC/'ROOT-SOURCE-REVIEW.json',result);save(DOC/'ROOT-INSPECTED-EXPORTS.json',viewed);module('ronsdale_final_source_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-original-assembly-qualified-source-review',refs,result)
if __name__=='__main__':main()
