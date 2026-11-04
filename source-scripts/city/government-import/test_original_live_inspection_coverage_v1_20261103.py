import json,tempfile,unittest
from pathlib import Path
from original_live_inspection_coverage_v1_20261103 import report_targets,committed_review
class CompletedLiveCoverage(unittest.TestCase):
    def setUp(self):self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name).resolve();self.report={'passed':True,'errors':[],'views':[{'time':'15:00','file':'live-landsd-7-0-390-1500-canvas.png'}],'retainedNativeOwnViews':[]}
    def test_complete_report_set(self):self.assertEqual(len(report_targets(self.root,self.report,1,self.root)),1)
    def test_report_failure_rejected(self):
        self.report['passed']=False
        with self.assertRaises(AssertionError):report_targets(self.root,self.report,1,self.root)
    def test_report_errors_rejected(self):
        self.report['errors']=['shader-error']
        with self.assertRaises(AssertionError):report_targets(self.root,self.report,1,self.root)
    def test_missing_capture_rejected(self):
        with self.assertRaises(AssertionError):report_targets(self.root,self.report,2,self.root)
    def test_duplicate_capture_rejected(self):
        self.report['views']*=2
        with self.assertRaises(AssertionError):report_targets(self.root,self.report,2,self.root)
    def test_outside_capture_rejected(self):
        self.report['views'][0]['file']='../outside.png'
        with self.assertRaises(AssertionError):report_targets(self.root,self.report,1,self.root)
    def test_non_time_phase_does_not_substitute_for_image(self):
        self.report['views'].append({'phase':'retry','file':'retry.png'});self.assertEqual(len(report_targets(self.root,self.report,1,self.root)),1)
    def test_committed_actual_review_binds(self):
        p=self.root/'ROOT.json';raw=json.dumps(dict(reviewer='ROOT',allListedExportsActuallyInspected=True)).encode();p.write_bytes(raw);self.assertEqual(committed_review(p,self.root,lambda name:raw)['binding'],'exact-committed-HEAD-bytes')
    def test_modified_review_rejected(self):
        p=self.root/'ROOT.json';p.write_text('{}')
        with self.assertRaises(AssertionError):committed_review(p,self.root,lambda name:b'{"reviewer":"ROOT"}')
    def test_nonactual_review_rejected(self):
        p=self.root/'ROOT.json';raw=json.dumps(dict(reviewer='ROOT',allListedExportsActuallyInspected=False)).encode();p.write_bytes(raw)
        with self.assertRaises(AssertionError):committed_review(p,self.root,lambda name:raw)
if __name__=='__main__':unittest.main()
