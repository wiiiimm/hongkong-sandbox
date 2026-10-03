import json,hashlib,unittest,copy
from pathlib import Path
from reviewed_terrain_changes import reviewed_changes
ROOT=Path(__file__).resolve().parents[3]
class ExactMaskCorrection(unittest.TestCase):
 def test_only_hash_pinned_source_land_nodes_accepted(self):
  plan=json.loads((ROOT/'source-scripts/city/model-integration-20260909/station-correction-plan.json').read_text());entry=plan['topLevelTerrainPatches'][0]
  old=json.loads((ROOT/'3d-viewer'/entry['replaces']['url']).read_text());new=json.loads((ROOT/entry['source']).read_text())
  allowed=reviewed_changes(ROOT,entry,old,new);self.assertEqual(len(allowed),8787)
  first=next(iter(allowed.values()));new['elev'][first]+=1
  with self.assertRaises(AssertionError):reviewed_changes(ROOT,entry,old,new)
if __name__=='__main__':unittest.main()
