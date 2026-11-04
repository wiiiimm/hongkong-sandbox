"""Exact source-specific pier extent, shoreline and apron interpretation; no publication."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from conditional_canopy_install_contract_v1_20261029 import form_sha
P='government-xl-disneyland-eastern75643-apron-current-';D='-v1-20261030'
UID='landsd/75643:0';BASIC='way/334029318:0';NATIVE='landsd/75642:0'
SHA='4c8e577256875f9ecc67fe5728e262113d852748ac743798b804f9b090f0dbc2'
BATCH=P+'source-review'+D

def main():
 base=ROOT/'docs/astra-city/government-import';out=base/BATCH;assert not out.exists();refs=[Path(__file__)];pins={}
 def take(batch,name):
  if batch not in pins:pins[batch]=authenticate(base/batch)[1];refs.append(base/batch/'result.json')
  p=base/batch/name;assert digest(p.read_bytes())==pins[batch][str(p.relative_to(ROOT))];refs.append(p);return read(p)
 def doc(suffix,name='summary.json'):return take(P+suffix+D,name)
 selection=doc('current-ground','selection.json.gz');assert len(selection['rows'])==1;row=selection['rows'][0];assert row['uid']==UID and row['sourceSHA256']==SHA and row['triangles']==32634
 manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256'];refs.append(manifest)
 source=row['source']['building'];assert source['uid']==UID and source['objectId']==75643 and source['buildingCSUID']=='2275118668T20050725'
 scope=doc('source-scope');assert scope['rows'][0]['currentNativeActorsChecked']==7029 and [r['uid']for r in scope['rows'][0]['nearbyNativeActors']]==[NATIVE]
 forms=doc('source-scope','75643:0-forms.json.gz');byuid={r['building']['uid']:r['building']for r in forms};assert set(byuid)=={UID,BASIC} and byuid[UID]==source
 old=take('government-xl-disneyland-piers-extent-identity-review-v1-20261029','75643:0/ROOT-SOURCE-IDENTITY-DECISION.json');assert old['sourceSHA256']==SHA and old['uid']==UID and old['sourceIdentityInterpretationApproved']and old['identityOnlyApproved']and not old['installationApproved']
 identity=doc('identity');assert identity['rows']==[dict(uid=UID,sourceSHA256=SHA,passed=False,reasons=old['interpretedRawReasons'])]
 foundation=doc('current-foundations');assert not foundation['establishedFoundationPolicyPassed']and len(foundation['rows'])==4
 for r in foundation['rows']:assert r['fullyBuriedTriangles']==2 and r['fullyBuriedUpwardTriangles']==0 and r['completeTerrainTriangles']==32634
 shore=doc('shore-closure');assert shore['sourceSHA256']==SHA and shore['sourceFaceIds']==[32612,32613]and shore['allFourStreamsStrictContinuousNativeAndActualGroundCover']and not shore['ordinaryBurialPolicyPassed']
 roles=doc('native-roles');assert len(roles['rows'])==4
 for r in roles['rows']:
  assert r['uid']==UID and r['nativeUid']==NATIVE
  if r['mode']!='literal':assert r['roles']=={'coplanar-edge-contact':2,'source-edge-surface-contact':32,'surface-point-contact':104}
  else:assert r['roles']=={'shared-plane-area-contact':2,'source-edge-surface-contact':25,'surface-point-contact':39,'transverse-surface-crossing':3}
 lineage=doc('native-lineage');assert len(lineage['rows'])==1
 for r in lineage['rows'][0]['modes']:assert r['allRepresentedCrossingsHaveOriginalFacetPairContacts']and r['transverseSegments']==(3 if r['mode']=='literal'else 0)
 foreign=doc('foreign-contacts');assert len(foreign['rows'])==1 and foreign['rows'][0]['foreignUid']==BASIC
 featurebatch='government-xl-disneyland-eastern75643-osm-apron-decision-v1-20261030';feature=take(featurebatch,'ROOT-OSM-APRON-DECISION.json');assert feature['exactBasicForm']==byuid[BASIC]and feature['sourceSHA256']==SHA and feature['graphicInterpretationAccepted']and not feature['installationApproved']
 visual=doc('visual-observations','ROOT-VISUAL-OBSERVATIONS.json');assert len(visual['imagesActuallyViewed'])==12
 for ref in visual['imagesActuallyViewed']:
  p=ROOT/ref['path'];assert digest(p.read_bytes())==ref['sha256'];refs.append(p)
 lifecycle=doc('lifecycle','report.json');assert lifecycle['passed']and not lifecycle['pageErrors']
 images=[];nativeimages=[];reports=[]
 for width in [1280,390]:
  path=base/(P+'native-preview'+D)/str(width)/'staged-browser.json';report=take(P+'native-preview'+D,str(width)+'/staged-browser.json');assert report['passed']and not report['errors'];reports.append(dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes())))
  views=[v for v in report['views']if 'time'in v];assert len(views)==2
  for v in views:
   assert v['fullyFramed']and v['solidAppearance']and v['fallbackFaces']==0 and v['sourceSHA256']==SHA and v['pick']==v['collision']==UID
   native=v['nativeSupports'][NATIVE];assert native['active']and native['visible']and native['wanted']
   p=path.parent/v['file'];images.append(dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes())))
  assert len(report['retainedNativeOwnViews'])==2
  for v in report['retainedNativeOwnViews']:
   assert v['uid']==NATIVE and v['active']and v['visible']and v['fullyFramed']and not v['fallbackFaces'];p=path.parent/v['file'];nativeimages.append(dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes())))
 replacement=dict(sourceUid=UID,basicUid=BASIC,sourceSHA256=SHA,sourceFormSHA256=form_sha(source),basicFormSHA256=form_sha(byuid[BASIC]),onlyWhileExactOwnerActive=True,approved=True)
 review=dict(uids=[UID],sourceSHA256ByUid={UID:SHA},currentManifest=dict(path=str(manifest.relative_to(ROOT)),sha256=digest(manifest.read_bytes())),identityAccepted=True,sourceSpecificPhysicalInterpretationAccepted=True,completeNeighbourInterpretationAccepted=True,visualAcceptance=True,completeFourWorldFoundations=True,completeCurrentNeighbourChecks=2,identityProof=dict(exactObjectId=True,exactBuildingCSUID=True,uniqueViewerMatch=True,identityAccepted=True),supportByUid={},requiredOriginalAssembly={UID:SHA},terrainEdits=False,sourceGeometryChanges=0,sourcePoseChanges=0,conditionalApronReplacement=replacement,imagesActuallyViewed=images,retainedNativeImagesActuallyViewed=nativeimages,browserReports=reports,apronLifecycleReport=dict(path=str((base/(P+'lifecycle'+D)/'report.json').relative_to(ROOT)),sha256=digest((base/(P+'lifecycle'+D)/'report.json').read_bytes())),apronFeatureReview=dict(path=str((base/featurebatch/'ROOT-OSM-APRON-DECISION.json').relative_to(ROOT)),sha256=digest((base/featurebatch/'ROOT-OSM-APRON-DECISION.json').read_bytes())),leaseResources=sorted(['building:'+UID,'source-form:'+BASIC,'building:'+NATIVE,'terrain:city/data/terrain.json']),rawGenericIdentityPassed=False,rawGenericFoundationPassed=False,installationApproved=False,publication=False,aiGeometryModelling=False,sourceEvidenceInterpretationUsedAI=True,interpretation=['Exact unchanged full pier/apron source extent is already individually identity-reviewed; current generic reasons match that review. No footprint, pose or height edits.','Two exact low terminal wall facets are strictly covered by native and actual current ground in all4streams; this bounded lower shore-closure interpretation retains raw generic failure.','Original western/eastern contacts are edge/point contacts. Three literal-renderer crossings trace to original edge/point facet pairs; no new original transverse crossing. Accept exact unedited pair interface only.','The sole remaining foreign BASIC conflict is the exact unsupported24m apron graphic, conditionally hidden under the separately hash-bound primary-evidence decision. Full availability/collision lifecycle passed.','All12actual privateexports inspected; existing terrain faceting and dark night appearance are acknowledged, no terrain/performance improvement claimed.'])
 save(out/'ROOT-PHYSICAL-REVIEW.json',review);save(out/'ROOT-SOURCE-REVIEW.json',review)
 module('eastern_apron_bounded_source_review',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'bounded-original-pier-extent-shore-interface-and-apron-source-review',refs,review)
if __name__=='__main__':main()
