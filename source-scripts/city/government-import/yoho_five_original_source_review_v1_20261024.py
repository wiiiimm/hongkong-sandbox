"""Bounded ROOT acceptance interpretation for five unchanged Yoho originals.

Raw spatial, strict-support and compound-clearance failures stay in their receipts.
No publication, new geometry, engineering certification or generic exemption.
"""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from yoho_five_unapproved_original_preview_v2_20261024 import SOURCES,SUPPORTS,RETAINED,PARENT
from original_supported_catalogue_scope_v1_20261024 import verify as verify_support_scope

BASE=ROOT/'docs/astra-city/government-import';P='government-xl-next-repairs-yoho-'
BATCH=P+'five-original-source-review-v1-20261024';BROWSER=P+'five-unapproved-preview-v2-20261024'

def main():
    out=BASE/BATCH;assert not out.exists();refs=[Path(__file__)];pins={}
    def take(batch,path):
        if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
        assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    def summary(suffix):
        batch=P+suffix+'-20261024';return take(batch,BASE/batch/'summary.json')
    def ref(path):return dict(path=str(path.relative_to(ROOT)),sha256=digest(path.read_bytes()))
    runtime=P+'five-inset-runtime-v1-20261024';selection=take(runtime,BASE/runtime/'selection.json.gz');assert {r['uid']:r['sourceSHA256']for r in selection['rows']}==SOURCES
    assert sum(r['triangles']for r in selection['rows'])==74290
    manifest=ROOT/'3d-viewer/city/data/manifest.json';assert ref(manifest)['sha256']==selection['manifestSHA256'];refs.append(manifest)
    metrics=take(runtime,BASE/runtime/'metrics.json');assert len(metrics['rows'])==5
    geometry={g['uid']:g for g in take(runtime,HERE/'local'/runtime/'runtime-geometry.json.gz')['rows']}
    attrsName=P+'five-current-attributes-v1-20261024';attrs={r['uid']:r for r in take(attrsName,BASE/attrsName/'attributes.json.gz')['rows']}
    # Exact transitive numeric binding, never a historical current-scene approval.
    oldruntime=P+'two-ramp-inset-runtime-v3-20261024';old={g['uid']:g for g in take(oldruntime,HERE/'local'/oldruntime/'runtime-geometry.json.gz')['rows']}
    oldattrName=P+'two-current-attributes-v2-20261024';oldattrs={r['uid']:r for r in take(oldattrName,BASE/oldattrName/'attributes.json.gz')['rows']}
    identical=[]
    for uid,g in old.items():
        assert g['sourceSHA256']==SOURCES[uid]==geometry[uid]['sourceSHA256']
        for field in ['position','index','drawnGroundGeometry']:assert np.array_equal(np.asarray(g[field]),np.asarray(geometry[uid][field]))
        for field in ['completeOriginalIndex','completeLiteralWorldPosition','completeExplicitLeftAssociatedFloat32WorldPosition','completeExplicitBalancedFloat32WorldPosition']:assert np.array_equal(np.asarray(oldattrs[uid][field]),np.asarray(attrs[uid][field]))
        identical.append(dict(uid=uid,allSourceGroundAndFourWorldAttributeInputsIdentical=True))
    rebound=summary('two-inset-current-numeric-rebind-v1');assert rebound['priorNumericRelationsStillApplyToExactCurrentInputs']and rebound['allActualLiteralSourceAndDrawnGroundInputsIdentical']and rebound['allFourWorldSourceAttributesIdentical']
    foundations=[];identity=[];allowed={'fresh-current-spatial-bound:sourceExcessCoveredByUnrelatedFormsM2','fresh-current-spatial-bound:sourceExcessMaximumDistanceFromTargetM','full-source-maximum-extent','full-source-unrelated-overlap'}
    for row in selection['rows']:
        uid=row['uid'];number=uid.split('/')[1].split(':')[0];f=summary(number+'-final-foundations-v1');assert len(f['rows'])==4 and all(r['completeTerrainTriangles']==r['triangles']==row['triangles']and r['fullyBuriedTriangles']==r['fullyBuriedUpwardTriangles']==0 for r in f['rows']);foundations.extend(f['rows'])
        batch=P+'five-current-identity-v1-20261024';raw=take(batch,BASE/batch/(uid.split('/')[1]+'/identity.json'));assert raw['sourceSHA256']==SOURCES[uid]and raw['exactCurrentComponentRoute']['qualified']and raw['exactWholeCellCoverage']['covered']
        assert raw['originalOwnership']['originalRootName']==row['modelId']
        reasons=set(raw['reasons'])
        if uid=='landsd/56771:0':
            name=P+'56771-original-yaw-v1-20261024';yaw=take(name,BASE/name/'proof.json');assert yaw['sourceSHA256']==SOURCES[uid]and yaw['sourceBoundRootFramePassed']and yaw['frame']['passed']and yaw['completeNativeBoundsErrorM']==0;assert reasons-allowed=={'original-unit-hkpd-root-pose'}
        else:assert raw['originalOwnership']['sourceGraphVerified']and reasons<=allowed
        identity.append(dict(uid=uid,rawIdentity=ref(BASE/batch/(uid.split('/')[1]+'/identity.json')),rawReasonsRetained=raw['reasons'],qualifiedExactCurrentRoute=raw['exactCurrentComponentRoute']['basis']))
        asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==SOURCES[uid];refs.append(asset)
        tile=ROOT/'3d-viewer'/row['source']['tile'];assert digest(tile.read_bytes())==row['source']['tileSHA256']and next(f for f in read(tile)['buildings']if f['uid']==uid)==row['source']['building'];refs.append(tile)
    # All podium actual-ground negatives are walls, not the public ramps183/184.
    low=summary('podium-inset-low-faces-v1');assert len(low['rows'])==4 and all(r['allAffectedWallLike']and r['allAffectedHaveExposedHighestVertex']and not{183,184}&set(r['exactAffectedFaces'])for r in low['rows'])
    assert summary('podium-inset-cap-paths-v1')['allFourCompleteGroundClearCapPaths']
    rawsupports=[]
    for uid,count in [('landsd/122702:0',19),('landsd/60281:0',52),('landsd/56771:0',46)]:
        number=uid.split('/')[1].split(':')[0];support=summary(number+'-original-podium-support-v1');paths=summary(number+'-original-podium-paths-v1');assert support['sourceSHA256ByUid']=={uid:SOURCES[uid],PARENT:SOURCES[PARENT]};assert paths['allUnresolvedHaveFinitePaths']and len(paths['rows'])==4 and all(r['targets']==r['verifiedPaths']==count and not r['remaining']for r in paths['rows']);rawsupports.append(support)
    for number in ['61738','122702','60281']:
        q=summary(number+'-compound-clearance-v1');assert len(q['rows'])==4 and all(r['compoundCapPathsPassed']and not r['negativeNonWallFaces']for r in q['rows'])
    downName=P+'56771-downward-context-v1-20261024';down=take(downName,BASE/downName/'exact-context.json');assert len(down['modes'])==4 and all(r['allWallCapPathsVerified']and not r['rawAggregatePassed']and{f['sourceFace']for f in r['downwardFaces']}=={13247,13630,13631}for r in down['modes'])
    scope=summary('five-current-model-scope-v1');assert scope['currentManifestSHA256']==ref(manifest)['sha256']and all(r['currentNativeActorsChecked']==6876 for r in scope['rows']);forms={}
    scopeName=P+'five-current-model-scope-v1-20261024'
    for r in scope['rows']:
        for item in take(scopeName,BASE/scopeName/(r['uid'].split('/')[1]+'-forms.json.gz')):forms[item['building']['uid']]=item['building']
    assert len(forms)==31 and{n['uid']for r in scope['rows']for n in r['nearbyNativeActors']}==set(RETAINED)
    foreign=summary('five-current-basic-contacts-v1');assert foreign['foreignPairs']==49
    for pair in foreign['rows']:
        before=next(m for m in pair['modes']if m['mode']=='before-basic')
        if any(m['positiveContactPairs']for m in pair['modes']if m['mode']!='before-basic')and not before['positiveContactPairs']:assert pair['foreignUid']in SOURCES and(pair['uid'],pair['foreignUid'])in [('landsd/56771:0','landsd/60281:0'),('landsd/60281:0','landsd/122702:0')]
    pairs=summary('five-original-pair-context-v1');assert pairs['sourceSHA256ByUid']==SOURCES and pairs['completeUnorderedPairs']==10 and pairs['coordinateModes']==4 and len(pairs['rows'])==40
    native=summary('five-native-contacts-v1');assert len(native['rows'])==4
    assert{(r['uid'],r['nativeUid'])for r in native['rows']}=={('landsd/61738:0','landsd/58849:0'),(PARENT,'landsd/121143:0'),(PARENT,'landsd/58849:0'),(PARENT,'landsd/146396:0')}
    assert all(not r['rawCurrentNativeEntry'].get('supportDependencies')and not r['rawCurrentNativeEntry'].get('retainedBasicSupportDependencies')for r in native['rows'])
    current={m['uid']:m for url in read(manifest)['officialModelCatalogues']for m in read(ROOT/'3d-viewer'/url)['models']};assert len(current)==6876
    for r in native['rows']:assert current[r['nativeUid']]==r['rawCurrentNativeEntry']and current[r['nativeUid']]['sha256']==r['nativeSHA256']
    terrain=summary('local-inset-current-validation-v1');assert terrain['status']=='private-terrain-validator-passed'and terrain['actualCurrentParentIdentical']and terrain['targetSetUnchanged']and terrain['uids']==[PARENT]
    terrainScopeName=P+'local-inset-current-scope-v1-20261024';ts=take(terrainScopeName,BASE/terrainScopeName/'scope.json');assert ts['currentNativeActors']==6876 and not ts['touchingNativeUids']and ts['positiveAreaTerrainOverlaps']==0
    neighbours=summary('local-inset-current-forms-v1');assert neighbours['forms']==17 and not neighbours['flagged']and not neighbours['ordinaryFlagged']
    checkpoint=P+'five-current-review-checkpoint-v2-20261024';inspection=take(checkpoint,BASE/checkpoint/'ROOT-EXPORT-INSPECTION.json');assert inspection['visualInspectionComplete']and len(inspection['imagesActuallyViewed'])==32
    deck=take(checkpoint,BASE/checkpoint/'native-deck-area-context.json');assert len(deck['rows'])==2 and all(r['contactPairs']==10 and r['heightHKPD']==[17.82699966430664]and all(n==[1.,-1.]for n in r['normalYPairs'])for r in deck['rows'])
    local=HERE/'local'/BROWSER;cat=take(BROWSER,local/'catalogue.json');assert verify_support_scope(cat['models'],SOURCES,SUPPORTS)
    reports=[]
    for width in [1280,390]:
        path=BASE/BROWSER/str(width)/'staged-browser.json';r=take(BROWSER,path);assert r['passed']and not r['errors'];reports.append(ref(path))
    sourceImages=[r for r in inspection['imagesActuallyViewed']if r['uid']in SOURCES];retainedImages=[r for r in inspection['imagesActuallyViewed']if r['uid']in RETAINED];assert len(sourceImages)==20 and len(retainedImages)==12
    for image in sourceImages+retainedImages:
        path=ROOT/image['path'];assert digest(path.read_bytes())==image['sha256']==pins[BROWSER][image['path']];refs.append(path)
    resources=sorted({'building:'+u for u in set(forms)|set(SOURCES)|set(RETAINED)}|{'terrain:city/data/terrain.json'})
    observations=[
        'Four exact named Tower records and the original common Podium have unique current ObjectId/CSUID/GeoRef/type routing, complete coordinate-cell coverage and source-owned named graphs. Block6 retains its government-authored unit horizontal yaw, separately proved without modifying its matrix. Approximate GIS footprints omit original lower terrace/facade extensions, so full-source extent and unrelated-projection flags remain archived; they do not imply mixed mesh ownership. This interpretation binds only these five complete source hashes and current31forms.',
        'Complete current-ground foundations cover every one of74290faces in all four coordinate streams, with zero wholly buried or upward-wholly-buried faces. The source-TIN local inset clears the two upward original ramps183/184; remaining233podium low faces are exposed lower walls with complete original clear-cap paths. Their raw negative gaps remain. No walking/ramp surface is accepted beneath actual ground.',
        'Blocks3/5/6 attach to the original podium through complete current finite contacts and19/52/46 additional original-surface paths in every representation. Block2 is independently ground-rooted and gets no invented support. Compound-envelope wall embeddings are original facade/pier construction interfaces, distinct from actual earth. Block6 additionally has three tiny downward lower-facade return faces atY10.08intersecting that original podium envelope; exact shared-vertex context and ROOT-inspected two-angle local plot identify these as lower facade interfaces, not public upward floors. Raw nonwall/aggregateFALSE remains; no generic downward-face exception is introduced.',
        'All10original pair interfaces are measured in all4coordinate representations, including source-authored shared-area/line joints. The newly positive BASIC comparisons involve only co-import tower peers and are replaced together. All other positively contacting retained basic neighbours already contact the former BASIC models; these are retained low courtyard/access structures around the authored terraces. The original source extensions and complete site preview show coherent lower compound relationships; counts alone are not ownership or identical-volume proofs. No foreign form is suppressed, moved or reclassified.',
        'Current installed Blocks1/7/8 keep every entry and geometry byte unchanged. Their contacts with the new podium/tower are authored lower compound interfaces. The10Float32area pairs with Block7 are coplanar podium-top/tower-underside surfaces atHKPD17.8269996643with opposing normals; exact union area1.4363569083m2is retained. This accepts the bounded original construction interface, not arbitrary intersecting models or support metadata migration. All3installed actors have no support dependencies, and none is manufactured or removed.',
        'All6876native bounds and all17terrain-domain basic forms were checked for the exact412face source-TIN inset; no native touches its changed domain and no basic regression or positive-area patch overlap remains. Only podium231756remains in terrain target metadata. All31whole-source forms and native contacts remain separately bound. Global retained-BASIC dependency publication guards remain mandatory.',
        inspection['visualFinding'],
        'Accept this exact unchanged original assembly for guarded integration only. Existing thresholds and raw negatives are preserved. Native support dependencies are only Blocks3/5/6to231756; no building edits, placement shift, suppression, estimate change or optimisation. Guarded publisher, live device checks, complete old-actor preservation and all521ledger readback still gate installation credit.'
    ]
    common=dict(uids=sorted(SOURCES),reviewer='ROOT',sourceSHA256ByUid=SOURCES,requiredOriginalAssembly=SOURCES,sourceSpecificPhysicalInterpretationAccepted=True,identityAccepted=True,completeNeighbourInterpretationAccepted=True,completeFourWorldFoundations=True,completeCurrentNeighbourChecks=31,terrainChangedNeighbourForms=17,currentManifest=ref(manifest),identityProof={k:True for k in ['exactObjectId','exactBuildingCSUID','uniqueViewerMatch','identityAccepted']},leaseResources=resources,supportByUid=SUPPORTS,nativeSupportByUid=SUPPORTS,retainedBasicSupportDependencies=[],retainedCurrentBasicSupportUids=[],terrainTargetUids=[PARENT],sourceGeometryChanges=0,sourcePoseChanges=0,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,rawIdentityNegatives=identity,rawClearancePassed=False,qualifiedFourWorldSourceClearance=True,completeFourWorldSourceClearance=True,originalSourceReviewAccepted=True,visualAcceptance=True,browserReports=reports,imagesActuallyViewed=sourceImages,retainedImagesActuallyViewed=retainedImages,inspectionPreviewsActuallyViewed=inspection['inspectionSheetsActuallyViewed'],observations=observations,publication=False,installationApproved=False)
    save(out/'ROOT-PHYSICAL-REVIEW.json',common);save(out/'ROOT-SOURCE-REVIEW.json',common);save(out/'numeric-input-equivalence.json',identical);save(out/'raw-support-negatives.json',rawsupports)
    refs.extend([HERE/'original_supported_catalogue_scope_v1_20261024.py',HERE/'yoho_five_unapproved_original_preview_v2_20261024.py'])
    module('yoho_original_review_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'bounded-five-original-yoho-source-physical-and-inspected-preview-review',list(dict.fromkeys(refs)),dict(uids=sorted(SOURCES),sourceSHA256ByUid=SOURCES,originalSourceReviewAccepted=True,identityAccepted=True,sourceSpecificPhysicalInterpretationAccepted=True,visualAcceptance=True,installationApproved=False,sourceGeometryChanges=0))

if __name__=='__main__':main()
