"""Only the actual ROOT-reviewed exact-source warning disposition; no strict pass."""
import json
REASON='terrain-intersects-source-over-0.5m';FAILED=[7525,7526,7527]
def encoded(x):return json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def bind_review(review,packet,*,uid,csuid,source_sha,current_manifest,current_snapshot):
    assert review['schema']=='exact-original-source-functional-applicability-v1'and review['reviewer']=='ROOT'
    assert review['rootFunctionalReviewAccepted']and review['sourceInterpretationAccepted']and review['acceptedReasons']==[REASON]and review['applicableExistingReason']==REASON
    assert review['UID']==uid and review['CSUID']==csuid and review['sourceSHA256']==source_sha and review['currentManifestSHA256']==current_manifest and review['currentSnapshot']==current_snapshot
    assert review['exactFailedFaceIDs']==FAILED and review['all278PartialFacesRetained']and review['partialFaceRolesRemainUnassigned']and review['doesNotApproveOtherFacesOrModels']
    assert not review['rawStrictFoundationPassed']and not review['physicalAccepted']and not review['publicationApproved']and review['governmentGeometryChanges']==review['terrainChanges']==review['sourcePoseChanges']==0 and review['sourceScale']==1
    assert encoded(review['rawFoundationVerbatim'])==encoded(packet['rawFoundationVerbatim'])and review['rawOrdinaryReasonsVerbatim']==packet['rawOrdinaryReasonsVerbatim']==[REASON]and review['wholeMinimumGapVerbatim']==packet['minimumWholeSurfaceGapVerbatim']
    w=review['worldAndGroundBindings'];assert w['UID']==uid and w['CSUID']==csuid and w['sourceSHA256']==source_sha and w['currentManifestSHA256']==current_manifest and w['currentSnapshot']==current_snapshot
    for key in ['completeActualGroundSHA256','completeLiteralWorldSHA256','completeSavedOriginalWorldSHA256','actualRuntimeArrays','allCurrentGroundSourceInputRefs']:assert encoded(w[key])==encoded(packet[key])
    assert encoded(w['savedOriginalCensus'])==encoded(packet['savedFullOriginalSourceCensus'])
    return dict(existingReasonOnly=REASON,exactFunctionalSourceFaceIDs=FAILED,rootDecisionVerbatim=review,rawStrictFoundationPassed=False,raw278PartialsRemainContext=True,otherFaceApplicabilityGranted=False,foreignCollisionExemption=False,physicalAccepted=False,installationApproved=False)
