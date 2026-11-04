"""Named exact Harbourfront source/ground/interface review; no installation."""
import sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
P='government-xl-harbourfront-horizon233227-';BATCH=P+'original-review-v2-20261102'
UID='landsd/233227:0';SHA='b59787a14f989eae55dcb47cafdc4f076215e9190ebcb2136a2277d10f4203a0'
R=P+'floor-regression-v2-20261102';N=P+'floor-neighbours-v2-20261102';G=P+'floor-ground-context-v2-20261102';V=P+'retained-terrain-preview-v1-20261102'
def main():
    out=BASE/BATCH;lp=HERE/'local'/BATCH/'reservation.json';assert not out.exists()
    resources=read(BASE/(P+'floor-resources-v2-20261102.json'))['resources']
    if '--owned'not in sys.argv:
        assert not lp.parent.exists();c=reservations.claim('harbourfront-original-review-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert c['ok'],c
        return execute_reserved(c['reservation'],lp,[sys.executable,__file__,'--owned'])
    lease=read(lp);assert reservations.owns(lease)and set(lease['resources'])==set(resources)
    refs=[Path(__file__),BASE/(P+'floor-resources-v2-20261102.json')];pins={}
    def take(batch,name='summary.json',local=False):
        if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
        p=(HERE/'local'/batch if local else BASE/batch)/name
        assert digest(p.read_bytes())==pins[batch][str(p.relative_to(ROOT))];refs.append(p);return read(p)
    selection=take(R+'-runtime','selection.json.gz');source=selection['rows'][0];assert len(selection['rows'])==1 and source['uid']==UID and source['sourceSHA256']==SHA
    raw=take(P+'after-hkust-staff-v1-20261102-identity','233227:0/identity.json');ctx=raw['originalOwnership']['fullProjection']
    reasons=['fresh-current-spatial-bound:sourceExcessMaximumDistanceFromTargetM','full-source-maximum-extent']
    assert raw['reasons']==reasons and not raw['passed'] and raw['sourceSHA256']==SHA
    assert raw['originalOwnership']['sourceGraphVerified']and raw['originalOwnership']['originalRootName']==source['modelId']=='B370971793102063C0'
    route=raw['exactCurrentComponentRoute'];assert route['qualified']and route['official']['objectId']==233227 and route['official']['buildingCSUID']=='3709717931P20060110'
    assert raw['exactWholeCellCoverage']['covered']and raw['exactWholeCellCoverage']['wholeOriginalFacesAccounted']==source['triangles']==25646
    assert ctx['exactObjectAndCSUID']and ctx['targetCoveredBySourceProjection']>=.95
    assert {r['uid']for r in ctx['intersectingForms']}=={UID,'landsd/31275:0'} and all(r['sameParent']and r['parent']=='way/184431111'for r in ctx['intersectingForms'])
    plot=take(P+'current-source-views-v1-20261102');assert plot['sourceSHA256']==SHA and plot['originalWorldSHA256']==raw['worldTrianglesSHA256'];im=plot['image'];image=ROOT/im['path'];assert digest(image.read_bytes())==im['sha256'];refs.append(image)
    foundations=take(R+'-foundations');assert foundations['establishedFoundationPolicyPassed']and len(foundations['rows'])==4
    assert all(r['triangles']==r['completeTerrainTriangles']==25646 and r['fullyBuriedTriangles']==r['fullyBuriedUpwardTriangles']==0 for r in foundations['rows'])
    clearance=take(G+'-clearance');assert clearance['sourceSHA256']==SHA and len(clearance['rows'])==4 and all(not r['exactAffectedFaces']for r in clearance['rows'])
    metrics=take(R+'-runtime','metrics.json')['rows'];assert len(metrics)==1;m=metrics[0]
    assert m['uid']==UID and m['sourceSHA256']==SHA and m['sourcePreserved']
    assert m['missingTerrain']==m['missingDrawnTerrain']['count']==m['samplerDisagreement']['count']==0
    assert m['minSurfaceGap']>=-.5 and m['minLowGap']>=-.1 and m['minLowGap']<=.1 and m['maxLowGap']<=1 and m['maxSamplerDelta']<=.004
    neighbours=take(N+'-checks');assert neighbours['forms']==12 and not neighbours['basicFlags']and set(neighbours['requiredNativeUids'])==set(neighbours['nativeResolved'])=={'landsd/31275:0','landsd/240841:0'} and all(r['passed']for r in neighbours['nativeRows'])
    replacement=take(N+'-binding')['candidate']['replaces'];assert replacement['retainedUids']==['landsd/31275:0']
    contacts=take(P+'current-interfaces-v1-20261102-native-contacts');assert len(contacts['rows'])==1;c=contacts['rows'][0];assert c['nativeUid']=='landsd/31275:0'and c['nativeSHA256']=='f17c8e510e679719b8df50f3000dea7ea6ed5010124fe3005a7fcde7374e3e67'
    assert [r['areaContactPairs']for r in c['modes']]==[0,0,845,845] and [r['positiveSurfaceContactPairs']for r in c['modes']]==[966,966,9503,9503]
    foreign=take(P+'current-interfaces-v1-20261102-foreign');assert all(v['positiveContactPairs']==0 for r in foreign['rows']for v in r['modes']if v['mode']!='before-basic')
    observations=BASE/(P+'preview-observations-v2-20261102.json');seen=read(observations);refs.append(observations);assert seen['reviewer']=='Codex ROOT'and seen['allTwelveExportsActuallyOpened']and len(seen['imagesActuallyViewed'])==12
    observed={r['path']:r['sha256']for r in seen['imagesActuallyViewed']};reports=[]
    for width in [1280,390]:
        report=take(V,str(width)+'/staged-browser.json');assert report['passed']and not report['errors'];views=[v for v in report['views']if'time'in v];assert len(views)==2
        assert len(report['retainedNativeOwnViews'])==4
        for v in views:
            assert v['active']and v['visible']and v['fullyFramed']and v['solidAppearance']and not v['fallbackFaces']and v['pick']==v['collision']==UID and v['sourceSHA256']==SHA
        for v in views+report['retainedNativeOwnViews']:
            image=BASE/V/str(width)/v['file'];assert observed[str(image.relative_to(ROOT))]==digest(image.read_bytes());refs.append(image)
        reports.append(dict(path=str((BASE/V/str(width)/'staged-browser.json').relative_to(ROOT)),sha256=digest((BASE/V/str(width)/'staged-browser.json').read_bytes())))
    manifest=ROOT/'3d-viewer/city/data/manifest.json';mh=digest(manifest.read_bytes());assert mh==selection['manifestSHA256']==raw['exactRouteManifestSHA256'];refs.append(manifest)
    asset=ROOT/source['candidate']['path'];assert digest(asset.read_bytes())==SHA;refs.append(asset)
    proof={k:True for k in ['exactObjectId','exactBuildingCSUID','uniqueViewerMatch','identityAccepted']}
    result=dict(uids=[UID],sourceSHA256ByUid={UID:SHA},requiredOriginalAssembly={UID:SHA},supportByUid={},identityAccepted=True,identityProof=proof,identityProofByUid={UID:proof},sourceSpecificPhysicalInterpretationAccepted=True,completeNeighbourInterpretationAccepted=True,visualAcceptance=True,currentManifest=dict(path=str(manifest.relative_to(ROOT)),sha256=mh),currentManifestSHA256=mh,leaseResources=resources,exactTerrainReplacement=replacement,retainedNativeRegression=neighbours,completeCurrentNeighbourChecks=12,completeFourWorldFoundations=True,rawIdentity=raw,rawCanonicalFailuresPreserved=True,rawNativeContacts=contacts,rawForeignContacts=foreign,rawRuntimeMetrics=m,imagesActuallyViewed=[r for r in seen['imagesActuallyViewed']if '/staged-landsd-233227-'in r['path']],retainedNativeImagesActuallyViewed=[r for r in seen['imagesActuallyViewed']if '/staged-retained-own-'in r['path']],allImagesActuallyViewed=seen['imagesActuallyViewed'],browserReports=reports,sourceGeometryChanges=0,sourcePoseChanges=0,terrainEdits=True,publicTerrainWritesPerformed=False,installationApproved=False,publication=False,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,interpretation=[
      'Named identity acceptance applies only to this intact original podium component and frozen viewer OBJECTID/CSUID, not whole-landmark completeness. Exact provider root, complete geographic cell and current 97.599% target coverage agree. The 63.514m individual-outline extent warning is retained: full-source diagrams show the middle E wing mapped to same-parent Tower31275 while the podium polygon follows the outer wings/front bar. Both exact originals render aligned in desktop/mobile views. No generic identity threshold, unrelated form or legal-ownership inference is changed.',
      'Original podium and retained original tower are authored overlapping parts of the same mapped hotel. Preserve all finite/positive contacts and the845coplanar area contacts in each Float32 stream; these are not claimed disjoint or collision-free. Exact full originals, unchanged pose, same complex projection and inspected views support this particular nested base/tower interface. No source triangles are removed or remodelled, and existing support contracts/flags remain unchanged. This grants no exception for another source or revision.',
      'All original faces have complete current ground and pass four-world foundation and exact-0.5m clearance checks after the bounded derived terrain return. Runtime lower-rim contact and sampler agreement pass unchanged limits. Complete12form/two-native regressions pass. Existing240841burial remains unchanged and is not certified repaired.',
      'All12actual desktop/mobile day/night exports were opened; source and retained objects are visible, loading/picking/collision/failure-retry pass. Low podium parts are partly occluded by the taller source; no every-facade, walking route, physical-phone or FPS claim. Final guarded publisher/live verification and independent521/source/old-assets/support readback remain mandatory.'])
    save(out/'233227:0-identity-review.json',dict(uid=UID,sourceSHA256=SHA,identityAccepted=True,identityProof=proof,rawProof=raw,rawReasonsPreserved=reasons,componentIdentityOnly=True,installationApproved=False,publication=False,sourceGeometryChanges=0))
    save(out/'ROOT-SOURCE-REVIEW.json',result);save(out/'ROOT-PHYSICAL-REVIEW.json',result);save(out/'summary.json',result)
    assert reservations.owns(lease)and digest(manifest.read_bytes())==mh
    module('harbourfront_original_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'named-exact-harbourfront-podium-ground-and-authored-tower-interface-review',list(dict.fromkeys(refs)),result)
if __name__=='__main__':main()
