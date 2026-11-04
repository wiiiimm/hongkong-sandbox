"""Named Southside source proposals only; retained failures never become waivers.

Derives exact positive original-edge subsegments from byte-bound saved finite
proofs. No source/ground geometry is generated; terminal visuals cannot root.
"""
from fractions import Fraction as F
import hashlib,json,struct
UIDS=['landsd/315025:0','landsd/300867:0']
MODES={'providerOriginal','actualLiteral','explicitLeftAssociatedF32ModelMatrix','explicitBalancedF32ModelMatrix'}
CLOSURES={59:[1044,1045],128:[5294,5295,5296,5297],130:[5320]}
RESIDUAL={59,119,128,130}
def canonical(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def certify_original_subsegment(edge,proof,*,expected_saved_proof_sha256):
 assert canonical(proof)==expected_saved_proof_sha256
 assert len(edge)==2 and all(len(p)==3 for p in edge)
 a,b=[tuple(F(float(v))for v in p)for p in edge];assert a!=b
 source_sha=hashlib.sha256(struct.pack('<9d',*(list(map(float,a))+list(map(float,b))+list(map(float,b))))).hexdigest()
 coarse=proof['coarse'];assert coarse['sourceFaceSHA256']==source_sha and coarse['groundProjectionCovered']is True
 assert coarse['completeOriginalProjectionCoverage']['exactProjectionCovered']is True
 ground_sha=coarse['completeCurrentGroundSHA256'];axis=next(k for k in range(3)if a[k]!=b[k])
 def output(lo,hi,minimum,method):
  assert 0<=lo<hi<=1 and minimum>0
  return dict(exactOriginalParameters=[str(lo),str(hi)],exactOriginalEndpoints=[[str(a[k]+t*(b[k]-a[k]))for k in range(3)]for t in [lo,hi]],exactCertifiedPositiveClearanceM=str(minimum),completeSavedFiniteProofSHA256=expected_saved_proof_sha256,completeGroundSHA256=ground_sha,method=method,wholeEdgeFailureRetained=not(proof['completeFiniteOrdinaryBoundProved']and F((coarse if coarse['existingOrdinaryClearanceBoundProved']else proof['paired'])['exactCertifiedLowerClearanceM'])>0),geometryChanges=0,rootCredit=False)
 chosen=coarse if coarse['existingOrdinaryClearanceBoundProved']else proof['paired']
 if chosen is not None and chosen['groundProjectionCovered']and F(chosen['exactCertifiedLowerClearanceM'])>0:
  assert chosen['sourceFaceSHA256']==source_sha and chosen['completeCurrentGroundSHA256']==ground_sha
  return output(F(0),F(1),F(chosen['exactCertifiedLowerClearanceM']),'saved-complete-strict-edge')
 ceiling=F(coarse['exactMaximumAllCandidateOriginalGroundHeightM']);low,high=sorted([F(0),F(1)],key=lambda t:a[1]+t*(b[1]-a[1]));high_y=a[1]+high*(b[1]-a[1])
 if high_y>ceiling:
  low_y=a[1]+low*(b[1]-a[1]);cut=low if low_y>ceiling else (((ceiling+high_y)/2)-a[1])/(b[1]-a[1]);lo,hi=sorted([cut,high]);minimum=min(a[1]+t*(b[1]-a[1])for t in [lo,hi])-ceiling
  return output(lo,hi,minimum,'saved-complete-candidate-height-ceiling')
 paired=proof['paired'];assert paired is not None and paired['sourceFaceSHA256']==source_sha and paired['completeCurrentGroundSHA256']==ground_sha and paired['groundProjectionCovered']
 assert paired['completeOriginalProjectionCoverage']['exactProjectionCovered']is True
 intervals=[];knots={F(0),F(1)}
 for piece in paired['allExactFiniteSourceGroundPieces']:
  samples=[]
  for p in piece['allExactSourcePrismIntersectionVertices']:
   xyz=tuple(F(v)for v in p['exactOriginalSourcePoint']);t=(xyz[axis]-a[axis])/(b[axis]-a[axis]);assert 0<=t<=1 and xyz==tuple(a[k]+t*(b[k]-a[k])for k in range(3));samples.append((t,F(p['exactGapM'])))
  assert samples;knots.update(t for t,v in samples);lo,y0=min(samples);hi,y1=max(samples)
  if lo==hi:continue
  slope=(y1-y0)/(hi-lo);intercept=y0-slope*lo;assert all(slope*t+intercept==v for t,v in samples)
  if slope and lo<-intercept/slope<hi:knots.add(-intercept/slope)
  intervals.append((lo,hi,slope,intercept))
 assert intervals
 for lo,hi in zip(sorted(knots),sorted(knots)[1:]):
  if lo==hi:continue
  mid=(lo+hi)/2;active=[p for p in intervals if p[0]<=mid<=p[1]]
  if not active or any(s*mid+k<=0 for x,y,s,k in active):continue
  left=(3*lo+hi)/4;right=(lo+3*hi)/4
  minimum=min(s*t+k for x,y,s,k in active for t in [left,right]);assert minimum>0
  return output(left,right,minimum,'saved-complete-finite-prism-affine-piece-interior')
 return None

def reconcile(review,grade,*,expected_review_sha256,expected_grade_sha256):
 assert canonical(review)==expected_review_sha256 and canonical(grade)==expected_grade_sha256
 assert review['sourceRoleAccepted']is review['currentAcceptance']is review['physicalAccepted']is False
 rows={(q['uid'],q['arithmetic']):q for q in grade['rows']};assert set(rows)=={(u,m)for u in UIDS for m in MODES}
 roles=review['complete19SourceRoleAndHostObligations'];assert len(roles)==19
 expected={(UIDS[0],i)for i in [16,59,76,101,119,120,127,128,129,130,131,134,141,143,146,149,152]}|{(UIDS[1],i)for i in [33,35]};assert {(q['uid'],q['historicalOriginalComponent'])for q in roles}==expected
 out=[]
 for role in roles:
  uid=role['uid'];component=role['historicalOriginalComponent'];ids=role['completeHistoricalPartVerbatim']['allOriginalFaceIds'];modes=[]
  assert role['sourceRoleAccepted']is role['rootCredit']is False
  for mode in sorted(MODES):
   row=rows[uid,mode];body=next(q for q in row['completeBodyObligationAccount']if q['originalComponent']==component);assert body['completeOriginalFaceIds']==ids and body['rootCredit']is body['fullBodyRootProved']is False
   saved=next(q for q in role['actualSavedBodyModeObligations']if q['arithmetic']==mode);assert saved['bodyVerbatim']==body and saved['completeWorldSHA256']==row['completeWorldSHA256']and saved['completeAuthenticGroundSHA256']==row['completeGroundSHA256']
   failures=body['authenticatedResidualIds'];paths=saved['diagnosticPathsVerbatim'];contacts=row['completeFailedSteepGradeContactInventory']['contacts'];genuine={c['sourceFaceA']for c in contacts if c['dimension']>0 and c['sourcePrimitiveDimensionA']==c['sourcePrimitiveDimensionB']==2};proposed=[]
   for p in paths:
    assert p in row['wholeOriginalSharedEdgeAndCapExposure'] and p['sourceOriginalComponent']==component and set(p['completeSourceFacePath'])<=set(ids)
    segments=[]
    if p['nonemptyOriginalWallPath']and p['sourceFace']in genuine and p['terminalCapWholeFiniteStrictlyClear']:
     assert p['completeSourceFacePath'][0]==p['sourceFace']and len(p['completeSourceFacePath'])>=2 and not set(p['completeSourceFacePath'])&set(CLOSURES.get(component,[]))and not set(p['completeSourceFacePath'])&set(row['allZeroFacesUncredited'])
     assert [i['sourceFaces']for i in p['interfaces']]==[list(pair)for pair in zip(p['completeSourceFacePath'],p['completeSourceFacePath'][1:])]
     for iface in p['interfaces']:
      choices=[certify_original_subsegment(e['exactWholeOriginalNonzeroSharedEdge'],e['completeFiniteExposureProof'],expected_saved_proof_sha256=canonical(e['completeFiniteExposureProof']))for e in iface['allExactSharedEdges']];segments.append(next((c for c in choices if c is not None),None))
    proposed.append(dict(sourceFace=p['sourceFace'],rawWholeEdgePathVerbatim=p,positiveOriginalSubsegmentInterfaces=segments,nonemptyGradeToClearCapWithPositiveExposedInterfaces=bool(segments and all(s is not None for s in segments)),rootCredit=False))
   closure=CLOSURES.get(component,[]);assert set(closure)<=set(failures) and set(body['excludedNonsteepResidualIds'])==set(closure)
   finite=row['allCompleteOriginalFiniteRecords'];assert all(finite[i]['sourceFace']==i for i in ids)
   if not failures:assert all(finite[i]['authenticatedOriginalGroundComparison']['completeFiniteOrdinaryBoundProved']for i in ids)
   modes.append(dict(arithmetic=mode,completeWorldSHA256=row['completeWorldSHA256'],completeAuthenticGroundSHA256=row['completeGroundSHA256'],completeOriginalFaceIds=ids,rawBodyObligationVerbatim=body,retainedLowerClosureIds=closure,lowerClosuresProvideNoBridge=True,positiveExposedPathProposals=proposed,unresolvedSteepResidualIds=[p['sourceFace']for p in proposed if not p['nonemptyGradeToClearCapWithPositiveExposedInterfaces']],allOriginalFacetsOrdinaryClear=not failures,sourceRoleAccepted=False,rootCredit=False))
  kind='standing-or-embedded-original-skin-review-required'if component in RESIDUAL and uid==UIDS[0]else'authored-terminal-placement-review-required'
  out.append(dict(uid=uid,originalComponent=component,sourceRoleRoute=kind,sourceDescription=role['rootObservedSourceCategoryProposalOnly'],completeModes=modes,rawHistoricalContactsVerbatim=role['actualHistoricalSourceContactRecords'],rawCoordinateBandNegativeVerbatim=role['historicalCoordinateBandNegativeVerbatim'],sourceRoleAccepted=False,providesInterComponentRootOrBridge=False))
 return dict(uids=UIDS,complete19SourceSpecificRouteProposals=out,all19HistoricalFailuresRetained=True,onlySavedFiniteProofsReused=True,terminalVisualsNeverRootOrBridge=True,lowerClosureGeometryIsNotFoundationPermission=True,sourceRoleAccepted=False,currentAcceptance=False,physicalAccepted=False,installationApproved=False,sourceGeometryChanges=0,terrainGeometryChanges=0)
