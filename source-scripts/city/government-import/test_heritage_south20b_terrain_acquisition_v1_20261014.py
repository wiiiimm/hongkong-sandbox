"""Actual saved south directory/lease metadata, no acquisition/decoder/DB."""
import copy,unittest
from unittest.mock import patch
import heritage165054_south20b_terrain_acquisition_v1_20261014 as a
class SouthOriginalMetadata(unittest.TestCase):
    def parsed(self):
        row=a.read(a.DIRECTORY/'result.json'); infos,proof=a.module(a.PARSER,'south20b_fixture_directory').parse_directory((a.DIRECTORY/'zip-directory.bin').read_bytes());return row,infos,proof
    def test_actual_directory_selects_only_pinned_south_terrain(self):
        row,infos,proof=self.parsed();before=copy.deepcopy(row); target=a.terrain_selection(row,infos,proof)
        self.assertEqual(row,before);self.assertEqual(target['models'],[]);self.assertEqual(sum(e['compressedBytes'] for e in a.MEMBERS),3463662)
        self.assertEqual({e['name'] for e in a.MEMBERS},{'TERRAIN(TB)/T36750258000106E10/T36750258000106E10.bin','TERRAIN(TB)/T36750258000106E10/T36750258000106E10.gltf'})
    def test_actual_south_revision_or_etag_cannot_silently_refresh(self):
        for k in ['revision','etag']:
            row,infos,proof=self.parsed();row[k]='unreviewed-new-revision'
            with self.subTest(k=k),self.assertRaises(AssertionError):a.terrain_selection(row,infos,proof)
    def test_actual_whole_45_actor_scope_uses_canonical_foreign_key_without_DB(self):
        scope=a.read(a.NORTH/'proposal-input.json')['scope']['allActorsForNominationLease'];self.assertEqual(len(scope),45)
        from run import reservations
        with patch.object(reservations,'connect',side_effect=AssertionError('DB forbidden')):r=a.canonical_resources(scope)
        self.assertEqual(len(r),91);self.assertIn('foreign-form:way/261065256:0',r);self.assertIn('terrain-patch:way/261065256:0',r)
if __name__=='__main__':unittest.main()
