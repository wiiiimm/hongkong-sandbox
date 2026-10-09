import copy
import hashlib
import unittest
import numpy as np
from original_face_ground_crossing_v2_20261009 import face_ground_context
from unchanged_closed_column_role_20261009 import column_role,context_digest


def fixture():
    v=np.array([[0,-1,0],[1,-1,0],[1,-1,1],[0,-1,1],
                [0,2,0],[1,2,0],[1,2,1],[0,2,1]],float)
    f=[[0,1,2],[0,2,3],[4,6,5],[4,7,6],
       [0,4,5],[0,5,1],[1,5,6],[1,6,2],[2,6,7],[2,7,3],[3,7,4],[3,4,0]]
    tri=np.concatenate([v[f],np.array([[[.1,2,.1],[.8,2,.1],[.1,2,.8]]])])
    ground=np.array([[[-10,0,-10],[10,0,-10],[10,0,10]],[[-10,0,-10],[10,0,10],[-10,0,10]]],float)
    return tri,ground


def evidence(tri,ground):
    contexts=[dict(face_ground_context(f,ground),sourceFace=i) for i,f in enumerate(tri)]
    binding={k:'original-attribute-byte-binding' for k in ['sourceSHA256','positionTriangleStreamSHA256',
                 'normalTriangleStreamSHA256','colourTriangleStreamSHA256']}
    binding.update(rootMatrix=[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1],
                   decodedWorldTrianglesSHA256=hashlib.sha256(tri.tobytes()).hexdigest(),
                   decodedGroundTrianglesSHA256=hashlib.sha256(ground.tobytes()).hexdigest(),
                   continuousFaceContextSHA256=context_digest(contexts))
    return contexts,binding


class ColumnRoleTests(unittest.TestCase):
    def run_role(self,tri=None,ground=None,foreign=()):
        a,b=fixture();tri=a if tri is None else tri;ground=b if ground is None else ground
        contexts,binding=evidence(tri,ground)
        return column_role(tri,ground,contexts,list(range(12)),expected_binding=binding,
                           current_binding=binding,foreign_triangles=foreign)

    def test_original_column_preserves_raw_buried_bottom(self):
        r=self.run_role();self.assertTrue(r['verifiedColumnRole']);self.assertTrue(r['rawStrictBurialFaceFailures'])
        self.assertFalse(r['installationApproved']);self.assertFalse(r['basementCertified'])
        self.assertEqual(len(r['ordinarySourceFaces']),1)

    def test_detached_cap_attachment(self):
        tri,g=fixture();tri[12,:,1]+=1e-12
        self.assertIn('no-positive-length-original-cap-attachment-to-clear-exterior',self.run_role(tri)['reasons'])

    def test_reversed_closed_original_shell(self):
        tri,g=fixture();tri[:12]=tri[:12,::-1]
        self.assertIn('column-not-closed-outward-solid',self.run_role(tri)['reasons'])

    def test_buried_upward_cap(self):
        tri,g=fixture();g[:,:,1]=3
        self.assertFalse(self.run_role(tri,g)['verifiedColumnRole'])

    def test_missing_ground_projection(self):
        tri,g=fixture();g[:,:,0]+=100
        self.assertFalse(self.run_role(tri,g)['verifiedColumnRole'])

    def test_foreign_clear_geometry_intersection_rejects(self):
        tri,g=fixture()
        self.assertIn('foreign-column-intersection',self.run_role(foreign=tri[12:])['reasons'])

    def test_changed_source_or_context_binding(self):
        tri,g=fixture();contexts,binding=evidence(tri,g)
        for key in ['sourceSHA256','rootMatrix','continuousFaceContextSHA256','decodedGroundTrianglesSHA256']:
            changed=copy.deepcopy(binding);changed[key]='changed'
            with self.assertRaises(AssertionError):column_role(tri,g,contexts,list(range(12)),expected_binding=binding,current_binding=changed)

    def test_omitted_original_face(self):
        tri,g=fixture();contexts,binding=evidence(tri,g)
        with self.assertRaises(AssertionError):column_role(tri,g,contexts,list(range(11)),expected_binding=binding,current_binding=binding)

    def test_ordinary_face_burial_cannot_receive_column_credit(self):
        tri,g=fixture();tri[12,:,1]=-2
        self.assertIn('ordinary-clearance:12',self.run_role(tri)['reasons'])


if __name__=='__main__':unittest.main()
