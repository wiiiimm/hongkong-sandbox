"""One-source finite-V2 profile with proven zero native/detail-fallback contacts.

Retains the V1 support/current-native/image checks. Both detailed and BASIC
native contact streams must be empty; no native availability edge is inferred.
"""
import numpy as np
from run import ROOT,HERE,read,digest,jobs
from china_ferry_current_foundations_v1_20261020 import authenticate
from finite_embedded_basic_support_contract_v2_20261025 import verify_mode
from finite_height_clearance_bound_v1_20261023 import verify as clearance
from original_retained_own_views_contract_v1_20261025 import verify as verify_views
BASE=ROOT/'docs/astra-city/government-import'

def replay(config,review):
 refs=[HERE/'finite_basic_native_independent_admission_v1_20261026.py',HERE/'finite_embedded_basic_support_contract_v2_20261025.py',HERE/'finite_height_clearance_bound_v1_20261023.py',HERE/'original_retained_own_views_contract_v1_20261025.py'];pins={}
 def take(batch,name):
  if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
  p=BASE/batch/name;assert digest(p.read_bytes())==pins[batch][str(p.relative_to(ROOT))];refs.append(p);return read(p)
 assert review['sourceSpecificPhysicalInterpretationAccepted']is True and review['completeNeighbourInterpretationAccepted']is True
 assert review['completeFourWorldCanonicalRetainedBasicSupport']is False and review['completeFourWorldFiniteRetainedBasicSupport']is True
 assert review['sourceGeometryChanges']==review['sourcePoseChanges']==0 and review['terrainEdits']is False
 sources=config['sources'];assert review['sourceSHA256ByUid']==sources and len(sources)==1
 uid=next(iter(sources));finite=take(config['finiteEvidence'],'finite-basic-evidence.json');assert finite['uids']==[uid]and finite['sourceSHA256']==sources[uid]
 assert finite['completeFourWorldCanonicalRetainedBasicSupport']is False and finite['completeFourWorldFiniteRetainedBasicSupport']is True and finite['separateFiniteSupportEvidence']is True
 bindings=take(config['finiteEvidence'],'support-bindings.json');assert review['retainedBasicSupportDependencies']==bindings and len(bindings)==1
 binding=bindings[0];assert binding['uid']==uid and binding['sourceSHA256']==sources[uid] and binding['supportUid']==finite['supportUid']
 support_ref=dict(path=str((BASE/config['finiteEvidence']/'finite-basic-evidence.json').relative_to(ROOT)),sha256=digest((BASE/config['finiteEvidence']/'finite-basic-evidence.json').read_bytes()));assert binding['supportEvidence']==support_ref
 payload=take(config['finiteModes'],'mode-inputs.json.gz')['rows'];assert len(payload)==1;payload=payload[0];assert payload['uid']==uid and payload['supportUid']==binding['supportUid'] and payload['sourceSHA256']==sources[uid]
 g=payload['supportGeometry'];assert digest(jobs.encode(g).encode())==binding['completeIndexedBasicGeometrySHA256'];p=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)]
 checks=take(config['finiteModes'],'mode-checks.json.gz')['rows'];assert len(checks)==len(payload['modes'])==len(finite['rows'])==4
 modes={'original','literal','leftF32','balancedF32'};assert {m['mode']for m in payload['modes']}=={m['mode']for m in checks}=={m['mode']for m in finite['rows']}==modes
 for mode in payload['modes']:
  name=mode['mode'];x=mode['geometry'];t=np.asarray(x['position']).reshape(-1,3)[np.asarray(x['index']).reshape(-1,3)];detail=take(config['finitePaths'],name+'.json.gz');raw=next(c['proof']for c in checks if c['mode']==name)
  proof=verify_mode(t,p,raw,detail);expected=next(r for r in finite['rows']if r['mode']==name)
  assert all(expected[k]==v for k,v in proof.items())and expected['sourceWorldSHA256']==detail['sourceWorldSHA256']and expected['supportWorldSHA256']==detail['supportWorldSHA256']
  assert clearance(x['position'],g['position'])['ordinaryClearanceBoundProved']
 retained=review['retainedNativeEntries'];assert set(retained)==set(config['retainedNativeUids'])and not set(retained)&set(sources)
 native=take(config['nativeContext'],'summary.json')['rows'];assert len(native)==len(retained)
 for row in native:
  nuid=row['nativeUid'];assert row['rawCurrentNativeEntry']==retained[nuid] and row['sourceSHA256']==sources[uid]and row['nativeSHA256']==retained[nuid]['sha256']
  assert len(row['modes'])==4 and {m['mode']for m in row['modes']}==modes
  for m in row['modes']:
   proof=take(config['nativeContext'],uid.split('/')[1]+'--'+nuid.split('/')[1]+'--'+m['mode']+'.json.gz')
   assert proof['allPairsExamined']is True and proof['sourceFacesOmitted']==proof['geometryChanges']==0
   assert len(proof['contacts'])==m['finiteContactPairs']==0,'Independent profile requires zero native detail contacts'
 manifest=ROOT/'3d-viewer/city/data/manifest.json';assert review['currentManifest']==dict(path=str(manifest.relative_to(ROOT)),sha256=digest(manifest.read_bytes()));refs.append(manifest)
 current={m['uid']:(m,(ROOT/'3d-viewer'/url).parent/m['asset'])for url in read(manifest)['officialModelCatalogues']for m in read(ROOT/'3d-viewer'/url)['models']};assert len(current)==config['currentNativeActors']
 for nuid,entry in retained.items():
  old,asset=current[nuid];assert old==entry and digest(asset.read_bytes())==entry['sha256'];refs.append(asset)
 images=review['retainedImagesActuallyViewed'];assert len(images)==4*len(retained) and len({i['path']for i in images})==len(images)
 assert {(i['uid'],i['width'],i['time'])for i in images}=={(u,w,t)for u in retained for w in [390,1280]for t in ['15:00','22:00']}
 for image in images:
  path=ROOT/image['path'];assert digest(path.read_bytes())==image['sha256'];refs.append(path)
 for report in review['browserReports']:
  path=ROOT/report['path'];assert digest(path.read_bytes())==report['sha256'];refs.append(path);r=read(path);assert r['passed']and not r['errors'];views=r['retainedNativeOwnViews'];width=views[0]['width'];assert verify_views(views,retained,widths=(width,))
  for v in views:
   expected=str((path.parent/v['file']).resolve().relative_to(ROOT));assert len([i for i in images if i['path']==expected and(i['uid'],i['width'],i['time'])==(v['uid'],v['width'],v['time'])])==1
 assert config['nativeAvailabilityDependenciesByUid']==review['runtimeAvailabilityDependenciesByUid']=={}
 scope=take(config['scope'],'summary.json');assert scope['uids']==[uid]and len(scope['rows'])==1
 assert scope['currentManifestSHA256']==digest(manifest.read_bytes())and scope['rows'][0]['currentNativeActorsChecked']==config['currentNativeActors']
 assert {n['uid']for n in scope['rows'][0]['nearbyNativeActors']}==set(retained)and retained
 fallbacks=take(config['nativeFallbackContext'],'summary.json')['rows'];assert len(fallbacks)==len(retained)and{r['nativeFallbackUid']for r in fallbacks}==set(retained)
 for row in fallbacks:
  nuid=row['nativeFallbackUid'];assert row['uid']==uid and row['sourceSHA256']==sources[uid]and row['nativeSHA256']==retained[nuid]['sha256']and row['rawCurrentNativeEntry']==retained[nuid]
  measured=[m for m in row['modes']if m['mode']!='before-basic'];assert len(measured)==4 and {m['mode']for m in measured}==modes
  for mode in measured:
   raw=take(config['nativeFallbackContext'],uid.split('/')[1]+'--'+nuid.split('/')[1]+'--'+mode['mode']+'.json.gz')
   assert raw['allPairsExamined']and raw['sourceFacesOmitted']==0
   assert len(raw['contacts'])==mode['finiteContactPairs']==0,'Independent profile requires zero native BASIC fallback contacts'
 browser,browserpins=authenticate(BASE/config['browser']);refs.append(BASE/config['browser']/'result.json')
 assert browser['proposedSupportByUid']=={}and browser['allBrowserDiagnosticsPassed']
 preview=ROOT/'source-scripts/city/government-import/local'/config['browser']/'catalogue.json';assert digest(preview.read_bytes())==browserpins[str(preview.relative_to(ROOT))];refs.append(preview)
 cat=read(preview);assert len(cat['models'])==1 and cat['models'][0]['uid']==uid and cat['models'][0]['sha256']==sources[uid]and not cat['models'][0].get('supportDependencies')
 return list(dict.fromkeys(refs))
