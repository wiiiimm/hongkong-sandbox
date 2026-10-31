import unittest
import numpy as np
import shapely
from unchanged_open_exterior_paths_v2_20261009 import original_open_paths
from test_unchanged_open_exterior_paths_20261009 import binding
from test_authored_wall_roof_paths_20261009 import fixture
from test_original_face_ground_crossing_20261009 import flat
from original_face_ground_crossing_v2_20261009 import face_ground_context
from original_degenerate_ground_context_20261009 import degenerate_ground_context


def evaluate(tri,affected=[2,3]):
    normal=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);length=np.linalg.norm(normal,axis=1)
    ground=flat();polygons=shapely.polygons(ground[:,:,[0,2]]);tree=shapely.STRtree(polygons)
    contexts=[face_ground_context(t,ground) if length[i]>0 else degenerate_ground_context(t,ground,polygons,tree) for i,t in enumerate(tri)]
    b=binding(tri)
    return original_open_paths(tri,contexts,affected,range(len(tri)),expected_binding=b,current_binding=b)


class CollapsedOriginalTests(unittest.TestCase):
    def test_account_collapsed_ordinary_without_role_bridge(self):
        tri=np.concatenate([fixture(),np.array([[[10,0,0],[11,0,0],[12,0,0]]],float)])
        r=evaluate(tri);self.assertTrue(r['allAffectedWallsHaveRoles'])
        self.assertEqual(r['collapsedOriginalFacesExcludedFromRolePaths'],[4]);self.assertEqual(r['originalComponentFaces'],list(range(5)))
    def test_collapsed_face_cannot_receive_wall_credit(self):
        tri=np.concatenate([fixture(),np.array([[[10,-1,0],[11,0,0],[12,1,0]]],float)])
        with self.assertRaises(AssertionError):evaluate(tri,[4])
    def test_collapsed_face_does_not_connect_detached_wall_to_roof(self):
        tri=fixture();tri[2:,:,0]+=4
        bridge=np.array([[tri[0,0],tri[2,0],tri[2,0]]],float)
        self.assertFalse(evaluate(np.concatenate([tri,bridge]))['allAffectedWallsHaveRoles'])


if __name__=='__main__':unittest.main()
