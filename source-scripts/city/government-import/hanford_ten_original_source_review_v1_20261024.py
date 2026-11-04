"""Bounded ten-original Hanford physical/source-role and inspected-export review."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from hanford_ten_original_catalogue_scope_v1_20261024 import SOURCES,SUPPORTS,PRIMARY,SECONDARY,verify_metadata
BASE=ROOT/'docs/astra-city/government-import';P='government-xl-next-repairs-hanford-ten-original-'
BATCH=P+'source-review-v1-20261024';BROWSER=P+'unapproved-preview-v3-20261024'


def main():
    out=BASE/BATCH;assert not out.exists();refs=[Path(__file__),HERE/'hanford_ten_original_catalogue_scope_v1_20261024.py'];pins={}
    def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
    def take(batch,file='summary.json'):
        if batch not in pins:
            _,pins[batch]=authenticate(BASE/batch);refs.append(BASE/batch/'result.json')
        path=BASE/batch/file;assert ref(path)['sha256']==pins[batch][ref(path)['path']];refs.append(path);return read(path)
    def summary(name):return take(P+name+'-20261024')
    selection=take(P+'two-podium-runtime-v1-20261024','selection.json.gz')
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert ref(manifest)['sha256']==selection['manifestSHA256'];refs.append(manifest)
    assert {r['uid']:r['sourceSHA256']for r in selection['rows']}==SOURCES
    for r in selection['rows']:
        asset=ROOT/r['candidate']['path'];assert ref(asset)['sha256']==SOURCES[r['uid']];refs.append(asset)
        tile=ROOT/'3d-viewer'/r['source']['tile'];assert ref(tile)['sha256']==r['source']['tileSHA256']and next(b for b in read(tile)['buildings']if b['uid']==r['uid'])==r['source']['building'];refs.append(tile)
        f=summary(r['uid'].split('/')[1].split(':')[0]+'-two-podium-foundations-v1')
        assert len(f['rows'])==4 and all(q['completeTerrainTriangles']==q['triangles']==r['triangles']and q['fullyBuriedTriangles']==q['fullyBuriedUpwardTriangles']==0 for q in f['rows'])
    identity=take(P+'bounded-identity-review-v1-20261024','ROOT-IDENTITY-REVIEW.json')
    assert identity['identityAccepted']and identity['requiredOriginalAssembly']==SOURCES and all(identity['identityProof'].values())
    follow=summary('support-followthrough-v1');path_counts=[]
    for uid,parent in SUPPORTS.items():
        r=next(r for r in follow['rows']if r['uid']==uid and r['supportUid']==parent)
        paths=take(r['pathsBatch']);assert paths['allUnresolvedHaveFinitePaths']and len(paths['rows'])==4
        assert all(q['targets']==q['verifiedPaths']and not q['remaining']for q in paths['rows']);path_counts.append(r['pathCounts'][0]['verified'])
    assert sum(path_counts)==398
    primary=summary('276187-two-podium-cap-paths-v1');tiny=summary('195682-two-podium-cap-paths-v1');secondary=summary('203884-two-podium-cap-paths-v1')
    assert not primary['allFourCompleteGroundClearCapPaths']and tiny['allFourCompleteGroundClearCapPaths']
    covered_name=P+'primary-covered-low-context-v1-20261024';covered=take(covered_name)
    assert covered['allFourWorldTargetsHaveClearSourceOwnedOverhead']and len(covered['rows'])==4
    for row in primary['rows']:
        part=row['completeGroundClearancePartition'];assert len(part['negativeSourceFaces'])==328
        clear={p['sourceFace']for p in part['paths']if p['hasExactSharedEdgeClearCapPath']};assert len(clear)==220
        proof=take(covered_name,row['mode']+'.json.gz');records=proof['rows'];assert len(records)==108
        assert clear|{r['sourceFace']for r in records}==set(part['negativeSourceFaces'])and not clear&{r['sourceFace']for r in records}
        assert all(r['wholeSourceProjectionCoveredByDominatingClearOriginalFaces']and r['completelyClearOriginalOverheadFaces']for r in records)
        nonwall={r['sourceFace']:r for r in records if r['negativeNonWall']};assert set(nonwall)=={10750,10751,10752,12216,12217}
        assert all(nonwall[i]['signedNormalYRatio']<0 for i in [10750,10751,10752])and all(nonwall[i]['signedNormalYRatio']>0 for i in [12216,12217])
    assert all(not r['completeGroundClearancePartition']['negativeSourceFaces']and not r['completeGroundClearancePartition']['negativeNonWallFaces']for r in secondary['rows'])
    assert all({p['sourceFace']for p in r['completeGroundClearancePartition']['paths']}=={22,27,28}and all(p['hasExactSharedEdgeClearCapPath']for p in r['completeGroundClearancePartition']['paths'])for r in tiny['rows'])
    patch=summary('two-podium-terrain-v1');assert patch['status']=='private-terrain-validator-passed'and patch['allSubFloorRegionsNonregressing']
    low=take(P+'two-podium-terrain-v1-20261024','low-base-preservation.json');assert low['sameCompleteFloat32Multiset']and low['allSubFloorRegionsNonregressing']
    candidate=ROOT/patch['candidate']['path'];assert ref(candidate)['sha256']==patch['candidate']['sha256'];refs.append(candidate)
    assert read(candidate)['meta']['targetUids']==sorted([PRIMARY,SECONDARY])
    scope_name=P+'two-podium-current-scope-v1-20261024-276187-0-scope';scope=take(scope_name,'scope.json')
    assert scope['currentNativeActors']==6884 and scope['intersectingForms']==39 and not scope['touchingNativeUids']and scope['positiveAreaTerrainOverlaps']==0 and not scope['terrainContacts']
    forms=take(scope_name,'form-obligations.json.gz');assert len(forms)==39 and set(SOURCES)<={f['uid']for f in forms}
    neighbours=take(P+'two-podium-current-scope-v1-20261024-276187-0-forms')
    assert neighbours['forms']==39 and len(neighbours['flagged'])==6 and all(r['uid']in SUPPORTS and r['reasons']==['increased-neighbour-ground-gap']for r in neighbours['flagged'])
    foreign=summary('current-basic-contacts-v1');assert foreign['foreignPairs']==29
    assert all(q['positiveContactPairs']==0 for r in foreign['rows']if r['foreignUid']not in SOURCES for q in r['modes']if q['mode']!='before-basic')
    pairs=summary('all-pair-context-v1');assert pairs['sourceSHA256ByUid']==SOURCES and pairs['completeUnorderedPairs']==45 and len(pairs['rows'])==180
    cat=HERE/'local'/BROWSER/'catalogue.json'
    # Authenticate private assets/configuration and every actual canvas export.
    if BROWSER not in pins:
        _,pins[BROWSER]=authenticate(BASE/BROWSER);refs.append(BASE/BROWSER/'result.json')
    assert ref(cat)['sha256']==pins[BROWSER][ref(cat)['path']]and verify_metadata(read(cat)['models']);refs.append(cat)
    images=[];sheets=[];reports=[]
    for width in [1280,390]:
        path=BASE/BROWSER/str(width)/'staged-browser.json';report=take(BROWSER,str(width)+'/staged-browser.json');assert report['passed']and not report['errors'];reports.append(ref(path))
        views=[v for v in report['views']if 'time'in v];assert len(views)==20
        assert {(v['uid'],v['time'])for v in views}=={(u,t)for u in SOURCES for t in ['15:00','22:00']}
        for v in views:
            assert v['width']==width and v['sourceSHA256']==SOURCES[v['uid']]and v['fullyFramed']and v['solidAppearance']and not v['fallbackFaces']and v['pick']==v['collision']==v['uid']
            p=path.parent/v['file'];assert ref(p)['sha256']==pins[BROWSER][ref(p)['path']];refs.append(p);images.append(dict(**ref(p),uid=v['uid'],width=width,time=v['time']))
        for time in ['1500','2200']:
            sheet=BASE/(P+'root-inspection-v3-20261024')/str(width)/(str(width)+'-'+time+'.jpg');assert sheet.exists();refs.append(sheet);sheets.append(ref(sheet))
    observations=[
        'Exact ten original sources form the authored Hanford tower/podium assembly. The completed bounded identity review preserves individual footprint/cell/root-pattern negatives; no geometry, pose, scale, name or ownership inference changes.',
        'All28973 original facets have complete actual-ground coverage in four worlds and zero wholly buried or wholly buried upward faces. Six towers depend on original276187; Tower2depends on original203884. All398 unresolved chosen support rims per world have exact finite paths into their original source podium. No decorative component is required to have an invented engineering root.',
        'Primary328 partial ground-clearance negatives are completely accounted:220 lower facade wall faces have exact clear-cap paths;103 remaining wall faces and5 nonwall faces are wholly covered by clear upward facets of the same original276187 in every world. Faces10750/51/52 are downward source undersides;12216/17 are covered upward lower ramps. Retain raw capaggregateFALSE and every source/ground negative. Accept these bounded source-owned covered lower/interior details, without asserting a basement, structural purpose or public exposed surface below ground. No ground-root credit is inferred from an overhead roof.',
        'Secondary203884has no faces in the exact ordinary negative partition. Its empty cap resultFALSE creates no additional failure. Tiny195682has three lower wall faces22/27/28, each with complete exact clear-cap paths. Source pair contacts are authored tower/podium and adjoining site interfaces of this exact co-import, supported by the measured original graphs and full original views; no foreign intersection exemption is introduced.',
        'Two original-TIN podium replacements preserve source geometry and the existing coastal low-parent region. The exact Float32 coastal repair changes derived return vertices by at most0.036mm; every final low-face no-lowering proof and ordinary terrain validator passes. Both podium targetUIDs stay exact. Entire350x280m coarse domain:39 current forms, all6884 native actors screened, no touching native or prior terrain overlap. Six co-import BASIC towers have increased terrain gaps, retained as raw flags and resolved by their actual imported native podium dependencies; all33 other forms unflagged. All external basic source contacts zero.',
        'ROOT inspected all40 desktop/mobile day/night exports through four full-frame contact sheets. Original tower roof recesses, facade returns, stepped podium terraces and the small lower component are visible. Natural partial occlusion by neighbouring towers and the dark original night appearance remain. Earlier mobile frames intentionally retain un-retried companions in basic form during the failure sequence; only each selected source is asserted detailed in its own export, and the final ten-source joint activation is separately required. No procedural window pattern is added to the originals. This is a bounded source-role review, not photographic or engineering certification.',
        'Approve this exact co-import for guarded integration only. Complete39form plus terrain leases, unchanged old assets/catalogues, global retained-basic bindings, atomic publication, live failure/retry/picking/collision/joint activation and independent521ledger/readback still gate completed installation.'
    ]
    common=dict(uids=sorted(SOURCES),reviewer='ROOT',sourceSHA256ByUid=SOURCES,requiredOriginalAssembly=SOURCES,sourceSpecificPhysicalInterpretationAccepted=True,originalSourceReviewAccepted=True,identityAccepted=True,identityProof=identity['identityProof'],completeNeighbourInterpretationAccepted=True,completeFourWorldFoundations=True,qualifiedFourWorldSourceClearance=True,completeFourWorldSourceClearance=True,completeFourWorldCanonicalRetainedBasicSupport=True,rawClearancePassed=False,completeCurrentNeighbourChecks=39,currentManifest=ref(manifest),leaseResources=sorted({'building:'+f['uid']for f in forms}|{'terrain:city/data/terrain.json'}),supportByUid=SUPPORTS,nativeSupportByUid=SUPPORTS,retainedBasicSupportDependencies=[],retainedCurrentBasicSupportUids=[],terrainEdits=True,sourceGeometryChanges=0,sourcePoseChanges=0,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,visualAcceptance=True,browserReports=reports,imagesActuallyViewed=images,inspectionPreviewsActuallyViewed=sheets,observations=observations,publication=False,installationApproved=False)
    save(out/'ROOT-PHYSICAL-REVIEW.json',common);save(out/'ROOT-SOURCE-REVIEW.json',common)
    module('hanford_bounded_source_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'bounded-hanford-ten-original-source-physical-and-inspected-preview-review',list(dict.fromkeys(refs)),dict(uids=sorted(SOURCES),sourceSHA256ByUid=SOURCES,originalSourceReviewAccepted=True,sourceSpecificPhysicalInterpretationAccepted=True,identityAccepted=True,visualAcceptance=True,installationApproved=False,sourceGeometryChanges=0))


if __name__=='__main__':main()
