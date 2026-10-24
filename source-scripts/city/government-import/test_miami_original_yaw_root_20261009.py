"""Actual source-bound yaw regression and forbidden transform mutations."""
import unittest,copy,numpy as np
from run import ROOT,read
from miami_original_yaw_root_20261009 import verify_original_root,frame_measurement
from original_source_ownership import document
class SourceHeadingTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  sel=read(ROOT/'docs/astra-city/government-import/government-xl-miami-nine-independent-original-diagnostic-20261009/selection.json.gz');cls.row=next(r for r in sel['rows'] if r['uid']=='landsd/202994:0');cls.raw=(ROOT/cls.row['candidate']['path']).read_bytes();inp=read(ROOT/'docs/astra-city/government-import/government-xl-miami-nine-original-contact-20261009/all-original-source-contact-inputs.json.gz');g=next(r for r in inp['rows'] if r['uid']==cls.row['uid']);cls.tri=np.array(g['position']).reshape(-1,3,3);cls.matrix=document(cls.raw)['nodes'][0]['matrix']
 def test_actual_original(self):
  p=verify_original_root(self.raw,self.row,self.tri);self.assertTrue(p['passed']);self.assertEqual(p['legacyGraphReasons'],['original-unit-hkpd-root-pose']);self.assertEqual(p['actualSourceMatrixUnchanged'],self.matrix)
 def test_forbidden_unit_frame_mutations(self):
  for name,indices in [('scale',[(0,self.matrix[0]*2)]),('shear',[(4,self.matrix[4]+.1)]),('reflection',[(0,-self.matrix[0]),(2,-self.matrix[2])]),('z-tilt',[(8,.01)]),('translation',[(12,self.matrix[12]+1)])]:
   with self.subTest(name=name):
    m=list(self.matrix)
    for i,v in indices:m[i]=v
    self.assertFalse(frame_measurement(m,self.matrix)['passed'])
 def test_native_world_geometry_shift(self):
  p=verify_original_root(self.raw,self.row,self.tri+[1,0,0]);self.assertFalse(p['passed'])
 def test_source_bytes_mutation(self):
  with self.assertRaises((AssertionError,OSError,ValueError)):verify_original_root(self.raw[:-1]+bytes([self.raw[-1]^1]),self.row,self.tri)
 def test_scope_not_general_pose_waiver(self):
  other=copy.deepcopy(self.row);other['uid']='landsd/231147:0'
  with self.assertRaises(AssertionError):verify_original_root(self.raw,other,self.tri)
if __name__=='__main__':unittest.main()
