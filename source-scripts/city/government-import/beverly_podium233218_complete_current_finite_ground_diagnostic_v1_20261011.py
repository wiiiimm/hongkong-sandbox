"""DRAFT whole4712-facet original/literal/explicitF32 podium ordinary finite proof; no acceptance.
Exact complete current drawn ground only. Four spatial identity failures and all14 source-body/foreign/native obligations unchanged.
"""
from pathlib import Path
from fractions import Fraction as F
import numpy as np,json
from run import ROOT,HERE,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_face_conservative_clearance_v5_20261010 import verify as finite
from exact_original_triangle_pair_column_gap_20261010 import verify as column
B=ROOT/'docs/astra-city/government-import';BATCH='government-xl-beverly-podium233218-complete-current-finite-ground-diagnostic-v1-20261011';DOC=B/BATCH;CAPTURE=B/'government-xl-beverly-podium233218-complete-current-ground-capture-v1-20261011';RUNTIME=HERE/'local'/CAPTURE.name/'runtime-geometry.json.gz';UID='landsd/233218:0'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();assert read(CAPTURE/'result.json')['sourceOnly'];actor=read(CAPTURE/'review.json');assert actor['uid']==UID and not actor['wholeSourceIdentityAccepted']and len(actor['rawHistoricalIdentityReasons'])==4;selection=next(r for r in read(CAPTURE/'selection.json.gz')['rows']if r['uid']==UID);p=ROOT/selection['candidate']['path'];original=decode_original_world_triangles(p.read_bytes());rt=next(r for r in read(RUNTIME)['rows']if r['uid']==UID);ground=np.asarray(rt['drawnGroundGeometry'],float).reshape(-1,3,3);assert original.shape==(4712,3,3)and digest(original.tobytes())==actor['completeOriginalWorldSHA256']and digest(ground.tobytes())==actor['completeActualCurrentGroundSHA256'];a=next(r for r in read(CAPTURE/'actual-render-geometry.json.gz')['rows']if r['uid']==UID);index=np.asarray(a['completeOriginalIndex']).reshape(-1,3);streams={'original':original}
 for name,key in [('literal','completeLiteralWorldPosition'),('explicitLeftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('explicitBalancedF32','completeExplicitBalancedFloat32WorldPosition')]:streams[name]=np.asarray(a[key],float).reshape(-1,3)[index]
 proofs={};bindings={}
 for name,source in streams.items():
  h=digest(source.tobytes());bindings[name]=dict(completeWorldSHA256=h,completeFaces=len(source),proofTupleSHA256=h)
  if h in proofs:continue
  rows=[]
  for i,face in enumerate(source):
   prior=finite(face,ground);lower=F(prior['exactCertifiedLowerClearanceM']);pieces=[]
   if prior['groundProjectionCovered']and lower< -F(1,2):
    pieces=[dict(originalGroundFace=j,proof=column(face,ground[j]))for j in prior['allProjectedBoundingCandidateOriginalGroundFacets']];gaps=[F(x['proof']['exactMinimumFiniteColumnGapM'])for x in pieces if x['proof']['exactClosedHorizontalProjectionsMeet']];assert gaps;lower=min(gaps)
   rows.append(dict(face=i,priorCompleteFiniteProof=prior,refinedCompleteFinitePairs=pieces,exactLowerM=str(lower),completeProjectionCovered=prior['groundProjectionCovered'],ordinaryFiniteProved=bool(prior['groundProjectionCovered']and lower>=-F(1,2)),strictPositiveFiniteProved=bool(prior['groundProjectionCovered']and lower>0)))
  proofs[h]=dict(allWholeOriginalFacetProofs=rows,completeFacetsAccounted=len(rows),ordinaryFailingSourceFaces=[r['face']for r in rows if not r['ordinaryFiniteProved']],coverageFailingSourceFaces=[r['face']for r in rows if not r['completeProjectionCovered']],allOrdinaryFiniteProved=all(r['ordinaryFiniteProved']for r in rows),allStrictPositiveFiniteProved=all(r['strictPositiveFiniteProved']for r in rows),minimumCertifiedOrRefinedLowerM=str(min(F(r['exactLowerM'])for r in rows)))
 pre=read(CAPTURE/'source-preflight.json');refs=[ref(p)for p in [Path(__file__),p,RUNTIME,CAPTURE/'result.json',CAPTURE/'review.json',CAPTURE/'selection.json.gz',CAPTURE/'actual-render-geometry.json.gz',CAPTURE/'source-preflight.json',B/'government-xl-beverly-hill-k-j-original-podium233218-provenance-complete-contact-v2-20261011/result.json']]+[ref(HERE/(n+'.py'))for n in ['exact_packed_world_geometry_20261009','exact_original_face_conservative_clearance_v5_20261010','exact_original_triangle_pair_column_gap_20261010','exact_original_projection_coverage_v2_20261010']]
 for r in refs:assert ref(ROOT/r['path'])==r
 result=dict(uids=[UID],sourceOnly=True,currentAcceptance=False,installationApproved=False,sourceGeometryChanges=0,terrainGeometryChanges=0,noHistoricalFailureWaiver=True,currentManifest=pre['currentManifest'],completeActualCurrentGroundFaces=len(ground),completeActualCurrentGroundSHA256=digest(ground.tobytes()),allFourStreamBindings=bindings,allDistinctWholeSourceFiniteProofs=proofs,exactByteIdenticalFullWorldTupleReuseOnly=True,ordinaryThresholdM='-1/2',strictPositiveSeparate=True,wholePodiumGradeRootProved=False,foreignRegressionsDischarged=False,nativeReapproval=False,rawHistoricalIdentityReasons=actor['rawHistoricalIdentityReasons'],wholeSourceIdentityAccepted=False,genuineOriginalBodies=14,allCurrentProtectiveForms=pre['allCurrentRelevantForeignBasicNativeForms'],allHistoricalRawObligations=pre,evidenceRefs=refs,qualification='Every4712 source facet accounted against complete relevant actual current makeTerrain Float32 surface. Existing ordinary>=-.5m proof is separate from strict-positive exposure/grade/root and does not permit arbitrary cap or geometry roles. 109 original Pbody0-to-Kbody8 and137 Pbody0-to-Jbody8 interfaces remain conditional source-only context; all14 podium bodies, K231 bodies/J273 bodies, four whole-source identity failures and foreign70279/native obligations remain separate. No authenticTIN/proposed/current scope conflation.')
 save(DOC/'diagnostic.json.gz',result);print(json.dumps(dict(streams=bindings,proofs={h:{k:v for k,v in r.items()if k!='allWholeOriginalFacetProofs'}for h,r in proofs.items()},currentAcceptance=False)),flush=True)
if __name__=='__main__':main()
