import unittest
import numpy as np
from original_face_ground_rank_context_v1_20261024 import face_ground_context
from original_face_ground_crossing_v2_20261009 import face_ground_context as previous


class ExactRankContextTests(unittest.TestCase):
    faces = [
        [[5179.583984375,25.14100837707519,2.4677734375],[5176.9912109375,25.141008377075195,-6.144531249999999],[5176.9912109375,22.257007598876953,-6.14453125]],
        [[5177.5400390625,22.25700759887695,3.287109375],[5174.9833984375,22.257007598876953,-5.564453125],[5174.9833984375,25.141008377075195,-5.564453124999999]],
        [[5148.8173828125,5.482988357543949,-26.6982421875],[5161.5078125,5.48298835754394,14.7548828125],[5161.5078125,23.385988712310784,14.754882812500004]],
    ]

    def ground(self, y):
        return np.array([[[5140,y,-40],[5190,y,-40],[5190,y,20]],[[5140,y,-40],[5190,y,20],[5140,y,20]]],float)

    def test_exact_cancellation_faces_preserve_vertices_and_certify_clearance(self):
        for face in self.faces:
            source=np.array(face);saved=source.tobytes()
            with self.assertRaisesRegex(AssertionError,'Projection rank mismatch'):
                previous(source,self.ground(0))
            result=face_ground_context(source,self.ground(0))
            self.assertEqual(source.tobytes(),saved)
            self.assertTrue(result['groundProjectionCovered'])
            self.assertEqual(result['minimum']['minimumGapM'],source[:,1].min())
            self.assertTrue(result['exactRankCancellationProof']['existingOrdinaryClearanceBoundProved'])
            self.assertFalse(result['installationApproved'])

    def test_genuine_intersection_retained_without_threshold_relaxation(self):
        for face in self.faces:
            source=np.array(face);height=float(source[:,1].min()+2)
            result=face_ground_context(source,self.ground(height))
            self.assertAlmostEqual(result['minimum']['minimumGapM'],-2)
            self.assertFalse(result['exactRankCancellationProof']['existingOrdinaryClearanceBoundProved'])

    def test_ordinary_diagnostic_unchanged(self):
        face=np.array([[5150,3,-10],[5160,3,-10],[5150,3,0]],float)
        self.assertEqual(face_ground_context(face,self.ground(0)),previous(face,self.ground(0)))

if __name__=='__main__':unittest.main()
