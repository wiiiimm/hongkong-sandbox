"""Actual complete proposal and adversarial source/terrain binding tests."""
import copy,unittest
import numpy as np
from run import ROOT,read
from man_fuk_source_ledge_terrain_ceiling_20261010 import propose,IDS,FACES
class Actual(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  d=ROOT/'docs/astra-city/government-import/government-xl-man-fuk-complete-retained-original-physical-v3-20261010';r=read(d/'selection.json.gz')['rows'][0];cls.source=(ROOT/r['candidate']['path']).read_bytes();cls.patch=read(ROOT/read(d/'terrain-candidates.json')[0]['path'])
 def test_actual_six_record_correction_preserves_every_other_value(self):
  before=copy.deepcopy(self.patch);out,p=propose(self.patch,self.source);self.assertEqual(self.patch,before);self.assertEqual(p['changedTerrainVertexRecords'],IDS);self.assertEqual(p['changedIncidentTerrainFaces'],FACES);self.assertTrue(.63<p['verticalTerrainChangeM']<.65);self.assertFalse(p['fullAcceptance']);self.assertEqual(p['sourceGeometryChanges'],0)
  a=np.asarray(out['nativeMesh']['position']).reshape(-1,3);b=np.asarray(before['nativeMesh']['position']).reshape(-1,3);self.assertEqual(np.flatnonzero(np.any(a!=b,axis=1)).tolist(),IDS);self.assertTrue(np.array_equal(a[:,[0,2]],b[:,[0,2]]));self.assertEqual(out['nativeMesh']['index'],before['nativeMesh']['index'])
 def test_changed_source_rejected(self):
  with self.assertRaises(AssertionError):propose(self.patch,self.source+b'x')
 def test_changed_unrelated_height_rejected(self):
  p=copy.deepcopy(self.patch);p['nativeMesh']['position'][1]+=.001
  with self.assertRaises(AssertionError):propose(p,self.source)
 def test_changed_horizontal_coordinate_rejected(self):
  p=copy.deepcopy(self.patch);p['nativeMesh']['position'][IDS[0]*3]+=.001
  with self.assertRaises(AssertionError):propose(p,self.source)
 def test_changed_indices_rejected(self):
  p=copy.deepcopy(self.patch);p['nativeMesh']['index'][0]=1
  with self.assertRaises(AssertionError):propose(p,self.source)
 def test_missing_duplicate_record_rejected(self):
  p=copy.deepcopy(self.patch);p['nativeMesh']['position'][IDS[0]*3+1]-=.001
  with self.assertRaises(AssertionError):propose(p,self.source)
 def test_cannot_apply_again_or_claim_equivalence(self):
  p,proof=propose(self.patch,self.source);self.assertFalse(proof['exactSameSurfaceClaim'])
  with self.assertRaises(AssertionError):propose(p,self.source)
if __name__=='__main__':unittest.main()
