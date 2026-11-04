"""Bind ROOT's inspected source/native interface and exact browser evidence; no publication."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from polyu_lee_shau_kee_original_catalogue_scope_v1_20261025 import SOURCES,SUPPORTS,RETAINED,MAIN,SMALL,LIB,SPORT,verify_metadata,verify_native_scope
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-polyu-lee-shau-kee-original-root-review-v1-20261025'
RT='government-xl-polyu-lee-shau-kee-current-ground-v2-20261025'
SCOPE='government-xl-polyu-lee-shau-kee-current-scope-v2-20261025'
NATIVE='government-xl-after-tvb-next-three-with-companions-native-contacts-v1-20261025'
BROWSER='government-xl-polyu-two-original-retained-native-unapproved-browser-v3-20261025'
ID='government-xl-polyu-lee-shau-kee-bounded-identity-panel-review-v1-20261025'
JOIN='government-xl-polyu-lee-shau-kee-native-join-context-v1-20261025'


def main():
 out=BASE/BATCH;assert not out.exists();pins={};refs=[Path(__file__),HERE/'polyu_lee_shau_kee_original_catalogue_scope_v1_20261025.py'];reports=[];images=[];retained_images=[]
 def take(n,path):
  if n not in pins:pins[n]=authenticate(BASE/n)[1];refs.append(BASE/n/'result.json')
  assert digest(path.read_bytes())==pins[n][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 def item(n,file='summary.json'):return take(n,BASE/n/file)
 identity=item(ID,'ROOT-IDENTITY-PANEL-CONTEXT.json');assert identity['identityAccepted']and identity['sourceSHA256ByUid']==SOURCES
 assert len(identity['mainExposedOriginalPanels'])==8 and {r['sourceFace']for r in identity['mainExposedOriginalPanels']}=={4292,4293}
 assert all(r['highestOriginalVertexAboveEveryOverlappingGroundFace']and r['exactFiniteGradeCrossingPairs']for r in identity['mainExposedOriginalPanels'])
 join=item(JOIN);assert join['sourceSHA256ByUid']==SOURCES and len(join['rows'])==8 and all(r['zeroAreaContactPairs']for r in join['rows'])
 continuous=item('government-xl-polyu-lee-shau-kee-current-continuous-v2-20261025');assert len(continuous['rows'])==2
 assert all(r['upwardContinuousMinimumGapM']>0 and set(r['continuousAffectedFaces'])==set(r['affectedWallFaces'])for r in continuous['rows'])
 coverage=item('government-xl-polyu-lee-shau-kee-current-exact-coverage-v2-20261025');assert all(not r['stillUncoveredFaces']for r in coverage['rows'])
 support=item('government-xl-polyu-lee-shau-kee-library-support-v2-20261025');small=[r for r in support['rows']if r['uid']==SMALL]
 assert len(small)==4 and all(r['strictPassed']and r['strictContacts']==34 and r['unresolved']==0 and not r['compoundFullyBuried']and not r['compoundUpwardBuried']for r in small)
 assert item('government-xl-polyu-library-support-current-stream-binding-v1-20261025')['nativeStreamReuseVerified']
 manifest=ROOT/'3d-viewer/city/data/manifest.json';manifest_ref=dict(path=str(manifest.relative_to(ROOT)),sha256=digest(manifest.read_bytes()));refs.append(manifest)
 current={m['uid']:m for url in read(manifest)['officialModelCatalogues']for m in read(ROOT/'3d-viewer'/url)['models']}
 scope=item(SCOPE);assert scope['currentManifestSHA256']==manifest_ref['sha256']
 native=item(NATIVE);assert verify_native_scope(scope,native,current)
 for uid,sha in RETAINED.items():assert current[uid]==identity['retainedNativeEntries'][uid]and current[uid]['sha256']==sha
 forms={}
 for uid in SOURCES:
  for row in item(SCOPE,uid.split('/')[1]+'-forms.json.gz'):forms[row['building']['uid']]=row['building']
 assert len(forms)==8 and set(forms)-set(SOURCES)-set(RETAINED)<=set(current[LIB]['suppressesBuildingUids'])
 selection=item(RT,'selection.json.gz');entries={r['uid']:r['candidate']['entry']for r in selection['rows']};assert selection['manifestSHA256']==manifest_ref['sha256']
 local=HERE/'local'/BROWSER;cat=take(BROWSER,local/'catalogue.json');assert verify_metadata(cat['models'],entries)
 configs=[take(BROWSER,local/('browser-config-'+str(w)+'.json'))for w in [1280,390]]
 protections=configs[0]['basicFallbackProtections'];assert len(protections)==2 and {r['uid']for r in protections}==set(SOURCES)
 for p in protections:assert p['buildingCSUID']==entries[p['uid']]['buildingCSUID']and p['sourceSHA256']==SOURCES[p['uid']]and p['suppressorUid']==LIB and p['suppressorSourceSHA256']==RETAINED[LIB]
 for width,cfg in zip([1280,390],configs):
  assert cfg['terrain']==[]and cfg['basicFallbackProtections']==protections and cfg['nativeSupportUidsByModel']=={SMALL:[LIB]}and set(cfg['additionalRetainedUids'])==set(RETAINED)
  path=BASE/BROWSER/str(width)/'staged-browser.json';report=take(BROWSER,path);assert report['passed']and not report['errors'];reports.append(dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes())))
  views=[v for v in report['views']if 'time'in v];assert len(views)==4 and{(v['uid'],v['time'])for v in views}=={(u,t)for u in SOURCES for t in ['15:00','22:00']}
  for v in views:
   assert v['fullyFramed']and v['solidAppearance']and not v['fallbackFaces']and v['active']and v['visible']and v['pick']==v['collision']==v['uid']and v['sourceSHA256']==SOURCES[v['uid']]
   p=path.parent/v['file'];take(BROWSER,p)if p.suffix=='.json'else refs.append(p)
   assert digest(p.read_bytes())==pins[BROWSER][str(p.relative_to(ROOT))]
   images.append(dict(uid=v['uid'],width=width,time=v['time'],path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes())))
  assert report['jointViews']and any({m['uid']for m in j['models']}==set(SOURCES)and all(m['active']and m['visible']and not m['fallbackFaces']and m['sourceSHA256']==SOURCES[m['uid']]for m in j['models'])for j in report['jointViews'])
  retained=report['retainedNativeOwnViews'];assert len(retained)==4 and{(v['uid'],v['time'])for v in retained}=={(u,t)for u in RETAINED for t in ['15:00','22:00']}
  for v in retained:
   assert v['active']and v['visible']and v['fullyFramed']and not v['overflow']and not v['fallbackFaces']and v['sourceSHA256']==RETAINED[v['uid']]and v['originalTriangles']==current[v['uid']]['triangles']and all(v['meshVisibility'])and not any(v['wireframeFlags'])
   p=path.parent/v['file'];assert digest(p.read_bytes())==pins[BROWSER][str(p.relative_to(ROOT))];refs.append(p);retained_images.append(dict(uid=v['uid'],width=width,time=v['time'],path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes())))
  if width==390:
   failed=[v for v in report['views']if v.get('phase')=='failed-download'];assert len(failed)==2 and{v['uid']for v in failed}==set(SOURCES)and all(v['fallbackRetained']for v in failed)
 for path in ['3d-viewer/city.html','3d-viewer/city/app.js','3d-viewer/city/streaming.js','3d-viewer/city/basic-fallback-protections.js','3d-viewer/city/tests/basic-fallback-protections.test.js','3d-viewer/city/tests/official-models.test.js','source-scripts/city/island-detail-integration/basic_fallback_protections.py','source-scripts/city/island-detail-integration/publish.py','source-scripts/city/island-detail-integration/test_basic_fallback_protections.py']:
  refs.append(ROOT/path)
 result=dict(uids=sorted(SOURCES),reviewer='ROOT',sourceSHA256ByUid=SOURCES,requiredOriginalAssembly=SOURCES,currentManifest=manifest_ref,supportByUid=SUPPORTS,identityProof=identity['identityProof'],identityAccepted=True,sourceSpecificPhysicalInterpretationAccepted=True,completeNeighbourInterpretationAccepted=True,completeFourWorldFoundations=True,completeFourWorldSourceClearance=True,completeFourWorldCanonicalRetainedBasicSupport=True,completeCurrentNeighbourChecks=len(forms),leaseResources=sorted('building:'+u for u in forms),retainedCurrentBasicSupportUids=[],retainedBasicSupportDependencies=[],retainedLibraryPublicationHoldUnchanged=True,retainedNativeEntries={u:current[u]for u in RETAINED},basicFallbackProtections=protections,rawPhysicalFailuresPreserved=True,terrainEdits=False,sourceGeometryChanges=0,nativeMetadataChanges=0,visualAcceptance=True,imagesActuallyViewed=images,retainedImagesActuallyViewed=retained_images,browserReports=reports,aiGeometryModelling=False,sourceEvidenceInterpretationUsedAI=True,installationApproved=False,publication=False,observations=[
 'ROOT inspected all16 exact desktop/mobile day/night PNGs and the exact contact-witness diagram. Curved tower, elevated stair/landing companion and existing low campus platforms are coherent original source roles. No dimensioned photo accuracy or full legacy-library engineering approval is claimed.',
 'Main has36 exact clear-cap wall paths and2 original vertical grade-crossing panels with exposed highest vertices in every stream. Five failed library roof-root probes are embedded wall toes, not a reason to invent a main-to-library support. Main is reviewed against actual ground; all source projections are covered and all upward surfaces clear it.',
 'Companion has34 strict original-library support contacts in all4streams. Only companion depends on exact installed library. All raw main/library and companion/library finite intersections remain recorded, including float32 changes; their witnesses remain in the original low interface12.1515..15.7300m, with zero area-contact pairs. These source-authored joins are accepted for this exact assembly, not a new generic zero-interpenetration gate.',
 'Sports contact proofs are zero in every stream. The elevated16.108m2 original corner overlap is at least4.4485m above its entire original Sports source, as separately reviewed. All8 current local source forms are bound; other local BASIC forms are existing unchanged library suppressions. No retained metadata or45-item suppression list changes.',
 'Private V3/V12 browser tests use actual target BASIC feature geometry after deliberate mobile HTTP503 failures. Both targets retain BASIC while library stays active, retry to unchanged originals, remove ownBASIC on activation and pass final joint source/native checks. A pending companion BASIC can appear during the earlier tower capture; final joint checks and retained captures occur after both originals activate. The earlier V2 mobile failure is preserved, not relabelled a source defect.',
 'Library publicationApproved:false remains false. Accept only the two new exact originals and their source-specific interfaces; no optimisation eligibility or blanket approval transfers to the retained library. Publisher must apply the two exact source-bound BASIC protection records together with these sources.'
 ])
 save(out/'ROOT-PHYSICAL-REVIEW.json',result);save(out/'ROOT-SOURCE-REVIEW.json',result)
 module('polyu_root_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'root-reviewed-exact-two-original-library-interface-and-repaired-fallback',list(dict.fromkeys(refs)),{k:v for k,v in result.items()if k!='retainedNativeEntries'})


if __name__=='__main__':main()
