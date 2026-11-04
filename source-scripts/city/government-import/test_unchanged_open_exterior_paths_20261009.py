import copy
import hashlib
import unittest
import numpy as np
from unchanged_open_exterior_paths_20261009 import original_open_paths
from original_face_ground_crossing_v2_20261009 import face_ground_context
from test_authored_wall_roof_paths_20261009 import fixture
from test_original_face_ground_crossing_20261009 import flat


def binding(tri):
    return {'sourceSHA256':'original-source','rootMatrix':list(np.eye(4).ravel()),
        'positionTriangleStreamSHA256':'original-position','normalTriangleStreamSHA256':'original-normal',
        'colourTriangleStreamSHA256':'original-colour','decodedWorldTrianglesSHA256':hashlib.sha256(tri.tobytes()).hexdigest(),
        'drawnGroundSHA256':'original-ground'}


def evaluate(tri,ground=None,expected=None,current=None):
    b=binding(tri);ground=flat() if ground is None else ground
    return original_open_paths(tri,[face_ground_context(t,ground) for t in tri],[2,3],range(len(tri)),
                               expected_binding=b if expected is None else expected,current_binding=b if current is None else current)


class OpenExteriorTests(unittest.TestCase):
    def test_original_open_body_never_certifies_solid(self):
        r=evaluate(fixture());self.assertTrue(r['allAffectedWallsHaveRoles'])
        self.assertFalse(r['closedSolidCertified']);self.assertFalse(r['installationApproved'])

    def test_authored_open_winding_conflict_preserved(self):
        tri=fixture();tri[2]=tri[2,[0,2,1]]
        r=evaluate(tri);self.assertTrue(r['allAffectedWallsHaveRoles'])
        self.assertGreater(len(r['originalOrientationConflicts']),0)

    def test_reversed_port_rejects_original_hash(self):
        tri=fixture();expected=binding(tri);tri[2]=tri[2,[0,2,1]]
        with self.assertRaises(AssertionError):evaluate(tri,expected=expected,current=expected)

    def test_detached_original_component_rejects(self):
        tri=fixture();tri[2:,:,0]+=4
        self.assertFalse(evaluate(tri)['allAffectedWallsHaveRoles'])

    def test_buried_upward_roof_and_unexposed_wall_reject(self):
        self.assertFalse(evaluate(fixture(),flat(3))['allAffectedWallsHaveRoles'])

    def test_missing_ground_rejects(self):
        g=np.array([[[1,0,-2],[4,0,-2],[1,0,4]]],float)
        self.assertFalse(evaluate(fixture(),g)['allAffectedWallsHaveRoles'])

    def test_changed_context_and_root_reject(self):
        t=fixture();a=binding(t);b=copy.deepcopy(a);b['drawnGroundSHA256']='other-ground'
        with self.assertRaises(AssertionError):evaluate(t,expected=a,current=b)
        b=copy.deepcopy(a);b['rootMatrix'][12]=1
        with self.assertRaises(AssertionError):evaluate(t,expected=a,current=b)


if __name__=='__main__':unittest.main()
