import unittest
from run import ROOT,read,digest
from native_patch_resolution import _faces,_patch_bounds
from original_unchanged_adjacent_terrain_boundary_20261010 import verify,sha
class ActualChingBoundary(unittest.TestCase):
 def test_complete_original_parent_and_new_proposal(self):
  d=ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261010-ching-hin-exact-parent-boundary-proposal-v2';r=read(d/'diagnostic.json.gz');candidate=r['terrainProposal'];p_path=ROOT/'3d-viewer/city/data/government-native-26542-0.json';a_path=ROOT/'3d-viewer/city/data/government-native-23004-0.json';q_path=ROOT/candidate['path'];self.assertEqual(digest(p_path.read_bytes()),'46982b10f64af071916ff14984174b26e491664373f888765d4aad8b4c75b6d9');self.assertEqual(digest(q_path.read_bytes()),'0cb26d1e8b007aa73bc46d7ff285bc4fef1270f68e708ed35e40a00b31380d7f');p,q,a=[read(x) for x in [p_path,q_path,a_path]];record=r['completeExactAdjacentSeamProofs'][0]['proof'];b=record['binding'];self.assertEqual(digest(a_path.read_bytes()),b['unchangedAdjacentAsset']['sha256']);self.assertEqual(verify(_faces(p),_faces(q),_faces(a),parent_bounds=_patch_bounds(p),proposal_bounds=candidate['bounds'],adjacent_bounds=_patch_bounds(a),expected_binding=b,current_binding=b),record)
if __name__=='__main__':unittest.main()
