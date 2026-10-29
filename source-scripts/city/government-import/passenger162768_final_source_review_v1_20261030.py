"""Bind reviewed unchanged Passenger original, local terrain and exact six roofs."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from conditional_canopy_install_contract_v1_20261029 import form_sha
from passenger162768_surveyed_roof_contract_v1_20261030 import UID,SHA,TERRAIN,ROOFS,verify
P='government-xl-passenger162768-after-civic-five-'
BATCH=P+'final-source-review-v1-20261030'

def main():
    base=ROOT/'docs/astra-city/government-import';out=base/BATCH;assert not out.exists()
    refs=[Path(__file__),HERE/'passenger162768_surveyed_roof_contract_v1_20261030.py'];pins={}
    def ref(path):return dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes()))
    def take(suffix,path):
        batch=P+suffix
        if batch not in pins:
            pins[batch]=authenticate(base/batch)[1];refs.append(base/batch/'result.json')
        assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))]
        refs.append(path);return read(path)
    def doc(suffix,name='summary.json'):return take(suffix,base/(P+suffix)/name)
    manifest=ROOT/'3d-viewer/city/data/manifest.json';current=ref(manifest);refs.append(manifest)
    identity=doc('identity-v1-20261030','162768:0/identity.json');route=identity['exactCurrentComponentRoute']
    assert route['qualified']and not route['reasons']and identity['originalOwnership']['sourceGraphVerified']
    assert identity['originalOwnership']['originalRootName']=='B130291991401063C1'and identity['sourceSHA256']==SHA
    assert route['official']['objectId']==route['source']['building']['objectId']==162768
    primary=route['source']['building'];assert primary['buildingCSUID']=='1302919914T20180305'
    tile=ROOT/'3d-viewer'/route['source']['tile'];assert digest(tile.read_bytes())==route['source']['tileSHA256'];refs.append(tile)
    assert [b for b in read(tile)['buildings']if b.get('buildingCSUID')==primary['buildingCSUID']]==[primary]
    selection=doc('post-preserving-runtime-v1-20261030','selection.json.gz');row,=selection['rows']
    assert row['uid']==UID and row['sourceSHA256']==SHA and selection['manifestSHA256']==current['sha256']
    asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==SHA;refs.append(asset)
    modelscope=doc('source-scope-v1-20261030');assert modelscope['currentManifestSHA256']==current['sha256']
    s,=modelscope['rows'];assert s['currentNativeActorsChecked']==7027 and not s['nearbyNativeActors']
    forms=[r['building']for r in doc('source-scope-v1-20261030','162768:0-forms.json.gz')];by={b['uid']:b for b in forms}
    assert len(forms)==len(by)==23 and by[UID]==primary
    foreign=doc('foreign-contacts-v1-20261030');assert foreign['foreignPairs']==22
    positive={r['foreignUid']for r in foreign['rows'] if any(m['positiveContactPairs'] for m in r['modes']if m['mode']!='before-basic')}
    assert positive==set(ROOFS)|{'landsd/153422:0','landsd/332872:0'}
    basic=doc('foreign-contacts-v1-20261030','basic.json')
    for path,sha in basic['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha;refs.append(ROOT/path)
    foundation=doc('post-preserving-foundations-v1-20261030');assert foundation['establishedFoundationPolicyPassed']
    assert len(foundation['rows'])==4 and all(r['fullyBuriedTriangles']==8 and r['fullyBuriedUpwardTriangles']==0 for r in foundation['rows'])
    buried=doc('targeted-buried-context-v1-20261030','162768:0.json')
    assert [r['faceIndex']for r in buried['buriedFaces']]==[224,225,304,305,384,385,944,945]
    assert all(not r['upward']for r in buried['buriedFaces'])
    terrain=doc('post-preserving-inset-v1-20261030');assert terrain['status']=='private-terrain-validator-passed'and terrain['candidate']['sha256']==TERRAIN
    scope=doc('post-preserving-scope-v1-20261030','scope.json')
    assert scope['currentNativeActors']==7027 and not scope['touchingNativeUids']and not scope['terrainContacts']and scope['positiveAreaTerrainOverlaps']==0
    patchforms=doc('post-preserving-scope-v1-20261030','form-obligations.json.gz');assert len(patchforms)==3 and all(by[b['uid']]==b for b in patchforms)
    neighbours=doc('post-preserving-forms-v1-20261030');assert neighbours['forms']==3 and neighbours['ordinaryFlagged']==1
    assert [r['uid']for r in neighbours['flagged']]==['landsd/161745:0']
    posts=doc('complete-fallback-post-ground-v1-20261030')['rows']
    assert doc('post-preserving-domain-context-v1-20261030')['allEightCompletePostFootprintsStrictlyOutsideModifiedRegion']
    auxiliaries=doc('retained-tower-contact-context-v1-20261030');assert auxiliaries['sourceSHA256']==SHA
    assert [r['uid']for r in auxiliaries['rows']]==['landsd/153422:0','landsd/332872:0']
    for aux in auxiliaries['rows']:
        assert aux['exactBasicForm']==by[aux['uid']]
        for mode in aux['modes']:
            assert mode['positiveContacts']==(126 if aux['uid']=='landsd/153422:0' else 56)
            assert len(mode['sourceFaceIds'])==(1 if aux['uid']=='landsd/153422:0' else 17)
        image=ROOT/aux['diagram'];assert image.is_file();refs.append(image)
    coverage=doc('contact-roof-context-v1-20261030')['rows'];features=[];replacements=[]
    for uid in ROOFS:
        feature=dict(currentManifest=current,sourceUid=UID,sourceSHA256=SHA,basicUid=uid,exactBasicForm=by[uid],reviewedArchitecturalRole='surveyed-flat-subdivision-of-same-wave-roof',fourWorldRoofContext=[r for r in coverage if r['uid']==uid],privateCanopyExperimentApproved=True,publication=False,installationApproved=False)
        features.append(feature);save(out/('ROOT-SURVEYED-ROOF-'+uid.split('/')[1]+'.json'),feature)
        replacements.append(dict(sourceUid=UID,basicUid=uid,sourceSHA256=SHA,sourceFormSHA256=form_sha(primary),basicFormSHA256=form_sha(by[uid]),onlyWhileExactOwnerActive=True,approved=True))
    viewed=doc('post-preserving-visual-context-v1-20261030');assert len(viewed['images'])==6 and all(i['actuallyViewedBy']=='root'for i in viewed['images'])
    preview='post-preserving-roof-private-preview-v1-20261030';reports=[];images=[]
    for width in [390,1280]:
        path=base/(P+preview)/str(width)/'staged-browser.json';report=take(preview,path);assert report['passed']and not report['errors'];reports.append(ref(path))
        for v in [v for v in report['views']if 'time'in v]:
            assert v['fullyFramed']and v['solidAppearance']and not v['fallbackFaces']and v['pick']==v['collision']==UID and v['sourceSHA256']==SHA
            path=base/(P+preview)/str(width)/v['file'];image=ref(path);assert any(i['path']==image['path']and i['sha256']==image['sha256']for i in viewed['images']);refs.append(path);images.append(image)
    assert len(images)==4
    lifecycle=doc('six-roof-lifecycle-v1-20261030','report.json')
    cat=take(preview,HERE/'local'/(P+preview)/'catalogue.json')
    basis=[
      'Exact government root, current unique viewer object/CSUID and unchanged 32238-face source accepted for the whole Passenger Clearance assembly; fixed 1x pose and source elevation retained.',
      'Six surveyed GIS open-sided forms are flat top37 subdivisions over the original continuous wave roof, not six independent buildings. Their complete original roof coverage, whole-building source, official architecture and actually viewed before/isolation/refined exports are reviewed together; coverage alone is not the decision rule.',
      'Only these exact six BASIC graphic roofs hide, and only while this exact original is active. Their survey fields and original source geometry remain immutable. Verified failed-download/retry/Base-only/Auto/eviction restores every fallback.',
      '161745 broad footprint flag is retained. Complete actual ground overlays cover all eight post footprints, whose bottoms remain below ground; the 1m terrain return is strictly disjoint from these posts. No post/elevation edits or blanket clearance exception.',
      'Retained153422 has a shallow local meeting with one slightly sloped original surface at15.37..15.47m; retained332872 intersects original vertical column facets5.172..14.042m. Local source-coordinate diagrams were actually viewed. These bounded co-located port assembly contacts are accepted for graphics; both existing auxiliary forms remain retained, without inventing their functional names or treating them as support dependencies.',
      'Eight small lower vertical source facets remain buried, zero upward facets buried in all4worlds. Established full-source foundation policy passes. Original lower strips remain intact; no engineering structural certification is asserted.'
    ]
    common=dict(sourceSHA256ByUid={UID:SHA},currentManifest=current,identityAccepted=True,sourceSpecificPhysicalInterpretationAccepted=True,completeNeighbourInterpretationAccepted=True,visualAcceptance=True,sourceGeometryChanges=0,sourcePoseChanges=0,aiGeometryModelling=False,sourceEvidenceInterpretationUsedAI=True,installationApproved=False,publication=False,surveyedRoofCase='passenger162768-original-wave-roof-v1',conditionalCanopyReplacements=replacements,qualification=basis)
    physical=dict(**common,identityProof=dict(exactObjectId=True,exactBuildingCSUID=True,uniqueViewerMatch=True,identityAccepted=True),completeFourWorldFoundations=True,completeCurrentNeighbourChecks=23,currentNativeActors=7027,completeOriginalFaces=32238,ordinaryFoundationRows=foundation['rows'],surveyedFallbackPosts=posts,retainedAuxiliaryUids=['landsd/153422:0','landsd/332872:0'],retainedAuxiliaryContactContext=auxiliaries['rows'],rawBroadFootprintFlagRetained=True,rawFormFlags=neighbours['flagged'],rawIdentityDiagnosticsRetained=identity['reasons'],terrainCandidate=terrain['candidate'],globalClearanceExceptionsCreated=0,retainedNativeUids=[],supportByUid={UID:[]},auxiliaryDiagramsActuallyViewed=[ref(ROOT/r['diagram'])for r in auxiliaries['rows']])
    visual=dict(**common,imagesActuallyViewed=images,browserReports=reports,canopyLifecycleReport=ref(base/(P+'six-roof-lifecycle-v1-20261030')/'report.json'),canopyFeatureReviews=[ref(out/('ROOT-SURVEYED-ROOF-'+u.split('/')[1]+'.json'))for u in ROOFS])
    proof=verify(cat['models'],visual,physical,lifecycle,features,by)
    save(out/'ROOT-SOURCE-REVIEW.json',visual);save(out/'ROOT-PHYSICAL-REVIEW.json',physical);save(out/'surveyed-roof-contract.json',proof);save(out/'form-obligations.json.gz',forms)
    module('passenger_final_source_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-passenger-original-surveyed-roof-and-local-terrain-source-review',refs,dict(uids=[UID],sourceSHA256ByUid={UID:SHA},identityAccepted=True,sourceSpecificPhysicalInterpretationAccepted=True,completeNeighbourInterpretationAccepted=True,visualAcceptance=True,sourceGeometryChanges=0,installationApproved=False,publication=False,nextStep='Source-specific surveyed roof guarded staging and live verification; preserve all installed terrain, support, ledger and rollback guards.'))

if __name__=='__main__':main()
