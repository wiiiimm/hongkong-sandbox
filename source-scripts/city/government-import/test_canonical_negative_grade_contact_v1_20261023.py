"""Exercise the real import authority at the contact-band boundaries."""
import importlib.util
from pathlib import Path
import unittest
p = Path(__file__).with_name('acceptance-policy.py')
spec = importlib.util.spec_from_file_location('canonical_contact_policy', p)
policy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(policy)


class ContactPolicyTests(unittest.TestCase):
    def reasons(self, **changes):
        row = dict(state='runtime-validated-awaiting-acceptance', sourceSHA256='same', identityProof=dict(exactObjectId=True, exactBuildingCSUID=True, uniqueViewerMatch=True, identityAccepted=True))
        metric = dict(sourcePreserved=True, sourceSHA256='same', minSurfaceGap=-.46, minLowGap=-.46, maxLowGap=-.18, maxSamplerDelta=0, missingTerrain=0, lowRimChecks=441, identity=dict(overlap=1, centroidDistance=0), budget=dict(triangles=1, geometryBytes=1, residentBytes=1))
        metric.update(changes)
        return policy.reasons(row, metric, dict(triangles=2, geometryBytes=2, residentBytes=2))

    def test_negative_contact_band_does_not_need_near_zero_vertex(self):
        self.assertEqual(self.reasons(), [])

    def test_clearance_limit_still_rejects_burial(self):
        self.assertIn('terrain-intersects-source-over-0.5m', self.reasons(minSurfaceGap=-.50001))

    def test_floating_minimum_still_rejected(self):
        self.assertIn('ground-contact-unresolved', self.reasons(minLowGap=.10001, maxLowGap=.2))

    def test_raised_rim_still_rejected(self):
        self.assertIn('ground-contact-unresolved', self.reasons(maxLowGap=1.00001))

    def test_missing_coverage_still_rejected(self):
        self.assertIn('terrain-coverage', self.reasons(missingTerrain=1))


if __name__ == '__main__':
    unittest.main()
