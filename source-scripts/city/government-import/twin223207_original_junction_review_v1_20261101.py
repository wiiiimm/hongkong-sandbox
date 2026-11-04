"""Bounded exact original Twin Regency T1/installed podium junction review.
Raw warnings and all negative facets remain recorded; no geometry/policy edits.
"""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';P='government-xl-twin-after-aqua-'
UID='landsd/223207:0';PARENT='landsd/223206:0';SHA='ba739fa1425007e305a489fe97738edf800795fbdcc38cc9e11705e6475253af';PSHA='fd67218f6828e36899e689d071c55bf95fa0df159ac2927643be46eead74d347'
AFFECTED=[3330,3331,3332,3333,3334,3335,3339,4711,4721,4722,4858,4861]
def main():
 batch=P+'physical-review-v1-20261101';out=BASE/batch;assert not out.exists();refs=[Path(__file__)];pins={}
 def take(n,file='summary.json',local=False):
  if n not in pins:pins[n]=authenticate(BASE/n)[1];refs.append(BASE/n/'result.json')
  path=(HERE/'local'/n if local else BASE/n)/file;assert digest(path.read_bytes())==pins[n][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 runtime=P+'current-original-checks-v1-20261101-runtime';selection=take(runtime,'selection.json.gz');source=selection['rows'][0];assert source['uid']==UID and source['sourceSHA256']==SHA and source['triangles']==11796
 attrs=take(P+'original-attributes-v1-20261101','attributes.json.gz');assert attrs['startEndAllInputsVerified'];attr=attrs['rows'][0];assert attr['uid']==UID and attr['sourceSHA256']==SHA
 asset=ROOT/source['candidate']['path'];assert digest(asset.read_bytes())==SHA;refs.append(asset);ix=np.asarray(attr['completeOriginalIndex']).reshape(-1,3)
 worlds={'original':decode_original_world_triangles(asset.read_bytes()),**{m:np.asarray(attr[k],dtype='<f8').reshape(-1,3)[ix]for m,k in [('literal','completeLiteralWorldPosition'),('leftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('balancedF32','completeExplicitBalancedFloat32WorldPosition')]}}
 geom=take(runtime,'runtime-geometry.json.gz',True)['rows'][0];actual=np.asarray(geom['position']).reshape(-1,3)[np.asarray(geom['index']).reshape(-1,3)];assert np.array_equal(actual,worlds['literal'])
 ground=np.asarray(geom['drawnGroundGeometry']).reshape(-1,3,3);margin=min(float(t[:,:,1].min()-ground[:,:,1].max())for t in worlds.values());assert margin>10
 metric=take(runtime,'metrics.json')['rows'][0];assert metric['sourcePreserved']and metric['sourceSHA256']==SHA and metric['missingTerrain']==metric['missingDrawnTerrain']['count']==metric['samplerDisagreement']['count']==0
 assert metric['budget']['triangles']==11796 and metric['budget']['geometryBytes']<50331648 and metric['budget']['residentBytes']<134217728
 identity=take(P+'current-original-checks-v1-20261101-identity','223207:0/identity.json');assert identity['passed']and not identity['reasons'];proof=identity['proof'];assert all(proof[k]is True for k in ['exactObjectId','exactBuildingCSUID','uniqueViewerMatch','identityAccepted'])
 scope=take(P+'complete-source-scope-v1-20261101');s=scope['rows'][0];assert s['uid']==UID and s['currentNativeActorsChecked']==7068 and [r['uid']for r in s['nearbyNativeActors']]==[PARENT]
 forms=take(P+'complete-source-scope-v1-20261101','223207:0-forms.json.gz');assert len(forms)==2 and {r['building']['uid']for r in forms}=={UID,PARENT}
 contacts=take(P+'installed-native-contacts-v1-20261101');assert len(contacts['rows'])==1;pair=contacts['rows'][0];parent=pair['rawCurrentNativeEntry'];assert pair['uid']==UID and pair['nativeUid']==PARENT and pair['sourceSHA256']==SHA and pair['nativeSHA256']==parent['sha256']==PSHA
 assert all(parent[k]is True for k in ['publicationApproved','sourceIdentityReviewed','placementReviewed','identityReviewApproved'])and parent['rootTranslation']==[-834500,0,816500]and parent.get('verticalPlacementOffsetHKPD',0)==0
 support=take(P+'installed-support-v1-20261101');compound=take(P+'complete-compound-context-v1-20261101');roles=take(P+'native-contact-roles-v1-20261101');plane=take(P+'adjacent-plane-v2-20261101');assert plane['capturedSceneIsCurrent']and plane['exactOriginalAdjacentCoplanarNativePatch']and plane['sourceSHA256ByUid']=={UID:SHA,PARENT:PSHA}
 views=take(P+'complete-low-joint-views-v1-20261101');assert views['completeNegativeSourceFaces']==AFFECTED and len(views['images'])==13
 for image in views['images']:
  path=ROOT/image['path'];assert digest(path.read_bytes())==image['sha256'];refs.append(path)
 facts={};original_pairs={(r['sourceFaceA'],r['sourceFaceB'])for r in take(P+'native-contact-roles-v1-20261101','223207:0--223206:0--original.json.gz')}
 for mode,tri in worlds.items():
  sha=digest(tri.astype('<f8').tobytes());raw=take(P+'installed-support-v1-20261101',mode+'/diagnostic.json.gz');assert raw['sourceWorldSHA256ByUid'][UID]==sha and raw['unresolved']==raw['finitePaths']==28 and raw['compoundFoundation']['fullyBuriedTriangles']==raw['compoundFoundation']['fullyBuriedUpwardTriangles']==0
  assert len(raw['paths'])==28 and all(p['verifiedPath']and len(p['verifiedPath']['faces'])==1 and p['verifiedPath']['withinEndpointHeight']and p['verifiedPath']['maximumResidualM']<=.001 and p['verifiedPath']['contact']['dimension']>0 for p in raw['paths'])
  c=next(r for r in compound['rows']if r['mode']=={'leftF32':'left','balancedF32':'balanced'}.get(mode,mode));assert c['exactAffectedFaces']==AFFECTED and c['negativeNonWallFaces']==[3334,3335,4721,4722]and not c['compoundCapPathsPassed']
  for i in c['negativeNonWallFaces']:
   t=tri[i];n=np.cross(t[1]-t[0],t[2]-t[0]);assert n[1]/np.linalg.norm(n)<-.99 and t[:,1].max()<16.357 and np.linalg.norm(n)/2<.73
  classified=take(P+'native-contact-roles-v1-20261101','223207:0--223206:0--'+mode+'.json.gz');cross=[r for r in classified if r['contactRole']=='transverse-surface-crossing'];role=next(r for r in roles['rows']if r['mode']==mode);assert len(cross)==546 and role['sourceWorldSHA256']==sha and role['contactBounds'][1][1]<17.772
  new={(r['sourceFaceA'],r['sourceFaceB'])for r in cross}-original_pairs;assert new<=({(4523,50)}if mode in ['leftF32','balancedF32']else set())
  facts[mode]=dict(sourceWorldSHA256=sha,rawSupport=raw['support'],all28HaveSingleFacetPositiveContactPaths=True,rawCompoundClearance=c,rawWholeCompoundFoundation=raw['compoundFoundation'],rawTransverseCrossings=546,newFacetPairs=[list(p)for p in sorted(new)])
 images=[];retained=[];reports=[];browser=P+'installed-supported-preview-v2-20261101'
 for width in [1280,390]:
  report=take(browser,str(width)+'/staged-browser.json');assert report['passed']and not report['errors'];reports.append(dict(path=str((BASE/browser/str(width)/'staged-browser.json').relative_to(ROOT)),sha256=digest((BASE/browser/str(width)/'staged-browser.json').read_bytes())))
  for field,target,expected in [('views',images,SHA),('retainedNativeOwnViews',retained,PSHA)]:
   rows=[r for r in report[field]if r.get('file')];assert len(rows)==2
   for r in rows:
    assert r['active']and r['visible']and r['fullyFramed']and not r['fallbackFaces']and r['sourceSHA256']==expected
    if field=='views':assert r['solidAppearance']and r['pick']==r['collision']==UID
    path=BASE/browser/str(width)/r['file'];assert digest(path.read_bytes())==pins[browser][str(path.relative_to(ROOT))];refs.append(path);target.append(dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes()),uid=r['uid'],width=width,time=r['time']))
 manifest=ROOT/'3d-viewer/city/data/manifest.json';msha=digest(manifest.read_bytes());assert msha==selection['manifestSHA256']==scope['currentManifestSHA256']==plane['observedCurrentManifestSHA256'];refs.append(manifest)
 result=dict(uids=[UID],sourceSHA256ByUid={UID:SHA},requiredOriginalAssembly={UID:SHA},supportByUid={UID:PARENT},nativeSupportByUid={UID:PARENT},retainedNativeEntries={PARENT:parent},retainedNativeUids=[PARENT],reviewer='ROOT',identityAccepted=True,identityProof=proof,rawIdentityReasonsRetained=[],sourceSpecificPhysicalInterpretationAccepted=True,completeNeighbourInterpretationAccepted=True,completeFourWorldFoundations=True,completeFourWorldSourceClearance=True,completeCurrentNeighbourChecks=2,leaseResources=sorted('building:'+r['building']['uid']for r in forms),retainedBasicSupportDependencies=[],retainedCurrentBasicSupportUids=[],currentManifest=dict(path=str(manifest.relative_to(ROOT)),sha256=msha),currentManifestSHA256=msha,terrainEdits=False,sourceGeometryChanges=0,sourcePoseChanges=0,aiGeometryModelling=False,sourceEvidenceInterpretationUsedAI=True,rawCanonicalFailuresPreserved=True,unresolvedExternalBasicContacts=[],acceptedInstalledSupportContacts=[dict(uid=UID,nativeUid=PARENT,physicalInterpretationAccepted=True,rawContactSummary=pair)],junctionFacts=facts,rawSupportAndCompoundVerdicts=support,rawCompoundClearance=compound,actualEarthGlobalClearanceLowerBoundM=margin,imagesActuallyViewed=images,retainedImagesActuallyViewed=retained,browserReports=reports,sourceJunctionImagesActuallyViewed=views['images'],visualAcceptance=False,installationApproved=False,publication=False,interpretation=[
 'Bounded acceptance of these exact original T1 and already installed podium bytes at their original fixed1x/HKPD poses. No terrain edits or native metadata changes. Every source vertex is over10m above the maximum actual drawn earth vertex; no earth-burial exception.',
 'Keep all28support warnings, zero strict rim anchors and raw cap failures. Each warning reaches positive original podium contact along one incident source facet within the unchanged endpoint-height/residual gates. These are authored lower source projections; no canonical-anchor or structural-certification claim.',
 'All12compound-negative facets were individually plotted and inspected. Eight are vertical walls;3334/3335/4721/4722 are downward-facing original undersides, each below.73m2 and below16.357mHKPD, at the podium joint. No upward floor face or whole sampled triangle is buried. Named lower cap/podium overlap is accepted for these unchanged original components; no global embedding limit or collision rule is widened.',
 'All546transverse contacts stay below17.772mHKPD in the lower authored joint. The sole extra represented pair4523/50 partitions a pre-existing4523/49contact across an exactly coplanar ORIGINAL49/50edge. Actual represented plane residuals and new pair remain recorded; no epsilon or pair suppression.',
 'ROOT opened all13exact source-joint plots plus all8current desktop/mobile source/retained day/night exports. Full original roof/body/base and complete podium remain visible; provider surfaces stay unlit at night without procedural window skin. Existing staged/live, old-asset, retained-support and521ledger guards still apply.'])
 save(out/'ROOT-PHYSICAL-REVIEW.json',result);save(out/'junction-facts.json',facts);refs.append(HERE/'original_installed_support_model_only_contract_v1_20261027.py');module('twin_original_junction_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(batch,'bounded-exact-original-twin-t1-installed-podium-junction-review',list(dict.fromkeys(refs)),result)
if __name__=='__main__':main()
