"""Invalid upstream GeoRefs must fail identity without aborting other models."""
import unittest
from copy import deepcopy
from selected_original_identity_v3 import complete_identity

class UpstreamCellFailure(unittest.TestCase):
    def test_failure_preserved(self):
        raw=dict(uid='landsd/example:0', geographicCell={}, passed=False,
                 reasons=['invalid-geographic-cell'], proof={'identityAccepted':False})
        before=deepcopy(raw)
        result=complete_identity(raw,None,None)
        self.assertEqual(raw,before)
        self.assertFalse(result['passed'])
        self.assertEqual(result['reasons'],before['reasons'])
        self.assertEqual(result['proof'],before['proof'])
        self.assertIn('exactCellFallbackNotApplicable',result)
    def test_empty_cell_cannot_be_accepted(self):
        for raw in [dict(geographicCell={},passed=True,reasons=[]),dict(geographicCell={'unexpected':1},passed=False,reasons=['invalid-geographic-cell'])]:
            with self.assertRaises(AssertionError): complete_identity(raw,None,None)
if __name__=='__main__': unittest.main()
