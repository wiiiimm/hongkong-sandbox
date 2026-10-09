import hashlib,unittest
import numpy as np
from shapely.geometry import box,Polygon
from original_native_projection_protection_20261009 import verify

def check(native,source,protected,changed=False):
    n=np.asarray(native,float);s=np.asarray(source,float)
    b={'nativeDecodedWorldTrianglesSHA256':hashlib.sha256(n.tobytes()).hexdigest(),'sourceDecodedWorldTrianglesSHA256':hashlib.sha256(s.tobytes()).hexdigest(),
       'nativeSourceSHA256':'native','nativeCatalogueSHA256':'catalogue','sourceSHA256':'source','currentManifestSHA256':'manifest','currentNativeParentSHA256':'parent'}
    return verify(n,s,protected,expected_binding=b,current_binding={**b,'nativeSourceSHA256':'changed'} if changed else b)

class ProjectionProtectionTests(unittest.TestCase):
    native=[[[0,0,0],[1,0,0],[0,1,1]],[[4,0,4],[5,0,4],[4,1,5]]]
    source=[[[2,0,2],[3,0,2],[2,1,3]]]
    def test_actual_disjoint_mesh_survives_false_whole_bounds_overlap(self):
        protected=box(-1,-1,6,6).difference(box(1.5,1.5,3.5,3.5));r=check(self.native,self.source,protected)
        self.assertGreater(r['rawWholeBoundsProjectionOverlapM2'],0);self.assertTrue(r['completeOriginalNativeProjectionCoveredByProtectedParent']);self.assertFalse(r['installationApproved'])
    def test_real_native_face_inside_unprotected_hole_rejects(self):
        with self.assertRaisesRegex(AssertionError,'misses'):check(self.native,self.source,box(-1,-1,2,2))
    def test_source_touching_actual_native_face_rejects(self):
        with self.assertRaisesRegex(AssertionError,'touch'):check(self.native,self.native[:1],box(-1,-1,6,6))
    def test_original_vertical_face_cannot_be_omitted(self):
        n=self.native+[[[2,0,2],[2,1,2],[2,1,3]]]
        with self.assertRaisesRegex(AssertionError,'touch'):check(n,self.source,box(-1,-1,6,6))
    def test_original_collapsed_point_cannot_be_omitted(self):
        n=self.native+[[[2,0,2],[2,0,2],[2,0,2]]]
        with self.assertRaisesRegex(AssertionError,'touch'):check(n,self.source,box(-1,-1,6,6))
    def test_changed_native_source_binding_rejects(self):
        with self.assertRaises(AssertionError):check(self.native,self.source,box(-1,-1,6,6),changed=True)
    def test_unprotected_vertical_native_face_rejects(self):
        n=self.native+[[[7,0,7],[7,1,7],[7,1,8]]]
        with self.assertRaisesRegex(AssertionError,'misses'):check(n,self.source,box(-1,-1,6,6))

if __name__=='__main__':unittest.main()
