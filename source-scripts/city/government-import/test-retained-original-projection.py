import copy,unittest
from shapely.geometry import box
from retained_original_projection import retained_projection

class ProjectionTest(unittest.TestCase):
 def fixture(self):
  # Concave L mesh: its empty bounding-box corner intersects the new model.
  p=[0,0,0,10,0,0,0,0,2,10,0,2,0,0,10,2,0,10,2,0,2]
  r={'uid':'a','sourceSHA256':'sha','position':p,'index':[0,1,2,1,3,2,2,6,4,6,5,4]}
  e={'a':{'sha256':'sha','triangles':4,'worldBounds':[[0,0,0],[10,0,10]]}}
  return r,e
 def test_empty_bbox_corner_is_not_mesh_overlap(self):
  r,e=self.fixture();p=retained_projection([r],e,[-1,-1,11,11],box(5,5,8,8));self.assertTrue(p.covers(box(.1,.1,1,9)))
 def test_actual_original_overlap_rejected(self):
  r,e=self.fixture()
  with self.assertRaises(AssertionError):retained_projection([r],e,[-1,-1,11,11],box(1,5,3,8))
 def test_full_face_not_just_vertices_is_protected(self):
  r,e=self.fixture()
  with self.assertRaises(AssertionError):retained_projection([r],e,[-1,-1,11,11],box(4,.5,5,1.5))
 def test_missing_duplicate_or_changed_original(self):
  r,e=self.fixture()
  for rows in [[],[r,r],[{**r,'sourceSHA256':'changed'}]]:
   with self.assertRaises(AssertionError):retained_projection(rows,e,[-1,-1,11,11],box(20,20,21,21))
 def test_mesh_must_fit_original_parent(self):
  r,e=self.fixture()
  with self.assertRaises(AssertionError):retained_projection([r],e,[0,0,5,5],box(20,20,21,21))
 def test_missing_faces_and_invalid_geometry_rejected(self):
  r,e=self.fixture()
  for changed in [{**r,'index':r['index'][:-3]},{**r,'index':[100,1,2]},{**r,'position':[float('nan')]+r['position'][1:]}]:
   with self.assertRaises(AssertionError):retained_projection([changed],e,[-1,-1,11,11],box(20,20,21,21))
 def test_vertical_face_is_protected(self):
  r={'uid':'a','sourceSHA256':'s','position':[0,0,0,0,10,0,0,10,10],'index':[0,1,2]};e={'a':{'sha256':'s','triangles':1,'worldBounds':[[0,0,0],[0,10,10]]}}
  with self.assertRaises(AssertionError):retained_projection([r],e,[-1,-1,11,11],box(-.01,4,.01,6))
 def test_geometry_bounds_must_match(self):
  r,e=self.fixture();e['a']['worldBounds'][1][0]=11
  with self.assertRaises(AssertionError):retained_projection([r],e,[-1,-1,12,12],box(20,20,21,21))
if __name__=='__main__':unittest.main()
