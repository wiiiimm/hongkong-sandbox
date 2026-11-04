"""Bind ROOT's exact three-source Miu Fat interpretation and inspected preview.
No publication. Original source negatives remain in their immutable receipts.
"""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from miu_fat_original_catalogue_scope_v1_20261024 import SOURCES,PRIMARY,HALL,GATE,SUPPORTS,verify_metadata
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-next-repairs-miu-fat-original-source-review-v1-20261024'
P='government-xl-next-repairs-miu-fat-';RUNTIME=P+'three-current-runtime-v1-20261024';BROWSER=P+'unapproved-original-preview-v2-20261024';HOME='landsd/6393:0';SMALL='landsd/233638:0'

def main():
    out=BASE/BATCH;assert not out.exists();refs=[Path(__file__),HERE/'miu_fat_original_catalogue_scope_v1_20261024.py'];pins={}
    def take(batch,path):
        if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
        assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    selection=take(RUNTIME,BASE/RUNTIME/'selection.json.gz');assert {r['uid']:r['sourceSHA256']for r in selection['rows']}==SOURCES
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256'];refs.append(manifest)
    for row in selection['rows']:
        path=ROOT/row['candidate']['path'];assert digest(path.read_bytes())==SOURCES[row['uid']];refs.append(path)
        tile=ROOT/'3d-viewer'/row['source']['tile'];assert digest(tile.read_bytes())==row['source']['tileSHA256'];assert next(b for b in read(tile)['buildings']if b['uid']==row['uid'])==row['source']['building'];refs.append(tile)
    for label in ['current-prephysical','small-podium-prephysical']:
        batch=P+label+'-v1-20261024';s=take(batch,BASE/batch/'summary.json');assert s['status']=='prephysical-evidence-complete-awaiting-identity-and-browser'
        assert {r['phase']for r in s['completed']} >= {'foundations','plots','boundary','continuous','coverage','rims'}
    support=take(P+'lin-wah-original-support-v1-20261024',BASE/(P+'lin-wah-original-support-v1-20261024')/'summary.json');assert support['allFourModesPassed']and support['sourceSHA256ByUid']=={u:SOURCES[u]for u in [PRIMARY,HALL]}
    assert len(support['rows'])==4 and all(r['support']['passed']and r['support']['samples']==r['support']['strictContacts']==441 and not r['support']['unresolved']for r in support['rows'])
    rawIdentity=[];identity=P+'three-current-identity-v1-20261024'
    for row in selection['rows']:
        r=take(identity,BASE/identity/(row['uid'].split('/')[1]+'/identity.json'))
        assert r['sourceSHA256']==SOURCES[row['uid']]and r['exactCurrentComponentRoute']['qualified']and r['originalOwnership']['sourceGraphVerified']and r['exactWholeCellCoverage']['covered']
        assert r['originalOwnership']['originalRootName']==row['modelId'];rawIdentity.append(dict(uid=row['uid'],rawPath=str((BASE/identity/(row['uid'].split('/')[1]+'/identity.json')).relative_to(ROOT))))
    rawSummary=take(identity,BASE/identity/'summary.json');allowed={'fresh-current-spatial-bound:sourceExcessCoveredByUnrelatedFormsM2','fresh-current-spatial-bound:sourceExcessMaximumDistanceFromTargetM','full-source-maximum-extent','full-source-unrelated-overlap'}
    assert all(set(r['reasons'])<=allowed for r in rawSummary['rows'])
    scopeName=P+'three-current-model-scope-v1-20261024';scope=take(scopeName,BASE/scopeName/'summary.json');assert scope['currentManifestSHA256']==selection['manifestSHA256']and all(not r['nearbyNativeActors']for r in scope['rows'])
    forms={}
    for r in scope['rows']:
        for item in take(scopeName,BASE/scopeName/(r['uid'].split('/')[1]+'-forms.json.gz')):forms[item['building']['uid']]=item
    contactsName=P+'three-current-basic-contacts-v1-20261024';contacts=take(contactsName,BASE/contactsName/'summary.json');assert contacts['foreignPairs']==21
    interfaces=[]
    for pair in contacts['rows']:
        assert pair['uid']in SOURCES
        if pair['foreignUid']in SOURCES:continue
        for measured in pair['modes']:
            if measured['mode']=='before-basic':continue
            assert measured['mode']in ['original','literal','leftF32','balancedF32']
            if measured['positiveContactPairs']:
                assert (pair['uid'],pair['foreignUid'],measured['positiveContactPairs'])in [(PRIMARY,GATE,24),(SMALL,HOME,22)]
                interfaces.append(dict(uid=pair['uid'],foreignUid=pair['foreignUid'],measurement=measured))
    assert len(interfaces)==8
    # The exact elderly-home original is context evidence, not an installation target.
    contextName=P+'small-elderly-original-pair-v1-20261024';context=take(contextName,BASE/contextName/'summary.json');assert context['completePairExamined']and context['contactDimensions']=={'1':56}
    assert next(r for r in context['rows']if r['uid']==SMALL)['sourceSHA256']==SOURCES[SMALL]
    assert next(r for r in context['rows']if r['uid']==HOME)['sourceSHA256']=='8b17999f822b3eae9260f475a7d99daf127c21d813e5eb76eaf5f276033c4107'
    for label in ['main-small-original-pair','main-hall-original-pair']:
        batch=P+label+'-v1-20261024';c=take(batch,BASE/batch/'summary.json');assert c['completePairExamined']
    coverageName=P+'gateway-coverage-review-v1-20261024';coverage=take(coverageName,BASE/coverageName/'gateway-coverage-review.json')
    local=HERE/'local'/BROWSER;cat=take(BROWSER,local/'catalogue.json');assert verify_metadata(cat['models'],coverage)
    images=[];reports=[];viewNotes=[]
    def ref(path):return dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes()))
    for width in [1280,390]:
        reportPath=BASE/BROWSER/str(width)/'staged-browser.json';report=take(BROWSER,reportPath);reports.append(ref(reportPath));assert report['passed']and not report['errors']
        views=[v for v in report['views']if 'time'in v];assert len(views)==6
        assert all(v['fullyFramed']and v['solidAppearance']and not v['fallbackFaces']and v['pick']==v['collision']==v['uid']and v['sourceSHA256']==SOURCES[v['uid']]for v in views)
        for v in views:
            path=reportPath.parent/v['file'];assert digest(path.read_bytes())==pins[BROWSER][str(path.relative_to(ROOT))];refs.append(path);images.append(ref(path))
            if v['uid']==PRIMARY:assert v['suppressed'][GATE]['suppressed']and not v['suppressed'][GATE]['detailedActive']
            if v['uid']==SMALL:assert v['retained'][HOME]['loaded']and not v['retained'][HOME]['hidden']and not v['retained'][HOME]['detailedActive']
        assert any({m['uid']for m in j['models']}==set(SOURCES)and all(m['active']and m['visible']and not m['fallbackFaces']for m in j['models'])for j in report['jointViews'])
        if width==390:
            failures=[v for v in report['views']if v.get('phase')=='failed-download'];assert {v['uid']for v in failures}==set(SOURCES)
            assert next(v for v in failures if v['uid']==PRIMARY)['suppressedBasicsRestored'][GATE]is True
        for time in ['1500','2200']:
            path=BASE/BROWSER/('ROOT-inspection-'+str(width))/(str(width)+'-'+time+'.jpg');assert path.is_file();refs.append(path);viewNotes.append(ref(path))
    # This record states the scope of actual ROOT inspection; it is not an automated visual decision.
    interpretation=dict(reviewer='ROOT',sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,sourceGeometryChanges=0,sourcePoseChanges=0,reviewedInstallationTargets=sorted(SOURCES),contextOnlyOriginals=[HOME],sourceRole='Exact government main complex with entrance/stairs, named lower access podium and Lin Wah Hall lotus crown. Provider root/GeoRef/type/current CSUID/ObjectID route and complete source graph bind each original. Wide roofs, stairs, facade returns and the authored access podium extend beyond approximate GIS footprints; those raw projection flags remain archived. This interpretation is limited to these exact three hashes and current forms.',jointRole='Main/Hall contacts are the authored upper-floor/podium construction interface, supported by 441/441 unchanged strict contacts in every coordinate stream. Main/access-podium contacts are original adjoining same-named compound surfaces. The retained elderly-home basic facade intersects only the access podium at its authored side connection; all 22 retained-basic contacts per world are preserved, with the exact original elderly-home source and its 56 original interface contacts as independent connection context. No source is moved, clipped, simplified or assigned new engineering dimensions.',gatewayRole='The estimated 3m flat canopy record duplicates the entrance gateway already contained in the main original. Suppress only that exact fallback while the main source is active; the mobile failed-load test proves it restores. Keep the source record and all terrain.',imagesActuallyViewed=images,inspectionPreviewsActuallyViewed=viewNotes,visualFinding='ROOT inspected all12 actual source exports through four complete-frame contact sheets and the full desktop main-source PNG. The original stairs, connecting podium and lotus crown are visible and coherent; no artificial window shader is added. Mobile main/access-podium own-source images intentionally precede the Hall failed-download retry, so the upper Hall coarse block is visible there. Final mobile Hall images and explicit joint activation show the original crown with all3 sources active. Do not claim every earlier mobile own-source image already shows all3 upgraded sources.')
    save(out/'ROOT-EXPORT-INSPECTION.json',interpretation)
    common=dict(sourceSHA256ByUid=SOURCES,currentManifest=ref(manifest),sourceSpecificPhysicalInterpretationAccepted=True,completeNeighbourInterpretationAccepted=True,identityAccepted=True,identityProof=dict(exactObjectId=True,exactBuildingCSUID=True,uniqueViewerMatch=True,identityAccepted=True),completeFourWorldSourceClearance=True,qualifiedFourWorldSourceClearance=True,completeFourWorldCanonicalRetainedBasicSupport=True,retainedBasicSupportDependencies=[],retainedCurrentBasicSupportUids=[],nativeSupportByUid=SUPPORTS,completeCurrentNeighbourChecks=len(forms),terrainEdits=False,sourceGeometryChanges=0,sourcePoseChanges=0,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,leaseResources=['building:'+uid for uid in sorted(set(forms)|set(SOURCES)|{GATE,HOME})],rawIdentityNegatives=rawIdentity,retainedInterfaceMeasurements=interfaces,browserReports=reports,imagesActuallyViewed=images,inspectionPreviewsActuallyViewed=viewNotes,visualAcceptance=True,sourceRoleReview=ref(out/'ROOT-EXPORT-INSPECTION.json'),publication=False,installationApproved=False,qualification='Exact-source physical/source-role and inspected private-preview qualification only. All generic current-map, retained-basic support, native dependency, atomic publication/live browser/installed-ledger gates still required. No other compound, source SHA, form, gateway, contact or terrain exception is approved.')
    save(out/'ROOT-PHYSICAL-REVIEW.json',common);save(out/'ROOT-SOURCE-REVIEW.json',common)
    module('miu_source_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-three-original-compound-source-role-and-inspected-preview-review',list(dict.fromkeys(refs)),dict(uids=sorted(SOURCES),sourceSHA256ByUid=SOURCES,sourceSpecificPhysicalInterpretationAccepted=True,identityAccepted=True,visualAcceptance=True,installationApproved=False,contextOnlyOriginals=[HOME],qualification=common['qualification']))

if __name__=='__main__':main()
