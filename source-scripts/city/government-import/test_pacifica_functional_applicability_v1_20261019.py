"""Fail-closed tests against the immutable reviewed Pacifica evidence fixture."""
import copy
import unittest
from pacifica_functional_applicability_v1_20261019 import inputs, qualify

class ApplicabilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.evidence = inputs()

    def test_exact_review(self):
        result = qualify(*copy.deepcopy(self.evidence))
        self.assertTrue(result['sourceScopedApplicabilityAccepted'])
        self.assertFalse(result['strictInterfacePassed'])
        self.assertFalse(result['strictAllFoundationsPassed'])
        self.assertFalse(result['installationApproved'])

    def test_changed_or_incomplete_evidence_rejected(self):
        mutations = {
            'extra_failure': lambda a: a[0]['rows'][0]['remainingPolicyReasons'].append('unknown-failure'),
            'source_changed': lambda a: a[1]['bindings'][0].update(sourceSHA256='changed'),
            'coordinate_missing': lambda a: a[1]['bindings'].pop(),
            'face_changed': lambda a: a[1]['descriptors'][0]['faces'][0].update(originalFaceID=-1),
            'extra_overlap_face': lambda a: a[3]['sourceFaceIds'].append(3030),
            'terrain_burial': lambda a: a[3]['exactFourModeEvidence'][0]['exactAttribution']['terrainOnlyFoundation'].update(fullyBuriedTriangles=1),
            'world_changed': lambda a: a[4][0].update(wholeWorldSHA256='changed'),
            'neighbour_failure': lambda a: a[0].update(completeNeighbourChecksPassed=False),
        }
        for name, mutate in mutations.items():
            with self.subTest(name=name):
                evidence = copy.deepcopy(self.evidence)
                mutate(evidence)
                with self.assertRaises((AssertionError, StopIteration)):
                    qualify(*evidence)

if __name__ == '__main__':
    unittest.main()
