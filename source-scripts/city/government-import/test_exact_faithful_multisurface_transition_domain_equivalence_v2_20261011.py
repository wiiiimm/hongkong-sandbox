"""DRAFT exact two-way union/boundary equivalence for efficiency v2; no epsilon."""
import unittest
from fractions import Fraction as F
import exact_faithful_multisurface_transition_domain_v1_20261011 as v1
import exact_faithful_multisurface_transition_domain_v2_20261011 as v2
from exact_original_projection_coverage_v2_20261010 import subtract,signed_area,cross
T=[(F(0),F(0)),(F(2),F(0)),(F(0),F(2))]
def uncovered(polys,cover):
 total=F(0)
 for p in polys:
  left=[p]
  for q in cover:left=[z for p in left for z in subtract(p,q)]
  total+=sum(signed_area(q)for q in left)
 return total
class Tests(unittest.TestCase):
 def check(self,source,full_domain=False):
  a,_=v1.partition(source);b,_=v2.partition(source);self.assertEqual(uncovered(a,b),0);self.assertEqual(uncovered(b,a),0);self.assertEqual(uncovered(source,b),0);self.assertEqual(uncovered(b,source),0)
  ea,pa=v1.planar_boundary(a);eb,pb=v2.planar_boundary(b);self.assertEqual(len(pa['completePositiveEdgeComponentCycles']),len(pb['completePositiveEdgeComponentCycles']))
  # Exact boundary finite segment unions, independent of redundant atom cuts.
  from exact_atomic_terrain_domain_boundary_ring_v1_20261011 import on
  for left,right in[(ea,eb),(eb,ea)]:
   for e in left:
    cuts={F(0),F(1)}
    for r in right:
     for p in[r['start'],r['end']]:
      t=on(e['start'],e['end'],p)
      if t is not None:cuts.add(t)
    cuts=sorted(cuts)
    for lo,hi in zip(cuts,cuts[1:]):
     p=v1.at(e['start'],e['end'],(lo+hi)/2);self.assertTrue(any(on(r['start'],r['end'],p)is not None and cross(e['start'],e['end'],r['start'])==cross(e['start'],e['end'],r['end'])==0 for r in right))
  if full_domain:
   x,y=v1.domain(source),v2.domain(source);ax=x['scratchOriginalProjectionUnionCells']+x['computeBandPolygons'];by=y['scratchOriginalProjectionUnionCells']+y['computeBandPolygons'];self.assertEqual(uncovered(ax,by),0);self.assertEqual(uncovered(by,ax),0);self.assertEqual(x['exactWholeDomainXZBounds'],y['exactWholeDomainXZBounds'])
 def test_single_triangle_keeps_exact_union_and_reduces_fans(self):
  self.check([T],True);_,a=v1.planar_boundary([T]);_,b=v2.planar_boundary([T]);self.assertEqual(a['completeScratchPositiveTriangles'],3);self.assertEqual(b['completeScratchPositiveTriangles'],1)
 def test_shared_diagonal_zero_positive_overlap(self):self.check([T,[(2,0),(2,2),(0,2)]],True)
 def test_point_touch_does_not_bridge(self):self.check([T,[(x+2,z)for x,z in T]])
 def test_partial_positive_overlap_not_skipped(self):self.check([T,[(x+1,z)for x,z in T]],True)
 def test_tiny_positive_overlap_not_waived(self):self.check([T,[(x+F(2)-F(1,10**30),z)for x,z in T]])
 def test_duplicate_projection_not_credited_twice(self):self.check([T,T])
 def test_contained_original_projection(self):self.check([T,[(F(1,4),F(1,4)),(F(1,2),F(1,4)),(F(1,4),F(1,2))]])
 def test_disconnected_islands_complete(self):self.check([T,[(x+30,z)for x,z in T]])
 def test_original_source_input_never_modified(self):
  import copy
  p=[T,[(x+1,z)for x,z in T]];old=copy.deepcopy(p);v2.partition(p);v2.domain(p);self.assertEqual(p,old)
 def test_nontriangle_scratch_cell_still_complete(self):self.check([[(0,0),(2,0),(2,2),(0,2)]])
if __name__=='__main__':unittest.main()
