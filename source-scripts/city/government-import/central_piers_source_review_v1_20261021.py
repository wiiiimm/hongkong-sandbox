"""Bind completed exact original, neighbour and explicitly inspected joint browser evidence."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-central-piers-source-review-v1-20261021';DOC=BASE/BATCH;UIDS=['landsd/213352:0','landsd/285475:0']
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={}
 def take(n,p):
  _,ps=authenticate(BASE/n);k=str(p.relative_to(ROOT));assert ref(p)['sha256']==ps[k];pins[k]=ps[k];refs.extend([BASE/n/'result.json',p]);return read(p)
 n='government-xl-central-piers-original-policy-v1-20261021';policy=take(n,BASE/n/'summary.json');assert len(policy['rows'])==2 and all(r['originalPolicyPassed']for r in policy['rows']);sources={r['uid']:r['sourceSHA256']for r in policy['rows']};assert set(sources)==set(UIDS)
 n='government-xl-central-piers-approach-identity-v1-20261021'
 for uid in UIDS:
  r=take(n,BASE/n/(uid.split('/')[1]+'.json'));assert r['passed']and r['sourceSHA256']==sources[uid]
 n='government-xl-central-piers-native-delta-v1-20261021';near=take(n,BASE/n/'summary.json');assert near['neighbourRegressionPassed']and near['checked']==1207 and near['ordinaryFormsChecked']==5312 and not near['introducedFailures']and near['ordinaryFailures']==0
 n='government-xl-central-piers-joint-browser-v1-20261021';folder=BASE/n;reports=[]
 for width in [1280,390]:
  p=folder/str(width)/'staged-browser.json';r=take(n,p);assert r['passed']and not r['errors'];views=[v for v in r['views']if 'time'in v];assert len(views)==4
  for v in views:assert v['active']and v['visible']and v['fullyFramed']and v['solidAppearance']and not v['fallbackFaces']and v['pick']==v['collision']==v['uid']and v['sourceSHA256']==sources[v['uid']]
  if width==390:assert {v['uid']for v in r['views']if v.get('phase')=='failed-download'and v['fallbackRetained']}==set(UIDS)
  assert len(r['localJointViews'])==1
  for v in r['localJointViews']:
   assert {m['uid']for m in v['models']}==set(UIDS)
   for m in v['models']:assert m['active']and m['visible']and not m['fallbackFaces']and m['sourceSHA256']==sources[m['uid']]
  reports.append(ref(p))
 # This file must be authored only after ROOT actually views every listed export.
 inspected=read(folder/'ROOT-INSPECTED-EXPORTS.json');assert inspected['reviewer']=='ROOT'and inspected['visualAcceptance']is True
 _,ps=authenticate(folder);images=inspected['imagesActuallyViewed'];assert len(images)==10
 for q in images:assert ref(ROOT/q['path'])==q and ps[q['path']]==q['sha256'];refs.append(ROOT/q['path'])
 refs.append(folder/'ROOT-INSPECTED-EXPORTS.json');manifest=ROOT/'3d-viewer/city/data/manifest.json'
 for label in ['pier8','pier7']:
  rn=f'government-xl-central-{label}-current-runtime-v1-20261021';metric=take(rn,BASE/rn/'metrics.json');assert metric['inputHashes'][str(manifest.relative_to(ROOT))]==ref(manifest)['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h
 review=dict(uids=UIDS,sourceSHA256ByUid=sources,currentManifest=ref(manifest),identityAccepted=True,sourceSpecificPhysicalInterpretationAccepted=True,completeNeighbourInterpretationAccepted=True,visualAcceptance=True,imagesActuallyViewed=images,browserReports=reports,unchangedBaselineNeighbourFlags=near['unchangedBaselineFlags'],sourceGeometryChanges=0,sourcePoseChanges=0,aiGeometryModelling=False,sourceEvidenceInterpretationUsedAI=True,installationApproved=False,qualification='Exact original approach identity and unchanged existing physical/mobile policy pass. Complete retained-neighbour delta introduces no failures. Existing baseline flags are retained, not newly approved. Joint staged desktop/mobile collision, selection, visibility and failed-download recovery verified; ROOT inspected exact exports. Live publication verification remains required.')
 save(DOC/'ROOT-SOURCE-REVIEW.json',review);refs.append(manifest);r=module('piers_source_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-original-pair-qualified-source-review',list(dict.fromkeys(refs)),review);print(r['jobId'],flush=True)
if __name__=='__main__':main()
