import unittest
from reviewed_image_provenance_v1_20261023 import verify_image

class ReviewedImageTests(unittest.TestCase):
    def setUp(self):
        self.bytes = {'new.png': 'same', 'viewed.png': 'same'}
        self.alias = dict(path='new.png', sha256='same', viewedOriginalPath='viewed.png', copiedByteIdentically=True)
    def check(self, ref):
        assert self.bytes[ref['path']] == ref['sha256']
    def test_original(self):
        verify_image(dict(path='viewed.png', sha256='same'), self.check)
    def test_exact_copy(self):
        verify_image(self.alias, self.check)
    def test_changed_copy(self):
        self.bytes['new.png'] = 'changed'
        with self.assertRaises(AssertionError): verify_image(self.alias, self.check)
    def test_changed_viewed_original(self):
        self.bytes['viewed.png'] = 'changed'
        with self.assertRaises(AssertionError): verify_image(self.alias, self.check)
    def test_false_claim(self):
        self.alias['copiedByteIdentically'] = False
        with self.assertRaises(AssertionError): verify_image(self.alias, self.check)
    def test_partial_provenance(self):
        del self.alias['viewedOriginalPath']
        with self.assertRaises(AssertionError): verify_image(self.alias, self.check)
    def test_unknown_provenance(self):
        self.alias['approved'] = True
        with self.assertRaises(AssertionError): verify_image(self.alias, self.check)

if __name__ == '__main__': unittest.main()
