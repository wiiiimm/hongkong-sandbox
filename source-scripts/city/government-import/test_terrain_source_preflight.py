"""Regression cases from original source geometry and the real government index."""
import unittest
from run import ROOT, read
from terrain_source_preflight import SourceSheetIndex, identity_proof


class SourcePreflightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index = SourceSheetIndex(read(ROOT / 'source-scripts/city/landmark-acquisition/index.json'))
        base = ROOT / 'docs/astra-city/government-import/government-xl-next-100-20261005'
        cls.rows = {r['uid']: r for r in read(base / 'check-selection.json.gz')['rows']}
        cls.context = {r['uid']: r for r in read(base / 'context.json.gz')['rows']}

    def test_hanford_selects_southern_quadrants(self):
        hits = self.index.covering_sheets(self.rows['landsd/276187:0']['native']['model']['worldBounds'])
        self.assertEqual({h['sheet'] for h in hits}, {'6-SW-11A', '6-SW-11B', '6-SW-11C', '6-SW-11D'})

    def test_1883_selects_exact_adjoining_sheet(self):
        hits = self.index.covering_sheets(self.rows['landsd/118475:0']['native']['model']['worldBounds'])
        self.assertEqual({h['sheet'] for h in hits}, {'11-NW-24D', '11-NW-25C'})

    def test_bus_terminus_avoids_unneeded_adjacent_download(self):
        hits = self.index.covering_sheets(self.rows['landsd/255415:0']['native']['model']['worldBounds'])
        self.assertEqual({h['sheet'] for h in hits}, {'11-NW-24A'})

    def test_coarse_identity_does_not_clear_source_projection(self):
        for uid in ('landsd/270142:0', 'landsd/11093:0', 'landsd/198440:0'):
            with self.subTest(uid=uid):
                result = identity_proof(self.rows[uid], self.context[uid])
                self.assertFalse(result['passed'])
                self.assertEqual(result['reasons'], ['source-identity-fit'])

    def test_bounded_detailed_identity_keeps_existing_proof(self):
        result = identity_proof(self.rows['landsd/118230:0'], self.context['landsd/118230:0'])
        self.assertTrue(result['passed'])
        self.assertTrue(all(result['proof'].values()))

    def test_partial_index_rejected(self):
        with self.assertRaises(AssertionError):
            SourceSheetIndex({'completePagination': False, 'features': []})


if __name__ == '__main__':
    unittest.main()
