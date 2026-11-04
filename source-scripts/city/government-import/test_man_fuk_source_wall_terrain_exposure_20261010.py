import copy,unittest
import numpy as np
from run import ROOT,HERE,read
from man_fuk_source_wall_terrain_exposure_20261010 import propose,IDS,INCIDENT
class Actual(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  doc=ROOT/'docs/astra-city/government-import/government-xl-man-fuk-complete-retained-original-physical-v4-20261010';cls.patch=read(ROOT/read(doc/'terrain-candidates.json')[0]['path']);cls.raw=(ROOT/read(doc/'selection.json.gz')['rows'][0]['candidate']['path']).read_bytes()
 def test_actual_minimal_finite_constraint_proposal(self):
  out,proof=propose(self.patch,self.raw);a=np.asarray(self.patch['nativeMesh']['position']).reshape(-1,3);b=np.asarray(out['nativeMesh']['position']).reshape(-1,3)
  self.assertEqual(np.flatnonzero((a!=b).any(1)).tolist(),IDS);self.assertEqual(proof['changedIncidentTerrainFaces'],INCIDENT);self.assertLess(proof['actualFloat32VerticalChangeM'],.65);self.assertFalse(proof['exactSameSurfaceClaim']);self.assertEqual(proof['sourceGeometryChanges'],0)
 def reject(self,change):
  p=copy.deepcopy(self.patch);change(p)
  with self.assertRaises(AssertionError):propose(p,self.raw)
 def test_unrelated_height_rejected(self):self.reject(lambda p:p['nativeMesh']['position'].__setitem__(1,p['nativeMesh']['position'][1]+.001))
 def test_horizontal_change_rejected(self):self.reject(lambda p:p['nativeMesh']['position'].__setitem__(IDS[0]*3,p['nativeMesh']['position'][IDS[0]*3]+.001))
 def test_index_change_rejected(self):self.reject(lambda p:p['nativeMesh']['index'].__setitem__(0,p['nativeMesh']['index'][0]+1))
 def test_source_mutation_rejected(self):
  with self.assertRaises(AssertionError):propose(self.patch,self.raw+b' ')
 def test_reapplication_rejected(self):
  p,_=propose(self.patch,self.raw)
  with self.assertRaises(AssertionError):propose(p,self.raw)
if __name__=='__main__':unittest.main()
