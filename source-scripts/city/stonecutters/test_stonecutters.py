"""Meaningful source-preservation, channel and unfinished-terrain checkpoint tests."""
import hashlib,json,pathlib,sys,unittest,numpy as np
from shapely.geometry import Polygon,Point,LineString,MultiPoint
from shapely.ops import unary_union
from fetch import HERE,ROOT
sys.path.insert(0,str(ROOT/'docs/astra-city/mui-wo-buildings/review'));from bake_model_geometry import bake
sys.path.insert(0,str(HERE.parent/'tai-o-completion'));from hydro_terrain import height

class StonecuttersTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads((HERE/'bridges-stonecutters.json').read_text());cls.hydro=json.loads((HERE/'hydro-stonecutters.json').read_text());cls.patch=json.loads((HERE/'terrain-stonecutters.json').read_text());cls.base=json.loads((ROOT/'3d-viewer/city/data/terrain.json').read_text());cls.water=unary_union([Polygon(p['rings'][0],p['rings'][1:]) for p in cls.hydro['water']]);cls.audit=json.loads((ROOT/'docs/astra-city/stonecutters/terrain-source-audit.json').read_text())
    def test_original_components_rebake_without_coordinate_or_height_changes(self):
        self.assertEqual(len(self.data['models']),3);self.assertEqual(self.data['counts']['sourceTriangles'],23634)
        for model in self.data['models']:
            g=model['modelGeometry'];spec={'id':g['modelId'],'url':model['sheet']+'/'+g['source'],'sourceEntry':g['source'],'sourceHashes':g['sourceHashes'],'worldBounds':g['worldBounds'],'officialMatches':g['officialMatches']}
            for name,sha in g['sourceHashes'].items():self.assertEqual(hashlib.sha256((HERE/'assets'/model['sheet']/name).read_bytes()).hexdigest(),sha)
            rebaked=bake(spec,HERE/'assets')
            for key in ['position','normal','colour','worldBounds']:self.assertEqual(g[key],rebaked[key])
    def test_tower_identity_and_recorded_top_are_not_forced_to_mesh_bounds(self):
        rows=[r for m in self.data['models'] for r in m['buildingMatches']];self.assertEqual({r['uid'] for r in rows},{'landsd/75319:0','landsd/75938:0'})
        for row in rows:
            self.assertEqual(row['buildingCSUID'][:10],row['identityModel'][1:11]);self.assertEqual(row['sourceTopHeightHKPD'],298);self.assertGreater(row['overlapOfSmallerFootprint'],.75);self.assertGreater(row['sourceModelTopMinusBuildingTopMetres'],1)
        report=json.loads((ROOT/'docs/astra-city/stonecutters/model-build.json').read_text());self.assertAlmostEqual(report['towerHorizontalSeparationMetres'],1018,delta=1)
        for model in self.data['models']:self.assertFalse(model['walkable']);self.assertEqual(model['walkTriangleIndices'],[])
    def test_exact_proxy_coverage_preserves_unmatched_original_tails(self):
        originals={r['id']:r for r in json.loads((ROOT/'3d-viewer/city/data/bridges.json').read_text())['bridges']};p=np.array(self.data['models'][0]['modelGeometry']['position']).reshape(-1,3);hull=MultiPoint(p[:,[0,2]]).convex_hull.buffer(1.5)
        ids=self.data['models'][0]['suppresses'];self.assertEqual(len(ids),12);self.assertEqual(len(self.data['proxyClips']),2)
        for uid in ids:self.assertEqual(originals[uid]['name'],'Stonecutters Bridge');self.assertLess(LineString(originals[uid]['path']).difference(hull).length,.001)
        for r in self.data['proxyClips']:
            original=LineString(originals[r['id']]['path']);remaining=unary_union([LineString(p) for p in r['keepPaths']]);self.assertLess(remaining.symmetric_difference(original.difference(hull)).length,1e-6);self.assertGreater(remaining.length,5);self.assertLess(remaining.length,7);self.assertNotIn(r['id'],ids)
    def test_source_water_preserves_both_port_foundations(self):
        for sample in self.audit['channelSamples']:self.assertTrue(self.water.covers(Point(sample['world'])));self.assertGreater(sample['coarseRenderedHKPD'],50)
        for sample in self.audit['foundations']:self.assertFalse(self.water.covers(Point(sample['centre'])));self.assertEqual(sample['verticesDifferingBeyondRounding'],0)
        self.assertAlmostEqual(self.water.area,1866061.6674,places=2)
    def test_cut_triangles_do_not_reintroduce_land_in_the_channel(self):
        for cut in self.hydro['terrainCuts']:
            cells=[(c['c'],c['r']) for c in cut['cells']];self.assertEqual(len(cells),len(set(cells)))
            for cell in cut['cells']:
                for t in np.array(cell['land']).reshape(-1,3,3):self.assertLess(Polygon(t[:,[0,2]]).intersection(self.water).area,.002)
        triangles=np.array(self.hydro['bedTriangles']).reshape(-1,3,3);self.assertTrue(np.all(triangles[:,:,1]==-4));self.assertAlmostEqual(sum(Polygon(t[:,[0,2]]).area for t in triangles),self.water.area,places=3)
    def test_full_port_land_audit_retains_unfinished_height_warning(self):
        land=self.audit['completeMappedPortLand'];self.assertEqual(land['gridNodes'],21055);self.assertEqual(land['missingSourceNodes'],0);self.assertEqual(land['verticesDifferingBeyondRounding'],1211);self.assertTrue(self.audit['portLandHeightReviewPending']);self.assertFalse(self.audit['livePublished'])
    def test_existing_outer_terrain_transition_is_continuous(self):
        p=self.patch;g=p['meta']['georef'];w,h=p['w'],p['h']
        for c,r in [(i,0) for i in range(w)]+[(i,h-1) for i in range(w)]+[(0,j) for j in range(h)]+[(w-1,j) for j in range(h)]:
            x=g['bE']+c*5-834500;z=816500-g['bN']+r*5;self.assertAlmostEqual(height(p,x,z),height(self.base,x,z),delta=1e-5)
if __name__=='__main__':unittest.main(verbosity=2)
