"""DRAFT source-bound completed-proof reconciliation; no transferred acceptance."""
import hashlib,json
from fractions import Fraction as Q
from west_wing26195_body0_saved_facet_role_partition_draft_v1_20261012 import partition
UID='landsd/26195:0';SOURCE='50da67a3a009c3c832d2bfdbd08640c89d958ef8cf077d1c172e7059900f8af9'
CONTRACT='original-exposed-wall-finite-upper-grade-root-graph-v1'
def sha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def binding(f,g,c,s,v,identity,contracts):
 return dict(completeSavedProofsSHA256=sha([f,g,c,s,v]),exactSourceIdentitySHA256=sha(identity),existingCarrierCodeRefsSHA256=sha(contracts))
def verify(f,g,c,s,v,identity,contracts,*,expected_binding,interpretation=None):
 assert binding(f,g,c,s,v,identity,contracts)==expected_binding
 assert identity['uid']==UID and identity['sourceSHA256']==SOURCE and identity['sourcePreserved'] and identity['unitScale']==1 and identity['poseChanges']==0
 assert contracts['actualContract']==CONTRACT and not contracts['acceptanceTransferred']
 p=partition(f,g,c,s,v);body=f['originalBodyCensus']['sharedEdgeConnectedComponents'][0];bodyset=set(body);streams={};complete_grade_ids=None
 for key,proof in f['distinctCompleteFiniteProofs'].items():
  records=proof['allWholeFacetProofs'];gr=g['distinctBoundedRouteDiagnostics'][key];cr=c['distinctBoundedCorridorDiagnostics'][key];sr=s['distinctBoundedDiagnostics'][key]
  grades={r['seedFace']:r for r in gr['routes']};ids=sorted(grades)
  if complete_grade_ids is None:complete_grade_ids=ids
  assert ids==complete_grade_ids and len(ids)==42 and set(ids)<=bodyset
  caps={};grade_refs=[]
  for i,r in grades.items():
   assert r['genuineExposedGradeDiagnostic'] and Q(r['completeUnchangedVertexExposure']['exactExposureLowerBoundM'])>0
   assert r['verifiedPositiveUpperGroundIntervals']
   for interval in r['verifiedPositiveUpperGroundIntervals']:
    ends=interval['nominatedInterval']['exactSegmentEndpoints'];assert len(ends)==2 and tuple(map(Q,ends[0]))!=tuple(map(Q,ends[1]))
    cert=interval['completeUpperEnvelopeSegmentProof'];assert cert['closedWholeSegmentProjectionCovered'] and Q(cert['exactMinimumGapM'])==0
   if r['boundedOriginalPath']:
    assert set(r['boundedOriginalPath'])<=bodyset and r['allTraversedWholeEdgesStrictlyExposed']
    cap=r['exactStrictPositiveCap'];assert cap in bodyset and records[cap]['strictPositiveFiniteProved'] and records[cap]['ordinaryFiniteProved'];caps[i]=cap
   grade_refs.append(dict(sourceFace=i,positiveDimensionalGradeProofReusedSHA256=sha(r),wholeFacetBurialRoleAccepted=False))
  for r in cr['boundedConnectedRoutes']:
   if not r['diagnosticRouteFound']:continue
   i=r['seedFace'];assert i in grades and i not in caps and r['completePathTransitionCertificates'] and r['exactStrictPositiveCapCertificate']
   cap=r['strictPositiveNonsteepCapFace'];assert cap in bodyset and records[cap]['strictPositiveFiniteProved'];caps[i]=cap
   for step in r['completePathTransitionCertificates']:
    if 'sourceFaces'in step:assert set(step['sourceFaces'])<=bodyset
  assert sr['diagnosticRouteFound'] and sr['sourceContextFaces']==[153,154,44545] and not sr['wholeFacet154StrictPositiveClaim'] and not sr['newGradeRootClaim']
  assert 153 not in caps and records[44545]['strictPositiveFiniteProved'] and sr['strictFullCap44545']==records[44545] and not records[154]['strictPositiveFiniteProved'];caps[153]=44545
  assert set(caps)==set(grades)
  streams[key]=dict(complete42GradeFaceIds=ids,all42PositiveDimensionalGradeAndCapRoutesReused=True,gradeProofBindings=grade_refs,strictCapsBySeed=caps,sourceFacet154SegmentOnly=True,ordinaryClearStrictWarningsRetained=p['distinctSavedPartitions'][key]['remainingOrdinaryPassStrictUncertifiedFaces'])
 interpretation_ok=False
 if interpretation is not None:
  assert interpretation['reviewer']=='ROOT' and interpretation['sourceIdentificationOnly'] and not interpretation['engineeringFunctionClaim']
  assert interpretation['uid']==UID and interpretation['sourceSHA256']==SOURCE and interpretation['completeBody0FaceIds']==body
  assert interpretation['completeGradeFaceIds']==complete_grade_ids and interpretation['allFourWorldBindings']==f['allFourStreamBindings'] and interpretation['completeSavedBinding']==expected_binding
  assert interpretation['actualUnchangedSourceViewsInspected'] and interpretation['sourceViewRefs'] and interpretation['observedRole']=='source-authored-exposed-grade-crossing-wall-surfaces-of-connected-body0'
  interpretation_ok=True
 return dict(contract='west-wing-body0-source-bound-saved-grade-role-reconciliation-draft-v1',uid=UID,sourceSHA256=SOURCE,existingCarrierContract=CONTRACT,completeBody0Faces=body,completeOriginalBodies=118,allFourWorldBindings=f['allFourStreamBindings'],distinctRouteEvidence=streams,all42GradeRoutesComplete=True,sourceInterpretationBound=interpretation_ok,body0RoleRootCandidateReady=interpretation_ok,remainingSourceInterpretation=None if interpretation_ok else 'ROOT-inspected complete body0 and focused 42 grade-wall source context with saved route/cap IDs; source authorship/exposed-wall interpretation only, no engineering foundation intent.',all376OrdinaryClearStrictWarningsRetained=True,sourceFacet154WholeRoleCredit=False,remaining117BodyObligationsIndependent=True,wholeSourcePhysicalAccepted=False,gradeRootAccepted=False,installationApproved=False,legacyAcceptanceBackfillAllowed=False,geometryChanges=0,binding=expected_binding)
