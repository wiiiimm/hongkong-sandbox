"""Bind bounded Beverly K original/source/native/support interpretation and inspected exports."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from finite_embedded_basic_support_contract_v1_20261025 import verify_mode
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-beverly-k-finite-source-review-v1-20261025'

def main():
 out=BASE/BATCH;assert not out.exists();refs=[Path(__file__)];pins={}
 def take(batch,name):
  if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
  p=BASE/batch/name;assert digest(p.read_bytes())==pins[batch][str(p.relative_to(ROOT))];refs.append(p);return read(p)
 def old(part):return 'government-xl-beverly-k-after-tuen-mun-'+part+'-20261025'
 runtime=old('runtime-v1');selection=take(runtime,'selection.json.gz');row=selection['rows'][0];uid=row['uid'];sources={uid:row['sourceSHA256']};assert uid=='landsd/255543:0'
 identity=take(old('identity-v1'),'255543:0/identity.json');assert identity['passed']and identity['sourceSHA256']==sources[uid];assert all(identity['proof'].values())
 metric=take(runtime,'metrics.json');policy=module('beverly_finite_policy',HERE/'acceptance-policy.py');reasons=policy.reasons(dict(state='runtime-validated-awaiting-acceptance',sourceSHA256=sources[uid],identityProof=identity['proof']),metric['rows'][0],metric['profiles']['mobile']);assert reasons==['ground-contact-unresolved'],reasons
 foundation=take(old('foundations-v1'),'summary.json');assert foundation['establishedFoundationPolicyPassed']and len(foundation['rows'])==4 and all(r['fullyBuriedTriangles']==r['fullyBuriedUpwardTriangles']==0 for r in foundation['rows'])
 continuous=take(old('continuous-v1'),'summary.json')['rows'][0];assert continuous['wholeSourceFaces']==10130 and continuous['wholeSourceUncoveredFaces']==0 and continuous['upwardContinuousMinimumGapM']>0 and continuous['sourceSHA256']==sources[uid]
 scopebatch=old('model-scope-v1');scope=take(scopebatch,'summary.json');assert len(scope['rows'])==1 and scope['rows'][0]['currentNativeActorsChecked']==6954
 forms={v['building']['uid']:v['building']for v in take(scopebatch,'255543:0-forms.json.gz')};assert set(forms)=={uid,'landsd/233218:0','landsd/255539:0','landsd/255939:0'}
 finitebatch=old('finite-basic-evidence-v1');finite=take(finitebatch,'finite-basic-evidence.json');bindings=take(finitebatch,'support-bindings.json');assert finite['completeFourWorldFiniteRetainedBasicSupport'] is True and finite['completeFourWorldCanonicalRetainedBasicSupport']is False and finite['sourceSHA256']==sources[uid]
 payload=take(old('four-world-basic-diagnostic-v1'),'mode-inputs.json.gz')['rows'][0];checks=take(old('four-world-basic-diagnostic-v1'),'mode-checks.json.gz')['rows'];g=payload['supportGeometry'];p=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)]
 assert bindings[0]['currentBasicForm']==forms['landsd/233218:0'] and forms[uid]['parent']==forms['landsd/233218:0']['parent']
 for mode in payload['modes']:
  x=mode['geometry'];t=np.asarray(x['position']).reshape(-1,3)[np.asarray(x['index']).reshape(-1,3)];proof=verify_mode(t,p,next(c['proof']for c in checks if c['mode']==mode['mode']),take(old('basic-finite-paths-v1'),mode['mode']+'.json.gz'));assert proof['verifiedPaths']==10
 nativebatch=old('full-native-contacts-v1');native=take(nativebatch,'summary.json')['rows'][0];entry=native['rawCurrentNativeEntry'];assert entry['uid']=='landsd/255939:0'and entry['publicationApproved']is False
 assert len(native['modes'])==4 and all(r['finiteContactPairs']==105 and r['positiveSurfaceContactPairs']==82 and r['areaContactPairs']==7 and r['sourceFaces']==10130 and r['nativeFaces']==12640 for r in native['modes'])
 for mode in ['original','literal','leftF32','balancedF32']:take(nativebatch,'255543:0--255939:0--'+mode+'.json.gz')
 orientation=take(old('contact-orientation-v1'),'summary.json');assert orientation['currentFootprintOverlapM2']==0 and orientation['currentFootprintDistanceM']==0
 assert len(orientation['rows'])==4 and all(r['horizontalAreaPairs']==7 and r['areaContactYLevels']==[189.08999633789062] and r['sumHorizontalPairAreaM2']==.005276418214587686 for r in orientation['rows'])
 foreign=take(old('foreign-basics-v1'),'summary.json');assert {r['foreignUid']for r in foreign['rows']}=={'landsd/233218:0','landsd/255539:0'}
 assert all(m['positiveContactPairs']==0 and m['projectedOverlapAreaM2']==0 for r in foreign['rows']if r['foreignUid']=='landsd/255539:0'for m in r['modes'])
 browser=old('private-basic-browser-v1');progress=take(old('progress-v2'),'remaining-work.json');assert progress['privateBrowserDiagnosticsPassed']and len(progress['privateImagesActuallyViewedByRoot'])==8
 reports=[];images=[];retained_images=[]
 for width in [390,1280]:
  report=take(browser,str(width)+'/staged-browser.json');assert report['passed']and not report['errors'];reports.append(dict(path=str((BASE/browser/str(width)/'staged-browser.json').relative_to(ROOT)),sha256=digest((BASE/browser/str(width)/'staged-browser.json').read_bytes())))
  from original_retained_own_views_contract_v1_20261025 import verify
  assert verify(report['retainedNativeOwnViews'],{entry['uid']:entry},widths=(width,))
  for v in [v for v in report['views']if 'time'in v]+report['retainedNativeOwnViews']:
   path=BASE/browser/str(width)/v['file'];key=str(path.relative_to(ROOT));assert dict(path=key,sha256=digest(path.read_bytes()))in progress['privateImagesActuallyViewedByRoot'];refs.append(path)
   image=dict(path=key,sha256=digest(path.read_bytes()))
   if v['uid']==uid:images.append(image)
   else:retained_images.append(dict(**image,uid=v['uid'],width=width,time=v['time']))
 manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256']==scope['currentManifestSHA256'];refs.append(manifest)
 review=dict(uids=[uid],sourceSHA256ByUid=sources,sourceSpecificPhysicalInterpretationAccepted=True,identityAccepted=True,completeNeighbourInterpretationAccepted=True,completeFourWorldSourceClearance=True,completeFourWorldCanonicalRetainedBasicSupport=False,completeFourWorldFiniteRetainedBasicSupport=True,completeCurrentNeighbourChecks=4,identityProof=identity['proof'],identityProofByUid={uid:identity['proof']},currentManifest=dict(path=str(manifest.relative_to(ROOT)),sha256=digest(manifest.read_bytes())),retainedCurrentBasicSupportUids=['landsd/233218:0'],retainedBasicSupportDependencies=bindings,leaseResources=sorted('building:'+u for u in forms),terrainEdits=False,sourceGeometryChanges=0,sourcePoseChanges=0,installationApproved=False,publication=False,visualAcceptance=True,originalSourceReviewAccepted=True,imagesActuallyViewed=images,retainedImagesActuallyViewed=retained_images,browserReports=reports,retainedNativeEntries={entry['uid']:entry},sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,finiteSupportEvidenceBatch=finitebatch,
 qualification='Accept exact original K on its unchanged surveyed BASIC estate podium: its underside is0.35m below the roof, real exposed source walls intersect that roof and every unresolved underside witness has an exact replayed finite source-facet path to the interface in all4worlds. Canonical strict support remains false; this separate finite support profile is mandatory. K and J are independently identified adjoining estate towers with touching recorded footprints. Preserve all105 native contacts, including7 tiny horizontal roof patches at189.09m (pair-area sum0.005276418m2, not a union). Bounded original roof/side interface contacts are accepted for this exact pair, not interpreted as source corruption or zero-interpenetration engineering proof. J bytes, complete entry, publicationApproved:false and prior support state remain unchanged and are not reapproved. BlockA is disjoint; current complete native bounds nominate only J. All terrain/source coverage/foundations pass. ROOT actually inspected4K+4J private day/night desktop/mobile images; K/J facades,roofs/base interfaces readable, originalgrey/darknight and existingBASICwindows retained. No new visible static defect; mobile failed-download fallback and P233218 BASIC retention pass. No geometry edits/terrain edits/scale changes. Guarded publication, retained support lifetime, live checks and independent full readback still mandatory.')
 save(out/'ROOT-PHYSICAL-REVIEW.json',review);save(out/'ROOT-SOURCE-REVIEW.json',review)
 refs.extend([HERE/'finite_embedded_basic_support_contract_v1_20261025.py',HERE/'original_retained_own_views_contract_v1_20261025.py',HERE/'acceptance-policy.py'])
 module('beverly_finite_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'bounded-original-finite-basic-support-and-native-role-review',list(dict.fromkeys(refs)),review)
if __name__=='__main__':main()
