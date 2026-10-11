import unittest
from original_ordinary_rim_accounting_20261009 import verify
from original_wall_rim_accounting_20261009 import original_samples
class OrdinaryOriginalRimTests(unittest.TestCase):
    def fixture(self,gaps=None):
        p=[0.,0.,0.,3.,0.,0.,0.,0.,3.];idx=[0,1,2];rows=original_samples(p,idx,0.)
        gaps=gaps or [0.]*len(rows)
        for r,g in zip(rows,gaps):r.update(ground=r['point'][1]-g,gap=g)
        return p,idx,rows,{'checks':len(rows),'lowRimChecks':len(rows),'minSurfaceGap':min(gaps),'minLowGap':min(gaps),'maxLowGap':max(gaps)}
    def check(self,data):
        p,i,r,m=data;return verify(p,i,0.,r,expected_metric=m)
    def test_negative_ordinary_gap_preserves_anchor_and_raw_warning(self):
        d=self.fixture();d[2][0].update(ground=.45,gap=-.45);d[3].update(minSurfaceGap=-.45,minLowGap=-.45)
        r=self.check(d);self.assertTrue(r['verified']);self.assertEqual(r['rawStricterResolverLowerRimSamplesRetained'],1);self.assertFalse(r['wallRoleCredit']);self.assertFalse(r['installationApproved'])
    def test_real_ordinary_burial_rejects(self):
        d=self.fixture();d[2][0].update(ground=.500001,gap=-.500001);d[3].update(minSurfaceGap=-.500001,minLowGap=-.500001)
        with self.assertRaises(AssertionError):self.check(d)
    def test_missing_strict_anchor_rejects(self):
        d=self.fixture();d=self.fixture([-.4]*len(d[2]))
        with self.assertRaises(AssertionError):self.check(d)
    def test_floating_rim_rejects(self):
        d=self.fixture();d[2][1].update(ground=-1.01,gap=1.01);d[3]['maxLowGap']=1.01
        with self.assertRaises(AssertionError):self.check(d)
    def test_missing_sample_rejects(self):
        d=self.fixture();d[2].pop()
        with self.assertRaises(AssertionError):self.check(d)
    def test_changed_incidence_rejects(self):
        d=self.fixture();d[2][0]['originalIncidentFaces']=[2]
        with self.assertRaises(AssertionError):self.check(d)
    def test_changed_metric_rejects(self):
        d=self.fixture();d[3]['minSurfaceGap']=-.1
        with self.assertRaises(AssertionError):self.check(d)
    def test_missing_ground_rejects(self):
        d=self.fixture();d[2][0]['ground']=float('nan')
        with self.assertRaises(AssertionError):self.check(d)
    def test_changed_gap_rejects(self):
        d=self.fixture();d[2][0]['ground']=.01
        with self.assertRaises(AssertionError):self.check(d)
    def test_unreferenced_vertex_rejects(self):
        p,i,r,m=self.fixture();p += [10.,0.,10.];rows=original_samples(p,i,0.)
        for r in rows:r.update(ground=0.,gap=0.)
        m.update(checks=len(rows),lowRimChecks=len(rows))
        with self.assertRaises(AssertionError):verify(p,i,0.,rows,expected_metric=m)
if __name__=='__main__':unittest.main()
