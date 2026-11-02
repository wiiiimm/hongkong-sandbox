import json,tempfile,unittest
from pathlib import Path
from inspected_export_byte_binding_v1_20261103 import bind_inspected_bytes,sha
class ExactInspectionBinding(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
        self.old=self.root/'staged-landsd-7-0-390-1500-canvas.png';self.old.write_bytes(b'exact actual image bytes')
        self.new=self.root/'live-landsd-7-0-390-1500-canvas.png';self.new.write_bytes(self.old.read_bytes())
        self.review=self.root/'ROOT.json';self.value=dict(reviewer='ROOT',allListedExportsActuallyInspected=True,unresolvedVisibleFailuresInListedExports=[],images=[dict(path=self.old.name,sha256=sha(self.old))]);self.save()
    def save(self):self.review.write_text(json.dumps(self.value))
    def bind(self,path=None):return bind_inspected_bytes([path or self.new.name],[self.review.name],self.root)
    def test_exact_same_capture_bytes_reused_without_approval(self):
        out=self.bind();self.assertEqual(len(out['matched']),1);self.assertEqual(out['unseen'],[]);self.assertFalse(out['visualAcceptance']);self.assertFalse(out['softwareAcceptance'])
    def different_capture(self,name):
        p=self.root/name;p.write_bytes(self.old.read_bytes());out=self.bind(p.name);self.assertEqual(out['matched'],[]);self.assertEqual(len(out['unseen']),1)
    def test_other_uid_same_pixels_not_reused(self):self.different_capture('live-landsd-8-0-390-1500-canvas.png')
    def test_other_viewport_not_reused(self):self.different_capture('live-landsd-7-0-1280-1500-canvas.png')
    def test_other_time_not_reused(self):self.different_capture('live-landsd-7-0-390-2200-canvas.png')
    def test_other_capture_role_not_reused(self):self.different_capture('live-retained-own-landsd-7-0-390-1500-canvas.png')
    def test_changed_target_needs_own_review(self):
        self.new.write_bytes(b'one different pixel');self.assertEqual(len(self.bind()['unseen']),1)
    def test_changed_prior_image_rejected(self):
        self.old.write_bytes(b'changed old image')
        with self.assertRaises(AssertionError):self.bind()
    def test_not_actually_inspected_rejected(self):
        self.value['allListedExportsActuallyInspected']=False;self.save()
        with self.assertRaises(AssertionError):self.bind()
    def test_unresolved_prior_review_rejected(self):
        self.value['unresolvedVisibleFailuresInListedExports']=['unclear source'];self.save()
        with self.assertRaises(AssertionError):self.bind()
    def test_duplicate_prior_path_rejected(self):
        self.value['images']*=2;self.save()
        with self.assertRaises(AssertionError):self.bind()
    def test_review_cannot_read_outside_root(self):
        self.value['images'][0]['path']='../outside.png';self.save()
        with self.assertRaises(AssertionError):self.bind()
if __name__=='__main__':unittest.main()
