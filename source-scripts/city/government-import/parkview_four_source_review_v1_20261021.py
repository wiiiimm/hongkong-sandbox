"""Require exact original evidence and reviewed source/retained exports before staging."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-parkview-four-source-review-v1-20261021';DOC=BASE/BATCH
BROWSERS={1280:'government-xl-parkview-retained-capture-diagnostic-v1-20261021',390:'government-xl-parkview-retained-mobile-v1-20261021'}
SUPPLEMENT='government-xl-parkview-block15-opposite-view-v1-20261021'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={}
 def take(n,f):
  folder=BASE/n;_,ps=authenticate(folder);p=folder/f;k=str(p.relative_to(ROOT));assert digest(p.read_bytes())==ps[k];pins[k]=ps[k];refs.extend([folder/'result.json',p]);return read(p)
 pre=take('government-xl-parkview-four-prebrowser-review-v2-20261021','review.json');assert pre['prebrowserChecksPassed'] and pre['ordinaryForms']==26 and pre['retainedNativeModels']==11
 sources={r['uid']:r['sourceSHA256']for r in pre['rows']};uids=set(sources);assert len(uids)==4
 retained=set(pre['terrainCandidates'][0]['replaces']['retainedUids']);assert len(retained)==11
 audit=take('government-xl-parkview-podium-flag-audit-v4-20261021','audit.json');assert audit['evidenceBackedOriginalApprovalReconciliation'] and audit['sameCatalogueAsInstalledAcceptance'] and audit['noLaterHoldOrRejection'] and audit['reviewState']=='installed-verified'
 # Both viewport runs and the supplemental view must use identical staged originals.
 catalogues=[]
 for n in [*BROWSERS.values(),SUPPLEMENT]:
  folder=BASE/n;_,ps=authenticate(folder);p=HERE/'local'/n/'catalogue.json';k=str(p.relative_to(ROOT));assert digest(p.read_bytes())==ps[k];refs.append(p);catalogues.append(read(p))
 assert all(c==catalogues[0]for c in catalogues[1:])
 expectedImages=set();reports=[];imagePins={}
 for width in [1280,390]:
  browser=BROWSERS[width];_,ps=authenticate(BASE/browser);imagePins.update(ps)
  p=BASE/browser/str(width)/'staged-browser.json';report=take(browser,str(width)+'/staged-browser.json');assert report['passed'] and not report['errors']
  views=[r for r in report['views']if 'time'in r];assert {(r['uid'],r['time'])for r in views}=={(u,t)for u in uids for t in ['15:00','22:00']} and len(views)==8
  for v in views:
   assert v['active'] and v['visible'] and v['fullyFramed'] and v['solidAppearance'] and not v['fallbackFaces'];assert v['pick']==v['collision']==v['uid'] and v['sourceSHA256']==sources[v['uid']];expectedImages.add(str((p.parent/v['file']).relative_to(ROOT)))
  own=report['retainedNativeOwnViews'];assert len(own)==22 and {(r['uid'],r['time'])for r in own}=={(u,t)for u in retained for t in ['15:00','22:00']}
  for v in own:
   assert v['active'] and v['visible'] and v['fullyFramed'] and not v['overflow'] and v['fallbackFaces']==0;assert all(v['meshVisibility']) and not any(v['wireframeFlags']);expectedImages.add(str((p.parent/v['file']).relative_to(ROOT)))
  assert report['jointViews']
  for joint in report['jointViews']:
   assert {m['uid']for m in joint['models']}==uids
   for m in joint['models']:assert m['active'] and m['visible'] and m['sourceSHA256']==sources[m['uid']] and m['fallbackFaces']==0
  if width==390:assert {v['uid']for v in report['views']if v.get('phase')=='failed-download'and v['fallbackRetained']}==uids
  reports.append(ref(p))
 _,ps=authenticate(BASE/SUPPLEMENT);imagePins.update(ps)
 for width in [1280,390]:
  p=BASE/SUPPLEMENT/str(width)/'staged-browser.json';report=take(SUPPLEMENT,str(width)+'/staged-browser.json');assert report['passed'] and not report['errors']
  views=[v for v in report['views']if 'time'in v];assert len(views)==2 and {(v['uid'],v['time'])for v in views}=={('landsd/255648:0',t)for t in ['15:00','22:00']}
  for v in views:
   assert v['active'] and v['visible'] and v['fullyFramed'] and v['solidAppearance'] and not v['fallbackFaces'];assert v['sourceSHA256']==sources[v['uid']];expectedImages.add(str((p.parent/v['file']).relative_to(ROOT)))
  reports.append(ref(p))
 inspection=BASE/BROWSERS[390]/'ROOT-INSPECTED-EXPORTS.json';review=read(inspection);assert review['reviewer']=='ROOT' and review['visualAcceptance']
 assert {q['path']for q in review['imagesActuallyViewed']}==expectedImages and len(expectedImages)==64
 for q in review['imagesActuallyViewed']:assert ref(ROOT/q['path'])==q and imagePins[q['path']]==q['sha256'];refs.append(ROOT/q['path'])
 refs.append(inspection);manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==pre['currentManifestSHA256'];refs.append(manifest)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h
 result=dict(uids=sorted(uids),sourceSHA256ByUid=sources,currentManifest=ref(manifest),identityAccepted=True,sourceSpecificPhysicalInterpretationAccepted=True,completeNeighbourInterpretationAccepted=True,visualAcceptance=True,imagesActuallyViewed=review['imagesActuallyViewed'],browserReports=reports,retainedUids=sorted(retained),prebrowserReview=ref(BASE/'government-xl-parkview-four-prebrowser-review-v2-20261021/review.json'),podiumApprovalReconciliation=ref(BASE/'government-xl-parkview-podium-flag-audit-v4-20261021/audit.json'),sourceGeometryChanges=0,sourcePoseChanges=0,aiGeometryModelling=False,installationApproved=False,qualification='Exact four unchanged originals, native shared podium and bounded terrain replacement. Retained11 checked for regression, not globally reapproved. Raw historical/contact negatives retained under source-specific interpretation. All staged exports inspected; guarded publication and live verification still required.')
 save(DOC/'ROOT-SOURCE-REVIEW.json',result);module('parkview_four_source_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'four-original-source-review-before-publication',list(dict.fromkeys(refs)),result)
if __name__=='__main__':main()
