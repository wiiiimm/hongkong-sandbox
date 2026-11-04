import unittest,numpy as np
from original_coplanar_exterior_continuation_20261009 import diagnose
class Tests(unittest.TestCase):
 def test_exact_shared_sheet(self):
  t=np.array([[[0,-2,0],[1,0,0],[0,0,0]],[[0,0,0],[1,0,0],[0,2,0]]],float);c=[{'sourceFace':i,'groundProjectionCovered':True,'minimum':{'minimumGapM':-2 if i==0 else 0},'maximumObservedGapM':0 if i==0 else 2} for i in range(2)];r=diagnose(t,c,[0]);self.assertEqual(r['rows'][0]['exactConnectedCoplanarSheetFaces'],[0,1]);self.assertTrue(r['rows'][0]['hasActualAboveGroundExteriorContinuation'])
 def test_parallel_offset_not_coplanar(self):
  t=np.array([[[0,-2,0],[1,0,0],[0,0,0]],[[0,0,.00000001],[1,0,.00000001],[0,2,.00000001]]],float);c=[{'sourceFace':i,'groundProjectionCovered':True,'minimum':{},'maximumObservedGapM':i} for i in range(2)];self.assertFalse(diagnose(t,c,[0])['rows'][0]['hasActualAboveGroundExteriorContinuation'])
 def test_corner_only_not_connected(self):
  t=np.array([[[0,-2,0],[1,0,0],[0,0,0]],[[1,0,0],[2,0,0],[2,2,0]]],float);c=[{'sourceFace':i,'groundProjectionCovered':True,'minimum':{},'maximumObservedGapM':i} for i in range(2)];self.assertEqual(diagnose(t,c,[0])['rows'][0]['exactConnectedCoplanarSheetFaces'],[0])
 def test_no_exposed_ground_context_rejects_role(self):
  t=np.array([[[0,-2,0],[1,0,0],[0,0,0]],[[0,0,0],[1,0,0],[0,2,0]]],float);c=[{'sourceFace':i,'groundProjectionCovered':True,'minimum':{'minimumGapM':-3},'maximumObservedGapM':-1} for i in range(2)];self.assertFalse(diagnose(t,c,[0])['rows'][0]['hasActualAboveGroundExteriorContinuation'])
if __name__=='__main__':unittest.main()
