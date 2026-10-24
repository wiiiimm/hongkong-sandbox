"""Exact source descriptors and narrowly proposed applicability, never strict pass."""
from fractions import Fraction as F
NARROW={'landsd/338946:0:ground-contact-unresolved','landsd/338946:0:sampled-ground-gap-below-model-bottom','original-support-interface-unresolved'}

def face_descriptor(face_id,points):
    p=[[F(v)for v in q]for q in points];assert len(p)==3 and all(len(q)==3 for q in p)
    a=[p[1][i]-p[0][i]for i in range(3)];b=[p[2][i]-p[0][i]for i in range(3)];n=[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];ys=[q[1]for q in p]
    return dict(originalFaceID=face_id,exactBinary64InputPoints=[[str(v)for v in q]for q in p],exactHeightIntervalM=[str(min(ys)),str(max(ys))],exactCrossProduct=[str(v)for v in n],exactNormalYIsZero=n[1]==0,exactProjectedSignedDoubleAreaXZ=str(-n[1]),nondegenerate=any(n),minimumHeightVertexIDs=[i for i,y in enumerate(ys)if y==min(ys)],edgeHeightEndpointPairs=[[str(ys[i]),str(ys[(i+1)%3])]for i in range(3)],wallBandInterpretationFromSourceReviewNotExactVerticalAssertion=True,noSourceTopologyOrStructuralCertificate=True,noContactOrRootCredit=True)

def proposal(raw_reasons,strict,unmatched,complete_context):
    assert strict['passed']is False and strict['samples']==138 and strict['strictContacts']==97 and strict['wallIntersections']==0
    assert sorted(unmatched)==[11,12,15,16,17,18,19,20,21,22,23,24,25]
    raw=sorted(set(raw_reasons));scoped=sorted(set(raw)&NARROW) if complete_context else[]
    return dict(rawExistingGuardReasons=raw,proposedSourceApplicabilityDisposition=scoped,otherReasonsNeverResolved=sorted(set(raw)-set(scoped)),strictOriginalInterfacePassed=False,strictOriginalInterfaceVerbatim=strict,all41FailuresRemainNumericallyFailed=True,sourceInterpretationReviewRequired=True,proposedFunctionalApplicabilityOnly=bool(complete_context and scoped),independentSupportFor13UnmatchedPointsProved=False,unmatchedPointIDsRetained=unmatched,roundedBodyCensusIsNotTopologyCertificate=True,noToleranceOrSourceGeometryChange=True,physicalAccepted=False,installationApproved=False)
