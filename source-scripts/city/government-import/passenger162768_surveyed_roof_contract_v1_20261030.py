"""Exact Passenger source/terrain/six-surveyed-roof contract, not a general waiver."""
from conditional_canopy_install_contract_v1_20261029 import form_sha
UID='landsd/162768:0'
SHA='8df09bfde9d69f09ccbec06f7c45cff3d0095d209616b49917465428f89a3c14'
TERRAIN='393ccdc4c0394af100fb6e65a111e0c91b16f954fa8d5d7e471ca2d342cbf0bd'
ROOFS={
 'landsd/71245:0':('1299619759T20180308',6),
 'landsd/83090:0':('1311919919T20180308',6),
 'landsd/129770:0':('1295719970T20180308',6.2),
 'landsd/161537:0':('1293919909T20180308',6.2),
 'landsd/161745:0':('1310019859T20180820',6),
 'landsd/232103:0':('1306220035T20180308',5.5),
}

def verify(models,review,physical,lifecycle,features,forms):
    assert len(models)==1
    model=models[0];assert model['uid']==UID and model['sha256']==SHA and model['triangles']==32238
    assert model['proceduralWindows']is False and not model.get('supportDependencies') and not model.get('activationGroup')
    assert model['suppressesBuildingUids']==list(ROOFS)
    assert all(model[k]is False for k in ['publicationApproved','placementReviewed','identityReviewApproved','sourceIdentityReviewed'])
    for decision in [review,physical]:
        assert decision['sourceSHA256ByUid']=={UID:SHA}
        assert all(decision[k]is True for k in ['identityAccepted','sourceSpecificPhysicalInterpretationAccepted','completeNeighbourInterpretationAccepted','visualAcceptance'])
        assert decision['sourceGeometryChanges']==decision['sourcePoseChanges']==0
        assert decision['surveyedRoofCase']=='passenger162768-original-wave-roof-v1'
    assert review['currentManifest']==physical['currentManifest']
    assert forms[UID]['buildingCSUID']=='1302919914T20180305'
    replacements=review['conditionalCanopyReplacements']
    assert replacements==physical['conditionalCanopyReplacements'] and len(features)==len(replacements)==6
    assert [r['basicUid']for r in replacements]==list(ROOFS)
    for replacement,feature,(basic,(csuid,base)) in zip(replacements,features,ROOFS.items()):
        assert set(replacement)=={'sourceUid','basicUid','sourceSHA256','sourceFormSHA256','basicFormSHA256','onlyWhileExactOwnerActive','approved'}
        assert replacement['sourceUid']==UID and replacement['basicUid']==basic and replacement['sourceSHA256']==SHA
        assert replacement['sourceFormSHA256']==form_sha(forms[UID]) and replacement['basicFormSHA256']==form_sha(forms[basic])
        assert replacement['onlyWhileExactOwnerActive']is True and replacement['approved']is True
        b=forms[basic];assert b==feature['exactBasicForm']
        assert b['structureType']=='Open-sided Structure' and b['buildingCSUID']==csuid
        assert b['baseSource']==b['heightSource']=='landsd' and b['baseHeightHKPD']==base and b['topHeightHKPD']==37
        assert feature['currentManifest']==review['currentManifest']
        assert feature['sourceUid']==UID and feature['sourceSHA256']==SHA and feature['basicUid']==basic
        assert feature['reviewedArchitecturalRole']=='surveyed-flat-subdivision-of-same-wave-roof'
        assert feature['privateCanopyExperimentApproved']is True and feature['publication']is False and feature['installationApproved']is False
        assert len(feature['fourWorldRoofContext'])==4
        # This reviewed case binds the actual four-world evidence; coverage alone
        # never qualifies a future source or arbitrary neighbouring BASIC actor.
        assert {r['mode']for r in feature['fourWorldRoofContext']}=={'packed','completeLiteralWorldPosition','completeExplicitLeftAssociatedFloat32WorldPosition','completeExplicitBalancedFloat32WorldPosition'}
        assert all(r['uid']==basic and .993<=r['originalProjectionCoverageFraction']<=1.000000001 for r in feature['fourWorldRoofContext'])
    assert physical['terrainCandidate']['sha256']==TERRAIN
    assert physical['completeOriginalFaces']==32238 and physical['currentNativeActors']==7027
    assert physical['completeFourWorldFoundations']is True
    foundation=physical['ordinaryFoundationRows'];assert len(foundation)==4
    assert all(r['establishedFoundationPolicyPassed']and r['triangles']==r['completeTerrainTriangles']==32238 and r['fullyBuriedUpwardTriangles']==0 for r in foundation)
    posts=physical['surveyedFallbackPosts'];assert len(posts)==8
    assert all(r['after']['uncoveredPostFootprintM2']==0 and r['after']['maximumPostBottomAboveGroundM']<=0 and r['completeOverlayMaximumAbsoluteGroundChangeM']<.00004 for r in posts)
    assert physical['retainedAuxiliaryUids']==['landsd/153422:0','landsd/332872:0']
    assert physical['rawBroadFootprintFlagRetained']is True and physical['globalClearanceExceptionsCreated']==0
    assert lifecycle['passed']is True and not lifecycle['pageErrors']and lifecycle['publication']is False
    cases=lifecycle['cases'];assert len(cases)==2 and {(r['width'],r['failedUid'])for r in cases}=={(1280,None),(390,UID)}
    for case in cases:
        assert case['completeGroupEvicted']and case['baseOnlyRestoredCompleteGroup']and not case['audit']['violations']
        assert case['sources']==[dict(uid=UID,sha256=SHA,triangles=32238,active=True)]
        phases={r['phase']:r for r in case['canopyLifecycle']}
        expected={'original-active','base-only','auto-restored','evicted-return-base-only'}|({'failed-download'}if case['failedUid']else set())
        assert set(phases)==expected and len(phases)==len(case['canopyLifecycle'])
        for phase,row in phases.items():
            active=phase in ['original-active','auto-restored']
            assert row['ownerActive']is active and row['canopies']==[dict(uid=u,basicCanopyVisible=not active)for u in ROOFS]
        if case['failedUid']:assert case['failureKeptAllBasics']
    return dict(sourceUid=UID,sourceSHA256=SHA,basicUids=list(ROOFS),exactSurveyedSourceSpecificCase=True,completeLifecycleVerified=True,publication=False)
