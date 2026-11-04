"""Bind bounded Academy source/interface interpretation to exact current evidence."""
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
P='government-xl-academy69025-'
BATCH=P+'final-source-review-v1-20261029'
UID='landsd/69025:0'
SHA='75d1193ec409e8522705df1f262f647e12beda5c4e309f9905ca8ba7e5e88414'


def main():
    out=BASE/BATCH;assert not out.exists()
    refs=[Path(__file__)];pins={}
    def take(batch,name):
        path=BASE/batch/name
        if batch not in pins:
            pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
        assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))]
        refs.append(path);return read(path)
    def pinned_file(batch,path):
        if batch not in pins:
            pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
        assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))]
        refs.append(path);return dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes()))
    manifest=ROOT/'3d-viewer/city/data/manifest.json';manifest_ref=dict(path=str(manifest.relative_to(ROOT)),sha256=digest(manifest.read_bytes()));refs.append(manifest)
    identity=take(P+'after-fortune-current-v2-20261029-identity','69025:0/identity.json')
    assert identity['uid']==UID and identity['sourceSHA256']==SHA
    assert identity['reasons']==['fresh-current-spatial-bound:sourceExcessMaximumDistanceFromTargetM','full-source-maximum-extent']
    assert identity['originalOwnership']['sourceGraphVerified'] and identity['originalOwnership']['originalRootName']=='B354511570301063C0'
    assert identity['exactCurrentComponentRoute']['qualified'] and not identity['exactCurrentComponentRoute']['reasons']
    route=identity['exactCurrentComponentRoute'];official=route['official'];building=route['source']['building']
    assert official['objectId']==building['objectId']==69025
    assert official['buildingCSUID']==building['buildingCSUID']=='3545115703T20050430'
    tile=ROOT/'3d-viewer'/route['source']['tile']
    assert digest(tile.read_bytes())==route['source']['tileSHA256'];refs.append(tile)
    matches=[b for b in read(tile)['buildings']if b.get('objectId')==69025 or b.get('buildingCSUID')=='3545115703T20050430']
    assert matches==[building]
    current_identity_proof=dict(exactBuildingCSUID=True,exactObjectId=True,uniqueViewerMatch=True,identityAccepted=True)
    projection=identity['originalOwnership']['fullProjection']
    assert projection['exactObjectAndCSUID'] and projection['unrelatedIntersectingForms']==0 and projection['sourceExcessCoveredByUnrelatedFormsM2']==0
    assert identity['exactWholeCellCoverage']['covered'] and identity['exactWholeCellCoverage']['wholeOriginalFacesAccounted']==14462
    runtime=P+'nested-original-runtime-v1-20261029';selection=take(runtime,'selection.json.gz')
    assert selection['manifestSHA256']==manifest_ref['sha256']
    source=next(r for r in selection['rows']if r['uid']==UID)
    asset=ROOT/source['candidate']['path'];assert digest(asset.read_bytes())==SHA;refs.append(asset)
    old=next(r for r in take(P+'after-fortune-current-v2-20261029-attributes','attributes.json.gz')['rows']if r['uid']==UID)
    new=next(r for r in take(P+'nested-original-attributes-v1-20261029','attributes.json.gz')['rows']if r['uid']==UID)
    for key in ['sourceSHA256','completeOriginalIndex','completeLiteralWorldPosition','completeExplicitLeftAssociatedFloat32WorldPosition','completeExplicitBalancedFloat32WorldPosition']:
        assert old[key]==new[key],key
    foundation=take(P+'nested-four-world-foundations-v1-20261029','summary.json')
    assert foundation['establishedFoundationPolicyPassed'] and len(foundation['rows'])==4
    assert all(r['fullyBuriedTriangles']==r['fullyBuriedUpwardTriangles']==0 for r in foundation['rows'])
    account=take(P+'candidate-wall-rim-account-v1-20261029','summary.json')
    assert account['allFourConditionalLimitsPassed'] and account['sourceRoleReviewApproved'] is False
    wall_sets=[]
    for mode in ['original','literal','left','balanced']:
        cap=take(P+'nested-cap-paths-v1-20261029',mode+'.json.gz')
        partition=cap['completeGroundClearancePartition']
        assert partition['negativeNonWallFaces']==[] and len(partition['paths'])==153
        assert all(r['hasExactSharedEdgeClearCapPath']for r in partition['paths'])
        wall_sets.append(dict(mode=mode,sourceWorldSHA256=cap['sourceWorldSHA256'],wallFaces=sorted(r['sourceFace']for r in partition['paths'])))
    neighbours=take(P+'nested-neighbours-v1-20261029','summary.json')
    native=take(P+'nested-neighbours-v1-20261029','native-neighbour-checks.json')
    assert neighbours['forms']==30 and not neighbours['basicFlags']
    assert len(native['rows'])==len(native['resolved'])==len(neighbours['requiredNativeUids'])==28
    assert {r['uid']for r in native['rows']}==set(neighbours['requiredNativeUids'])
    assert all(r['passed']and r['terrain']['newlyWhollyBuried']==r['terrain']['newlyUpwardWhollyBuried']==0 for r in native['rows'])
    contacts=take(P+'current-native-contacts-v1-20261029','summary.json')
    lineage=take(P+'current-native-lineage-v1-20261029','summary.json')
    roles=take(P+'current-native-roles-v1-20261029','summary.json')
    assert lineage['currentManifestSHA256']==manifest_ref['sha256']
    assert len(contacts['rows'])==len(lineage['rows'])==1
    pair=contacts['rows'][0]
    assert pair['uid']==UID and pair['sourceSHA256']==SHA and pair['nativeUid']=='landsd/337830:0'
    assert pair['nativeSHA256']=='8481067a24cdeaff8d51fd880c03cd10dae3f5380ea49dcd93cbc53c03de68d8'
    models=[m for url in read(manifest)['officialModelCatalogues']for m in read(ROOT/'3d-viewer'/url)['models']]
    assert len(models)==7016 and next(m for m in models if m['uid']==pair['nativeUid'])==pair['rawCurrentNativeEntry']
    assert len(lineage['rows'][0]['modes'])==4 and all(r['allRepresentedCrossingsHaveOriginalFacetPairContacts']and r['transverseSegments']==142 for r in lineage['rows'][0]['modes'])
    assert all(r['roles']=={'source-edge-surface-contact':2,'surface-point-contact':4,'transverse-surface-crossing':142}for r in roles['rows'])
    scope=take(P+'after-fortune-current-v2-20261029-model-scope','summary.json')
    assert scope['currentManifestSHA256']==manifest_ref['sha256'] and scope['rows'][0]['currentFormsWithinTwoMetreRegion']==2
    staging=take(P+'canonical-terrain-staging-probe-v1-20261029','summary.json');assert staging['passed']and staging['publicFilesWritten']==0
    patch=take(P+'nested-binding-scope-v1-20261029','summary.json')
    browser=P+'nested-private-preview-v2-20261029';reports=[];images=[];retained_images=[]
    for width in [390,1280]:
        report=take(browser,str(width)+'/staged-browser.json');assert report['passed']and not report['errors']
        reports.append(dict(path=str((BASE/browser/str(width)/'staged-browser.json').relative_to(ROOT)),sha256=digest((BASE/browser/str(width)/'staged-browser.json').read_bytes())))
        views=[v for v in report['views']if 'time'in v]
        assert len(views)==2 and all(v['uid']==UID and v['sourceSHA256']==SHA and v['fullyFramed']and v['solidAppearance']and not v['fallbackFaces']and v['pick']==v['collision']==UID for v in views)
        assert len(report['retainedNativeOwnViews'])==4
        for time in [1500,2200]:
            images.append(pinned_file(browser,BASE/browser/str(width)/f'staged-landsd-69025-0-{width}-{time}-canvas.png'))
            for uid in ['337711','337830']:
                retained_images.append(pinned_file(browser,BASE/browser/str(width)/f'staged-retained-own-landsd-{uid}-0-{width}-{time}.png'))
    supplementary=[]
    for batch,name in [(P+'current-identity-views-v1-20261029','whole-source-plan.png'),(P+'current-native-contact-views-v1-20261029','337830:0-native-contact-context.png')]:
        supplementary.append(pinned_file(batch,BASE/batch/name))
    basis=('Exact government component graph and current object/CSUID route identify this complete authored campus component. The footprint-excess warnings cover the visible exterior spiral stair, access plaza and curved interface with the retained Academy block; no unrelated building projection is intersected. ROOT reviewed the full source plan, exact original contact diagram and actual day/night source and retained-model exports. The142 transverse surface pairs belong to the pre-existing authored campus junction in the original source arrays, which are identical before/after terrain replacement. They are accepted as the opaque architectural junction shown, not an engineering support dependency; neither component is moved, clipped or replaced. All153 negative source facets are lower wall surfaces with exact exposed-cap paths; their below-grade portions are retained. The bounded wall roles are approved for the unchanged four-world rim account; raw clearance and contact warnings remain in evidence. Full four-world foundations have zero buried triangles, all30 neighbour obligations pass, and all28 detailed assets remain unchanged. No blanket spatial, wall, collision or clearance exemption is created.')
    common=dict(uids=[UID],sourceSHA256ByUid={UID:SHA},reviewer='ROOT',currentManifest=manifest_ref,
                identityAccepted=True,sourceSpecificPhysicalInterpretationAccepted=True,
                completeNeighbourInterpretationAccepted=True,visualAcceptance=True,
                requiredOriginalAssembly=[UID],sourceGeometryChanges=0,sourcePoseChanges=0,
                aiGeometryModelling=False,sourceEvidenceInterpretationUsedAI=True,
                installationApproved=False,publication=False,qualification=basis)
    physical=dict(**common,basis=basis,identityProof=current_identity_proof,rawCachedIdentityProofRetained=identity['proof'],
                  completeFourWorldFoundations=True,completeCurrentNeighbourChecks=30,
                  currentNativeActors=7016,completeOriginalFaces=14462,
                  sourceWorldArraysPreserved=True,supportByUid={UID:[]},terrainCandidate=patch['candidate'],
                  approvedWallRolesByWorld=wall_sets,rawIdentityReasonsRetained=identity['reasons'],
                  rawOriginalContactPairsRetained=True,ordinaryFoundationRows=foundation['rows'],ordinaryRimRows=account['rows'],
                  noGlobalClearanceException=True,retainedNativeUids=neighbours['requiredNativeUids'])
    visual=dict(**common,browserReports=reports,imagesActuallyViewed=images,
                retainedImagesActuallyViewed=retained_images,supplementaryImagesActuallyViewed=supplementary,
                sourceRoleReviewApproved=True,physicalReview=dict(path=str((out/'ROOT-PHYSICAL-REVIEW.json').relative_to(ROOT))))
    out.mkdir();save(out/'ROOT-PHYSICAL-REVIEW.json',physical)
    visual['physicalReview']['sha256']=digest((out/'ROOT-PHYSICAL-REVIEW.json').read_bytes());save(out/'ROOT-SOURCE-REVIEW.json',visual)
    result=dict(uids=[UID],sourceSHA256ByUid={UID:SHA},identityAccepted=True,sourceSpecificPhysicalInterpretationAccepted=True,
                completeNeighbourInterpretationAccepted=True,visualAcceptance=True,installationApproved=False,publication=False,
                noOriginalGeometryOrPoseEdits=True,nextStep='Guarded staging with exact nested parent replacement, then live checks and installed ledger.')
    module('academy_final_source_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-original-campus-component-interface-and-lower-wall-source-review',refs,result)


if __name__=='__main__':main()
