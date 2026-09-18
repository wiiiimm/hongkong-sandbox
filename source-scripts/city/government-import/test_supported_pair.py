import importlib.util
from pathlib import Path
import unittest
spec=importlib.util.spec_from_file_location('pair',Path(__file__).with_name('xxl-saxon-stage.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class SupportedPairTests(unittest.TestCase):
    def fixture(self):
        def metric(uid,sha,low):return {'uid':uid,'sourceSHA256':sha,'sourcePreserved':True,'minSurfaceGap':0,'minLowGap':low,'maxLowGap':low+.1,'maxSamplerDelta':0,'missingTerrain':0,'lowRimChecks':10,'budget':{'triangles':2,'geometryBytes':2,'residentBytes':2},'identity':{'overlap':1,'centroidDistance':0}}
        return {'rows':[metric(m.PODIUM,'p',0),metric(m.TOWER,'t',15)],'profiles':{'mobile':{'triangles':10,'geometryBytes':10,'residentBytes':10}}},{'supportSHA256':'p','towerSHA256':'t','lowRimSamples':10,'covered':10,'gapRange':[0,.33]}
    def test_supported_tower_requires_grounded_original_podium(self):
        a,b=self.fixture();self.assertEqual(m.supported_reasons(a,b),[]);a['rows'][0]['minSurfaceGap']=-2;self.assertIn('terrain-intersects-source-over-0.5m',m.supported_reasons(a,b))
    def test_missing_contact_or_large_gap_stays_held(self):
        for key,value in [('covered',9),('gapRange',[0,2]),('gapRange',[.2,.3])]:
            a,b=self.fixture();b[key]=value;self.assertIn('incomplete-native-podium-contact',m.supported_reasons(a,b))
    def test_source_integrity_and_identity_are_not_waived(self):
        a,b=self.fixture();a['rows'][1]['sourcePreserved']=False;a['rows'][1]['identity']['centroidDistance']=2;r=m.supported_reasons(a,b);self.assertIn('source-integrity',r);self.assertIn('strict-identity-fit',r)
if __name__=='__main__':unittest.main()
