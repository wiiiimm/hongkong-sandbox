"""Anonymous originals must not collapse onto one null-UID lease."""
import unittest
from fixed_xl_cached_neighbour_contacts_v2_20261028 import required_resources

class SourceKeyLeases(unittest.TestCase):
 def test_distinct_anonymous_neighbours_keep_distinct_leases(self):
  row=dict(uid='landsd/12:0',sourceKey='a/root',nearbyOriginalCandidates=[dict(uid=None,sourceKey='b/one'),dict(uid=None,sourceKey='b/two')])
  self.assertEqual(required_resources(row),{'building:landsd/12:0','native-source:b/one','native-source:b/two'})
 def test_anonymous_target_has_no_invented_building_uid(self):
  row=dict(uid=None,sourceKey='a/target',nearbyOriginalCandidates=[dict(uid='landsd/34:0',sourceKey='b/peer')])
  self.assertEqual(required_resources(row),{'native-source:a/target','building:landsd/34:0'})
 def test_identical_sources_do_not_require_competing_duplicate_leases(self):
  peer=dict(uid=None,sourceKey='b/same');row=dict(uid=None,sourceKey='a/root',nearbyOriginalCandidates=[peer,peer])
  self.assertEqual(required_resources(row),{'native-source:a/root','native-source:b/same'})

if __name__=='__main__':unittest.main()
