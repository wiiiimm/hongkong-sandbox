import copy,unittest
from native_terrain_validation import validate_native_mesh
class NativeTerrainGate(unittest.TestCase):
 def setUp(self):
  self.parent={'w':2,'h':2,'elev':[2]*4,'meta':{'georef':{'aE':10,'aN':-10,'bE':834500,'bN':816500}}}
  self.patch={'w':3,'h':3,'meta':{'georef':{'aE':5,'aN':-5,'bE':834500,'bN':816500}},'nativeMesh':{'position':[0,2,0,10,2,0,10,2,10,0,2,10,5,12,5],'index':[0,1,4,1,2,4,2,3,4,3,0,4]}}
 def test_complete_non_overlapping_native_surface_with_parent_seam(self):validate_native_mesh(self.patch,self.parent)
 def test_hole_is_rejected(self):
  self.patch['nativeMesh']['index']=self.patch['nativeMesh']['index'][:-3]
  with self.assertRaisesRegex(AssertionError,'cover'):validate_native_mesh(self.patch,self.parent)
 def test_duplicate_surface_is_rejected(self):
  self.patch['nativeMesh']['index']+=self.patch['nativeMesh']['index'][:3]
  with self.assertRaisesRegex(AssertionError,'overlapping'):validate_native_mesh(self.patch,self.parent)
 def test_incorrect_boundary_is_rejected(self):
  self.patch['nativeMesh']['position'][1]=3
  with self.assertRaisesRegex(AssertionError,'boundary'):validate_native_mesh(self.patch,self.parent)
if __name__=='__main__':unittest.main()
