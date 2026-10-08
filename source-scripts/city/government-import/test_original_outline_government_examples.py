import json,unittest
from pathlib import Path
from pyproj import Transformer
from original_outline_curves import verify_polygon

class OriginalGovernmentCurveExamples(unittest.TestCase):
 def test_real_original_government_arc_lineage_does_not_clear_all_holds(self):
  root=Path(__file__).resolve().parents[3];folder=root/'docs/astra-city/government-import/government-xl-three-outline-provenance-20261008';archive=json.loads((folder/'archive-features.json').read_text())['features'];current=json.loads((folder/'official-true-curves.json').read_text())['features'];project=Transformer.from_crs(4326,2326,always_xy=True)
  expected={'3620912586P20160225':True,'3415819951T20120223':True,'3410619932P20120223':False,'3351521183P20180122':False}
  for f in archive:
   csuid=f['properties']['BuildingCSUID'];rings=[[list(project.transform(*p)) for p in ring] for ring in f['geometry']['coordinates']];curve=next(r for r in current if r['attributes']['BuildingCSUID']==csuid)['geometry']['curveRings']
   self.assertEqual(verify_polygon(rings,curve)['passed'],expected[csuid],csuid)
if __name__=='__main__':unittest.main()
