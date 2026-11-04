"""Eight unchanged adverse cases plus the byte-pinned original Elements frame."""
from pathlib import Path
import gzip,json,hashlib,unittest
from test_exact_original_four_side_frame_patch_census_diagnostic_v1_20261011 import CompleteFramePatchTests
from exact_original_four_side_frame_patch_census_diagnostic_v1_20261011 import verify
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
class ActualCompleteFramePatchTests(CompleteFramePatchTests):
 def test_actual_complete12129_source_frame393(self):
  root=Path(__file__).resolve().parents[3]
  p=root/'docs/astra-city/government-import/xl-terrain-recovery-20261011-elements-complete-owned-original-contact-graph-v1/diagnostic.json.gz'
  graph=json.loads(gzip.decompress(p.read_bytes()));source=graph['binding']['completeSourceInputs'][0];asset=root/source['asset']['path'];raw=asset.read_bytes()
  self.assertEqual(hashlib.sha256(raw).hexdigest(),source['sourceSHA256']);self.assertEqual(source['sourceSHA256'],'7015f9c5489eb757589cbd5876955dba3f8ffd99187d42bda8661e857493dce3')
  world=decode_original_world_triangles(raw);self.assertEqual(len(world),12129);ids=graph['components'][393]['globalOriginalFaces'];self.assertEqual(len(ids),16)
  r=verify(world,ids);self.assertTrue(r['verifiedCompleteFourSidePatchPartition']);self.assertEqual([len(p['completeOriginalPatchFacetIds'])for p in r['allFourCompleteOriginalSidePatches']],[4]*4)
  self.assertEqual(sorted(f for p in r['allFourCompleteOriginalSidePatches']for f in p['completeOriginalPatchFacetIds']),ids);self.assertFalse(r['authoredRoleAccepted'])
if __name__=='__main__':unittest.main()
