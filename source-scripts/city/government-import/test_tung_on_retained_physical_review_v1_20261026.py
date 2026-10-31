"""Reject broadened source/face exceptions using the actual frozen measurements."""
import copy,json,unittest
from pathlib import Path
from tung_on_retained_physical_review_v1_20261026 import validate_grade_context,ROOT,PREFIX

class GradeBindingTests(unittest.TestCase):
    def setUp(self):
        base=ROOT/'docs/astra-city/government-import'
        self.data=[json.loads((base/(PREFIX+n+'-20261026')/'summary.json').read_text())for n in ['retained-low-faces-v2','complete-cap-paths-v1','bottom-face-context-v1']]
    def reject(self,mutate):
        data=copy.deepcopy(self.data);mutate(data)
        with self.assertRaises(AssertionError):validate_grade_context(*data)
    def test_actual_complete_four_world_measurements(self):validate_grade_context(*self.data)
    def test_wrong_source(self):self.reject(lambda d:d[0].update(sourceSHA256='0'*64))
    def test_upward_bottom(self):self.reject(lambda d:d[2]['rows'][0]['faces'][0].update(downward=False))
    def test_unpaired_bottom(self):self.reject(lambda d:d[2]['rows'][0]['faces'][0]['exactEdgeIncidence'][0].update(incidentSourceFaces=[22]))
    def test_additional_nonwall(self):self.reject(lambda d:d[1]['rows'][0]['completeGroundClearancePartition'].update(negativeNonWallFaces=[22,23]))
    def test_failed_wall_cap(self):self.reject(lambda d:d[1]['rows'][0]['completeGroundClearancePartition']['paths'][0].update(hasExactSharedEdgeClearCapPath=False))
    def test_changed_negative_partition(self):self.reject(lambda d:d[0]['rows'][0]['exactAffectedFaces'].append(100))
    def test_missing_world(self):self.reject(lambda d:d[2]['rows'].pop())
    def test_false_raw_pass(self):self.reject(lambda d:d[1].update(allFourCompleteGroundClearCapPaths=True))

if __name__=='__main__':unittest.main()
