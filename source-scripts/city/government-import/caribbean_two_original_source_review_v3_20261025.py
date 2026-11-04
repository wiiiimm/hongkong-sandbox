"""Bind ROOT's exact Caribbean original source interpretation to completed checks."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-caribbean-two-final-source-review-v3-20261025'
SOURCES={'landsd/290981:0':'5d15afc0e09f7975844fbd2bcb0f2943546933a9424d7459f855bb7892ad76a8','landsd/95518:0':'07cf0e2ad38d16c8f548845005fc3560e5b60d987db09897fac44826a111f9d9'}
COUNTS={'landsd/290981:0':16521,'landsd/95518:0':263}
SUPPORT={'landsd/95518:0':'landsd/290981:0'}
def main():
 out=BASE/BATCH;assert not out.exists();refs=[Path(__file__)];pins={}
 def take(batch,name='summary.json',local=False):
  if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
  p=(HERE/'local'/batch if local else BASE/batch)/name;assert digest(p.read_bytes())==pins[batch][str(p.relative_to(ROOT))];refs.append(p);return read(p)
 def image_viewed(p):
  assert p.is_file();refs.append(p);return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
 runtime='government-xl-caribbean-minimal-seams-runtime-v1-20261025'
 selected=take(runtime,'selection.json.gz');assert {r['uid']:r['sourceSHA256']for r in selected['rows']}==SOURCES
 geometry={g['uid']:g for g in take(runtime,'runtime-geometry.json.gz',True)['rows']}
 attrs={r['uid']:r for r in take('government-xl-caribbean-two-after-high-court-attributes-v1-20261025','attributes.json.gz')['rows']}
 numeric=take('government-xl-caribbean-minimal-seams-numeric-rebind-v1-20261025');assert numeric['allActualLiteralSourceAndDrawnGroundInputsIdentical']and numeric['allFourWorldSourceAttributesIdentical']
 raw={};images=[];source_images=[]
 for row in selected['rows']:
  uid=row['uid'];short=uid.split('/')[1];number=short.split(':')[0];assert row['triangles']==COUNTS[uid]
  asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==SOURCES[uid];refs.append(asset)
  entry=row['candidate']['entry'];assert entry['rootTranslation']==[-834500,0,816500]and entry.get('verticalPlacementOffsetHKPD',0)==0
  identity=take('government-xl-caribbean-two-after-high-court-identity-v1-20261025',short+'/identity.json')
  assert identity['sourceSHA256']==SOURCES[uid]and identity['originalOwnership']['sourceGraphVerified']and identity['exactCurrentComponentRoute']['qualified']and identity['freshCurrentIdentity']['exactObjectAndCSUID']
  assert identity['exactWholeCellCoverage']['covered']and identity['exactWholeCellCoverage']['wholeOriginalFacesAccounted']==COUNTS[uid];raw[uid]=identity['reasons']
  foundation=take('government-xl-caribbean-minimal-'+number+'-foundations-v1-20261025');assert foundation['establishedFoundationPolicyPassed']and len(foundation['rows'])==4
  for r in foundation['rows']:assert r['completeTerrainTriangles']==COUNTS[uid]and r['fullyBuriedUpwardTriangles']==0 and r['fullyBuriedAreaFraction']<=.001
  # Reuse ONLY exact mathematical relations, after independent complete array
  # equality, not scene approval from the superseded trial terrain producer.
  ground_batch='government-xl-caribbean-'+('seams-complete-ground'if number=='290981'else'companion-seams-complete-ground')+'-v1-20261025'
  ground=take(ground_batch);assert len(ground['rows'])==4
  g=geometry[uid];ground_sha=digest(np.asarray(g['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3).tobytes());a=attrs[uid];ix=np.asarray(a['completeOriginalIndex']).reshape(-1,3)
  worlds={'original':decode_original_world_triangles(asset.read_bytes()),**{n:np.asarray(a[f]).reshape(-1,3)[ix]for n,f in [('literal','completeLiteralWorldPosition'),('left','completeExplicitLeftAssociatedFloat32WorldPosition'),('balanced','completeExplicitBalancedFloat32WorldPosition')]}}
  for r in ground['rows']:
   mode=r['mode'];low=take(ground_batch,mode+'.json.gz');cap=take(ground_batch,mode+'-cap-paths.json.gz');sha=digest(worlds[mode].astype('<f8').tobytes())
   assert low['sourceWorldSHA256']==cap['sourceWorldSHA256']==sha and low['groundSHA256']==cap['actualGroundSHA256']==ground_sha
   assert r['negativeNonWallFaces']==([16059]if number=='290981'else[])
   assert all(p['hasExactSharedEdgeClearCapPath']for p in cap['proof']['paths'])and len(cap['proof']['paths'])==(270 if number=='290981'else 21)
  if number=='290981':
   t=worlds['original'][16059];n=np.cross(t[1]-t[0],t[2]-t[0]);assert n[1]/np.linalg.norm(n)<-.999
  view_batch='government-xl-caribbean-'+number+'-source-views-v1-20261025';take(view_batch)
  for filename in ['whole-source-plan.png','whole-source-perspectives.png']:source_images.append(image_viewed(BASE/view_batch/filename))
 primary=take('government-xl-caribbean-two-after-high-court-primary-records-v1-20261025');assert not primary['missingRequestedCSUIDs']
 foreign=take('government-xl-caribbean-two-foreign-forms-primary-records-v1-20261025');assert not foreign['missingRequestedCSUIDs']
 compound=take('government-xl-caribbean-two-compound-projection-v1-20261025');assert compound['completeOriginalFaces']==16784
 for r in compound['rows']:
  assert r['ownCoverageByWholeOriginalAssembly']>.99 and r['wholeCellCoveredByOriginalAssembly']
  assert set(r['sourceExcessOverlapOutsideCurrentAssemblyByForeignUid'])==({'landsd/176036:0','landsd/177774:0'}if r['uid']=='landsd/290981:0'else set())
 support=take('government-xl-caribbean-two-current-support-paths-v1-20261025');assert support['allUnresolvedHaveFinitePaths']and len(support['rows'])==4
 for r in support['rows']:assert r['targets']==r['verifiedPaths']==157 and r['remaining']==0
 take('government-xl-caribbean-two-current-strict-support-v1-20261025')
 continuous=take('government-xl-caribbean-minimal-seams-continuous-v1-20261025');assert all(r['upwardContinuousMinimumGapM']>=-.5 for r in continuous['rows'])
 assert all(not r['stillUncoveredFaces']for r in take('government-xl-caribbean-minimal-seams-exact-coverage-v1-20261025')['rows'])
 patch=take('government-xl-caribbean-minimal-seams-v1-20261025');assert patch['status']=='private-terrain-validator-passed'and patch['terrainTriangles']==16120 and patch['seamCover']['addedDomainAreaM2']<=.25 and not patch['replacedNativeTerrain']
 scope_name='government-xl-caribbean-upward-return-scope-v1-20261025';scope=take(scope_name,'scope.json');assert scope['currentNativeActors']==6947 and not scope['touchingNativeUids']and not scope['terrainContacts']and scope['positiveAreaTerrainOverlaps']==0
 forms={f['uid']:f for f in take(scope_name,'form-obligations.json.gz')};model_name='government-xl-caribbean-two-after-high-court-model-scope-v1-20261025'
 for r in take(model_name)['rows']:
  assert not r['nearbyNativeActors']and r['currentNativeActorsChecked']==6947
  for f in take(model_name,r['uid'].split('/')[1]+'-forms.json.gz'):
   b=f['building'];assert b['uid']not in forms or forms[b['uid']]==b;forms[b['uid']]=b
 assert len(forms)==85
 neighbours=take('government-xl-caribbean-minimal-seams-neighbours-v1-20261025');assert neighbours['forms']==85 and not neighbours['flagged']
 browser='government-xl-caribbean-two-private-browser-v2-20261025';reports=[]
 for width in [390,1280]:
  report=take(browser,str(width)+'/staged-browser.json');assert report['passed']and not report['errors']
  views=[v for v in report['views']if'time'in v];assert len(views)==4
  for v in views:
   assert v['active']and v['visible']and v['fullyFramed']and v['solidAppearance']and not v['fallbackFaces']and v['pick']==v['collision']==v['uid']and v['sourceSHA256']==SOURCES[v['uid']]
  assert all({m['uid']for m in j['models']if m['active']}==set(SOURCES)for j in report['jointViews'])
  for uid in ['290981','95518']:
   for time in [1500,2200]:images.append(dict(uid='landsd/'+uid+':0',width=width,time='15:00'if time==1500 else'22:00',**image_viewed(BASE/browser/str(width)/f'staged-landsd-{uid}-0-{width}-{time}-canvas.png')))
  p=BASE/browser/str(width)/'staged-browser.json';reports.append(dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes())))
 assert len(images)==8 and all(set(i)=={'uid','width','time','path','sha256'}for i in images)
 manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selected['manifestSHA256'];refs.append(manifest)
 resources=sorted([('building:'if u.startswith('landsd/')else'source-form:')+u for u in forms]+['terrain:city/data/terrain.json'])
 result=dict(uids=list(SOURCES),sourceSHA256ByUid=SOURCES,requiredOriginalAssembly=SOURCES,supportByUid=SUPPORT,retainedNativeUids=[],reviewer='ROOT',identityAccepted=True,identityProof=dict(exactObjectId=True,exactBuildingCSUID=True,uniqueViewerMatch=True,identityAccepted=True),currentManifest=dict(path=str(manifest.relative_to(ROOT)),sha256=digest(manifest.read_bytes())),sourceSpecificPhysicalInterpretationAccepted=True,completeNeighbourInterpretationAccepted=True,completeFourWorldFoundations=True,completeCurrentNeighbourChecks=85,totalNeighbourForms=85,terrainAffectedForms=85,leaseResources=resources,visualAcceptance=True,imagesActuallyViewed=images,sourceDiagramsActuallyViewed=source_images,browserReports=reports,originalSourceReviewAccepted=True,rawIdentityReasonsRetained=raw,rawBasalAndExtentFailuresRetained=True,sourceGeometryChanges=0,sourcePoseChanges=0,aiGeometryModelling=False,sourceEvidenceInterpretationUsedAI=True,installationApproved=False,observations=[
 'Exact unchanged government roots, native source graphs, qualified current ObjectID/CSUID routes and full GeoRef cells identify these two originals. Compound projection covers >99% of each current footprint. Main source contains broad podium roofs, ramps, projecting access structures and small elevated details; the current plan footprint is not an envelope of all original elevated geometry. Preserve the30.058m main extent and raw foreign overlap flags. The two narrow excess projections overlap separately recorded unnamed current forms176036/177774 by1.8134/17.9991m2; their official records remain separately bound. No ownership or shared-permit inference, alias reassignment, deletion or suppression of these neighbours is made; the exact publisher original is retained in full.',
 '95518 is an elevated ancillary source over the podium; official description records filtration plant/pool/ancillary accommodation, not a tall residential tower inferred from its generic form subtype. Strict raw interface remains false; all157 unresolved probes have verified finite paths in each of4current streams. Adopt only95518->290981; failed-parent download must preserve BASIC fallback as verified in the mobile browser.',
 'All270main affected wall paths and21companion affected wall paths reach clear original caps in all4worlds. Preserve downward basal16059 and raw aggregate cap false. Its fully buried area fraction5.9287e-7 is below the existing.001policy, with zero upward burial. No excavation to expose a downward basal closure or engineering watertightness claim.',
 'Derived terrain correction changes no model vertices or pose. Disconnected ramp domains and minimal Float32 seam covers pass unchanged height/area/2mm/complexity validators, complete exact source coverage and all85current-neighbour checks. Numeric rebind independently proves complete arrays equal to the earlier ground diagnostic; this transfers pure mathematical relations only, not stale producer or scene approval. Final guarded terrain receipt is the separate minimal-seam producer with unchanged native-replacement guards.',
 'ROOT opened all4source diagrams and all8V2desktop/mobile day/night exports. Podium roof/access outlines and ancillary block are readable from the higher opposite view. Original materials are grey and dark at night; existing BASIC towers retain lit windows. V1source exports were actually inspected and rejected for foreground tower occlusion. Fresh live exports and independent all6947oldassets/full521/globalBASICreadback remain mandatory.'
 ])
 save(out/'ROOT-PHYSICAL-REVIEW.json',result);save(out/'ROOT-SOURCE-REVIEW.json',result)
 refs.append(HERE/'exact_packed_world_geometry_20261009.py');module('caribbean_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'bounded-original-caribbean-source-physical-and-visual-review',list(dict.fromkeys(refs)),result)
if __name__=='__main__':main()
