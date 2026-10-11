import unittest
from terrain_diagnostic_resolution import resolve_global_bottom_warning as resolve

class TerrainDiagnosticTest(unittest.TestCase):
    def inputs(self):
        return ({'uid': 'u', 'outcome': 'runtime-accepted-placement-unreviewed',
                 'concerns': ['sampled-terrain-above-model-bottom', 'unknown-warning']},
                {'uid': 'u', 'sourceSHA256': 'sha', 'sourcePreserved': True,
                 'lowRimChecks': 20, 'missingTerrain': 0, 'minSurfaceGap': -.22,
                 'minLowGap': -.22, 'maxLowGap': .24, 'maxSamplerDelta': 0},
                {'uid': 'u', 'sourceSHA256': 'sha', 'strictFoundationAccepted': True,
                 'foundation': {'triangles': 10, 'completeTerrainTriangles': 10,
                  'fullyBuriedUpwardTriangles': 0, 'fullyBuriedAreaFraction': 0}})
    def test_only_global_warning_is_resolved(self):
        result = resolve(*self.inputs())
        self.assertEqual(result['resolved'], ['sampled-terrain-above-model-bottom'])
        self.assertEqual(result['remaining'], ['unknown-warning'])
    def test_actual_contact_failure_cannot_resolve_warning(self):
        for key, value in [('minSurfaceGap', -.501), ('maxLowGap', 1.001),
                           ('maxSamplerDelta', .00401), ('missingTerrain', 1),
                           ('sourcePreserved', False), ('minLowGap', float('nan'))]:
            with self.subTest(key=key):
                v, m, f = self.inputs(); m[key] = value
                self.assertEqual(resolve(v, m, f)['resolved'], [])
    def test_incomplete_or_mismatched_foundation_cannot_resolve(self):
        for key, value in [('completeTerrainTriangles', 9),
                           ('fullyBuriedUpwardTriangles', 1), ('fullyBuriedAreaFraction', .001)]:
            v, m, f = self.inputs(); f['foundation'][key] = value
            self.assertEqual(resolve(v, m, f)['resolved'], [])
        v, m, f = self.inputs(); f['sourceSHA256'] = 'changed'
        self.assertEqual(resolve(v, m, f)['resolved'], [])
    def test_loader_exception_cannot_resolve(self):
        v, m, f = self.inputs(); v['outcome'] = 'validation-exception'
        self.assertEqual(resolve(v, m, f)['resolved'], [])

if __name__ == '__main__': unittest.main()
