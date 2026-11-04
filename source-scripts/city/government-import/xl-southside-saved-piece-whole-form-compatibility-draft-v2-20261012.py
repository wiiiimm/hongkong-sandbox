"""UNEXECUTED saved-piece compatibility; no lease, DB, construction or full proof."""
import sys,json,base64,hashlib
from pathlib import Path
import numpy as np
import shapely
from shapely.geometry import Polygon
from run import ROOT,HERE,read,digest
from exact_original_polygon_triangle_partition_20261010 import exact_partition
from southside_saved_finite_piece_guard_domain_v1_20261012 import restrict_saved_piece,rational_point
from southside_saved_piece_closed_bounds_schedule_v1_20261012 import prepare_domains,saved_piece_bounds,nominate_domains
BASE=ROOT/'docs/astra-city/government-import';D=BASE/'government-xl-southside-private-authentic-terrain-draft-v2-20261012';OUT=D/'neighbour-regression-cause-draft-v1/saved-piece-whole-form-compatibility-v2';CURRENT='2dde0cfc3c0869963c185c3398e48a1928c76802b2efa6c2d9713183a6ad5540'
INPUT=BASE/'government-xl-southside-315025-300867-current-actual-ground-capture-v1-20261012';FINITE=BASE/'government-xl-southside-315025-300867-complete-four-stream-current-finite-v1-20261012';AUTH=BASE/'government-xl-southside-315025-300867-unfiltered-original-sheets-comparison-v2-20261012';CAPTURE=BASE/'government-xl-southside-source-local-v4-private-ground-capture-v1-20261012';MODES=['providerOriginal','actualLiteral','explicitLeftAssociatedF32ModelMatrix','explicitBalancedF32ModelMatrix']
def domain(form,actual):
 polygon=Polygon(form['rings'][0],form['rings'][1:]);assert polygon.is_valid
 candidate=shapely.constrained_delaunay_triangles(polygon);triangles=[list(g.exterior.coords)[:-1]for g in candidate.geoms];assert triangles
 certificate=exact_partition(form['rings'],triangles) # GEOS only proposes; full exact chain proves the domain.
 domains=[dict(domainID='guard-ring-triangle-'+str(i),domainKind='exact-complete-ordinary-guard-ring-domain',completeXZPoints=t)for i,t in enumerate(triangles)]
 assert actual['classification']=='actual-production-BASIC'and actual['currentForm']==form and actual['wholeUnusedPositionVerticesIncluded']
 index=np.frombuffer(base64.b64decode(actual['completeIndexBytesBase64']),dtype='<u4')
 assert digest(index.tobytes())==actual['completeIndexSHA256']and len(index)==3*actual['completeIndexedFaces']
 for mode in ['actualLiteral','explicitLeftAssociatedF32ModelMatrix','explicitBalancedF32ModelMatrix']:
  raw=base64.b64decode(actual['completeStreamBytesBase64'][mode]);expected={'actualLiteral':'actualLiteralSHA256','explicitLeftAssociatedF32ModelMatrix':'explicitLeftAssociatedF32SHA256','explicitBalancedF32ModelMatrix':'explicitBalancedF32SHA256'}[mode];assert digest(raw)==actual[expected];p=np.frombuffer(raw,dtype='<f8').reshape(-1,3);assert len(p)==actual['completePositionVertices']and np.isfinite(p).all();assert index.max()<len(p)
  domains.extend(dict(domainID=mode+'-indexed-projection-'+str(i),domainKind='complete-actual-BASIC-indexed-projection',completeXZPoints=t[:,[0,2]].tolist())for i,t in enumerate(p[index].reshape(-1,3,3)))
  domains.extend(dict(domainID=mode+'-unused-position-'+str(i),domainKind='complete-unused-POSITION-point',completeXZPoints=[p[i,[0,2]].tolist()])for i in sorted(set(range(len(p)))-set(map(int,index))))
 return domains,certificate

def preflight():
 paths=[ROOT/'3d-viewer/city/data/manifest.json',D/'actual-basic-extent-proof.json.gz',CAPTURE/'result.json',CAPTURE/'input.json.gz',CAPTURE/'neighbour-inputs.json.gz',CAPTURE/'neighbour-checks.json',INPUT/'complete-two-actor-four-stream-ground-inputs.json.gz',FINITE/'diagnostic.json.gz',AUTH/'diagnostic.json.gz',HERE/'southside_saved_finite_piece_guard_domain_v1_20261012.py',HERE/'test_southside_saved_finite_piece_guard_domain_v1_20261012.py',Path(__file__),HERE/'southside_saved_piece_closed_bounds_schedule_v1_20261012.py',HERE/'test_southside_saved_piece_closed_bounds_schedule_v1_20261012.py',OUT.parent/'saved-piece-scheduling-cost-measurement-v1.json',OUT.parent/'immutable-saved-piece-import-preflight-v1/preparation-terminal-receipt.json',OUT.parent/'saved-baseline-authentic-body-restoration-join.json',HERE/'exact_original_paired_finite_clearance_20261010.py',HERE/'exact_original_polygon_triangle_partition_20261010.py',HERE/'exact_original_projection_coverage_v2_20261010.py',HERE/'test_exact_original_paired_finite_clearance_20261010.py',HERE/'test_exact_original_polygon_triangle_partition_20261010.py',BASE/'government-xl-original-installation-followup-20261011/root-southside-coverage-reuse-tests-20261012.json']
 pins={str(p.relative_to(ROOT)):digest(p.read_bytes())for p in paths};assert pins['3d-viewer/city/data/manifest.json']==CURRENT
 result=read(CAPTURE/'result.json');assert result['jobId']=='73dc1d5f866d4a85ddef92ace0d2238844b355ed5aa1061398ce0fb116a811aa'
 for ref in result['evidenceRefs']:assert digest((ROOT/ref['path']).read_bytes())==ref['sha256']
 selection=read(CAPTURE/'neighbour-inputs.json.gz');failed=read(CAPTURE/'neighbour-checks.json');bad=sorted(r['uid']for r in failed['rows']if r['reasons']);assert len(bad)==16
 forms={r['building']['uid']:r['building']for r in selection['rows']};actual={r['uid']:r for r in read(D/'actual-basic-extent-proof.json.gz')['rows']};worlds=read(INPUT/'complete-two-actor-four-stream-ground-inputs.json.gz')['rows'];old=read(FINITE/'diagnostic.json.gz');auth=read(AUTH/'diagnostic.json.gz');assert len(old['rows'])==len(auth['rows'])==8
 for row in old['rows']:
  u,m=row['uid'],row['arithmetic'];w=worlds[u]['completeWorldStreams'][m];a=np.asarray(w['completeWorldTriangles'],dtype='<f8');g=np.asarray(worlds[u]['completeDrawnGround'],dtype='<f8');assert digest(a.tobytes())==row['completeWholeWorldSHA256']and digest(g.tobytes())==row['completeCurrentGroundSHA256'];assert len(row['completeOriginalFaceComparisons'])==row['completeOriginalFaceCount']==len(a)
  ar=next(q for q in auth['rows']if q['uid']==u and q['arithmetic']==m);assert ar['completeWorldSHA256']==row['completeWholeWorldSHA256'];assert [q['sourceFace']for q in row['completeOriginalFaceComparisons']]==list(range(len(a)))
  for q in row['completeOriginalFaceComparisons']:assert digest(a[q['sourceFace']].tobytes())==q['completeOriginalFacetSHA256']
 return pins,bad,forms,actual,worlds,old,auth

def main():
 pins,bad,forms,actual,worlds,old,auth=preflight()
 if '--preflight-only'in sys.argv:print(json.dumps(dict(noDB=True,noLease=True,noNewFinitePredicates=True,wholeSavedSlots=51560,completeForms=len(bad),currentAcceptance=False)));return
 assert not OUT.exists();OUT.mkdir();domains={};certs={}
 for uid in bad:domains[uid],certs[uid]=domain(forms[uid],actual[uid])
 prepared={uid:prepare_domains(domains[uid])for uid in bad};scheduling=dict(completeSavedPieceActorPairs=0,actorStrictDisjointPairs=0,primitiveStrictDisjointPairs=0,nominatedPrimitivePairs=0,nonFiniteRecordActorPairs=0)
 rows=[]
 for row in old['rows']:
  u,m=row['uid'],row['arithmetic'];ground=[list(map(rational_point,t))for t in worlds[u]['completeDrawnGround']];ar=next(q for q in auth['rows']if q['uid']==u and q['arithmetic']==m);authfailed=set(ar['allAuthenticatedGroundFailuresRetained']);results=[]
  for q in row['completeOriginalFaceComparisons']:
   comparison=q['currentDrawnGroundComparison']
   if comparison['completeFiniteOrdinaryBoundProved']:continue # complete existing positive proof, not an omission.
   paired=comparison['paired']
   if paired is None:results.append(dict(sourceFace=q['sourceFace'],savedFullRecord=q,unresolvedMissingPairedPieces=True));continue
   for piece_id,piece in enumerate(paired['allExactFiniteSourceGroundPieces']):
    restrict_saved_piece(piece,ground[piece['originalGroundFace']],[]) # unchanged exact saved-plane/gap validation before any exclusion.
    piece_bounds=saved_piece_bounds(piece)
    for uid in bad:
     nominated,audit=nominate_domains(piece_bounds,prepared[uid]);scheduling['completeSavedPieceActorPairs']+=1;scheduling['actorStrictDisjointPairs']+=int(audit['actorStrictDisjoint']);scheduling['primitiveStrictDisjointPairs']+=audit['primitiveStrictDisjoint'];scheduling['nominatedPrimitivePairs']+=audit['nominatedDomains'];scheduling['nonFiniteRecordActorPairs']+=int(audit['nonFiniteRecordNotPruned'])
     if not nominated:continue # exact closed AABB strict disjointness; touches remain nominated.
     clipped=restrict_saved_piece(piece,ground[piece['originalGroundFace']],nominated);restrictions=clipped['restrictions']
     if restrictions or clipped['unresolved']:results.append(dict(sourceFace=q['sourceFace'],neighbourUID=uid,savedPieceID=piece_id,authenticWholeFacetFinitePositive=q['sourceFace']not in authfailed,restriction=clipped))
  rows.append(dict(uid=u,arithmetic=m,completeSourceFaces=row['completeOriginalFaceCount'],completeSourceWorldSHA256=row['completeWholeWorldSHA256'],savedCurrentGroundSHA256=row['completeCurrentGroundSHA256'],completeSavedFalseWholeFacetIDs=[q['sourceFace']for q in row['completeOriginalFaceComparisons']if not q['currentDrawnGroundComparison']['completeFiniteOrdinaryBoundProved']],restrictedRecords=results,currentAcceptance=False))
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h
 lost=[dict(uid=r['uid'],arithmetic=r['arithmetic'],sourceFace=q['sourceFace'],neighbourUID=q['neighbourUID'],restriction=v)for r in rows for q in r['restrictedRecords']if q.get('authenticWholeFacetFinitePositive')for v in q['restriction']['restrictions']if not v['unchangedOrdinaryBoundProvedOnRestriction']]
 unresolved=[dict(uid=r['uid'],arithmetic=r['arithmetic'],sourceFace=q['sourceFace'])for r in rows for q in r['restrictedRecords']if q.get('unresolvedMissingPairedPieces')or(q.get('authenticWholeFacetFinitePositive')and q['restriction']['unresolved'])]
 out=dict(baselineFalseAuthenticTrueRestrictionFailures=lost,unresolvedRestrictions=unresolved,noImprovedClippedRegionLost=(not lost and not unresolved),noImprovedClippedRegionLostIsNotWholeCandidateAcceptance=True,all19HistoricalObligationsVerbatim=auth['allHistoricalObligationsVerbatim'],all46ProtectedFormsVerbatim=auth['all46CurrentFormsRetainedVerbatim'],schema='southside-saved-piece-complete-guard-domain-compatibility-v2',exactClosedAABBScheduling=scheduling,closedAABBSchedulingChangesNoClippingPredicate=True,rows=rows,completeForms={u:forms[u]for u in bad},completeDomainRecords=domains,exactGuardRingPartitionCertificates=certs,inputHashes=pins,shapelyVersion=shapely.__version__,GEOSOnlyProposesCertifiedPartitions=True,all51560ExistingSlotsAccounted=True,noNewFullFiniteOrCoveragePass=True,noTerrainConstruction=True,noDB=True,noLease=True,currentAcceptance=False,physicalAccepted=False,installationApproved=False)
 with(OUT/'diagnostic.json').open('x')as f:json.dump(out,f,indent=2,sort_keys=True);f.write('\n')
 print(json.dumps(dict(path=str((OUT/'diagnostic.json').relative_to(ROOT)),sha256=digest((OUT/'diagnostic.json').read_bytes()),currentAcceptance=False)))
if __name__=='__main__':main()
