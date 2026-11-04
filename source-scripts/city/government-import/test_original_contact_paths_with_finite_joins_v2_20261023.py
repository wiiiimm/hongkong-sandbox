import unittest
import numpy as np
from original_contact_paths_with_finite_joins_v2_20261023 import paths

def report(start,endface,endpoints):
    return dict(targets=[dict(witness=dict(position=start),incidentFaces=[0])],proof=dict(contacts=[dict(sourcePrimitiveDimensionA=2,sourcePrimitiveDimensionB=2,dimension=1,sourceFaceA=endface,sourceFaceB=0,maximumSpanM=1,exactPoints=endpoints)]))

class FinitePaths(unittest.TestCase):
    def test_valid_shared_edge_path_remains(self):
        t=np.array([[[0.,0.,0.],[1.,0.,0.],[0.,0.,1.]],[[1.,0.,0.],[1.,0.,1.],[0.,0.,1.]]])
        r=report([0.,0.,0.],1,[['1','0','0'],['1','0','1']]);self.assertIsNotNone(paths(t,r,[])[0]['verifiedPath'])
    def test_nonrendering_line_cannot_bridge_two_surfaces(self):
        t=np.array([[[0.,0.,0.],[1.,0.,0.],[0.,1.,0.]],[[1.,0.,0.],[3.,0.,0.],[3.,1.,0.]],[[0.,0.,0.],[1.,0.,0.],[3.,0.,0.]]])
        r=report([0.,0.,0.],1,[['1','0','0'],['3','0','0']]);self.assertIsNone(paths(t,r,[])[0]['verifiedPath'])
    def test_point_only_join_is_rejected(self):
        t=np.array([[[0.,0.,0.],[1.,0.,0.],[0.,0.,1.]],[[1.,0.,0.],[1.,0.,1.],[0.,0.,1.]]]);r=report([0.,0.,0.],1,[['1','0','0'],['1','0','1']])
        c=dict(sourceFaceA=0,sourceFaceB=1,dimension=0,primitiveDimensions=[2,2],exactPoints=[['1','0','0']])
        with self.assertRaises(AssertionError):paths(t,r,[c])
    def test_wrong_surface_contact_is_rejected(self):
        t=np.array([[[0.,0.,0.],[1.,0.,0.],[0.,0.,1.]],[[1.,0.,0.],[1.,0.,1.],[0.,0.,1.]]]);r=report([0.,0.,0.],1,[['1','0','0'],['1','0','1']])
        c=dict(sourceFaceA=0,sourceFaceB=1,dimension=1,primitiveDimensions=[2,2],exactPoints=[['100','0','0'],['101','0','0']])
        with self.assertRaises(AssertionError):paths(t,r,[c])

if __name__=='__main__':unittest.main()
