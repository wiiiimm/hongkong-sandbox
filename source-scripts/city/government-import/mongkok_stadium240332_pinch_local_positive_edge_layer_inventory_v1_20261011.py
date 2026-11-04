"""DRAFT first causal extra layer at17 proved authentic/current boundary pinches.
Maximum method budget: two additional positive-edge layers beyond original ring.
Only this first layer is inventoried; no apron or candidate mesh is emitted.
"""
from pathlib import Path
from fractions import Fraction as F
import json,numpy as np
from run import ROOT,HERE,read,save,digest,connect
from exact_atomic_terrain_domain_boundary_ring_v1_20261011 import atomic_boundary,one_edge_ring
from exact_pinch_local_positive_edge_expansion_v1_20261011 import select
from mongkok_stadium240332_one_ring_inner_outer_anchor_feasibility_v1_20261011 import boundary_nodes,strings
B=ROOT/'docs/astra-city/government-import'
ANCHOR=B/'government-xl-mongkok-stadium240332-one-ring-inner-outer-anchor-feasibility-v1-20261011'
OUTER=B/'government-xl-mongkok-stadium240332-atomic-ring-outer-ground-capture-v1-20261011'
DOC=B/'government-xl-mongkok-stadium240332-pinch-local-positive-edge-layer-inventory-v1-20261011'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();refs=[ref(Path(__file__)),ref(B/'government-xl-mongkok-stadium240332-pinch-local-transition-method-v1-20261011/METHOD.md')]
 for folder in [ANCHOR,OUTER]:
  r=read(folder/'result.json')
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  for e in r['evidenceRefs']:assert ref(ROOT/e['path'])==e
  refs.extend([ref(folder/'result.json'),ref(folder/'diagnostic.json.gz')])
 a=read(ANCHOR/'diagnostic.json.gz');g=read(OUTER/'complete-outer-current-ground.json.gz');assert a['completeCoincidentInnerOuterNodes']==17 and len(a['allCoincidentAnchorIncompatibilities'])==17 and not a['allOuterBoundaryHeightConflicts'];assert g['all151UniqueOriginalGlobalProvenance']and g['completeOutsideNeighbourBroadphase'];allrows=g['completeClosedDomainAABBActualGroundFacets'];owned=[r for r in allrows if r['frozenDomainRingFace']is not None];retained=[r for r in allrows if r['frozenDomainRingFace']is None];assert len(owned)==151;tri=np.asarray([r['actualTriangle']for r in owned],float).reshape(-1,3,3);other=np.asarray([r['actualTriangle']for r in retained],float).reshape(-1,3,3)
 # All retained facets touching this complete whole151 bounds were captured globally.
 # Therefore every positive boundary edge neighbour for THIS layer is present.
 intervals=one_edge_ring(tri,other);chosen=select(intervals['domainAtomicBoundary'],intervals['allExactPositiveAdjacentIntervals'],[r['point']for r in a['allCoincidentAnchorIncompatibilities']]);ids=chosen['completeSelectedRetainedFaces'];added=[retained[i]for i in ids];combined=np.concatenate([tri,other[ids]])if ids else tri;boundary=atomic_boundary(combined);outer=boundary_nodes(boundary);source={tuple(F(v)for v in r['point']):r for r in a['allInnerBoundarySourceHeightIncidences']};pinches=[]
 for point,inc in sorted(outer.items()):
  if point not in source:continue
  sh={F(r['height'])for r in source[point]['allClosedSourcePieceHeightIncidences']};oh={r['height']for r in inc}
  pinches.append(dict(point=point,allOriginalSourceHeightIncidences=source[point]['allClosedSourcePieceHeightIncidences'],newOuterIncidences=inc,compatible=bool(len(sh)==1 and len(oh)==1 and sh==oh),allExactHeightGaps=[s-o for s in sorted(sh)for o in sorted(oh)]))
 lo,hi=combined[:,:,[0,2]].min((0,1)),combined[:,:,[0,2]].max((0,1));old=g['completeFrozenDomainAndRingXZBounds'];inside=bool(lo[0]>=old[0]and lo[1]>=old[1]and hi[0]<=old[2]and hi[1]<=old[3]);projected_ok=not boundary['completePositiveProjectedOverlapPairs']and not boundary['boundaryBranchPoints']and all(r.get('oppositeDirectedIncidence',False)for r in boundary['allInternalAtomicEdges'])and all(len(r['allOriginalIncidences'])<=2 for r in boundary['allAtomicEdges'])and len(boundary['completeSimpleDirectedBoundaryCycles'])==1 and all(F(r['exactSignedProjectedAreaM2'])!=0 for r in boundary['completeSimpleDirectedBoundaryCycles'])
 refs.extend(ref(HERE/(n+'.py'))for n in ['exact_atomic_terrain_domain_boundary_ring_v1_20261011','exact_pinch_local_positive_edge_expansion_v1_20261011','test_exact_pinch_local_positive_edge_expansion_v1_20261011','mongkok_stadium240332_one_ring_inner_outer_anchor_feasibility_v1_20261011']);refs.append(ref(OUTER/'complete-outer-current-ground.json.gz'));assert all(ref(ROOT/r['path'])==r for r in refs)
 save(DOC/'diagnostic.json.gz',strings(dict(uid='landsd/240332:0',sourceOnly=True,currentAcceptance=False,terrainProposalCreated=False,apronTriangulationCreated=False,sourceGeometryChanges=0,terrainGeometryChanges=0,additionalPositiveEdgeLayer=1,maximumAdditionalLayersPermittedByThisMethod=2,completeOriginalCoreRingFaces=151,completeRetainedCandidates=len(retained),allCompleteCausalPositiveEdgeIntervals=intervals,exactPinchLocalSelection=chosen,allAddedWholeCurrentFacets=added,completeExpandedDomainFaces=len(combined),allExpandedActualWholeFacets=combined.tolist(),exactExpandedAtomicBoundary=boundary,projectedTopologyQualifiedIgnoringPreservedExistingHeightCracks=projected_ok,allRemainingCoincidentSourceOuterAnchors=pinches,incompatibleRemainingAnchors=[r for r in pinches if not r['compatible']],allNewOuterHeightConflicts=[dict(point=p,incidences=r)for p,r in sorted(outer.items())if len({e['height']for e in r})!=1],completeExpandedXZBounds=[lo.tolist(),hi.tolist()],expandedBoundsWithinPreviousCompleteNeighbourCapture=inside,newExpandedNeighbourAndActorCaptureRequired=not inside,allExpandedActorRegressionsStillRequired=True,allCurrent3DInternalCracksPreservedNotBlanketRepairObligations=True,evidenceRefs=refs,qualification='One deterministic geometry-driven extra positive-edge layer ONLY at the17 proved authentic-inner/current-outer pinch nodes, never a rectangle/global expansion or point-neighbour credit. Complete closed151-bound capture supplies all original whole facets sharing each positive boundary interval. Existing current3D layer cracks remain raw context; replacement must have valid new internal seams and exact actual retained outer seams. Method stops after at most two additional local layers and demands a new globally complete bounded capture/actor census whenever whole expanded bounds extend beyond pinned capture. This result is not generated terrain or an installable candidate. A compatible boundary still requires complete authentic source-piece topology and deterministic positive generated triangulation, exact/F32 seams and full protected source/native/BASIC/body/grade/foreign regression including240527.')))
 print(json.dumps(dict(addedWholeFacets=len(added),expandedFaces=len(combined),remainingPinches=len(pinches),remainingIncompatibleAnchors=sum(not r['compatible']for r in pinches),projectedTopologyQualified=projected_ok,expandedCaptureRequired=not inside,candidateCreated=False)))
if __name__=='__main__':main()
