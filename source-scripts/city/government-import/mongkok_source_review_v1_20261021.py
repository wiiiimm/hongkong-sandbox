"""Bind exact canonical and inspected staged browser evidence for one unchanged stadium stand."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-mongkok-source-review-v1-20261021';DOC=BASE/BATCH;BROWSER='government-xl-mongkok-staged-browser-v2-20261021'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={}
 def take(n,p):
  _,ps=authenticate(BASE/n);k=str(p.relative_to(ROOT));assert ref(p)['sha256']==ps[k];pins[k]=ps[k];refs.extend([BASE/n/'result.json',p]);return read(p)
 n='government-xl-mongkok-physical-review-v1-20261021';physical=take(n,BASE/n/'ROOT-PHYSICAL-REVIEW.json');assert all(physical[k]for k in ['identityAccepted','sourceSpecificPhysicalInterpretationAccepted','completeNeighbourInterpretationAccepted']);sources=physical['sourceSHA256ByUid']
 reports=[];images=[];_,imagePins=authenticate(BASE/BROWSER)
 for width in [1280,390]:
  p=BASE/BROWSER/str(width)/'staged-browser.json';r=take(BROWSER,p);assert r['passed']and not r['errors'];views=[v for v in r['views']if 'time'in v];assert len(views)==2
  for v in views:assert v['uid']=='landsd/240332:0'and v['fullyFramed']and v['solidAppearance']and v['active']and v['visible']and not v['fallbackFaces']and v['pick']==v['collision']==v['uid']and v['sourceSHA256']==sources[v['uid']]
  retained=r['retainedNativeOwnViews'];assert len(retained)==2
  for v in retained:assert v['uid']=='landsd/240527:0'and v['fullyFramed']and v['active']and v['visible']and not v['fallbackFaces']and v['sourceSHA256']==sources[v['uid']]
  assert r['jointViews']and all({m['uid']for m in j['models']}==set(sources)and all(m['active']and m['visible']and not m['fallbackFaces']and m['sourceSHA256']==sources[m['uid']]for m in j['models'])for j in r['jointViews'])
  if width==390:assert {v['uid']for v in r['views']if v.get('phase')=='failed-download'and v['fallbackRetained']}=={'landsd/240332:0'}
  for v in views+retained:
   ip=p.parent/v['file'];q=ref(ip);assert imagePins[q['path']]==q['sha256'];images.append(q);refs.append(ip)
  reports.append(ref(p))
 inspected=read(BASE/BROWSER/'ROOT-INSPECTED-EXPORTS.json');assert inspected['reviewer']=='ROOT'and inspected['visualAcceptance']is True and inspected['imagesActuallyViewed']==images;refs.append(BASE/BROWSER/'ROOT-INSPECTED-EXPORTS.json')
 manifest=ROOT/'3d-viewer/city/data/manifest.json';n='government-xl-mongkok-inset-pair-runtime-v1-20261021';metric=take(n,BASE/n/'after-metrics.json');assert metric['inputHashes'][str(manifest.relative_to(ROOT))]==ref(manifest)['sha256'];refs.append(manifest)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h
 review=dict(**{k:v for k,v in physical.items()if k not in ['qualification']},currentManifest=ref(manifest),visualAcceptance=True,imagesActuallyViewed=images,browserReports=reports,sourceEvidenceInterpretationUsedAI=True,qualification='One unchanged original north stand; opposite installed stand stays unchanged. Canonical physical tests, complete four-world foundations,66forms and retained stand pass. ROOT inspected exact desktop/mobile day/night exports. Staged picking/collision, solid original meshes, joint visibility and mobile503/retry pass. Browser waits for base tiles: settled-map correctness evidence only, not cold-load performance certification. Final live verification remains required.')
 save(DOC/'ROOT-SOURCE-REVIEW.json',review);module('stadium_source_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'qualified-original-stadium-source-review',list(dict.fromkeys(refs)),review)
if __name__=='__main__':main()
