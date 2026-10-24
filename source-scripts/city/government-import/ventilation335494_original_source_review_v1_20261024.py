"""Bounded unchanged ventilation source, lower-wall and actual-export review."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from original_independent_model_only_contract_v1_20261024 import verify_metadata,verify_native_scope
from ventilation335494_original_identity_review_v1_20261024 import UID,SHA
BASE=ROOT/'docs/astra-city/government-import';P='government-xl-ventilation335494-'
BATCH=P+'source-review-v1-20261024';BROWSER=P+'unapproved-preview-v1-20261024'
RUNTIME='government-xl-next-four-after-hanford-runtime-v1-20261024';SCOPE='government-xl-next-four-after-hanford-model-scope-v1-20261024';NATIVE='government-xl-next-four-after-hanford-native-contacts-v2-20261024'
SOURCES={UID:SHA};RETAINED={'landsd/93826:0','landsd/257115:0'}


def main():
    out=BASE/BATCH;assert not out.exists();refs=[Path(__file__),HERE/'original_independent_model_only_contract_v1_20261024.py',HERE/'ventilation335494_original_identity_review_v1_20261024.py'];pins={}
    def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
    def take(batch,file='summary.json'):
        if batch not in pins:
            _,pins[batch]=authenticate(BASE/batch);refs.append(BASE/batch/'result.json')
        path=BASE/batch/file;assert ref(path)['sha256']==pins[batch][ref(path)['path']];refs.append(path);return read(path)
    selection=take(RUNTIME,'selection.json.gz');row=next(r for r in selection['rows']if r['uid']==UID);assert row['sourceSHA256']==SHA and row['triangles']==10338
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert ref(manifest)['sha256']==selection['manifestSHA256'];refs.append(manifest)
    identity=take(P+'bounded-identity-review-v1-20261024','ROOT-IDENTITY-REVIEW.json');assert identity['identityAccepted']and identity['sourceSHA256ByUid']==SOURCES and identity['rawExtentFailuresRetained']
    foundation=take(P+'current-foundations-v1-20261024');assert len(foundation['rows'])==4
    assert all(r['completeTerrainTriangles']==r['triangles']==10338 and r['fullyBuriedTriangles']==r['fullyBuriedUpwardTriangles']==0 for r in foundation['rows'])
    low=take(P+'current-low-faces-v1-20261024');caps=take(P+'current-cap-paths-v1-20261024');assert caps['allFourCompleteGroundClearCapPaths']and len(caps['rows'])==4
    expected={1902,10278,10279,10280,10283,10284,10288,10290,10294}
    for r in low['rows']:assert set(r['exactAffectedFaces'])==expected and r['allAffectedWallLike']and r['allAffectedHaveExposedHighestVertex']
    for r in caps['rows']:
        p=r['completeGroundClearancePartition'];assert not p['negativeNonWallFaces']and set(p['negativeSourceFaces'])==expected
        assert len(p['paths'])==9 and all(v['hasExactSharedEdgeClearCapPath']for v in p['paths'])
    scope=take(SCOPE);scope={**scope,'uids':[UID],'rows':[r for r in scope['rows']if r['uid']==UID]};forms=take(SCOPE,'335494:0-forms.json.gz');assert len(forms)==3
    assert {r['building']['uid']for r in forms}==RETAINED|{UID}
    native=take(NATIVE);current={}
    for url in read(manifest)['officialModelCatalogues']:
        p=ROOT/'3d-viewer'/url;refs.append(p)
        for m in read(p)['models']:assert m['uid']not in current;current[m['uid']]=m
    assert len(current)==6894 and verify_native_scope(scope,native,current,SOURCES,RETAINED,6894)
    basic=take(P+'current-basic-contacts-v1-20261024');assert basic['foreignPairs']==0
    for u in RETAINED:
        r=next(r for r in native['rows']if r['uid']==UID and r['nativeUid']==u);assert r['rawCurrentNativeEntry']==current[u]
    if BROWSER not in pins:
        _,pins[BROWSER]=authenticate(BASE/BROWSER);refs.append(BASE/BROWSER/'result.json')
    catalogue=HERE/'local'/BROWSER/'catalogue.json';assert ref(catalogue)['sha256']==pins[BROWSER][ref(catalogue)['path']]and verify_metadata(read(catalogue)['models'],SOURCES);refs.append(catalogue)
    images=[];oldimages=[];reports=[];sheets=[]
    for width in [1280,390]:
        reportpath=BASE/BROWSER/str(width)/'staged-browser.json';report=take(BROWSER,str(width)+'/staged-browser.json');assert report['passed']and not report['errors'];reports.append(ref(reportpath))
        views=[v for v in report['views']if'time'in v];retained=report['retainedNativeOwnViews'];assert len(views)==2 and len(retained)==4 and{v['uid']for v in retained}==RETAINED
        for values,output in [(views,images),(retained,oldimages)]:
            for v in values:
                assert v['active']and v['visible']and v['fullyFramed']and not v['fallbackFaces']and all(v['meshVisibility'])and not any(v['wireframeFlags'])
                if v['uid']==UID:assert v['sourceSHA256']==SHA and v['solidAppearance']and v['pick']==v['collision']==UID
                else:assert v['sourceSHA256']==current[v['uid']]['sha256']and v['originalTriangles']==current[v['uid']]['triangles']
                image=reportpath.parent/v['file'];assert ref(image)['sha256']==pins[BROWSER][ref(image)['path']];refs.append(image);output.append(dict(**ref(image),uid=v['uid'],width=width,time=v['time']))
        for t in ['1500','2200']:
            p=BASE/(P+'root-inspection-v1-20261024')/str(width)/(str(width)+'-'+t+'.jpg');assert p.exists();refs.append(p);sheets.append(ref(p))
    observations=[
        'Identity is accepted only for this exact10338face source and current form by the bounded official-photo/source-graph/GeoRef review. The original extended leaf roof and portal truss canopy are retained; generic extent policy and raw extent negatives remain unchanged.',
        'All four actual-source representations have complete current-ground coverage with zero whole-face/upward-whole-face burial. The exact ordinary-.5m clearance negatives are nine lower wall faces only, with minimum gap about-.78575m. Every affected face has an exposed highest vertex and a complete positive-original-surface path to an upward cap proven clear against every actual drawn ground facet. No negative nonwall or upward floor remains. ROOT inspected the complete original source and twelve runtime canvases: these are original lower facade/portal-frame walls crossing the current grade while the source body and roof remain above. Accept these bounded partial lower-wall intersections, retaining every raw negative; do not assert that strict raw clearance passed or invent an engineering root, basement or support.',
        'All6894 installed actors were checked through complete four-world bounds. The complete source region nominates exactly three current forms: this source, substation93826 and IFCpodium257115. Both retained original assets have zero finite contact pairs, including point-only contacts, in all four worlds. No other foreign BASIC actor occurs in the complete scope. No terrain, existing asset, metadata, dependency, suppression or source pose changes are needed.',
        'The native diagnostic initially omitted catalogue-level rootTranslation on older entries. Its corrected capture invokes the actual production prepareModelCatalogue and proves all three captured native coordinate-bound representations match the pinned current inventory exactly. Raw current entries remain unchanged; the setup failure is not model corruption.',
        'ROOT inspected all twelve actual source/retained desktop/mobile day/night canvases through four full-frame sheets. The complete curved roof and open truss portal are visible. Both retained natives remain visible in their own frames. Natural foreground tower occlusion in the IFCwide view, original dark source night appearance and unchanged legacy window shaders on retained actors remain; no procedural windows are added to the new roof.',
        'Approve guarded original-model-only integration for this exact source. All terrain, all6894 prior asset bytes/catalogue entries, both global retained-BASIC bindings, complete three-form lease, live failed-download/retry/picking/collision and actual twelve live canvases remain installation gates.'
    ]
    common=dict(uids=[UID],reviewer='ROOT',sourceSHA256ByUid=SOURCES,requiredOriginalAssembly=SOURCES,currentManifest=ref(manifest),identityAccepted=True,identityProof=identity['identityProof'],sourceSpecificPhysicalInterpretationAccepted=True,originalSourceReviewAccepted=True,completeNeighbourInterpretationAccepted=True,completeFourWorldFoundations=True,qualifiedFourWorldSourceClearance=True,completeFourWorldSourceClearance=True,rawClearancePassed=False,completeCurrentNeighbourChecks=3,leaseResources=sorted('building:'+u for u in RETAINED|{UID}),supportByUid={},nativeSupportByUid={},retainedBasicSupportDependencies=[],retainedCurrentBasicSupportUids=[],retainedNativeEntries={u:current[u]for u in RETAINED},terrainEdits=False,sourceGeometryChanges=0,sourcePoseChanges=0,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,visualAcceptance=True,browserReports=reports,imagesActuallyViewed=images,retainedImagesActuallyViewed=oldimages,inspectionPreviewsActuallyViewed=sheets,observations=observations,publication=False,installationApproved=False)
    save(out/'ROOT-PHYSICAL-REVIEW.json',common);save(out/'ROOT-SOURCE-REVIEW.json',common)
    module('ventilation_source_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'bounded-independent-original-ventilation-source-wall-and-current-neighbour-review',list(dict.fromkeys(refs)),{k:common[k]for k in ['uids','sourceSHA256ByUid','identityAccepted','sourceSpecificPhysicalInterpretationAccepted','visualAcceptance','terrainEdits','sourceGeometryChanges','sourcePoseChanges','sourceEvidenceInterpretationUsedAI']})

if __name__=='__main__':main()
