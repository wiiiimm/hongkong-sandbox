import copy,unittest
from polyu_saved64_site_selection_v1_draft_20261014 import select
def fixture(n=64):
    rows=[dict(leftFace=i,rightFace=i+100,group='old-append',sameAuthenticatedIdealPlane=False,measuredPositiveAreaM2=1.,
        measuredIntersectionVerticesXZ=[['0','0'],['1/3','0'],['0','1']])for i in range(n)]
    return [({'path':'synthetic.json','sha256':'0'*64},{'completeDeterministicIntersectingPairs':rows})]
class Selection(unittest.TestCase):
    def test_full_saved_row_and_rational_mean_preserved(self):
        chunks=fixture();before=copy.deepcopy(chunks);out=select(chunks)
        self.assertEqual(chunks,before);self.assertEqual(out['samples'],64)
        self.assertEqual(out['rows'][0]['exactMeanOfSavedGEOSVerticesXZ'],['1/9','1/3'])
        self.assertEqual(out['rows'][0]['fullSavedMeasuredPair'],chunks[0][1]['completeDeterministicIntersectingPairs'][0])
    def test_insufficient_rows_and_duplicate_pair_fail(self):
        with self.assertRaises(AssertionError):select(fixture(63))
        c=fixture();c[0][1]['completeDeterministicIntersectingPairs'].append(copy.deepcopy(c[0][1]['completeDeterministicIntersectingPairs'][0]))
        with self.assertRaises(AssertionError):select(c)
    def test_line_tiny_and_invalid_source_identity_never_selected(self):
        c=fixture();c[0][1]['completeDeterministicIntersectingPairs']+=[dict(projectedDimension='line'),dict(measuredPositiveAreaM2=1e-9)]
        self.assertEqual(select(c)['samples'],64)
        c=fixture();c[0][1]['completeDeterministicIntersectingPairs'][0]['rightFace']=148459
        with self.assertRaises(AssertionError):select(c)
if __name__=='__main__':unittest.main()
