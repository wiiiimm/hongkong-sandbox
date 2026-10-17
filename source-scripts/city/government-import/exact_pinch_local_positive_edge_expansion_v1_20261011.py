"""Deterministic local positive-edge selection at proved inner/outer pinches.
No triangulation, acceptance, tolerance or point-only neighbour credit.
"""
from fractions import Fraction as F
from exact_atomic_terrain_domain_boundary_ring_v1_20261011 import on
def select(boundary,positive_intervals,pinches):
 pinches={tuple(F(v)for v in p)for p in pinches};selected=set();rows=[]
 for r in positive_intervals:
  if not r['oppositeDirectedBoundaryEdge']:continue
  lo,hi=[F(v)for v in r['exactPositiveParameterInterval']];assert 0<=lo<hi<=1
  atom=boundary['allBoundaryAtomicEdges'][r['boundaryAtom']];assert len(atom['allOriginalIncidences'])==1
  e=atom['allOriginalIncidences'][0];a=tuple(F(v)for v in e['start']);b=tuple(F(v)for v in e['end']);assert a!=b
  matched=[]
  for p in sorted(pinches):
   t=on(a,b,p)
   if t is not None and lo<=t<=hi:matched.append(dict(point=p,exactBoundaryParameter=t))
  if matched:selected.add(r['retainedFace']);rows.append(dict(positiveAdjacentInterval=r,allMatchedPinchNodes=matched))
 return dict(completeSelectedRetainedFaces=sorted(selected),allCausalPinchPositiveEdgeSelections=rows,pointOnlyNeighboursCredited=False,current3DCompatibilityCredited=False,terrainCandidateApproved=False)
