import copy
import unittest
from run import ROOT, read
from man_fuk_exact_recorded_height_metadata_20261010 import repair


class ExactMetadataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        row = read(ROOT / 'docs/astra-city/government-import/government-xl-man-fuk-current-bound-envelope-inputs-v2-20261010/selection.json.gz')['rows'][0]
        cls.entry, cls.building = row['candidate']['entry'], row['source']['building']
        cls.raw = (ROOT / row['candidate']['path']).read_bytes()

    def test_actual_exact_metadata_only(self):
        before = copy.deepcopy(self.entry)
        out, proof = repair(self.entry, self.building, self.raw)
        self.assertEqual(out['recordedTopHeight'], 43.4)
        self.assertEqual(self.entry, before)
        self.assertEqual(proof['changedFields'], ['recordedTopHeight'])
        self.assertFalse(proof['physicalAccepted'])

    def test_wrong_source_bytes(self):
        with self.assertRaises(AssertionError): repair(self.entry, self.building, self.raw + b'x')

    def test_other_recorded_height_mismatch(self):
        e = copy.deepcopy(self.entry); e['recordedTopHeight'] = 43.40001
        with self.assertRaises(AssertionError): repair(e, self.building, self.raw)

    def test_changed_authoritative_top(self):
        b = copy.deepcopy(self.building); b['topHeightHKPD'] = 44
        with self.assertRaises(AssertionError): repair(self.entry, b, self.raw)

    def test_changed_identity(self):
        b = copy.deepcopy(self.building); b['buildingCSUID'] = 'other'
        with self.assertRaises(AssertionError): repair(self.entry, b, self.raw)

    def test_changed_uid(self):
        b = copy.deepcopy(self.building); b['uid'] = 'landsd/75697:0'
        with self.assertRaises(AssertionError): repair(self.entry, b, self.raw)

    def test_changed_base(self):
        b = copy.deepcopy(self.building); b['baseHeightHKPD'] = 32.3
        with self.assertRaises(AssertionError): repair(self.entry, b, self.raw)


if __name__ == '__main__': unittest.main()
