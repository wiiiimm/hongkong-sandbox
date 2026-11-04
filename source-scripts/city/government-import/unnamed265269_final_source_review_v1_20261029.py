"""Review one immutable source and its exact conditional estimated canopy."""
from pathlib import Path
import json
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
P='government-xl-unnamed265269-'
BATCH=P+'final-source-review-v1-20261029'
CURRENT=P+'after-academy-current-v1-20261029'
UID='landsd/265269:0';BASIC='landsd/265270:0'
SHA='0adf753f5832d3598fd1d99c3700b704e33de74aa97c4d4f868ba68c6cb445da'


def formsha(form):return digest(json.dumps(form,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())


def main():
    out=BASE/BATCH;assert not out.exists();refs=[Path(__file__)];pins={}
    def take(batch,path):
        if batch not in pins:
            pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
        assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    def doc(batch,name):return take(batch,BASE/batch/name)
    manifest=ROOT/'3d-viewer/city/data/manifest.json';manifest_ref=dict(path=str(manifest.relative_to(ROOT)),sha256=digest(manifest.read_bytes()));refs.append(manifest)
    identity=doc(CURRENT+'-identity','265269:0/identity.json');route=identity['exactCurrentComponentRoute']
    assert identity['sourceSHA256']==SHA and identity['originalOwnership']['sourceGraphVerified']
    assert identity['originalOwnership']['originalRootName']=='B109882541501063C0'and route['qualified']and not route['reasons']
    building=route['source']['building'];official=route['official']
    assert official['objectId']==building['objectId']==265269 and official['buildingCSUID']==building['buildingCSUID']=='1098825415T20180117'
    tile=ROOT/'3d-viewer'/route['source']['tile'];assert digest(tile.read_bytes())==route['source']['tileSHA256'];refs.append(tile)
    assert [b for b in read(tile)['buildings']if b.get('objectId')==265269 or b.get('buildingCSUID')=='1098825415T20180117']==[building]
    feature=doc(P+'canopy-primary-feature-packet-v2-20261029','summary.json')
    live_owner=feature['officialRecords'][UID];assert live_owner['BuildingCSUID']==building['buildingCSUID']and live_owner['BuildingID']==1810170752 and live_owner['OBJECTID']==264848 and live_owner['Status']=='Active'
    assert feature['sourceSHA256']==SHA and feature['sourceModelId']=='B109882541501063C0'
    canopy=doc(P+'private-canopy-review-v2-20261029','ROOT-PRIVATE-CANOPY-REVIEW.json');assert canopy['sourceSHA256']==SHA and canopy['privateCanopyExperimentApproved']and canopy['currentManifest']==manifest_ref
    forms=doc(CURRENT+'-model-scope','265269:0-forms.json.gz');byuid={r['building']['uid']:r['building']for r in forms}
    assert len(forms)==6 and byuid[UID]==building and byuid[BASIC]==canopy['exactBasicForm']
    b=byuid[BASIC];assert b['structureType']=='Open-sided Structure'and b['heightSource']=='estimated'and b['baseHeightHKPD']is None and b['topHeightHKPD']is None
    for r in forms:
        path=ROOT/'3d-viewer'/r['tile'];assert digest(path.read_bytes())==r['tileSHA256'];refs.append(path)
        assert next(q for q in read(path)['buildings']if q['uid']==r['building']['uid'])==r['building']
    scope=doc(CURRENT+'-model-scope','summary.json');assert scope['currentManifestSHA256']==manifest_ref['sha256']and scope['rows'][0]['currentNativeActorsChecked']==7017
    assert not scope['rows'][0]['nearbyNativeActors']
    grade=doc(P+'exact-current-grade-rebind-v1-20261029','summary.json');assert grade['currentManifestSHA256']==manifest_ref['sha256']and grade['sourceWorldArraysExactlyUnchanged']and grade['completeDrawnGroundArraysExactlyUnchanged']and grade['priorBoundedLowerRoleReviewApplicable']and grade['allFourCurrentFoundationsPassed']
    foundation=doc(CURRENT+'-foundation-265269-0','summary.json');assert foundation['establishedFoundationPolicyPassed']and len(foundation['rows'])==4
    assert all(r['fullyBuriedTriangles']==2 and r['fullyBuriedUpwardTriangles']==0 for r in foundation['rows'])
    foreign=doc(P+'after-academy-foreign-contacts-v1-20261029','summary.json');assert foreign['foreignPairs']==5
    assert {r['foreignUid']for r in foreign['rows']}==set(byuid)-{UID}
    for r in foreign['rows']:
        assert len(r['modes'])==5
        for m in r['modes']:
            if r['foreignUid']==BASIC:assert m['positiveContactPairs']==(24 if m['mode']=='before-basic'else 28)
            else:assert m['positiveContactPairs']==0
    lifecycle_batch=P+'canopy-lifecycle-v1-20261029';lifecycle=doc(lifecycle_batch,'summary.json');lifecycle_report=doc(lifecycle_batch,'report.json')
    assert lifecycle['passed']and lifecycle['sourceSHA256']==SHA and lifecycle_report['passed']and not lifecycle_report['pageErrors']
    lifecycle_cases=lifecycle_report['cases'];assert {(r['width'],r['failedUid'])for r in lifecycle_cases}=={(1280,None),(390,UID)}
    for r in lifecycle_cases:
        assert r['completeGroupEvicted']and r['baseOnlyRestoredCompleteGroup']and not r['audit']['violations']
        phases={v['phase']:v for v in r['canopyLifecycle']}
        assert len(phases)==len(r['canopyLifecycle'])and {'original-active','base-only','auto-restored','evicted-return-base-only'}<=set(phases)
        assert all(v['ownerActive']==(name in ['original-active','auto-restored'])and v['basicCanopyVisible']==(name not in ['original-active','auto-restored'])for name,v in phases.items())
        if r['failedUid']:assert r['failureKeptAllBasics']and 'failed-download'in phases
    preview=P+'after-academy-private-preview-v2-20261029';reports=[];images=[]
    for width in [390,1280]:
        path=BASE/preview/str(width)/'staged-browser.json';r=take(preview,path);assert r['passed']and not r['errors']
        reports.append(dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes())))
        views=[v for v in r['views']if 'time'in v];assert len(views)==2
        assert all(v['uid']==UID and v['sourceSHA256']==SHA and v['fullyFramed']and v['solidAppearance']and not v['fallbackFaces']and v['pick']==v['collision']==UID for v in views)
        for time in [1500,2200]:
            p=BASE/preview/str(width)/f'staged-landsd-265269-0-{width}-{time}-canvas.png';take(preview,p)if False else None
            assert digest(p.read_bytes())==pins[preview][str(p.relative_to(ROOT))];refs.append(p);images.append(dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes())))
    runtime=CURRENT+'-runtime';selection=doc(runtime,'selection.json.gz');assert selection['manifestSHA256']==manifest_ref['sha256']
    selected=next(r for r in selection['rows']if r['uid']==UID);asset=ROOT/selected['candidate']['path'];assert digest(asset.read_bytes())==SHA;refs.append(asset)
    basis=('Exact government graph/modelId and stable CSUID identify the complete unnamed original; no landmark name is invented. The pinned viewer object265269 remains stable while the live ActiveTower record is object264848 with the same CSUID/BuildingID; that reindexing is recorded explicitly. ROOT reviewed the complete current desktop/mobile day/night exports and prior source/canopy diagrams. The authored roof bands, perimeter overhangs and attached higher canopy belong to this exact original. Its raw24.7635m extent and174.378m2 overlap warnings remain recorded. Only the duplicate unsurveyed open-sided BASIC canopy265270 is conditionally hidden. Its roof/post coverage shortfalls are preserved verbatim; no coverage percentage is treated as an approval rule or a structural-support proof. The other four BASIC neighbours remain unchanged and have zero positive surface-contact pairs. All7017 detailed actors are strictly outside this local source region. Complete current source/ground arrays exactly match the reviewed lower-wall/two-downward-closure witnesses; raw88low-face warnings and8literal shared-edge warnings remain recorded. This is bounded original-source/opaque lower-surface and duplicate-feature interpretation, not an engineering support claim or a global clearance exception. Base-only/failure/eviction restore the exact BASIC canopy. Original bytes, pose and scale are untouched.')
    common=dict(uids=[UID],sourceSHA256ByUid={UID:SHA},reviewer='ROOT',currentManifest=manifest_ref,
                identityAccepted=True,sourceSpecificPhysicalInterpretationAccepted=True,
                completeNeighbourInterpretationAccepted=True,visualAcceptance=True,
                requiredOriginalAssembly=[UID],sourceGeometryChanges=0,sourcePoseChanges=0,
                aiGeometryModelling=False,sourceEvidenceInterpretationUsedAI=True,installationApproved=False,publication=False,qualification=basis)
    replacement=dict(sourceUid=UID,basicUid=BASIC,sourceSHA256=SHA,sourceFormSHA256=formsha(building),basicFormSHA256=formsha(b),onlyWhileExactOwnerActive=True,approved=True)
    physical=dict(**common,basis=basis,identityProof=dict(exactBuildingCSUID=True,exactObjectId=True,uniqueViewerMatch=True,identityAccepted=True),
                  pinnedViewerObjectId=265269,liveProviderObjectId=264848,stableBuildingCSUID=building['buildingCSUID'],rawIdentityDiagnosticsRetained=identity['reasons'],
                  completeFourWorldFoundations=True,completeCurrentNeighbourChecks=6,currentNativeActors=7017,completeOriginalFaces=11663,
                  sourceWorldArraysPreserved=True,supportByUid={UID:[]},terrainCandidate=None,ordinaryFoundationRows=foundation['rows'],ordinaryRimRows=grade['rows'],
                  conditionalCanopyReplacement=replacement,exactBasicCanopy=b,retainedBasicUids=sorted(set(byuid)-{UID,BASIC}),globalClearanceExceptionsCreated=0)
    visual=dict(**common,browserReports=reports,imagesActuallyViewed=images,conditionalCanopyReplacement=replacement,
                canopyLifecycleReport=dict(path=str((BASE/lifecycle_batch/'report.json').relative_to(ROOT)),sha256=digest((BASE/lifecycle_batch/'report.json').read_bytes())),
                canopyFeatureReview=dict(path=str((BASE/(P+'private-canopy-review-v2-20261029')/'ROOT-PRIVATE-CANOPY-REVIEW.json').relative_to(ROOT)),sha256=digest((BASE/(P+'private-canopy-review-v2-20261029')/'ROOT-PRIVATE-CANOPY-REVIEW.json').read_bytes())))
    out.mkdir();save(out/'ROOT-PHYSICAL-REVIEW.json',physical);save(out/'ROOT-SOURCE-REVIEW.json',visual)
    result=dict(uids=[UID],sourceSHA256ByUid={UID:SHA},identityAccepted=True,sourceSpecificPhysicalInterpretationAccepted=True,
                completeNeighbourInterpretationAccepted=True,visualAcceptance=True,conditionalCanopyReplacementApproved=True,
                installationApproved=False,publication=False,sourceGeometryChanges=0,nextStep='Guarded standalone no-terrain conditional-canopy staging and live installation; preserve all existing global support guards.')
    module('unnamed_final_source_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-unnamed-original-source-lower-role-and-conditional-canopy-review',refs,result)


if __name__=='__main__':main()
