import unittest
import numpy as np
from authored_wall_roof_paths_20261009 import authored_paths
from original_face_ground_crossing_v2_20261009 import face_ground_context
from test_original_face_ground_crossing_20261009 import flat


def fixture():
    a,b,c,d=np.array([[0,2,0],[2,2,0],[2,2,2],[0,2,2]],float)
    aa,bb=a.copy(),b.copy();aa[1]=bb[1]=-1
    return np.array([[a,d,c],[a,c,b],[aa,a,b],[aa,b,bb]])


def evaluate(tri,ground=None):
    ground=flat() if ground is None else ground
    context=[face_ground_context(t,ground) for t in tri]
    return authored_paths(tri,context,[2,3],range(len(tri)))


class AuthoredWallTests(unittest.TestCase):
    def test_original_opposed_edge_path(self):
        r=evaluate(fixture());self.assertTrue(r['allAffectedWallsHaveRoles'])
        self.assertEqual(r['faces'][1]['wallToRoofPath'],[3,2,1])
        self.assertFalse(r['installationApproved'])

    def test_detached_wall_rejects(self):
        t=fixture();t[2:,:,0]+=4
        self.assertFalse(evaluate(t)['allAffectedWallsHaveRoles'])

    def test_reversed_wall_rejects(self):
        t=fixture();t[2]=t[2,[0,2,1]]
        self.assertFalse(evaluate(t)['allAffectedWallsHaveRoles'])

    def test_reversed_roof_has_no_wall_role(self):
        t=fixture();t[1]=t[1,[0,2,1]]
        self.assertFalse(evaluate(t)['allAffectedWallsHaveRoles'])

    def test_buried_upward_roof_rejects(self):
        self.assertFalse(evaluate(fixture(),flat(3))['allAffectedWallsHaveRoles'])

    def test_real_missing_ground_rejects(self):
        g=np.array([[[1,0,-2],[4,0,-2],[1,0,4]]],float)
        self.assertFalse(evaluate(fixture(),g)['allAffectedWallsHaveRoles'])

    def test_no_exposed_wall_rejects(self):
        self.assertFalse(evaluate(fixture(),flat(2))['allAffectedWallsHaveRoles'])


if __name__=='__main__':unittest.main()
