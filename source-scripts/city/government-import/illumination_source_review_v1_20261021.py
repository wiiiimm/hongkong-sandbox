"""Bind completed exact original, neighbour and explicitly inspected joint browser evidence."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-illumination-source-review-v1-20261021';DOC=BASE/BATCH;UIDS=['landsd/255531:0','landsd/258737:0']
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={}
 def take(n,p):
  _,ps=authenticate(BASE/n);k=str(p.relative_to(ROOT));assert ref(p)['sha256']==ps[k];pins[k]=ps[k];refs.extend([BASE/n/'result.json',p]);return read(p)
 n='government-xl-illumination-physical-review-v2-20261021';physical=take(n,BASE/n/'ROOT-PHYSICAL-REVIEW.json');assert physical['sourceSpecificPhysicalInterpretationAccepted'] and physical['rawCanonicalFailuresPreserved'];sources=physical['sourceSHA256ByUid'];assert set(sources)==set(UIDS)
 n='government-xl-illumination-loader-v1-20261021';loader=take(n,BASE/n/'summary.json');assert loader['models']==loader['loaderAccepted']==loader['checksPassed']==2 and loader['exceptions']==0
 n='government-xl-illumination-regional-scope-v2-20261021';scope=take(n,BASE/n/'scope.json');assert scope['currentNativeActors']==6830 and scope['touchingNativeUids']==[] and scope['overlappingPatches']==[]
 n='government-xl-illumination-form-regression-v2-20261021';ordinary=take(n,BASE/n/'summary.json');assert ordinary['forms']==70 and ordinary['ordinaryFlagged']==0
 assert ordinary['flagged']==[]
 mobile='government-xl-illumination-mobile-base-ready-v1-20261021';desktop='government-xl-illumination-staged-browser-v1-20261021';archive='government-xl-illumination-browser-failure-record-v1-20261021';folder=BASE/mobile;reports=[];expectedImages=set()
 oldcat=take(archive,HERE/'local'/desktop/'catalogue.json');newcat=take(mobile,HERE/'local'/mobile/'catalogue.json');assert oldcat==newcat
 oldterrain=take(archive,HERE/'local'/desktop/'browser-config-1280.json')['terrain'];assert oldterrain==take(mobile,HERE/'local'/mobile/'browser-config-390.json')['terrain']
 for width in [1280,390]:
  n=archive if width==1280 else mobile;p=BASE/(desktop if width==1280 else mobile)/str(width)/'staged-browser.json';r=take(n,p);assert r['passed']and not r['errors'];views=[v for v in r['views']if 'time'in v];assert len(views)==4
  for v in views:assert v['active']and v['visible']and v['fullyFramed']and v['solidAppearance']and not v['fallbackFaces']and v['pick']==v['collision']==v['uid']and v['sourceSHA256']==sources[v['uid']]
  assert r['jointViews'] and all({m['uid']for m in j['models']}==set(UIDS) and all(m['active']and m['visible']and m['fallbackFaces']==0 and m['sourceSHA256']==sources[m['uid']]for m in j['models'])for j in r['jointViews'])
  if width==390:assert {v['uid']for v in r['views']if v.get('phase')=='failed-download'and v['fallbackRetained']}==set(UIDS)
  expectedImages.update(str((p.parent/v['file']).relative_to(ROOT))for v in views)
  reports.append(ref(p))
 # ROOT must actually inspect the four exact desktop/mobile day/night exports.
 inspected=read(folder/'ROOT-INSPECTED-EXPORTS.json');assert inspected['reviewer']=='ROOT'and inspected['visualAcceptance']is True
 images=inspected['imagesActuallyViewed'];assert len(images)==8 and len({q['path']for q in images})==8
 imagePins={}
 assert {q['path']for q in images}==expectedImages
 for n in [archive,mobile]:
  _,ps=authenticate(BASE/n);imagePins.update(ps)
 for q in images:assert ref(ROOT/q['path'])==q and imagePins[q['path']]==q['sha256'];refs.append(ROOT/q['path'])
 refs.append(folder/'ROOT-INSPECTED-EXPORTS.json');manifest=ROOT/'3d-viewer/city/data/manifest.json'
 rn='government-xl-illumination-inset-runtime-v2-20261021';metric=take(rn,BASE/rn/'metrics.json');assert metric['inputHashes'][str(manifest.relative_to(ROOT))]==ref(manifest)['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h
 review=dict(uids=UIDS,sourceSHA256ByUid=sources,currentManifest=ref(manifest),identityAccepted=True,sourceSpecificPhysicalInterpretationAccepted=True,completeNeighbourInterpretationAccepted=True,visualAcceptance=True,imagesActuallyViewed=images,browserReports=reports,unchangedBaselineNeighbourFlags=[],sourceGeometryChanges=0,sourcePoseChanges=0,aiGeometryModelling=False,sourceEvidenceInterpretationUsedAI=True,installationApproved=False,qualification='Exact Illumination identities and unchanged original tower/podium support pass. Podium face1044 retains source-specific original wall-ground embedment interpretation and all raw clearance negatives. All70 forms pass their checks; complete current actor bounds nominate zero installed neighbours. Staged desktop/mobile collision, selection, visibility and failed-download recovery verified; ROOT inspected exact exports. Cold-map runs timed out; the mobile pass waits for base-tile completion before testing unchanged60second model activation and recovery. This provides settled-map correctness evidence, not a cold-load performance pass. Live publication verification remains required.')
 save(DOC/'ROOT-SOURCE-REVIEW.json',review);refs.append(manifest);r=module('piers_source_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-original-qualified-source-review',list(dict.fromkeys(refs)),review);print(r['jobId'],flush=True)
if __name__=='__main__':main()
