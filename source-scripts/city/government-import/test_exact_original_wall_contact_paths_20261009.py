import hashlib,unittest
import numpy as np
from exact_original_wall_contact_paths_20261009 import contact_paths

class ExactOriginalContactPathTests(unittest.TestCase):
 def run_graph(self,tri,affected=(0,),changed=False):
  t=np.asarray(tri,float);contexts=[{'sourceFace':i,'groundProjectionCovered':True,'minimum':{'minimumGapM':1}} for i in range(len(t))]
  binding={'sourceSHA256':'original-source','positionTriangleStreamSHA256':'original-position','normalTriangleStreamSHA256':'original-normal','colourTriangleStreamSHA256':'original-colour','rootMatrix':[1],'drawnGroundSHA256':'pinned-ground','decodedWorldTrianglesSHA256':hashlib.sha256(t.tobytes()).hexdigest()}
  current={**binding,'sourceSHA256':'changed'} if changed else binding
  return contact_paths(t,contexts,affected,expected_source_binding=binding,current_source_binding=current)
 def fixture(self):
  # Wall top is a partial roof edge: there is no identical complete shared edge.
  return [[[0,0,0],[1,1,0],[0,1,0]],[[0,1,0],[2,1,2],[2,1,0]]]
 def test_exact_partial_edge_tjunction_reaches_original_roof(self):
  r=self.run_graph(self.fixture());self.assertTrue(r['allAffectedHaveExactContactRoofPaths']);self.assertEqual(r['originalSharedFullEdgePairs'],0);self.assertEqual(len(r['additionalExactOriginalContacts']),1)
 def test_vertex_only_touch_is_not_a_roof_attachment(self):
  tri=self.fixture();tri[1]=[[1,1,0],[2,1,1],[2,1,0]];self.assertFalse(self.run_graph(tri)['allAffectedHaveExactContactRoofPaths'])
 def test_tiny_real_gap_is_not_welded(self):
  tri=self.fixture();tri[1]=[[x,y+1e-10,z] for x,y,z in tri[1]];self.assertFalse(self.run_graph(tri)['allAffectedHaveExactContactRoofPaths'])
 def test_downward_surface_never_becomes_roof(self):
  tri=self.fixture();tri[1]=list(reversed(tri[1]));self.assertFalse(self.run_graph(tri)['allAffectedHaveExactContactRoofPaths'])
 def test_changed_original_source_binding_rejects(self):
  with self.assertRaises(AssertionError):self.run_graph(self.fixture(),changed=True)
 def test_collapsed_triangle_cannot_bridge_roof(self):
  tri=self.fixture();tri[1]=[[0,1,0],[1,1,0],[2,1,0]];r=self.run_graph(tri);self.assertFalse(r['allAffectedHaveExactContactRoofPaths']);self.assertEqual(r['collapsedOriginalFacesExcludedFromPaths'],[1]);self.assertEqual(r['completeOriginalFaceInventory'],[0,1])
if __name__=='__main__':unittest.main()
