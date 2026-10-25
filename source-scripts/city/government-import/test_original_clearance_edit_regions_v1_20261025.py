import unittest
from copy import deepcopy
import numpy as np
from run import digest
from original_clearance_edit_regions_v1_20261025 import edit_regions


class RegionTests(unittest.TestCase):
 def setUp(self):
  tri=np.asarray([[[0.,2.,0.],[1.,2.,0.],[0.,2.,1.]],[[10.,20.,10.],[11.,20.,10.],[10.,20.,11.]]],dtype='<f8');self.worlds={m:tri.copy()for m in ['original','literal','left','balanced']};self.ground=np.asarray([[[0.,3.,0.],[1.,3.,0.],[0.,3.,1.]]],dtype='<f8')
  self.proofs={m:dict(completeSourceFaces=2,sourceWorldSHA256=digest(t.tobytes()),groundSHA256=digest(self.ground.tobytes()),rows=[dict(sourceFace=0,vertices=t[0].tolist())])for m,t in self.worlds.items()}
 def test_all_four_negative_faces_are_included_without_unrelated_source_region(self):
  region,core,outer,bindings=edit_regions(self.worlds,self.ground,self.proofs)
  self.assertEqual(len(bindings),4);self.assertTrue(core.covers(region));self.assertTrue(outer.covers(core));self.assertLess(core.bounds[2],5)
 def test_any_changed_source_ground_or_witness_rejects(self):
  for kind in ['source','ground','witness','count','missing-mode','duplicate-face']:
   worlds=deepcopy(self.worlds);proofs=deepcopy(self.proofs);ground=self.ground.copy()
   if kind=='source':worlds['left'][0,0,1]+=.001
   elif kind=='ground':ground[0,0,1]+=.001
   elif kind=='witness':proofs['literal']['rows'][0]['vertices'][0][1]+=.001
   elif kind=='count':proofs['original']['completeSourceFaces']=1
   elif kind=='missing-mode':del proofs['balanced']
   else:proofs['original']['rows']*=2
   with self.subTest(kind=kind),self.assertRaises(AssertionError):edit_regions(worlds,ground,proofs)


if __name__=='__main__':unittest.main()
