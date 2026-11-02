"""The whole fixed cohort, both unmatched keys and prior installations persist."""
import copy
import unittest
import june_garden_installed_readback_v1_20261103 as readback


class FixedCohort(unittest.TestCase):
    def setUp(self):
        rows = [dict(sourceKey='source-'+str(i), uid='landsd/test'+str(i)+':0' if i<519 else None,
            indexedSourceSHA256='source-sha-'+str(i), runtimeSourceSHA256='source-sha-'+str(i) if i<426 else None,
            installedVerified=i<426) for i in range(521)]
        rows[426].update(uid=readback.P,indexedSourceSHA256=readback.SOURCES[readback.P])
        self.previous = dict(counts=dict(total=521,installedVerified=426,remaining=95),rows=rows)
        self.current = copy.deepcopy(self.previous)
        self.current['counts'] = dict(total=521,installedVerified=427,remaining=94)
        self.current['rows'][426].update(installedVerified=True,runtimeSourceSHA256=readback.SOURCES[readback.P])

    def test_exact_single_gain(self):
        self.assertEqual(readback.verify_fixed_cohort(self.previous,self.current)['uid'],readback.P)

    def test_missing_unmatched_source(self):
        self.current['rows'].pop()
        with self.assertRaises(AssertionError): readback.verify_fixed_cohort(self.previous,self.current)

    def test_duplicate_row_cannot_hide_extra_work(self):
        self.current['rows'].append(copy.deepcopy(self.current['rows'][0]))
        with self.assertRaises(AssertionError): readback.verify_fixed_cohort(self.previous,self.current)

    def test_previous_install_lost(self):
        self.current['rows'][0]['installedVerified'] = False
        with self.assertRaises(AssertionError): readback.verify_fixed_cohort(self.previous,self.current)

    def test_different_source_revision(self):
        self.current['rows'][426]['indexedSourceSHA256'] = 'different-revision'
        with self.assertRaises(AssertionError): readback.verify_fixed_cohort(self.previous,self.current)

    def test_unknown_uid_silently_assigned(self):
        self.current['rows'][520]['uid'] = 'landsd/invented:0'
        with self.assertRaises(AssertionError): readback.verify_fixed_cohort(self.previous,self.current)


if __name__ == '__main__': unittest.main()
