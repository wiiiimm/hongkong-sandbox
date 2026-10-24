import unittest
from pathlib import Path
from aqua_two_source_runtime_delta_v2_20261014 import assert_exact_delta
class Delta(unittest.TestCase):
    def setUp(self):
        p=Path(__file__).parent;self.old=(p/'aqua_marine193086138449_current_actual_attributes_v1_20261014.mjs').read_text();self.new=(p/'aqua_marine193086138449_current_actual_attributes_v2_20261014.mjs').read_text()
    def test_actual_exact_namespace_scanner_delta(self):self.assertTrue(assert_exact_delta(self.old,self.new))
    def test_arithmetic_change_rejected(self):
        with self.assertRaises(AssertionError):assert_exact_delta(self.old,self.new.replace('applyMatrix4(mesh.matrixWorld)','applyMatrix4(new THREE.Matrix4())'))
    def test_arbitrary_scanner_rejected(self):
        with self.assertRaises(AssertionError):assert_exact_delta(self.old,self.new.replace('exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs','arbitrary.mjs'))
if __name__=='__main__':unittest.main()
