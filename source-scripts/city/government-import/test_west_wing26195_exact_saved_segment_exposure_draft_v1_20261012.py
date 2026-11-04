"""Bounded mathematical/adverse tests, not current-scene acceptance."""
import copy,unittest
from fractions import Fraction as Q
from west_wing26195_exact_saved_segment_exposure_draft_v1_20261012 import classify,source_segment
from exact_closed_ground_aabb_pruning_v1_20261011 import CompleteGround
A=['0','0','0'];B=['1','0','0']
def wrapper(rows):
 pieces=[]
 for i,(l,r,g0,g1)in enumerate(rows):
  l,r,g0,g1=map(Q,[l,r,g0,g1]);pieces.append(dict(groundFace=i,exactParameterInterval=list(map(str,[l,r])),exactEndpointSourcePoints=[[str(l),'0','0'],[str(r),'0','0']],exactEndpointGroundHeights=list(map(str,[-g0,-g1])),exactMinimumGapM=str(min(g0,g1))))
 minimum=str(min(Q(p['exactMinimumGapM'])for p in pieces));ids=list(range(len(rows)))
 return dict(selection=dict(completeGroundSHA256='g',completeGroundFacetCount=len(rows),everyNoncandidateStrictlyDisjoint=True,touchingAndCollapsedProjectionsRetained=True,selectedOriginalGroundFaces=ids),originalGroundFaceBySelectedKernelFace=ids,closedWholeSegmentProjectionCovered=True,exactMinimumGapM=minimum,selectedGroundKernelProof=dict(exactEndpoints=[A,B],closedWholeSegmentProjectionCovered=True,completeFiniteGroundFacesAccounted=len(rows),allFinitePieces=pieces,exactMinimumGapM=minimum))
def run(p,**kw):return classify(p,expected_ground_sha=kw.get('sha','g'),expected_ground_faces=p['selection']['completeGroundFacetCount'],expected_endpoints=kw.get('endpoints',[A,B]))
class TestExposure(unittest.TestCase):
 def test_positive(self):self.assertEqual(len(run(wrapper([(0,1,1,1)]))['positiveLengthExposedNominees']),1)
 def test_fully_negative(self):self.assertTrue(run(wrapper([(0,1,-1,-2)]))['fullyStrictlyBuried'])
 def test_partial_rising(self):
  d=run(wrapper([(0,1,-1,1)]));self.assertEqual(d['positiveLengthExposedNominees'][0]['exactClosedInteriorParameterInterval'],['5/8','7/8'])
 def test_negative_ends_positive_interior(self):
  d=run(wrapper([(0,1,'-1/2','3/2'),(0,1,'3/2','-1/2')]));self.assertFalse(d['fullyStrictlyBuried']);self.assertEqual(d['positiveLengthExposedNominees'][0]['exactClosedInteriorParameterInterval'],['3/8','5/8'])
 def test_ground_island_splits(self):self.assertEqual(len(run(wrapper([(0,1,1,1),('1/3','2/3',-1,-1)]))['positiveLengthExposedNominees']),2)
 def test_isolated_contact_not_positive_length(self):
  d=run(wrapper([(0,1,'-1/2','1/2'),(0,1,'1/2','-1/2')]));self.assertFalse(d['fullyStrictlyBuried']);self.assertFalse(d['positiveLengthExposedNominees']);self.assertFalse(d['isolatedStrictPositiveCutPoints'])
 def test_grade_start_only(self):
  d=run(wrapper([(0,1,0,1)]));self.assertTrue(d['strictPositiveExceptInitialEndpoint']);self.assertEqual(d['initialEndpointGapM'],'0')
 def test_interior_island_rejects_except_start(self):self.assertFalse(run(wrapper([(0,1,0,1),('1/3','2/3',-1,-1)]))['strictPositiveExceptInitialEndpoint'])
 def test_missing_closed_coverage(self):
  with self.assertRaises(AssertionError):run(wrapper([(0,'4/5',1,1)]))
 def test_wrong_saved_source_point(self):
  p=wrapper([(0,1,1,1)]);p['selectedGroundKernelProof']['allFinitePieces'][0]['exactEndpointSourcePoints'][0]=['0','1','0']
  with self.assertRaises(AssertionError):run(p)
 def test_wrong_minimum(self):
  p=wrapper([(0,1,1,1)]);p['exactMinimumGapM']='0'
  with self.assertRaises(AssertionError):run(p)
 def test_wrong_ground_hash(self):
  with self.assertRaises(AssertionError):run(wrapper([(0,1,1,1)]),sha='changed')
 def test_collapsed_piece_rejected(self):
  p=wrapper([(0,1,1,1)]);p['selectedGroundKernelProof']['allFinitePieces'][0]['collapsedProjectionConservative']=True
  with self.assertRaises(AssertionError):run(p)
 def test_point_segment_rejected(self):
  p=wrapper([(0,1,1,1)]);p['selectedGroundKernelProof']['exactEndpoints']=[A,A]
  with self.assertRaises(AssertionError):run(p,endpoints=[A,A])
 def test_facet_containment_and_no_source_change(self):self.assertTrue(source_segment([['0','0','0'],['2','0','0'],['0','0','2']],[[0,0,0],[1,0,1]])['closedConvexOriginalFacetContainment'])
 def test_outside_or_offplane_rejected(self):
  for p in [[2,0,2],[1,1,0]]:
   with self.assertRaises(AssertionError):source_segment([[0,0,0],[2,0,0],[0,0,2]],[[0,0,0],p])
 def test_zero_facet_rejected(self):
  with self.assertRaises(AssertionError):source_segment([[0,0,0],[1,0,0],[2,0,0]],[[0,0,0],[1,0,0]])
 def test_float_endpoint_rejected(self):
  with self.assertRaises(AssertionError):source_segment([[0,0,0],[2,0,0],[0,0,2]],[[0,0,0],[1.0,0,0]])
 def test_reversed_interval_rejected(self):
  with self.assertRaises(AssertionError):run(wrapper([(1,0,1,1)]))
 def test_real_corridor_negative_interior(self):
  face=[[-2,2,-2],[2,2,-2],[0,2,2]];ends=[['-1','2','0'],['1','2','0']];source_segment(face,ends)
  ground=[[[-2,0,-2],[2,0,-2],[0,0,2]],[[-Q(1,2),3,-Q(1,2)],[Q(1,2),3,-Q(1,2)],[0,3,Q(1,2)]]];p=CompleteGround(ground).segment(ends);self.assertTrue(p['closedWholeSegmentProjectionCovered']);self.assertEqual(Q(p['exactMinimumGapM']),-1);self.assertFalse(p['strictlyExposedWholePositiveInterface'])
if __name__=='__main__':unittest.main()
