import unittest
from summarise_regional_batch import aggregate


class RegionalSummaryTests(unittest.TestCase):
    def test_nonbeneficial_candidates_retained_without_false_savings(self):
        def m(source, output):
            return {'originalDownloadBytes': source, 'downloadBytes': output,
                'beneficial': output < source, 'triangles': 2}
        result = aggregate([('progressive', 'high', m(100, 50), 3),
            ('progressive', 'high', m(100, 150), 3), ('embedded', 'high', m(500, 600), 3)])
        self.assertEqual(result['progressive / high']['candidateBytes'], 200)
        self.assertEqual(result['progressive / high']['effectiveBytesKeepingSmaller'], 150)
        self.assertEqual(result['progressive / high']['potentialSavingsPercent'], 25)
        self.assertEqual(result['embedded / high']['potentialSavingsPercent'], 0)
        self.assertEqual(result['embedded / high']['sourceBytes'], 500)

    def test_inconsistent_benefit_flag_is_rejected(self):
        with self.assertRaises(ValueError):
            aggregate([('embedded', 'high', {'originalDownloadBytes': 100,
                'downloadBytes': 200, 'beneficial': True, 'triangles': 2}, 2)])
