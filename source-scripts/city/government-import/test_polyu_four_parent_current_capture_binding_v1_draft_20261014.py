import copy,unittest
import numpy as np
from polyu_four_parent_current_capture_binding_v1_draft_20261014 import scene_delta,terrain_disjoint,UPTON_CAT,AQUA_CAT,UPTON_PATCH,OLD_PATCH
def scenes():
 old=dict(officialModelCatalogues=['old'],terrainPatches=[dict(url=OLD_PATCH),dict(url='other')],unchanged=dict(x=1))
 new=copy.deepcopy(old);new['officialModelCatalogues']+=[UPTON_CAT,AQUA_CAT];new['terrainPatches']=[dict(url='other'),dict(url=UPTON_PATCH)]
 return old,new
def patch():return dict(w=2,h=2,meta=dict(georef=dict(W=2,H=2,aE=1,aN=-1,bE=834500,bN=816500)),elev=[0]*4,renderedElev=[0]*4,vegetation=[0]*4,nativeMesh=dict(position=[0,0,0,1,0,0,0,0,1],index=[0,1,2]))
class Binding(unittest.TestCase):
 def test_exact_two_delta_preserves_original(self):
  old,new=scenes();saved=copy.deepcopy((old,new));self.assertEqual(scene_delta(old,new)['addedCatalogueURLs'],[UPTON_CAT,AQUA_CAT]);self.assertEqual((old,new),saved)
 def test_other_field_rejected(self):
  old,new=scenes();new['unchanged']['x']=2
  with self.assertRaises(AssertionError):scene_delta(old,new)
 def test_catalogue_order_rejected(self):
  old,new=scenes();new['officialModelCatalogues'][-2:]=[AQUA_CAT,UPTON_CAT]
  with self.assertRaises(AssertionError):scene_delta(old,new)
 def test_another_terrain_change_rejected(self):
  old,new=scenes();new['terrainPatches'].append(dict(url='extra'))
  with self.assertRaises(AssertionError):scene_delta(old,new)
 def test_unused_native_position_cannot_be_ignored(self):
  p=patch();p['nativeMesh']['position']+=[10,0,10]
  with self.assertRaises(AssertionError):terrain_disjoint(p,[9,9,11,11])
 def test_closed_touch_rejected(self):
  with self.assertRaises(AssertionError):terrain_disjoint(patch(),[1,1,2,2])
if __name__=='__main__':unittest.main()
