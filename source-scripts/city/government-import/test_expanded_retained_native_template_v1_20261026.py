import copy,unittest
from types import SimpleNamespace
import numpy as np
from expanded_retained_native_template_v1_20261026 import rendered_root_faces,verify_capture,expanded_grid

class ExpandedFaceTests(unittest.TestCase):
 def setUp(self):
  self.parent=dict(w=4,h=4,elev=[10.]*16,vegetation=[0]*16,meta=dict(georef=dict(aE=10,aN=-10,bE=834500,bN=816500)))
  self.cells=[0,0,3,3];self.oldcells=[1,1,2,2];self.old=np.asarray([[[10,12,10],[10,12,20],[20,12,10]],[[20,12,10],[10,12,20],[20,12,20]]],float)
  self.extras=rendered_root_faces(self.parent,self.cells,self.oldcells);self.baseline=np.concatenate([self.old,self.extras])
 def test_complete_rendered_multiset(self):self.assertEqual(verify_capture(self.old,self.baseline,self.parent,self.cells,self.oldcells)['exactAddedRootFaces'],16)
 def test_changed_old_surface(self):
  changed=self.baseline.copy();changed[0,0,1]+=.001
  with self.assertRaises(AssertionError):verify_capture(self.old,changed,self.parent,self.cells,self.oldcells)
 def test_missing_root_face(self):
  with self.assertRaises(AssertionError):verify_capture(self.old,self.baseline[:-1],self.parent,self.cells,self.oldcells)
 def test_duplicate_face_replaces_distinct_face(self):
  changed=self.baseline.copy();changed[-1]=changed[-2]
  with self.assertRaises(AssertionError):verify_capture(self.old,changed,self.parent,self.cells,self.oldcells)
 def test_extra_unexplained_face(self):
  with self.assertRaises(AssertionError):verify_capture(self.old,np.concatenate([self.baseline,self.old[:1]]),self.parent,self.cells,self.oldcells)
 def test_winding_and_order_match_renderer(self):verify_capture(self.old,self.baseline[::-1,::-1],self.parent,self.cells,self.oldcells)
 def test_excludes_new_domain_that_drops_old_cells(self):
  with self.assertRaises(AssertionError):rendered_root_faces(self.parent,[2,2,3,3],self.oldcells)
 def test_float32_height_contract(self):
  p=copy.deepcopy(self.parent);p['renderedElev']=[11.123456789]*16
  values=rendered_root_faces(p,self.cells,self.oldcells)
  self.assertTrue(np.all(values[:,:,1]==float(np.float32(11.123456789))))
 def test_zero_raw_water_cells_remain_unrendered(self):
  p=copy.deepcopy(self.parent);p['elev']=[0.]*16
  self.assertEqual(len(rendered_root_faces(p,self.cells,self.oldcells)),0)

class ExpandedGridTests(unittest.TestCase):
 def setUp(self):
  self.old=dict(w=3,h=3,cell=5,elev=list(range(10,19)),renderedElev=list(range(20,29)),vegetation=list(range(9)),coarseCells=[1,1,2,2],meta=dict(georef=dict(aE=5,aN=-5,bE=834510,bN=816490),source={}))
  self.parent=dict(w=4,h=4,elev=[10]*16,vegetation=[0]*16,meta=dict(georef=dict(aE=10,aN=-10,bE=834500,bN=816500)))
  class Sampler:
   def __init__(self,parent,rendered=False):self.height=11 if rendered else 10
   def ground(self,x,z):return self.height
  self.builder=SimpleNamespace(terrain=SimpleNamespace(fine=SimpleNamespace(DemSampler=Sampler)))
 def test_every_old_metadata_node_exactly_preserved(self):
  out=expanded_grid(self.old,self.parent,[0,0,3,3],[0,0,30,30],self.builder)
  for r in range(3):
   for c in range(3):
    for key in ['elev','renderedElev','vegetation']:self.assertEqual(out[key][(r+2)*7+c+2],self.old[key][r*3+c])
  self.assertEqual(out['elev'][0],10);self.assertEqual(out['renderedElev'][0],11);self.assertEqual(out['meta']['source']['parentWaterMask']['landNodes'],49)
 def test_unaligned_grid_offset_rejected(self):
  self.old['meta']['georef']['bE']+=.1
  with self.assertRaises(AssertionError):expanded_grid(self.old,self.parent,[0,0,3,3],[0,0,30,30],self.builder)
 def test_changed_old_water_classification_rejected(self):
  self.old['elev'][0]=0
  with self.assertRaises(AssertionError):expanded_grid(self.old,self.parent,[0,0,3,3],[0,0,30,30],self.builder)

if __name__=='__main__':unittest.main()
