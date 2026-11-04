"""Compose exact-source Sha Tin acceptance for guarded staged verification."""
import json
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';P='government-xl-sha-tin-';BATCH=P+'seven-original-qualification-v1-20261029'

def main():
    out=BASE/BATCH;assert not out.exists();refs=[Path(__file__)];pins={}
    def take(batch,name='summary.json'):
        if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
        path=BASE/batch/name;assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
    def packet(suffix,name='summary.json'):return take(P+suffix+'-20261029',name)
    cfgpath=HERE/'local'/(P+'source-bound-production-fixture-v1-20261029')/'config.json'
    batch=P+'source-bound-production-fixture-v1-20261029';take(batch)
    assert digest(cfgpath.read_bytes())==pins[batch][str(cfgpath.relative_to(ROOT))];refs.append(cfgpath);cfg=read(cfgpath)
    catpath=ROOT/cfg['stage']/'catalogue.json';assert digest(catpath.read_bytes())==pins[batch][str(catpath.relative_to(ROOT))];refs.append(catpath);cat=read(catpath);sources={m['uid']:m['sha256']for m in cat['models']};uids=sorted(sources);assert len(uids)==7
    manifest=ROOT/'3d-viewer/city/data/manifest.json';current_sha=digest(manifest.read_bytes());refs.append(manifest)
    scope=packet('seven-upward-floor-scope-v1','scope.json');assert sorted(scope['uids'])==uids and scope['currentNativeActors']==7007 and not scope['touchingNativeUids'] and scope['positiveAreaTerrainOverlaps']==0
    identity=take('government-xl-civic-seven-identity-v1-20261029');ordinary={r['uid']for r in identity['rows']if r['passed']and sources.get(r['uid'])==r['sourceSHA256']}
    association=packet('four-exact-source-associations-v1');assert association['identityOnlyApproved'];reviewed={r['uid']for r in association['rows']if r['identityOnlyApproved']and sources.get(r['uid'])==r['sourceSHA256']};assert ordinary|reviewed==set(uids)
    height=packet('seven-original-height-applicability-review-v1','ROOT-HEIGHT-APPLICABILITY.json');assert height['nativeHeightApplicabilityAcceptedForOriginalPort']and height['currentManifestSHA256']==current_sha
    assert {r['uid']:r['sourceSHA256']for r in height['rows']}==sources and all(r['verticalPlacementOffsetHKPD']==0 for r in height['rows'])
    grade=packet('seven-final-grade-composition-v1');assert grade['sourceGradeEvidenceComposed']and grade['finalCapPathsRevalidated']and sorted(grade['uids'])==uids
    for uid in uids:
        f=packet('upward-floor-'+uid.split('/')[1].replace(':','-')+'-foundations-v1');assert f['establishedFoundationPolicyPassed']and f['uids']==[uid]
    region=packet('seven-upward-floor-region-regression-v1');assert region['forms']==70 and not region['basicFlags']and not region['requiredNativeUids']
    pair=packet('seven-original-pair-context-v1');roles=packet('seven-original-pair-roles-v1');assert pair['completeUnorderedPairs']==21 and len(pair['rows'])==84 and roles['allRawContactsClassified']and pair['sourceSHA256ByUid']==roles['sourceSHA256ByUid']==sources
    native_reviews=[]
    bases={('231013','23220'):'The podium terraces and structural wall/column arrangement join the source tower at its lower envelope. Keep the complete independently grounded source units and their authored interfaces.',('231013','23759'):'The podium terrace/roof return joins the library wall and ledges. Shared-plane areas and point/edge/transverse contacts are retained as authored source junctions.',('231013','23761'):'The podium wraps the marriage-registry lower wall and roof interface. Preserve both source envelopes; the contact is not a reason to clip either immutable source.',('238142','271344'):'The connecting deck and wall returns meet the bus-terminus facade. Preserve the original connected viewer arrangement without inferring a structural dependency.',('271344','92881'):'The terminus wall/deck and Citylink stepped ledge/wall arrangement join at the visible connecting interface. Keep both original units at native pose.'}
    for r in pair['rows']:
        if r['mode']!='original'or not r.get('positiveSurfaceContacts',0):continue
        u,v=r['uid'],r['peerUid'];ids=tuple(x.split('/')[1].split(':')[0]for x in [u,v]);label='-'.join(ids)
        view=packet('native-junction-'+label+'-v1');assert view['sourceSHA256ByUid']=={x:sources[x]for x in [u,v]}
        image=ROOT/view['image']['path'];assert digest(image.read_bytes())==view['image']['sha256'];refs.append(image)
        rows=[x for x in roles['rows']if x['uid']==u and x['peerUid']==v];assert len(rows)==4 and all(x['contactCount']>0 for x in rows)
        native_reviews.append(dict(uid=u,peerUid=v,basis=bases[ids],allFourRawRoleRows=rows,diagram=view['image'],diagramActuallyInspected=True,boundedOpaqueJunctionAccepted=True,sourceGeometryChanges=0,physicalRootOrDependencyCredit=False,reverseSolidContainmentCertified=False))
    assert len(native_reviews)==5
    foreign=packet('civic-seven-foreign-contacts-v1');external={(r['uid'],r['foreignUid'])for r in foreign['rows']if r['foreignUid']not in sources and any(m['positiveContactPairs']for m in r['modes']if m['mode']!='before-basic')}
    opaque=packet('four-opaque-interface-role-reviews-v1','ROOT-OPAQUE-INTERFACE-REVIEWS.json');assert opaque['sourceSpecificOpaqueInterfaceRolesApproved'];covered={(r['uid'],r['foreignUid'])for r in opaque['rows']if r['boundedOpaqueJunctionRoleApproved']}
    canopy=packet('canopy-conditional-replacement-review-v1');assert canopy['conditionalReplacementDecisionApproved']and canopy['sourceSHA256']==sources[canopy['sourceUid']];assert external==covered|{(canopy['sourceUid'],canopy['basicUid'])}
    fallback=packet('qualified-basic-ground-v1');assert fallback['realPublisherStagersPassed']and fallback['actualProductionLifecyclePassed']and fallback['publicFilesWritten']==0
    geometry=packet('production-geometry-equivalence-v1');assert geometry['unchangedLegacyForms']==70 and geometry['unchangedOriginalModels']==7 and geometry['equivalentBasicContinuations']==3
    collision=packet('production-basic-collision-v1');assert collision['exactCellMapUnchanged']and collision['allRoofMaximaUnchanged']and collision['probes']==435204
    life=packet('source-bound-production-atomic-lifecycle-v1');assert life['browserPassed']and life['cases']==life['expectedCases']==8 and life['actualProductionGeometryHTTP']and life['moduleSubstitution']is False
    visual=packet('source-bound-full-scene-root-observations-v1','ROOT-IMAGE-OBSERVATIONS.json');assert visual['imagesActuallyReviewed']and visual['wholeSceneVisualObservationComplete']and visual['actualExportedImagesRepresented']==28
    basic=packet('source-bound-fallback-root-observations-v1','ROOT-FALLBACK-IMAGE-OBSERVATIONS.json');assert basic['allEightFallbackCanvasesActuallyInspected']and basic['boundedFallbackAppearanceReviewed']
    dry=packet('seven-original-full-plan-dry-run-v2');assert dry['canonicalFullPlanDryRunPassed']and dry['currentManifestSHA256']==current_sha and dry['originalApprovalFlagsRemainFalse']
    for m in cat['models']:
        asset=catpath.parent/m['asset'];assert digest(asset.read_bytes())==sources[m['uid']];refs.append(asset)
        assert m['proceduralWindows']is False and m['activationGroup']==uids and not m.get('supportDependencies')and not m.get('retainedBasicSupportDependencies')and m.get('verticalPlacementOffsetHKPD',0)==0
        assert m.get('suppressesBuildingUids',[])==(['landsd/92340:0']if m['uid']=='landsd/231013:0'else[])
    # Every consumed evidence file and current source is pinned; old diagnostic
    # negative flags remain in their immutable upstream packets.
    for path in refs:
        for pin in pins.values():
            key=str(path.relative_to(ROOT))
            if key in pin:assert digest(path.read_bytes())==pin[key]
    result=dict(uids=uids,sourceSHA256ByUid=sources,currentManifestSHA256=current_sha,identityAccepted=True,originalSourceApplicabilityAccepted=True,sourceSpecificPhysicalInterpretationAccepted=True,completeNeighbourInterpretationAccepted=True,visualAcceptance=True,collisionReviewApproved=True,originalSupportDependencyRolesAccepted=True,retainedBasicSupportDependencies=[],retainedCurrentBasicSupportUids=[],physicalSupportRelationshipsInvented=0,sourceGeometryChanges=0,sourcePoseChanges=0,aiGeometryModelling=False,evidenceInterpretationUsedAI=True,reviewer='ROOT',nativeJunctionReviews=native_reviews,externalOpaqueJunctionPairs=[list(x)for x in sorted(covered)],conditionalCanopySuppression=['landsd/92340:0'],rawProxyAndHeightFlagsRetained=True,rawNativePairContactsRetained=True,reverseSolidContainmentCertified=False,asBuiltSurveyCertified=False,privateStageQualified=True,qualifiedForLiveVerification=True,installationApproved=False,publication=False,qualification='Accept these exact seven original provider units for staged viewer integration at immutable native 1x pose. All independently grounded source-grade accounts, current terrain scope, complete native/retained-BASIC contact coverage and bounded authored junction roles, source identity/applicability, BASIC fallback collision, actual production lifecycle and inspected appearance evidence are composed. Original source/survey discrepancies and raw surface crossings remain visible in upstream records. Availability group is conservative all-or-none loading, not physical support. This grants no cadastral/engineering or as-built-height certification. Exact final qualified stage/browser and fenced live publication/readback remain mandatory.')
    save(out/'ROOT-SOURCE-REVIEW.json',result)
    module('sha_tin_full_original_qualification_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'seven-exact-original-source-grade-boundary-interface-visual-runtime-qualification',list(dict.fromkeys(refs)),result)
if __name__=='__main__':main()
