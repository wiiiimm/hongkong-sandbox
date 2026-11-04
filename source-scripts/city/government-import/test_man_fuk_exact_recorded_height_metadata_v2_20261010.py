"""Actual fresh corrected metadata and mutations must retain the old proof."""
import copy
import unittest
from run import ROOT, read
from man_fuk_exact_recorded_height_metadata_v2_20261010 import repair

ROW = read(ROOT / 'docs/astra-city/government-import/government-xl-man-fuk-current-bound-envelope-inputs-v3-20261010/selection.json.gz')['rows'][0]
ENTRY = ROW['candidate']['entry']
BUILDING = ROW['source']['building']
RAW = (ROOT / ROW['candidate']['path']).read_bytes()


class ExactPriorCorrection(unittest.TestCase):
    def test_actual_complete_prior_correction_replayed_without_changes(self):
        entry = copy.deepcopy(ENTRY)
        out, proof = repair(entry, BUILDING, RAW)
        self.assertEqual(entry, ENTRY)
        self.assertEqual(out, ENTRY)
        self.assertEqual(proof['changedFields'], [])
        self.assertFalse(proof['physicalAccepted'])
        self.assertFalse(proof['loaderSourceEqualityWaived'])

    def reject(self, entry=ENTRY, building=BUILDING, raw=RAW):
        with self.assertRaises(AssertionError):
            repair(entry, building, raw)

    def test_source_changed(self):
        self.reject(raw=RAW + b'x')

    def test_current_authoritative_top_changed(self):
        b = copy.deepcopy(BUILDING); b['topHeightHKPD'] = 44
        self.reject(building=b)

    def test_recorded_top_changed(self):
        e = copy.deepcopy(ENTRY); e['recordedTopHeight'] += .001
        self.reject(entry=e)

    def test_unrelated_complete_entry_field_changed(self):
        e = copy.deepcopy(ENTRY); e['triangles'] -= 1
        self.reject(entry=e)

    def test_source_transform_changed(self):
        e = copy.deepcopy(ENTRY); e['rootTranslation'][0] += 1
        self.reject(entry=e)

    def test_current_identity_changed(self):
        b = copy.deepcopy(BUILDING); b['buildingCSUID'] = 'other'
        self.reject(building=b)

    def test_arithmetic_value_not_silently_repaired(self):
        e = copy.deepcopy(ENTRY); e['recordedTopHeight'] = 43.400000000000006
        self.reject(entry=e)


if __name__ == '__main__':
    unittest.main()
