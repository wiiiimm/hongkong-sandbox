"""Actual existing viewer gates and exact reviewed warning; never strict pass."""
from aqua_three_foundation_saved_attribution_v1_20261014 import validate_runtime_rows
from aqua_exact_existing_warning_review_v1_20261014 import FAILED,REASON
MODES={'providerOriginal','actualLiteral','explicitLeftAssociatedF32','explicitBalancedF32'}
def qualify(diag,finite,packet,identity,disposition,uid,foreign):
    assert identity['passed']and not identity['reasons']and identity['foreignCollisionExemption']is False and identity['noCommonOwnershipOrSupportClaim']
    assert diag['uid']==uid and diag['ordinaryNumericReasons']==[REASON]and diag['loaderAccepted']==diag['runtimeChecksPassed']==1 and diag['runtimeExceptions']==0
    validate_runtime_rows(diag['rawRuntimeConcerns'],uid);assert diag['neighbourRegressionReasons']==[]and diag['nativeNeighbourChecks']['blocked']==[]
    assert disposition['existingReasonOnly']==REASON and disposition['exactFunctionalSourceFaceIDs']==FAILED and not disposition['rawStrictFoundationPassed']and not disposition['otherFaceApplicabilityGranted']
    assert not packet['strictFoundationAccepted']and len(packet['allOtherPartialBelowMinusHalfSourceFaceIDs'])==278
    baseline=sorted(packet['allOtherPartialBelowMinusHalfSourceFaceIDs']+FAILED);assert len(set(baseline))==281
    own=[r for r in finite['rows']if r['uid']==uid];other=[r for r in finite['rows']if r['uid']==foreign]
    assert len(own)==len(other)==4 and {r['arithmetic']for r in own}=={r['arithmetic']for r in other}==MODES
    for row in own:assert row['completeFaces']==22735 and row['rawProjectionUncoveredFaceIDs']==[]and row['rawOrdinaryUnprovedFaceIDs']==baseline and row['ownedRawBelowGradeIDsOutsideSaved281']==[]
    for row in other:assert row['completeFaces']==116 and row['rawProjectionUncoveredFaceIDs']==[]
    contacts=finite['foreignCollisionRows'];assert len(contacts)==4 and {r['arithmetic']for r in contacts}==MODES
    for row in contacts:assert row['completeOwnedFaces']==22735 and row['completeForeignFaces']==116 and row['contactCount']==0 and not row['sourceCollisionDispositionPending']
    assert finite['completeEightWorldFaceStreams']and finite['completeFourCoherentForeignCollisionStreams']and finite['allRawKernelNegativesRetained']and not finite['rawStrictFoundationPassed']
    return dict(uid=uid,remainingActualExistingViewerReasons=[],resolvedExistingReasonByExactSourceReview=[REASON],reviewedFaceIDs=FAILED,rawStrictFoundationPassed=False,rawOrdinaryNumericReasonsVerbatim=diag['ordinaryNumericReasons'],all278PartialFaceIDsVerbatim=packet['allOtherPartialBelowMinusHalfSourceFaceIDs'],wholeMinimumGapVerbatim=packet['minimumWholeSurfaceGapVerbatim'],fourWorldRawUnproved281Retained=True,noNewAllVertexStructuralRootWatertightnessAdmission=True,noOtherFaceApplicabilityGranted=True,independentForeignCollisionExemption=False,completeFourWorldOwnedProjectionCovered=True,completeFourWorldIndependentForeignContactsZero=True,foreignOriginalGradeRowsNotOwnedInstallationApproval=other,identityVerbatim=identity,ROOTDispositionVerbatim=disposition,privateStageSourceQualified=True,physicalFinalAccepted=False,publication=False,newlyInstalled=0,stagedLivePickingCollisionMobileAndImageReviewRequired=True)
