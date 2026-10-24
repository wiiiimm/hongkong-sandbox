"""Exact bounded ROOT source interpretation, candidate certificate only."""
import hashlib,json
UID='landsd/26195:0';SOURCE='50da67a3a009c3c832d2bfdbd08640c89d958ef8cf077d1c172e7059900f8af9'
def sha(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def verify(replayed,root_record,interpretation):
 replayed=json.loads(json.dumps(replayed,allow_nan=False))
 assert replayed==root_record,'Exact completed source candidate reconciliation differs'
 assert root_record['uid']==interpretation['uid']==UID and root_record['sourceSHA256']==interpretation['sourceSHA256']==SOURCE
 assert interpretation['reviewer']=='ROOT'and interpretation['sourceIdentificationOnly']and interpretation['actualUnchangedSourceViewsInspected']
 assert not interpretation['engineeringFunctionClaim']and interpretation['geometryChanges']==0 and interpretation['sourceFacet154SegmentOnly']
 assert not any(interpretation[k]for k in ['gradeRootAccepted','physicalAccepted','installationApproved','legacyAcceptanceBackfillAllowed'])
 assert root_record['binding']==interpretation['completeSavedBinding']and root_record['allFourWorldBindings']==interpretation['allFourWorldBindings']
 assert root_record['completeBody0Faces']==interpretation['completeBody0FaceIds']and len(set(root_record['completeBody0Faces']))==5062
 assert root_record['completeOriginalBodies']==118 and root_record['all42GradeRoutesComplete']and root_record['sourceInterpretationBound']and root_record['body0RoleRootCandidateReady']
 assert len(set(interpretation['completeGradeFaceIds']))==42 and set(interpretation['completeGradeFaceIds'])<=set(root_record['completeBody0Faces'])
 assert not any(root_record[k]for k in ['gradeRootAccepted','wholeSourcePhysicalAccepted','installationApproved','legacyAcceptanceBackfillAllowed','geometryChanges','sourceFacet154WholeRoleCredit'])
 assert root_record['remaining117BodyObligationsIndependent']and root_record['all376OrdinaryClearStrictWarningsRetained']
 assert set(root_record['allFourWorldBindings'])=={'original','literal','explicitLeftF32','explicitBalancedF32'}
 for b in root_record['allFourWorldBindings'].values():
  assert b['completeFaces']==46918;r=root_record['distinctRouteEvidence'][b['proofTupleSHA256']]
  assert r['complete42GradeFaceIds']==interpretation['completeGradeFaceIds']and r['all42PositiveDimensionalGradeAndCapRoutesReused']and r['sourceFacet154SegmentOnly']
  assert len(r['ordinaryClearStrictWarningsRetained'])==376 and len(r['strictCapsBySeed'])==42
 return dict(contract='west-wing-complete-current-body0-source-bound-candidate-role-certificate-v1',uid=UID,sourceSHA256=SOURCE,completeSourceFaces=46918,completeSourceBodies=118,completeBody0FaceIds=root_record['completeBody0Faces'],complete42GradeFaceIds=interpretation['completeGradeFaceIds'],allFourStreamBindings=root_record['allFourWorldBindings'],savedSourceCandidateReconciliationSHA256=sha(root_record),boundedROOTInterpretationSHA256=sha(interpretation),binding=root_record['binding'],body0SourceRoleCandidateQualified=True,sourceFacet154SegmentOnly=True,ordinaryClear376WarningsRetained=True,remaining117BodyObligationsIndependent=True,groundRootAccepted=False,bodySupportAccepted=False,physicalAccepted=False,installationApproved=False,legacyAcceptanceBackfillAllowed=False,sourceGeometryChanges=0,requiredActualRootQualification='Exact source-bound grade role plus complete current original identity/foreign/native/foundation/water/runtime guards before root acceptance; no catalogue-only or candidate-only support transfer.')
