"""Reject incomplete, unobserved, duplicate and changed visual evidence."""
import copy,hashlib,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import ocean_coordinated_source_review_v1_20261027 as review

class ImageEvidence(unittest.TestCase):
    def setUp(self):
        self.directory=tempfile.TemporaryDirectory();self.addCleanup(self.directory.cleanup)
        self.root=Path(self.directory.name);self.rows=[];self.pins={}
        for i in range(2):
            name=f'frame-{i}.png';raw=f'exact-image-{i}'.encode();(self.root/name).write_bytes(raw)
            sha=hashlib.sha256(raw).hexdigest();self.pins[name]=sha
            self.rows.append(dict(path=name,sha256=sha,actuallyViewedByRoot=True))
        self.expected=list(self.pins)

    def verify(self,rows=None):
        with patch.object(review,'ROOT',self.root):
            return review.checked_observations(self.rows if rows is None else rows,self.expected,self.pins)

    def test_exact_complete_evidence(self):
        self.assertEqual(len(self.verify()),2)

    def test_missing_view_rejected(self):
        with self.assertRaises(AssertionError):self.verify(self.rows[:1])

    def test_duplicate_cannot_replace_missing_view(self):
        with self.assertRaises(AssertionError):self.verify([self.rows[0],self.rows[0]])

    def test_unviewed_frame_rejected(self):
        rows=copy.deepcopy(self.rows);rows[1]['actuallyViewedByRoot']=False
        with self.assertRaises(AssertionError):self.verify(rows)

    def test_changed_image_rejected(self):
        (self.root/self.rows[1]['path']).write_bytes(b'changed-after-review')
        with self.assertRaises(AssertionError):self.verify()

    def test_claimed_new_hash_does_not_replace_authenticated_hash(self):
        rows=copy.deepcopy(self.rows);raw=b'replaced';(self.root/rows[1]['path']).write_bytes(raw)
        rows[1]['sha256']=hashlib.sha256(raw).hexdigest()
        with self.assertRaises(AssertionError):self.verify(rows)

if __name__=='__main__':unittest.main()
