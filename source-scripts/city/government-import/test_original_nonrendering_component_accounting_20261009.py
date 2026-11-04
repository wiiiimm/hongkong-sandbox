import hashlib,json,unittest,numpy as np
from original_nonrendering_component_accounting_20261009 import verify
class NonrenderingTests(unittest.TestCase):
    def fixture(self):
        t=np.asarray([[[0,0,0],[0,0,0],[0,1,0]]],float);c={'0':dict(sourceFace=0,sourceDegenerate=True,groundProjectionCovered=True,minimum={'minimumGapM':0})};return t,[dict(globalOriginalFaces=[0])],c
    def run_fixture(self,f,changed=None):
        t,com,c=f;b=dict(completeOriginalWorldTrianglesSHA256=hashlib.sha256(t.tobytes()).hexdigest(),originalBytesAndIndicesUnchanged=True,currentDrawnGroundSHA256='ground',completeOriginalSourceBindingSHA256='source',continuousNonrenderingContextsSHA256=hashlib.sha256(json.dumps(c,sort_keys=True,separators=(',',':')).encode()).hexdigest());return verify(*f,expected_binding=b,current_binding=changed or b)
    def test_original_repeated_vertex_line_retained(self):self.assertTrue(self.run_fixture(self.fixture())['verifiedNonrenderingAccounting'])
    def test_exact_collinear_three_vertices_retained(self):
        f=self.fixture();f[0][0,1]=[0,.5,0];self.assertTrue(self.run_fixture(f)['verifiedNonrenderingAccounting'])
    def test_tiny_real_area_rejected(self):
        f=self.fixture();f[0][0,1]=[1e-30,0,0]
        with self.assertRaises(AssertionError):self.run_fixture(f)
    def test_buried_original_line_rejected(self):
        f=self.fixture();f[2]['0']['minimum']['minimumGapM']=-.50000001
        with self.assertRaises(AssertionError):self.run_fixture(f)
    def test_missing_current_ground_rejected(self):
        f=self.fixture();f[2]['0']['groundProjectionCovered']=False
        with self.assertRaises(AssertionError):self.run_fixture(f)
    def test_omitted_original_context_rejected(self):
        f=self.fixture();f[2].clear()
        with self.assertRaises(AssertionError):self.run_fixture(f)
    def test_stale_source_rejected(self):
        with self.assertRaises(AssertionError):self.run_fixture(self.fixture(),{'source':'changed'})
    def test_repeated_original_face_rejected(self):
        f=self.fixture();f[1][0]['globalOriginalFaces']=[0,0]
        with self.assertRaises(AssertionError):self.run_fixture(f)
if __name__=='__main__':unittest.main()
