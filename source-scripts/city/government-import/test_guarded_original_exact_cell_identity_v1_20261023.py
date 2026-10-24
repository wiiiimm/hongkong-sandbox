import unittest
from copy import deepcopy
from test_exact_original_georef_cell_identity_20261009 import ExactOriginalCellTests
from guarded_original_exact_cell_identity_v1_20261023 import apply_exact_cell,REASON

class GuardedCellTests(unittest.TestCase):
    def fixture(self):return ExactOriginalCellTests().fixture()
    def test_unavailable_cell_preserves_other_rejections(self):
        t,p,b=self.fixture();p['geographicCell']={'error':'unsupported model identifier'};p['reasons']=['full-source-unrelated-overlap'];before=deepcopy(p)
        r=apply_exact_cell(p,t,expected_binding=b,current_binding=b)
        self.assertFalse(r['passed']);self.assertIn('full-source-unrelated-overlap',r['reasons']);self.assertIn(REASON,r['reasons']);self.assertFalse(r['installationApproved']);self.assertEqual(p,before)
    def test_missing_or_malformed_cell_is_a_hold(self):
        for cell in [None,[], 'unavailable']:
            t,p,b=self.fixture();p['geographicCell']=cell
            self.assertFalse(apply_exact_cell(p,t,expected_binding=b,current_binding=b)['passed'])
    def test_unsupported_cell_cannot_keep_a_raw_positive(self):
        t,p,b=self.fixture();p.update(geographicCell={},reasons=[],passed=True)
        r=apply_exact_cell(p,t,expected_binding=b,current_binding=b)
        self.assertFalse(r['passed']);self.assertFalse(any(r['proof'].values()))
    def test_unavailable_cell_still_rejects_changed_source(self):
        t,p,b=self.fixture();p['geographicCell']={};t[0,0,0]=.1
        with self.assertRaises(AssertionError):apply_exact_cell(p,t,expected_binding=b,current_binding=b)
    def test_unavailable_cell_still_rejects_changed_binding(self):
        t,p,b=self.fixture();p['geographicCell']={}
        with self.assertRaises(AssertionError):apply_exact_cell(p,t,expected_binding=b,current_binding={**b,'uid':'other'})
    def test_valid_cell_uses_existing_exact_policy(self):
        t,p,b=self.fixture();self.assertTrue(apply_exact_cell(p,t,expected_binding=b,current_binding=b)['passed'])
        t[1,1,0]-=1e-10
        import hashlib
        p['worldTrianglesSHA256']=b['decodedWorldTrianglesSHA256']=hashlib.sha256(t.tobytes()).hexdigest()
        self.assertFalse(apply_exact_cell(p,t,expected_binding=b,current_binding=b)['passed'])

if __name__=='__main__':unittest.main()
