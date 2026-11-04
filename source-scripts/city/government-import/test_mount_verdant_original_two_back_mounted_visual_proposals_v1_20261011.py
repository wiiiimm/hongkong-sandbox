"""Actual original641-face fixture and adverse named-role counterexamples."""
import unittest,copy
import numpy as np
from run import ROOT,read
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from mount_verdant_original_two_back_mounted_visual_proposals_v1_20261011 import verify,sha,canonical,SOURCE,UID
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  folder=ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261011-mount-verdant-podium-grade-cap-lower-loops-v2';d=read(folder/'diagnostic.json.gz');p=next(ROOT/r['path']for r in d['evidenceRefs']if r['path'].endswith(SOURCE+'.glb.gz'));cls.world=decode_original_world_triangles(p.read_bytes());cls.host=d['completeMainBody576OriginalFaces'];cls.BINDING=dict(uid=UID,sourceSHA256=SOURCE,completeWorldTrianglesSHA256=sha(cls.world),completeHostSourceFaceIdsSHA256=canonical(cls.host))
 def binding(self,t,h=None):return dict(self.__class__.BINDING,completeWorldTrianglesSHA256=sha(t),completeHostSourceFaceIdsSHA256=canonical(self.host if h is None else h))
 def check(self,t,h=None,b=None):
  ids=self.host if h is None else h;bound=self.binding(t,ids)if b is None else b;return verify(t,ids,expected_binding=bound,current_binding=bound)
 def test_actual_whole_original_proposals(self):
  p=self.check(self.world);self.assertTrue(all(r['mountAssociationVerified']for r in p['rows']));self.assertEqual(p['rows'][0]['originalUpperFaceIds'],[278,279]);self.assertEqual(p['rows'][0]['originalOpenBoundariesPreserved'],4);self.assertEqual(p['rows'][1]['completeOriginalBackingSideFaces'],[456,457]);self.assertFalse(p['visualRoleAccepted']);self.assertFalse(p['structuralRootCredit']);self.assertFalse(p['installationApproved'])
 def test_part1_detached(self):
  t=self.world.copy();t[270:280,:,0]+=10
  with self.assertRaises(AssertionError):self.check(t)
 def test_part6_detached(self):
  t=self.world.copy();t[448:460,:,0]+=10
  with self.assertRaises(AssertionError):self.check(t)
 def test_remove_authored_upper_face(self):
  t=self.world.copy();t[278]=t[279]
  with self.assertRaises(AssertionError):self.check(t)
 def test_remove_back_facet(self):
  t=self.world.copy();t[456]=t[457]
  with self.assertRaises(AssertionError):self.check(t)
 def test_reverse_strip(self):
  t=self.world.copy();t[270:280]=t[270:280,::-1]
  with self.assertRaises(AssertionError):self.check(t)
 def test_zero_facet(self):
  t=self.world.copy();t[270]=t[270,0]
  with self.assertRaises(AssertionError):self.check(t)
 def test_tower_or_foreign_host(self):
  with self.assertRaises(AssertionError):self.check(self.world,h=list(range(641)))
 def test_incomplete_host(self):
  with self.assertRaises(AssertionError):self.check(self.world,h=self.host[:-1])
 def test_changed_expected_pose_binding(self):
  t=self.world.copy();t[:,0,0]+=.001
  with self.assertRaises(AssertionError):verify(t,self.host,expected_binding=self.__class__.BINDING,current_binding=self.binding(t))
 def test_wrong_uid(self):
  b=dict(self.__class__.BINDING,uid='landsd/261717:0')
  with self.assertRaises(AssertionError):self.check(self.world,b=b)
 def test_changed_original_source(self):
  b=dict(self.__class__.BINDING,sourceSHA256='0'*64)
  with self.assertRaises(AssertionError):self.check(self.world,b=b)
 def test_nonfinite(self):
  t=self.world.copy();t[270,0,0]=np.nan
  with self.assertRaises(AssertionError):self.check(t)
if __name__=='__main__':unittest.main()
