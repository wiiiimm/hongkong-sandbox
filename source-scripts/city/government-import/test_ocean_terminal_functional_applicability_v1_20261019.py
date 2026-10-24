"""Changed source, missing coverage and new failures cannot inherit this review."""
import unittest
from copy import deepcopy
from ocean_terminal_functional_applicability_v1_20261019 import inputs,qualify
class Applicability(unittest.TestCase):
 def test_saved_evidence_qualifies_without_relabelling_strict_failures(self):
  r=qualify(**inputs());self.assertTrue(r['sourceScopedApplicabilityAccepted']);self.assertFalse(r['rawStrictFoundationPassed']);self.assertFalse(r['installationApproved'])
 def test_changed_or_incomplete_evidence_fails_closed(self):
  changes=[lambda d:d['metric'].update(sourceSHA256='0'*64),lambda d:d['foundations'].pop(),lambda d:d['foundations'][0]['foundation'].update(fullyBuriedUpwardTriangles=1),lambda d:d['foundations'][0]['buriedFaces'][0].update(faceId=17),lambda d:d['scope']['touchingNativeUids'].append('landsd/233905:0'),lambda d:d['equivalence'].update(retainedChildren=12),lambda d:d['sampler']['differences'].append({'unexpected':True}),lambda d:d['metric'].update(missingTerrain=1),lambda d:d['metric'].update(minLowGap=2),lambda d:d['neighbours']['flagged'].append({'uid':'unexpected'}),lambda d:d['validation']['results'][0]['concerns'].append('new-error'),lambda d:d['decision'].update(rawStrictFoundationPassed=True)]
  baseline=inputs()
  for mutate in changes:
   with self.subTest(mutation=changes.index(mutate)):
    data=deepcopy(baseline);mutate(data)
    with self.assertRaises(AssertionError):qualify(**data)
if __name__=='__main__':unittest.main()
