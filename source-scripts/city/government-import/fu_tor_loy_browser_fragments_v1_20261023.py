"""Bind complete exact-input browser cases across preserved and focused runs.
Never rewrite failed observations. Approve the explicit matrix only after every
case has a current positive witness, with all original failures retained.
"""
from pathlib import Path
import copy,shutil
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
PARENT='government-xl-fu-tor-loy-five-source-staged-browser-v2-20261023'
FAIL='government-xl-fu-tor-loy-staged-v2-mobile-failure-context-v1-20261023'
FOCUS='government-xl-fu-tor-loy-olympic-mobile-focused-v1-20261023'
BATCH='government-xl-fu-tor-loy-browser-matrix-v1-20261023'
def main():
 doc=BASE/BATCH;local=HERE/'local'/BATCH;assert not doc.exists()and not local.exists();refs=[Path(__file__)];cache={}
 def take(n,p):
  if n not in cache:cache[n]=authenticate(BASE/n)[1];refs.append(BASE/n/'result.json')
  assert digest(p.read_bytes())==cache[n][str(p.relative_to(ROOT))];refs.append(p);return read(p)
 original=take(FAIL,HERE/'local'/PARENT/'browser-config-390.json');focused=take(FOCUS,HERE/'local'/FOCUS/'focused-config.json')
 expected=copy.deepcopy(original);expected.update(additionalRetainedUids=['landsd/81242:0'],viewportWidths=[390],failureTestUids=[],retainedOnly=True,jointUids=[],doc=str((BASE/FOCUS/'390').relative_to(ROOT))+'/');assert focused==expected,'Focused replay changed scene or unrelated test knobs'
 cap='government-xl-fu-tor-loy-five-originals-current-v1-20261023-runtime';selection=take(cap,BASE/cap/'selection.json.gz');manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256'];refs.append(manifest)
 sources={r['uid']:r['sourceSHA256']for r in selection['rows']};assert len(sources)==5
 installed={m['uid']:m for url in read(manifest)['officialModelCatalogues']for m in read(ROOT/'3d-viewer'/url)['models']}
 retained=set(original['additionalRetainedUids']);assert len(retained)==24 and 'landsd/81242:0'in retained
 desktop=take(FAIL,BASE/PARENT/'1280/staged-browser.json');mobile=take(FAIL,BASE/PARENT/'390/staged-browser.json');replay=take(FOCUS,BASE/FOCUS/'390/staged-browser.json')
 assert desktop['passed']and not desktop['errors']
 assert not mobile.get('passed')and len(mobile['errors'])==1 and 'assert(state.active&&state.visible&&state.fullyFramed&&!state.overflow)'in mobile['errors'][0]
 failure=mobile['retainedCaptureFailure'];assert failure['uid']=='landsd/81242:0'and failure['time']=='22:00'and failure['missingDetailedActor']and failure['selected']is None
 assert replay['passed']and not replay['errors']and replay['focusedRetainedOnly']and not replay['views']
 assert {(r['uid'],r['time'])for r in replay['retainedNativeOwnViews']}=={('landsd/81242:0',t)for t in ['15:00','22:00']}
 # Exact same original source/terrain bytes; the replay changes only observation scope.
 for p in (HERE/'local'/PARENT).rglob('*'):
  if p.is_file()and p.name!='reservation.json':
   assert digest(p.read_bytes())==cache[FAIL][str(p.relative_to(ROOT))];refs.append(p);target=local/p.relative_to(HERE/'local'/PARENT);target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target)
 for terrain in original['terrain']:
  p=ROOT/terrain['source'];assert digest(p.read_bytes())==terrain['sha256'];refs.append(p)
 composite=copy.deepcopy(mobile);composite['retainedNativeOwnViews']=[r for r in mobile['retainedNativeOwnViews']if r['uid']!='landsd/81242:0']+replay['retainedNativeOwnViews'];composite.update(passed=True,errors=[],completionMode='complete-exact-input-case-matrix',preservedRawObservationErrors=mobile['errors'],fragmentReports=[dict(path=str((BASE/PARENT/'390/staged-browser.json').relative_to(ROOT)),sha256=digest((BASE/PARENT/'390/staged-browser.json').read_bytes())),dict(path=str((BASE/FOCUS/'390/staged-browser.json').relative_to(ROOT)),sha256=digest((BASE/FOCUS/'390/staged-browser.json').read_bytes()))])
 for width,report in [(1280,desktop),(390,composite)]:
  views=[r for r in report['views']if 'time'in r];assert len(views)==10 and {(r['uid'],r['time'])for r in views}=={(u,t)for u in sources for t in ['15:00','22:00']}
  for r in views:assert r['active']and r['visible']and r['fullyFramed']and r['solidAppearance']and not r['fallbackFaces']and r['sourceSHA256']==sources[r['uid']]and r['pick']==r['collision']==r['uid']
  assert report['jointViews']and any({r['uid']:r['sourceSHA256']for r in j['models']}==sources and all(r['active']and r['visible']and not r['fallbackFaces']for r in j['models'])for j in report['jointViews'])
  if width==390:assert {r['uid']for r in report['views']if r.get('phase')=='failed-download'and r['fallbackRetained']}==set(sources)
  own=report['retainedNativeOwnViews'];assert len(own)==48 and {(r['uid'],r['time'])for r in own}=={(u,t)for u in retained for t in ['15:00','22:00']}
  for r in own:
   assert r['active']and r['visible']and r['fullyFramed']and not r['overflow']and not r['fallbackFaces']and all(r['meshVisibility'])and not any(r['wireframeFlags'])
   assert r['sourceSHA256']==installed[r['uid']]['sha256']and r['originalTriangles']==installed[r['uid']]['triangles']
  for r in views+own:
   focused_case=width==390 and r.get('uid')=='landsd/81242:0'
   n=FOCUS if focused_case else FAIL;source=(BASE/FOCUS/'390'if focused_case else BASE/PARENT/str(width))/r['file'];assert digest(source.read_bytes())==cache[n][str(source.relative_to(ROOT))];refs.append(source);target=doc/str(width)/r['file'];target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
  save(doc/str(width)/'staged-browser.json',report)
 inspected=BASE/'government-xl-scripted-continuation-20261023/fu-tor-loy-partial-root-inspection-v2.json';viewed=read(inspected);refs.append(inspected);assert len(viewed['imagesActuallyViewed'])==20
 output=[]
 for q in viewed['imagesActuallyViewed']:
  p=ROOT/q['path'];assert digest(p.read_bytes())==q['sha256'];refs.append(p);width=p.parent.name;dest=doc/width/p.name;assert digest(dest.read_bytes())==q['sha256'];output.append(dict(path=str(dest.relative_to(ROOT)),sha256=q['sha256'],viewedOriginalPath=q['path'],copiedByteIdentically=True))
 save(doc/'ROOT-INSPECTED-SOURCE-EXPORTS.json',dict(reviewer='ROOT',visualAcceptance=True,imagesActuallyViewed=output,qualification='Exact byte-for-byte copies of all20 original source exports ROOT actually viewed. Complete source/picking/collision/failure/joint cases from original current run, and last retained actor independently recovered by an exact-input focused run. Failed raw observations remain separately preserved; this is a complete case matrix, not a claim the original monolithic run passed.'))
 result=dict(uids=sorted(sources),currentManifestSHA256=digest(manifest.read_bytes()),completeBrowserCaseMatrix=True,singleMonolithicRunPassed=False,sourceGeometryChanges=0,scriptExternalAICalls=0,installationApproved=False,sourceExports=20,retainedOwnViews=96,rawFailedObservationPreserved=True,qualification='Complete exact-input desktop/mobile acceptance matrix over unchanged private source/catalogue/terrain and normal runtime budgets. The original final mobile native snapshot failure stays frozen; fresh atomic day/night snapshots cover only that actor. Every other case retains its exact original positive witness, never inferred approval.')
 refs.extend([HERE/'ronsdale_three_live_browser_v8_20261023.mjs',*[p for p in local.rglob('*')if p.is_file()]])
 module('fu_tor_browser_matrix_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-exact-input-original-browser-case-matrix',refs,result);print(result,flush=True)
if __name__=='__main__':main()
