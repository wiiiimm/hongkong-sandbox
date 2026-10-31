"""Bind Plaza's exact original, existing foundation policy and inspected exports."""
from pathlib import Path
import numpy as np
from run import ROOT, HERE, read, save, digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles

BASE=ROOT/'docs/astra-city/government-import'
P='government-xl-plaza-hollywood-after-greenfield-'
UID='landsd/323185:0'
SHA='62159e4ff553517f922ca2652471c9e50103bccdf907e7ea32602b6224103b12'
BATCH=P+'final-source-review-v1-20261025'

def main():
    out=BASE/BATCH
    assert not out.exists()
    refs=[Path(__file__)];pins={}
    def take(batch,name='summary.json'):
        if batch not in pins:
            _,pins[batch]=authenticate(BASE/batch);refs.append(BASE/batch/'result.json')
        path=BASE/batch/name
        assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))]
        refs.append(path);return read(path)
    selection=take(P+'seam-runtime-v2-20261025','selection.json.gz')
    assert len(selection['rows'])==1
    row=selection['rows'][0];assert row['uid']==UID and row['sourceSHA256']==SHA and row['triangles']==10228
    asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==SHA;refs.append(asset)
    assert row['candidate']['entry']['rootTranslation']==[-834500,0,816500] and row['candidate']['entry'].get('verticalPlacementOffsetHKPD',0)==0
    identity=take(P+'identity-v1-20261025','323185:0/identity.json')
    assert identity['sourceSHA256']==SHA and not identity['passed']
    assert identity['originalOwnership']['sourceGraphVerified'] and identity['originalOwnership']['originalRootName']=='B388342241501063C0'
    route=identity['exactCurrentComponentRoute'];assert route['qualified'] and route['official']['objectId']==323185 and route['official']['buildingCSUID']=='3883422415T20050430'
    assert identity['exactWholeCellCoverage']['covered'] and identity['exactWholeCellCoverage']['wholeOriginalFacesAccounted']==10228
    spatial=identity['freshCurrentIdentity'];assert spatial['exactObjectAndCSUID'] and spatial['targetCoveredBySourceProjection']>=.95 and spatial['sourceExcessFraction']<=.10 and spatial['sourceExcessCoveredByUnrelatedFormsM2']<=1
    assert 17.28<spatial['sourceExcessMaximumDistanceFromTargetM']<17.29
    for name in ['whole-source-plan.png','whole-source-perspectives.png']:
        take(P+'identity-views-v1-20261025','summary.json');path=BASE/(P+'identity-views-v1-20261025')/name
        assert digest(path.read_bytes())==pins[P+'identity-views-v1-20261025'][str(path.relative_to(ROOT))];refs.append(path)
    permit=take(P+'complete-permit-v1-20261025');assert permit['permit']=='NK11/98' and not permit['missingSelectedCSUIDs']
    assert '3888022455P20060311' in permit['completePermitCSUIDs']
    attrs=take(P+'attributes-v1-20261025','attributes.json.gz');assert attrs['startEndAllInputsVerified'] and attrs['rows'][0]['sourceSHA256']==SHA
    foundation=take(P+'seam-foundation-context-v2-20261025');assert foundation['establishedFoundationPolicyPassed'] and len(foundation['rows'])==4
    for r in foundation['rows']:
        assert r['completeTerrainTriangles']==r['triangles']==10228 and r['fullyBuriedTriangles']==7 and r['fullyBuriedUpwardTriangles']==0 and r['fullyBuriedAreaFraction']<=.001
        take(P+'seam-foundation-context-v2-20261025',r['mode']+'.json')
    ground=take(P+'seam-complete-ground-v2-20261025');assert len(ground['rows'])==4
    for r in ground['rows']:
        assert r['negativeNonWallFaces']==[8844,8845] and len(r['exactAffectedFaces'])==141 and not r['compoundCapPathsPassed']
        cap=take(P+'seam-complete-ground-v2-20261025',r['mode']+'-cap-paths.json.gz')['proof']
        assert len(cap['paths'])==139 and all(x['hasExactSharedEdgeClearCapPath'] for x in cap['paths'])
    tri=decode_original_world_triangles(asset.read_bytes())
    for i in [8844,8845]:
        n=np.cross(tri[i,1]-tri[i,0],tri[i,2]-tri[i,0]);assert n[1]/np.linalg.norm(n)==-1
    views=take(P+'seven-face-views-v2-20261025');assert views['displayedExactNegativeFaces']==[8819,8830,8831,8832,8833,8844,8845]
    for r in views['regions']:
        path=ROOT/r['image'];assert digest(path.read_bytes())==r['imageSHA256'];refs.append(path)
    continuous=take(P+'seam-continuous-v2-20261025');assert continuous['rows'][0]['otherAffectedFaces']==[8844,8845] and continuous['rows'][0]['upwardContinuousMinimumGapM']>=-.5
    coverage=take(P+'exact-coverage-v2-20261025');assert not coverage['rows'][0]['stillUncoveredFaces']
    patch=take(P+'seam-terrain-v2-20261025');assert patch['status']=='private-terrain-validator-passed' and patch['terrainTriangles']==3800 and patch['seamCover']['unchangedOriginalTerrainTriangles']==3585
    scope=take(P+'seam-scope-v2-20261025','scope.json');forms={f['uid']:f for f in take(P+'seam-scope-v2-20261025','form-obligations.json.gz')}
    assert scope['currentNativeActors']==6942 and not scope['touchingNativeUids'] and not scope['terrainContacts'] and scope['positiveAreaTerrainOverlaps']==0
    model=take(P+'model-scope-v1-20261025');assert len(model['rows'])==1 and not model['rows'][0]['nearbyNativeActors'] and model['rows'][0]['currentNativeActorsChecked']==6942
    for item in take(P+'model-scope-v1-20261025','323185:0-forms.json.gz'):
        f=item['building']
        if f['uid'] in forms:assert forms[f['uid']]==f
        forms[f['uid']]=f
    assert len(forms)==31 and forms['landsd/228619:0']['buildingCSUID']=='3888022455P20060311'
    neighbours=take(P+'seam-neighbours-v2-20261025');assert neighbours['forms']==31 and not neighbours['flagged'] and neighbours['ordinaryFlagged']==0
    foreign=take(P+'foreign-contacts-v1-20261025');assert len(foreign['rows'])==13
    assert {r['foreignUid'] for r in foreign['rows'] if any(m['positiveContactPairs'] for m in r['modes'] if m['mode']!='before-basic')}=={'landsd/228619:0'}
    browser=P+'unapproved-browser-v3-20261025';reports=[];images=[]
    for width in [390,1280]:
        report=take(browser,str(width)+'/staged-browser.json');assert report['passed'] and not report['errors']
        for v in [v for v in report['views'] if 'time' in v]:
            assert v['fullyFramed'] and v['solidAppearance'] and v['active'] and v['visible'] and not v['fallbackFaces'] and v['pick']==v['collision']==UID and v['sourceSHA256']==SHA
            path=BASE/browser/str(width)/v['file'];key=str(path.relative_to(ROOT));assert digest(path.read_bytes())==pins[browser][key];refs.append(path)
            images.append(dict(uid=UID,width=width,time=v['time'],path=key,sha256=pins[browser][key]))
        assert report['jointViews'] and all(j['models'][0]['uid']==UID and j['models'][0]['sourceSHA256']==SHA and j['models'][0]['active'] for j in report['jointViews'])
        if width==390:assert any(v.get('phase')=='failed-download' and v['fallbackRetained'] for v in report['views'])
        path=BASE/browser/str(width)/'staged-browser.json';reports.append(dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes())))
    assert len(images)==4 and {(x['width'],x['time']) for x in images}=={(w,t) for w in [390,1280] for t in ['15:00','22:00']}
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256'];refs.append(manifest)
    resources=sorted({('building:' if u.startswith('landsd/') else 'source-form:')+u for u in forms}|{'terrain:city/data/terrain.json'})
    result=dict(uids=[UID],sourceSHA256ByUid={UID:SHA},requiredOriginalAssembly={UID:SHA},supportByUid={},retainedNativeUids=[],reviewer='ROOT',identityAccepted=True,identityProof=dict(exactObjectId=True,exactBuildingCSUID=True,uniqueViewerMatch=True,identityAccepted=True),currentManifest=dict(path=str(manifest.relative_to(ROOT)),sha256=digest(manifest.read_bytes())),sourceSpecificPhysicalInterpretationAccepted=True,completeNeighbourInterpretationAccepted=True,completeFourWorldFoundations=True,completeCurrentNeighbourChecks=31,totalNeighbourForms=31,terrainAffectedForms=31,leaseResources=resources,visualAcceptance=True,imagesActuallyViewed=images,browserReports=reports,originalSourceReviewAccepted=True,rawExtentGateStillFalse=True,rawSevenBuriedFacetsPreserved=True,rawCapAggregateStillFalse=True,sourceGeometryChanges=0,sourcePoseChanges=0,aiGeometryModelling=False,sourceEvidenceInterpretationUsedAI=True,installationApproved=False,observations=[
        'Accept only this complete immutable registered government body. Exact graph/root, current unique ObjectID/CSUID route, whole GeoRef cell,99.9156percent target coverage and0.1511m2 unrelated excess establish numeric identity. ROOT inspected both complete source diagrams and four final actual browser exports. Preserve17.2854m source-owned extension and failed generic10m extent predicate. This bounded source-specific decision does not widen the generic limit or claim every authored extension is architecturally complete.',
        'Existing xl-final-script-pass foundation policy passes all4worlds: complete10228faces, zero upward burial and seven below-grade basal facets10.3030m2/0.000201273 of source area below0.001limit. Preserve the stricter zero-any-burial helper failure; it is not the established general policy. Do not alter original geometry or excavate solely to expose downward closures.',
        'All139affected wall-like facets have exact shared-edge paths to clear original caps. Two other negatives8844/8845are downward-facing basal closures, signed normalY=-1. ROOT inspected both final seven-facet diagrams; five lower wall facets and two closures remain below grade. Raw aggregate cap/exposed-vertex failures stay false; no watertightness or structural engineering claim.',
        'Final3800triangle private terrain retains3585prior triangles plus215boundedFloat32seam covers. Exact source coverage and all31current neighbours pass. Sole positive external BASICcontact228619is the separately retained podium in exact common permitNK11/98. Preserve it and all five BASIC residential towers; no suppression, borrowed BASIC support credit or zero-interpenetration requirement.',
        'V1all4actualexports rejected for foreground tower occlusion. V2navigation failed because shared4176server stopped; no source acceptance. V3uses separate loopback4177with identicalV12checks and explicit test-origin support; all4actualexports inspected and readable from opposite side, all surroundings retained. Original night material is dark. Guarded live installation and fresh4exports/full6942oldassets/full521/globalBASICreadback still required.'
    ])
    save(out/'ROOT-PHYSICAL-REVIEW.json',result);save(out/'ROOT-SOURCE-REVIEW.json',result)
    refs.extend([HERE/'original_four_world_foundation_context_v1_20261025.py',HERE/'xl-final-script-pass.py',HERE/'exact_packed_world_geometry_20261009.py'])
    module('plaza_final_source_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'bounded-original-plaza-source-role-physical-and-visual-review',list(dict.fromkeys(refs)),result)

if __name__=='__main__':main()
