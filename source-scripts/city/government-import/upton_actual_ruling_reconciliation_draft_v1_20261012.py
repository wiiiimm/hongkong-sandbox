"""UNEXECUTED full actual incidence reconciliation; no new topology gate."""
from pathlib import Path
from fractions import Fraction as F
import ast,json,time,uuid,sys,subprocess
import numpy as np
from run import ROOT,HERE,read,save,connect,reservations
from upton_inherited_overlap_boundary_draft_v1_20261012 import ref,check,module,CURRENT,UIDS,FOREIGN
from upton_actual_candidate_clearance_audit_v1_20261012 import candidate_surface
from upton_actual_ruling_reconciliation_v1_20261012 import full_draw_attribution,prepare,reconcile,saved_change_contract
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-upton-actual-full-draw-ruling-reconciliation-v1-20261012';DOC=BASE/BATCH;PROPOSAL=BASE/(BATCH+'-proposal');LOCAL=HERE/'local'/BATCH;LEASE=LOCAL/'reservation.json'
PRIOR=BASE/'government-xl-upton-inherited-ring-overlap-finite-boundary-v1-20261012';NOM=BASE/'government-xl-upton-original-tin-current-ring-join-nomination-v2-20261012';CAP=BASE/'government-xl-upton-whole-parent-current-domain-capture-v2-20261012';AUD=BASE/'government-xl-upton-actual-candidate-clearance-measured-overlap-v2-20261012'
HELPER=HERE/'upton_actual_ruling_reconciliation_v1_20261012.py';TEST=HERE/'test_upton_actual_ruling_reconciliation_v1_20261012.py';FREEZER=HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py'
def code_paths():
 roots=[HERE,HERE.parent/'shared-modelling',HERE.parent/'citywide-native',HERE.parent/'island-detail-integration',ROOT/'docs/astra-city/mui-wo-buildings/review',HERE.parent/'assembly-support-review'];seen=set();todo=[Path(__file__),HELPER,TEST,FREEZER]
 while todo:
  p=todo.pop().resolve()
  if p in seen:continue
  seen.add(p)
  for n in ast.walk(ast.parse(p.read_text())):
   names=[n.module]if isinstance(n,ast.ImportFrom)and n.module else[x.name for x in n.names]if isinstance(n,ast.Import)else[]
   for name in names:
    for root in roots:
     q=root/(name.replace('.','/')+'.py')
     if q.is_file():todo.append(q)
 return sorted(seen)
def schema_only():
 pins=read(PROPOSAL/'draft-pins.json');assert pins['caller']==ref(Path(__file__))and pins['helper']==ref(HELPER)and pins['test']==ref(TEST)
 for q in pins['inputRefs']:check(q)
 boundaries=read(PRIOR/'complete-finite-3d-boundary-correspondence.json.gz');overlaps=read(PRIOR/'complete-ring-overlap-inheritance.json.gz');replay=read(NOM/'actual-production-replay.json.gz')
 assert boundaries['completeRows']==len(boundaries['rows'])==556 and overlaps['completePairs']==len(overlaps['rows'])==1260
 assert sum(len(q['allSavedRuledSegments'])for q in boundaries['rows'])==772
 assert sum(not q['rawPriorFixedUpperHeightBandVerbatim']['actualCandidateGroundProof']['verifiedCompleteOriginalEdgeContactBand']for q in boundaries['rows'])==433
 assert len(replay['after']['closedDomainDrawnTriplets'])==10770 and all(len(f)==9 for f in replay['after']['closedDomainDrawnTriplets'])
 nom=read(NOM/'complete-nominations-before-guards.json.gz');assert len(nom['completeCoreBoundaryNominations'])==556
 for i,row in enumerate(boundaries['rows']):
  js=nom['completeCoreBoundaryNominations'][i]['completeUpperEnvelopeNomination']['joinNominations'];assert len(js)==len(row['allSavedRuledSegments'])
  for saved,j in zip(row['allSavedRuledSegments'],js):
   assert saved['exactSavedParameterInterval']==j['exactParameterInterval']
   for name in ['sourceSide','sourceToJoinOrIdenticalRing','oldToActualCapturedRing','oldToJoinOrIdenticalRing']:
    assert 'existingAssociation1M'in saved[name]and 'actualCandidateFaceIDs'in saved[name]
 assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==CURRENT
 return dict(passed=True,caller=ref(Path(__file__)),completeRows=556,completeRulings=772,completeActualDrawnFacets=10770,rawPriorBandNegatives=433,noMathDBOrLease=True)
def owned():
 lease=read(LEASE);assert reservations.owns(lease)and not DOC.exists();last=time.monotonic()
 def pulse(force=False):
  nonlocal last
  if force or time.monotonic()-last>20:assert reservations.heartbeat(lease)['ok']and reservations.owns(lease);last=time.monotonic()
 v=read(PROPOSAL/'helper-validation.json');assert v['passedTests']==19 and v['failedTests']==0 and v['exitCode']==0 and v['helper']==ref(HELPER)and v['test']==ref(TEST);check(v['log'])
 pre=read(PROPOSAL/'schema-preflight.json');assert pre['passed']and pre['caller']==ref(Path(__file__))and pre['noMathDBOrLease']
 receipt=read(PRIOR/'result.json');assert receipt['jobId']=='8afdd174bc4cbf629535df003ea134826b938657fdee7af4b0be390d8cd92dcb'and ref(PRIOR/'result.json')['sha256']=='42f01d81e542e731edbf49b9eeb2bc96d6d60cb1a0e99e57117ff50c677722be'
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 refs=[ref(p)for p in code_paths()]+[ref(PROPOSAL/p)for p in ['METHOD.md','draft-pins.json','schema-preflight.json','helper-validation.json']]+[v['log'],ref(PRIOR/'result.json'),ref(PRIOR/'independent-completed-readback-summary.json')]
 for q in receipt['evidenceRefs']+read(PROPOSAL/'draft-pins.json')['inputRefs']:check(q);refs.append(q);pulse()
 def fence():
  for q in refs:check(q);pulse()
  assert ref(ROOT/'3d-viewer/city/data/manifest.json')['sha256']==CURRENT;pulse(True)
 fence();schema_only();replay=read(NOM/'actual-production-replay.json.gz');nom=read(NOM/'complete-nominations-before-guards.json.gz');patch=read(NOM/'private-native-terrain-candidate.json.gz');boundaries=read(PRIOR/'complete-finite-3d-boundary-correspondence.json.gz');overlaps=read(PRIOR/'complete-ring-overlap-inheritance.json.gz');current=read(CAP/'whole-domain-actual-parent-attribution.json.gz')['rows'][0];lineage=read(PRIOR/'complete-current-source-attribution.json.gz')['rows']
 drawn=np.asarray(replay['after']['closedDomainDrawnTriplets'],dtype='<f8').reshape(10770,3,3);old=np.asarray(current['completeActualDrawnTriplets'],dtype='<f8').reshape(9214,3,3);candidate=candidate_surface(patch,nom['candidateFaceProvenance']);assert len(candidate)==10742
 attribution=full_draw_attribution(drawn,candidate,nom['candidateFaceProvenance'],old,lineage);assert attribution['completeFallbackOccurrences']==28
 prepared=prepare(drawn);DOC.mkdir(parents=True);save(DOC/'complete-actual-draw-attribution.json.gz',attribution);save(DOC/'complete-actual-mesh-descriptive-inventory.json',dict(wholeDrawSHA256=prepared['worldSHA256'],completeFaces=10770,allExactDegenerateFacetsRetained=prepared['exactDegenerateFaceIDs'],completeExactNonzeroCoordinateEdges=len(prepared['edges']),notTopologyAdmissionGate=True,actualSourceParentIdentity=ref(PRIOR/'complete-current-source-attribution.json.gz')))
 cache={};output=[];processed=0
 def inspect(segment,priorproof):
  if priorproof.get('collapsedNominationRetainedUncredited'):return dict(priorVerbatim=priorproof,collapsedNominationRetainedUncredited=True)
  if priorproof['existingAssociation1M']['completeFinite3DCorrespondence']:return dict(priorVerbatim=priorproof,existingCompleteFiniteProofReusedWithoutRerun=True)
  sk=tuple(tuple(str(F(x))for x in p)for p in segment);cachekey=(prepared['worldSHA256'],sk)
  if cachekey not in cache:cache[cachekey]=reconcile([[F(x)for x in p]for p in segment],prepared)
  q=cache[cachekey];used=[]
  if not q.get('collapsedNominationRetainedUncredited'):
   used=sorted(set(q['completeActualDistanceCandidateFaceIDs']))
  return dict(priorVerbatim=priorproof,completeFullDrawReconciliation=q,allSafeCandidateFacetSourceIdentities=[attribution['rows'][i]for i in used],actualOneSidedBoundaryOrPackingDoesNotImposeNewHold=True)
 for i,row in enumerate(boundaries['rows']):
  nominations=nom['completeCoreBoundaryNominations'][i]['completeUpperEnvelopeNomination']['joinNominations'];rows=[]
  for j,saved in zip(nominations,row['allSavedRuledSegments']):
   new=j['ruled']['exactOriginalNewEndpoints'];oldseg=j['ruled']['exactOriginalOldEndpoints'];newproof=saved['sourceToJoinOrIdenticalRing'];oldproof=saved['oldToActualCapturedRing'];joinproof=saved['oldToJoinOrIdenticalRing']
   # Both original narrower target tests remain saved, including every failure.
   # The broader actual mesh query is performed only where one was unproved.
   if oldproof['existingAssociation1M']['completeFinite3DCorrespondence']and not joinproof['existingAssociation1M']['completeFinite3DCorrespondence']:oldproof=joinproof
   rows.append(dict(exactSavedParameterInterval=j['exactParameterInterval'],entirePriorRulingVerbatim=saved,newSideReconciliation=inspect(new,newproof),oldSideReconciliation=inspect(oldseg,oldproof),fullEndConnectorReconciliations=[inspect([new[k],oldseg[k]],saved['bothFullVerticalEndConnectors'][k])for k in range(2)],notSeamAdmissionGate=True));processed+=1;pulse()
  output.append(dict(savedBoundary=i,entirePriorBoundaryVerbatim=row,allRulingReconciliations=rows,wholeNominationSourceEdge=nom['completeCoreBoundaryNominations'][i]['packedSourceEdge']))
  if (i+1)%16==0:save(LOCAL/'progress.json.gz',dict(complete=False,expectedBoundaries=556,processedRulings=processed,rows=output));print(json.dumps(dict(boundaries=i+1,expected=556,rulings=processed)),flush=True)
 assert processed==772;save(DOC/'complete-actual-ruling-reconciliation.json.gz',dict(rows=output,completeBoundaries=556,completeRulings=772,all433OriginalBandNegativesRetained=True,completeWorldFaces=10770,actualFallbackFaces=28,uniqueSavedTraceResults=len(cache),noTopologyAdmissionGate=True))
 changes=[q for q in overlaps['rows']if not q['completeDrawnUnionIdealAffineMax']['proof']['exactIdealAffineMaxUnchanged']];assert len(changes)==15
 contracts=[saved_change_contract(q)for q in changes];save(DOC/'fifteen-saved-affine-change-existing-contract.json.gz',dict(rows=contracts,completeChanges=15,full1260MaxProofReused=ref(PRIOR/'complete-ring-overlap-inheritance.json.gz'),allNonzeroRangesPreserved=True,exactZeroNotRequired=True,noMaxOrRayRerun=True))
 measure=read(AUD/'measured-projection-and-parent-edge.json.gz');rays=read(AUD/'actual-native-sampler-ray-findings.json.gz')
 save(DOC/'existing-overlap-approval-contract-review-inputs.json',dict(candidate=ref(NOM/'private-native-terrain-candidate.json.gz'),wholeCandidateGeometryCanonicalSHA256=measure['candidateGeometryCanonicalSHA256'],measuredProjectedExcessM2=measure['nativeProjectedExcessM2'],fullCurrentInheritance=ref(PRIOR/'complete-ring-overlap-inheritance.json.gz'),fifteenFullAffineRanges=ref(DOC/'fifteen-saved-affine-change-existing-contract.json.gz'),actualProductionSamplerRayEvidence=ref(AUD/'actual-native-sampler-ray-findings.json.gz'),existingRaySamples=rays['samples'],existingRayMaxError=rays['maxError'],existingCurrentParentEdgeGapM=measure['parentEdgeMaximumGap'],existingCurrentParentEdgeLimitM=measure['parentEdgeExistingLimitM'],completeOwnedNativeBasicOrdinaryEvidence=ref(AUD/'complete-candidate-clearance.json.gz'),rawValidatorFailureUnchanged=ref(AUD/'real-validator-outcome.json'),fullBeforeAfterExteriorEvidence=ref(NOM/'actual-production-replay.json.gz'),geometryBoundOverlapApprovalStillRequiresROOTReview=True,noNewTopologyRequirement=True,noApprovalWritten=True,noCandidateEdits=True))
 save(DOC/'diagnostic.json.gz',dict(reconciliation=ref(DOC/'complete-actual-ruling-reconciliation.json.gz'),attribution=ref(DOC/'complete-actual-draw-attribution.json.gz'),existingOverlapContract=ref(DOC/'existing-overlap-approval-contract-review-inputs.json'),noActorSourceDecodeOrRayReruns=True,noCandidateEdits=True,noTopologyAdmissionGate=True,noApprovalWritten=True))
 refs+=[ref(p)for p in DOC.iterdir()if p.is_file()];fence();module(FREEZER,'upton_actual_reconciliation_freezer').freeze(BATCH,'actual-full-draw-incidence-existing-overlap-contract-diagnostic',[check(q)for q in{(q['path'],q['sha256']):q for q in refs}.values()],dict(uids=UIDS,currentManifestSHA256=CURRENT,completeFaces=10770,completeRulings=772,completeBoundaryRows=556,sourceOnly=True,physicalAccepted=False,newlyInstalled=0))
def main():
 if '--schema-only'in sys.argv:print(json.dumps(schema_only(),sort_keys=True));return
 if '--owned'in sys.argv:return owned()
 assert '--reconcile-actual-draw-only'in sys.argv and not DOC.exists()and not LOCAL.exists();resources=['building:'+u for u in UIDS+[FOREIGN]]+['terrain-patch:'+u for u in UIDS+[FOREIGN]]+['immutable-source-proof:'+BATCH];claim=reservations.claim('upton-actual-incidence-'+str(uuid.uuid4()),resources,batch=BATCH,ttl=3600);assert claim['ok'];save(LEASE,json.loads(json.dumps(claim['reservation'],default=str)));subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(LEASE),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
if __name__=='__main__':main()
