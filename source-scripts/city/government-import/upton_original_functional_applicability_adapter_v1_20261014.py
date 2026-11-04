"""Exact two-source applicability; raw numerical failures remain false/verbatim."""
import copy
from upton_wall_band_functional_context_v1_20261014 import NARROW
OWNED=['landsd/12728:0','landsd/338946:0']
EXPECTED={OWNED[0]:('3217816493P20150615','4f177100defad797c23530d4577676041bcbc6f6ee79de026f2af01c112552d2'),OWNED[1]:('3217516509T20150615','91112a4c6ef150da224da45c98064fb68b6a2523f9a45fabace8b2e7ff78e9bf')}
POLICY='upton-exact-original-authored-lower-facade-band-functional-applicability-v1'

def apply(*,decision,packet,descriptor_ref,display_ref,image_refs,packet_ref,raw_reasons,strict):
    assert decision['sourceFunctionalDispositionAccepted']is True and decision['reviewer']=='Codex ROOT'and decision['reviewType']=='exact-original-source-functional-applicability'
    assert decision['all12ExportedImagesInspected']is True
    assert decision['proposedDisposition']==packet_ref and decision['exact36FourWorldDescriptorsReviewed']==descriptor_ref and decision['displayBinding']==display_ref
    assert sorted(decision['imagesActuallyInspected'],key=lambda q:q['path'])==sorted(image_refs,key=lambda q:q['path']) and len(image_refs)==12
    assert decision['scope']==packet['scope']and decision['sourceBindings']==packet['scope']['sourceBindings']and decision['strictOriginalInterfacePassed']is False and decision['independentSupportFor13UnmatchedPointsProved']is False
    assert decision['strictOriginalInterfaceVerbatim']==strict and decision['all41FailuresRemainNumericallyFailed']is True
    assert decision['noNumericThresholdWaiver']is True and decision['noSourceTopologyStructuralOrEngineeringCertificate']is True and decision['sourceGeometryChanges']==0 and decision['originalFixedOneMetreScaleUnchanged']is True
    assert not decision['publicationApproved']and not decision['physicalAccepted']and not decision['installationApproved']
    scope=packet['scope'];assert scope['uids']==OWNED and len(scope['sourceBindings'])==8
    seen=set()
    for r in scope['sourceBindings']:
        assert (r['buildingCSUID'],r['sourceSHA256'])==EXPECTED[r['uid']]
        assert r['mode']in ['original','literal','explicitLeftF32','explicitBalancedF32']and len(r['wholeWorldSHA256'])==64
        assert (r['uid'],r['mode'])not in seen;seen.add((r['uid'],r['mode']))
    assert set(raw_reasons)==NARROW==set(packet['rawExistingGuardReasons'])==set(decision['acceptedReasons'])==set(decision['rawExistingGuardReasons'])
    assert strict==packet['strictOriginalInterfaceVerbatim']and strict['passed']is False and strict['samples']==138 and strict['strictContacts']==97 and strict['wallIntersections']==0 and len(strict['unresolved'])==41
    assert packet['strictOriginalInterfacePassed']is False and packet['all41FailuresRemainNumericallyFailed']is True and packet['independentSupportFor13UnmatchedPointsProved']is False
    assert packet['unmatchedPointIDsRetained']==[11,12,15,16,17,18,19,20,21,22,23,24,25]and packet['otherReasonsNeverResolved']==[]
    assert decision['unmatchedPointIDsRetained']==packet['unmatchedPointIDsRetained']and decision['otherReasonsNeverResolved']==[]
    return dict(policy=POLICY,uids=OWNED,sourceScopeVerbatim=copy.deepcopy(scope),rawReasonsVerbatim=list(raw_reasons),rawStrictInterfaceVerbatim=copy.deepcopy(strict),strictInterfacePassed=False,resolvedByExactSourceFunctionalApplicability=sorted(NARROW),remainingActualPhysicalReasons=[],scriptChecksPassed=True,sourceScopedApplicabilityAccepted=True,rawMetricThresholdResultsNeverRelabelled=True,noIndependent13PointSupportCredit=True,noRoundedBodyTopologyOrEngineeringGate=True,ROOTReviewVerbatim=copy.deepcopy(decision),publication=False,newlyInstalled=0,modelGeometryChanges=0,scriptExternalAICalls=0,sourceEvidenceInterpretationUsedAI=True,aiGeometryModelling=False,stagedLiveMobileBrowserStillRequired=True)
