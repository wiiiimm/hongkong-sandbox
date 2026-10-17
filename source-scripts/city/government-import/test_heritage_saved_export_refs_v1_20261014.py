import unittest
from heritage_saved_export_refs_v1_20261014 import saved_export_refs
import heritage165054_starmart57455_private_interface_review_v5_20261014 as a
class SavedExports(unittest.TestCase):
    def test_actual_six_saved_export_path_construction(self):
        views=a.read(a.FAILED_V3_DOC/'actual-private-interface-preview.json')['views']
        # The exact V4 expression reproduces the actual PosixPath setup failure.
        with self.assertRaises(TypeError):a.ref(a.ROOT[views[0]['cleanSolidImage']])
        refs=saved_export_refs(a.ROOT,views,a.ref)
        self.assertEqual(len(refs),6);self.assertEqual(len({q['path']for q in refs}),6)
        for q in refs:
            path=a.check(q);self.assertEqual(path,a.ROOT/q['path']);self.assertTrue(path.name.endswith('-1600x1100.png'));self.assertGreater(path.stat().st_size,1000)
        # Current preparation itself now exercises the SAME helper as owned().
        _,inputrefs=a.source_inputs();self.assertTrue(all(q in inputrefs for q in refs))
if __name__=='__main__':unittest.main()
