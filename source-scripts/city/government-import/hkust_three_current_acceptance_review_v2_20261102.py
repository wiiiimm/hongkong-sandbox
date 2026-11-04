"""Bind current original-port evidence and exact BASIC foundation resolutions.

Bounded evidence interpretation, not modelling, installation or publication.
"""
import argparse,copy,sys,uuid
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';P='government-xl-academic309823-after-harbour-'
BATCH=P+'qualified-current-review-v2-20261102'
POSTS=[29105,29139,29271,309840,31251,31639,33442]
EXCEPTIONS=[31181,309838,339024]
TERRAIN_URL='city/data/government-native-hkust-academic-three-original-v1-20261102.json'


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--owned',action='store_true');a=ap.parse_args()
    out=BASE/BATCH;local=HERE/'local'/BATCH;assert not out.exists();refs=[Path(__file__)];pins={}
    def take(batch,name='summary.json'):
        if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
        path=BASE/batch/name;assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    def summary(s):return take(P+s+'-20261102')
    def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
    scope=P+'repaired-floor-retention-scope-v1-20261102';forms=take(scope,'form-obligations.json.gz');sr=take(scope,'scope.json')
    resources={('building:'if b['uid'].startswith('landsd/')else'source-form:')+b['uid']for b in forms};resources.update('building:'+u for u in sr['uids']);resources.update('terrain:'+r['url']for r in sr['terrainContacts']);resources.add('terrain:city/data/terrain.json')
    leasefile=local/'reservation.json'
    if not a.owned:
        assert not local.exists();claim=reservations.claim('hkust-current-review-'+str(uuid.uuid4()),sorted(resources),batch=BATCH,ttl=3600);assert claim['ok'],claim
        return execute_reserved(claim['reservation'],leasefile,[sys.executable,__file__,'--owned'])
    lease=read(leasefile);assert reservations.owns(lease)and set(lease['resources'])==resources
    bounded=summary('bounded-source-review-v1');sources=bounded['sourceSHA256ByUid']
    assert bounded['identityAccepted']is True and bounded['sourceSurfaceAndGroundReviewAccepted']is True and bounded['activationGroupRequired']is True
    assert bounded['requiredOriginalAssembly']==sources and bounded['genericThresholdChanges']==0
    assert all(r['identityAccepted']is True and r['identityProof']['currentProviderObjectIdExact']is False for r in bounded['rows'])
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==bounded['currentManifestSHA256'];refs.append(manifest)
    assert len(forms)==36
    foundation=[]
    for uid in sorted(sources):
        s=summary('repaired-floor-'+uid.split('/')[1].replace(':','-')+'-foundations-v1')
        assert s['establishedFoundationPolicyPassed']is True and len(s['rows'])==4
        assert all(r['establishedFoundationPolicyPassed']is True and r['fullyBuriedUpwardTriangles']==0 and r['fullyBuriedAreaFraction']<=.001 for r in s['rows']);foundation.append(s)
    # The source-specific ground interpretation retains all canonical negatives.
    witness=summary('lower-patch-witnesses-v1');assert len(witness['rows'])==4 and witness['sourceGeometryChanges']==0 and witness['genericThresholdChanges']==0
    for suffix in ['complete-source-pairs-v1','pair-plane-context-v1','current-native-contacts-v1','native-contact-roles-v1','current-foreign-contacts-v1','foreign-excess-context-v1','current-grade-contacts-v1','current-belowgrade-context-v1','current-ground-root-paths-v1']:
        summary(suffix)
    native=summary('retained-native-regression-v1');assert native['requiredNativeUids']==native['nativeResolved']==['landsd/26949:0']
    assert all(r['passed']and r['terrain']['newlyWhollyBuried']==r['terrain']['newlyUpwardWhollyBuried']==0 for r in native['nativeRows'])
    expected={'landsd/'+str(i)+':0'for i in POSTS+EXCEPTIONS};assert {r['uid']for r in native['basicFlags']}==expected
    assert all(r['reasons']==['increased-neighbour-ground-gap']for r in native['basicFlags'])
    collision=summary('joint-basic-collision-v1');assert collision['simultaneousBasicFoundationProbesPassed']is True and collision['probes']==43050 and collision['forms']==36 and set(collision['uids'])==expected
    life_batch=P+'joint-foundation-lifecycle-recovery-v2-20261102';life=take(life_batch)
    assert life['actualAtomicLifecyclePassed']is True and life['lifecycleCases']==4 and life['desktopMobileDayNightCommandsPassed']is True
    atomic=take(life_batch,'lifecycle/report.json');assert atomic['passed']is True and not atomic['pageErrors']and atomic['actualProductionGeometryHTTPVerified']is True and atomic['moduleSubstitution']is False
    assert {r['failedUid']for r in atomic['cases']if r['width']==390}==set(sources)
    assert all(r['baseOnlyRestoredCompleteGroup']and r['completeGroupEvicted']and not r['audit']['violations']for r in atomic['cases'])
    east_batch=P+'small-components-east-preview-v2-20261102';east=take(east_batch);assert east['clearerEastViewCommandsPassed']is True
    for suffix,count in [('joint-visual-inspection-v1',16),('lifecycle-inspection-v1',11),('east-visual-inspection-v1',12)]:
        folder=BASE/(P+suffix+'-20261102');sheets=read(folder/'sheet-manifest.json');assert sheets['originalExports']==count and all(r['actuallyViewed']is True for r in sheets['sheets'])
        refs.extend([folder/'sheet-manifest.json',folder/'ROOT-OBSERVATIONS.json'])
        for sheet in sheets['sheets']:
            assert ref(folder/sheet['sheet'])['sha256']==sheet['sha256'];refs.append(folder/sheet['sheet'])
            for image in sheet['placements']:
                path=ROOT/image['path'];assert ref(path)['sha256']==image['sha256'];refs.append(path)
    terrain=summary('bounded-floor-v2');assert terrain['sourceSHA256ByUid']==sources and len(terrain['replacedNativeTerrain'])==1
    asset=ROOT/terrain['candidate']['path'];assert ref(asset)['sha256']==terrain['candidate']['sha256'];refs.append(asset)
    old=terrain['replacedNativeTerrain'][0];oldpath=ROOT/old['path'];assert ref(oldpath)['sha256']==old['sha256'];refs.append(oldpath)
    replacement=dict(url=old['url'],sha256=old['sha256'],retainedUids=['landsd/26949:0'])
    assert read(asset)['meta']['targetUids']==sorted([*sources,'landsd/26949:0'])
    sys.path.insert(0,str(HERE.parent/'island-detail-integration'))
    from basic_podium_footings import terrain_geometry_sha,value_sha
    from basic_unsurveyed_foundations import POLICY,COMMON_PROOFS
    refs.extend(HERE.parent/'island-detail-integration'/n for n in ['basic_podium_footings.py','basic_unsurveyed_foundations.py','illustrative_foundations.py'])
    deps=[dict(url=TERRAIN_URL,geometrySHA256=terrain_geometry_sha(read(asset)))]
    illustrative=[];unsurveyed=[]
    for number in POSTS+EXCEPTIONS:
        batch=P+('canopy-post-'if number in POSTS else'exception-')+str(number)+'-0-v1-20261102'
        s=take(batch);b=take(batch,'input.json')['building'];render=take(batch,'render-proof.json');uid=b['uid'];assert b in forms and s['installationApproved']is False
        tile=ROOT/'3d-viewer/city/data/tiles'/(b['tile']+'.json');assert next(f for f in read(tile)['buildings']if f['uid']==uid)==b;refs.append(tile)
        if b['structureType']=='Open-sided Structure':
            assert s['fullPostFootprintsMeetGround']and s['wholeRoofClear'];proposal=take(batch,'proposal.json');assert proposal['foundationBase']==s['foundationBase']
            assert all(render[k]is True for k in ['roofPartsExactlyUnchanged','allXZExactlyUnchanged','onlyIllustrativePostBottomVerticesChanged'])
            ground_name='continuous-part-ground-proof.json'
        else:
            assert s['fullFootprintGroundCovered']and s['wholeOriginalRoofClear']and render['originalBodyAndRoofPartsExactlyUnchanged']is True and render['newFoundationWindows']is False;ground_name='continuous-footprint-ground.json'
        take(batch,ground_name)
        for path,sha in render['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha;refs.append(ROOT/path)
        common=dict(uid=uid,status='approved-for-integration',sourceFormSHA256=value_sha(b),tileSHA256=digest(tile.read_bytes()),foundationBase=s['foundationBase'],fullPostFootprintsMeetGround=b['structureType']=='Open-sided Structure',wholeRoofClear=True,roofAndRecordedElevationsUnchanged=True,collisionReviewApproved=True,visualReviewApproved=True,actualAtomicLifecyclePassed=True,sourceGeometryChanges=0,governmentGeometryChanges=0,sourcePoseChanges=0,aiGeometryModelling=False,sourceEvidenceInterpretationUsedAI=True,nativeSupportCredit=False,reviewer='Codex ROOT')
        if number in EXCEPTIONS:
            common.update(policy=POLICY,**{k:True for k in COMMON_PROOFS},minimumCoveredGroundHKPD=s['foundationBase'],nativeTerrainDependencies=deps,renderProof=ref(BASE/batch/'render-proof.json'),evidence={
                'geometry':[ref(BASE/batch/'render-proof.json')], 'ground':[ref(BASE/batch/ground_name)],
                'collision':[ref(BASE/(P+'joint-basic-collision-v1-20261102')/'collision.json')],
                'jointScene':[ref(BASE/life_batch/'summary.json')],
                'desktop':[ref(BASE/east_batch/'1280/staged-browser.json')],
                'mobile':[ref(BASE/east_batch/'390/staged-browser.json')],
                'fallback':[ref(BASE/life_batch/'lifecycle/report.json')],
            })
        common['basis']='Exact unsurveyed BASIC fields and roof/body geometry are preserved. Existing renderer post bottoms or same-footprint below-base foundation volumes meet complete measured current ground; roofs remain clear. All ten changes pass simultaneous production collision probes and actual desktop/mobile group and neighbour lifecycle observations. No native support credit, surveyed offsets, new government geometry or architectural reconstruction. This resolves the raw base-only ground-gap proxy using the actual complete rendered parts, not a changed gap threshold.'
        path=out/(str(number)+'-qualified-foundation.json');save(path,common)
        update=dict(uid=uid,tile=str(tile.relative_to(ROOT/'3d-viewer')),tileSHA256=digest(tile.read_bytes()),before=b,foundationBase=s['foundationBase'],evidence=ref(path))
        if number in POSTS:update['proposal']=ref(BASE/batch/'proposal.json');illustrative.append(update)
        else:unsurveyed.append(update)
    save(out/'basic-plan-fragment.json',dict(illustrativeFoundations=illustrative,unsurveyedBasicFoundations=unsurveyed))
    resolved={**native,'basicFlags':[],'rawBasicFlags':native['basicFlags'],'resolvedByActualRenderedParts':sorted(expected),'qualification':'Raw base-only flags are retained verbatim. Seven roof-only and three exact unsurveyed forms are resolved by current full ground/roof proofs, unchanged source/body fields, all-ten collision and actual atomic/browser observations; their guarded plan fragment is mandatory for this resolution. Native full-mesh rows are reused byte-for-byte.'}
    save(out/'qualified-neighbours.json',resolved)
    physical=dict(requiredOriginalAssembly=sources,supportByUid={},exactTerrainReplacement=replacement,retainedNativeRegression=native,leaseResources=sorted(resources),terrainEdits=True,sourceGeometryChanges=0,sourcePoseChanges=0,sourceSpecificPhysicalInterpretationAccepted=True,completeNeighbourInterpretationAccepted=True,sourceBoundContinuationHintsProposed=False,rawFailuresPreserved=True,publication=False,installationApproved=False)
    physical.update(sourceSHA256ByUid=sources,completeFourWorldFoundations=foundation,completeCurrentNeighbourChecks=len(forms),identityProof={**{k:all(r['identityProof'][k]is True for r in bounded['rows'])for k in ['exactObjectId','exactBuildingCSUID','uniqueViewerMatch','identityAccepted']},'identifierScope':'current-viewer-record-and-frozen-native-match','currentProviderObjectIdExact':False})
    save(out/'ROOT-PHYSICAL-REVIEW.json',physical)
    review=dict(currentManifest=ref(manifest),sourceSHA256ByUid=sources,requiredOriginalAssembly=sources,activationGroupRequired=True,identityAccepted=True,sourceSpecificPhysicalInterpretationAccepted=True,completeNeighbourInterpretationAccepted=True,visualAcceptance=True,sourceGeometryChanges=0,sourcePoseChanges=0,aiGeometryModelling=False,sourceEvidenceInterpretationUsedAI=True,wholeLandmarkAccepted=False,sourceBoundContinuationHintsProposed=False,publication=False,installationApproved=False,basis='Accept these exact three immutable originals only as one atomic group. Preserve fresh provider OBJECTID differences, every raw footprint/foreign/canonical flag and all current source contacts. Existing foundation policy passes in four streams; canonical negatives are fully attributed to source walls/downward grade patches or exact root paths by the bounded source review. Authored source crossings alone add no engineering hold. Actual retained native regression, ten exact BASIC rendered-part resolutions, 43,050 simultaneous collision probes, desktop/mobile day/night, per-peer failure/Base-only/retry/eviction and all39 inspected exports are bound. Ordinary original BASIC owner fallbacks remain unchanged; rejected, unproposed continuation hints grant neither repair credit nor an extra publication gate. Existing publisher, global retained support, live and independent installed readback checks remain mandatory.')
    visual_doc=BASE/(P+'joint-foundation-private-preview-v3-20261102')
    images=sorted(p for width in [1280,390]for p in (visual_doc/str(width)).glob('staged-landsd-*-canvas.png'))
    assert len(images)==4*len(sources)
    reports=[visual_doc/str(width)/'staged-browser.json'for width in [1280,390]]
    for path in [*images,*reports]:
        assert digest(path.read_bytes())==pins[life_batch][str(path.relative_to(ROOT))];refs.append(path)
    review.update(imagesActuallyViewed=[ref(p)for p in images],browserReports=[ref(p)for p in reports],imageInspectionMethod='All12 original source exports were seen via four exact full-copy V3 sheets;12 additional east-view and11 lifecycle exports were inspected separately. Two east daytime PNGs were opened individually. This is not a claim of12 individual source-PNG opens.')
    save(out/'ROOT-SOURCE-REVIEW.json',review)
    assert reservations.owns(lease)and ref(manifest)==review['currentManifest']
    module('hkust_current_acceptance_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'bounded-current-hkust-three-original-and-ten-basic-foundation-review',list(dict.fromkeys(refs)),dict(uids=sorted(sources),sourceSHA256ByUid=sources,identityAccepted=True,sourceSpecificPhysicalInterpretationAccepted=True,completeNeighbourInterpretationAccepted=True,visualAcceptance=True,governmentGeometryChanges=0,sourcePoseChanges=0,aiGeometryModelling=False,installationApproved=False,publication=False))
if __name__=='__main__':main()
