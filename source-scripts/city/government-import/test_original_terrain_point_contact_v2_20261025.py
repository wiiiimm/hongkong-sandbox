import unittest
import test_original_terrain_point_contact_v1_20261025 as fixtures
from original_terrain_point_contact_v2_20261025 import verify


class ViewerPatchSchemaTests(unittest.TestCase):
    def setUp(self):
        self.f = fixtures.PointContactTests(); self.f.setUp()

    def proof(self):
        return verify(self.f.scope,self.f.new,self.f.root,{'old.json':self.f.old})

    def test_flat_exact_point_still_passes(self):
        self.assertEqual(self.proof()['rows'][0]['sharedPoint'],[1.,15.,1.])

    def test_actual_old_nested_patch_schema_is_rejected(self):
        self.f.old['patches']=[dict(nativeMesh={})]
        with self.assertRaises(AssertionError): self.proof()

    def test_actual_candidate_nested_patch_schema_is_rejected(self):
        self.f.new['patches']=[dict(nativeMesh={})]
        with self.assertRaises(AssertionError): self.proof()


if __name__ == '__main__': unittest.main()
