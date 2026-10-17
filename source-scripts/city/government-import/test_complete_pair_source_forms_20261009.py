import copy
import unittest
from complete_pair_source_forms_20261009 import add_form

class CompletePairSourceFormsTests(unittest.TestCase):
    def fixture(self):return {'building':{'uid':'landsd/177605:0','height':41.9},'tile':'city/data/tiles/0_-2.json','tileSHA256':'pinned'}
    def test_identical_overlap_between_verified_groups_is_valid(self):
        record=self.fixture();out={}
        add_form(out,set(),record);add_form(out,set(),copy.deepcopy(record))
        self.assertEqual(out,{record['building']['uid']:record})
    def test_duplicate_within_one_group_rejects(self):
        out={};seen=set();record=self.fixture();add_form(out,seen,record)
        with self.assertRaises(AssertionError):add_form(out,seen,record)
    def test_stale_geometry_or_different_tile_rejects(self):
        for field,value in [('tile','other.json'),('tileSHA256','changed')]:
            out={};record=self.fixture();add_form(out,set(),record)
            changed=copy.deepcopy(record);changed[field]=value
            with self.assertRaises(AssertionError):add_form(out,set(),changed)
        out={};record=self.fixture();add_form(out,set(),record)
        changed=copy.deepcopy(record);changed['building']['height']=42
        with self.assertRaises(AssertionError):add_form(out,set(),changed)

if __name__=='__main__':unittest.main()
