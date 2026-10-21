"""Bind completed exact original, neighbour and explicitly inspected joint browser evidence."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-murray-house-source-review-v4-20261021';DOC=BASE/BATCH;UIDS=['landsd/61216:0']
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={}
 def take(n,p):
  _,ps=authenticate(BASE/n);k=str(p.relative_to(ROOT));assert ref(p)['sha256']==ps[k];pins[k]=ps[k];refs.extend([BASE/n/'result.json',p]);return read(p)
 n='government-xl-murray-house-original-policy-v4-20261021';policy=take(n,BASE/n/'summary.json');assert len(policy['rows'])==1 and all(r['originalPolicyPassed']for r in policy['rows']);sources={r['uid']:r['sourceSHA256']for r in policy['rows']};assert set(sources)==set(UIDS)
 n='government-xl-murray-house-current-identity-v1-20261021'
 r=take(n,BASE/n/'identity-proof.json');assert r['passed']and r['sourceSHA256']==sources[UIDS[0]]
 n='government-xl-murray-house-regional-scope-v1-20261021';scope=take(n,BASE/n/'scope.json');assert scope['currentNativeActors']==6822 and scope['touchingNativeUids']==[] and scope['overlappingPatches']==[]
 n='government-xl-murray-house-form-regression-v4-20261021';ordinary=take(n,BASE/n/'summary.json');assert ordinary['forms']==19 and ordinary['ordinaryFlagged']==0
 assert ordinary['flagged']==[]
 n='government-xl-murray-house-staged-browser-v4-20261021';folder=BASE/n;reports=[]
 for width in [1280,390]:
  p=folder/str(width)/'staged-browser.json';r=take(n,p);assert r['passed']and not r['errors'];views=[v for v in r['views']if 'time'in v];assert len(views)==2
  for v in views:assert v['active']and v['visible']and v['fullyFramed']and v['solidAppearance']and not v['fallbackFaces']and v['pick']==v['collision']==v['uid']and v['sourceSHA256']==sources[v['uid']]
  if width==390:assert {v['uid']for v in r['views']if v.get('phase')=='failed-download'and v['fallbackRetained']}==set(UIDS)
  reports.append(ref(p))
 # ROOT must actually inspect the four exact desktop/mobile day/night exports.
 inspected=read(folder/'ROOT-INSPECTED-EXPORTS.json');assert inspected['reviewer']=='ROOT'and inspected['visualAcceptance']is True
 images=inspected['imagesActuallyViewed'];assert len(images)==4 and len({q['path']for q in images})==4
 imagePins={}
 for n in [folder.name]:
  _,ps=authenticate(BASE/n);imagePins.update(ps)
 for q in images:assert ref(ROOT/q['path'])==q and imagePins[q['path']]==q['sha256'];refs.append(ROOT/q['path'])
 refs.append(folder/'ROOT-INSPECTED-EXPORTS.json');manifest=ROOT/'3d-viewer/city/data/manifest.json'
 rn='government-xl-murray-house-candidate-runtime-v4-20261021';metric=take(rn,BASE/rn/'metrics.json');assert metric['inputHashes'][str(manifest.relative_to(ROOT))]==ref(manifest)['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h
 review=dict(uids=UIDS,sourceSHA256ByUid=sources,currentManifest=ref(manifest),identityAccepted=True,sourceSpecificPhysicalInterpretationAccepted=True,completeNeighbourInterpretationAccepted=True,visualAcceptance=True,imagesActuallyViewed=images,browserReports=reports,unchangedBaselineNeighbourFlags=[],sourceGeometryChanges=0,sourcePoseChanges=0,aiGeometryModelling=False,sourceEvidenceInterpretationUsedAI=True,installationApproved=False,qualification='Exact original walkway/exterior-projection identity and unchanged existing physical/mobile policy pass. All 19 forms pass their checks; complete current actor bounds nominate zero installed neighbours. Staged desktop/mobile collision, selection, visibility and failed-download recovery verified; ROOT inspected exact exports. Live publication verification remains required.')
 save(DOC/'ROOT-SOURCE-REVIEW.json',review);refs.append(manifest);r=module('piers_source_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-original-qualified-source-review',list(dict.fromkeys(refs)),review);print(r['jobId'],flush=True)
if __name__=='__main__':main()
