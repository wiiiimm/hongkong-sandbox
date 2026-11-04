"""Prevent the QE review from applying to another source, omitted faces or hidden raw failures."""
import unittest
from copy import deepcopy
from run import ROOT,read
from qe311317_original_physical_review_v1_20261026 import validate_grade,validate_lineage
BASE=ROOT/'docs/astra-city/government-import'
PREFIX='government-xl-after-tung-on-qe311317-'

class QEPhysicalReviewTests(unittest.TestCase):
    def setUp(self):
        self.low=read(BASE/(PREFIX+'retained-low-faces-v1-20261026')/'summary.json');self.caps=read(BASE/(PREFIX+'retained-cap-paths-v1-20261026')/'summary.json');self.components=read(BASE/(PREFIX+'sloped-face-components-v1-20261026')/'summary.json');self.lineage=read(BASE/(PREFIX+'pair161194-crossing-lineage-v1-20261026')/'summary.json');self.crossings=read(BASE/(PREFIX+'pair161194-four-world-crossing-ground-v1-20261026')/'summary.json')
    def test_exact_recorded_evidence(self):
        validate_grade(self.low,self.caps,self.components);validate_lineage(self.lineage,self.crossings)
    def test_reject_different_source(self):
        self.low['sourceSHA256']='0'*64
        with self.assertRaises(AssertionError):validate_grade(self.low,self.caps,self.components)
    def test_reject_omitted_negative_facet(self):
        self.low['rows'][0]['exactAffectedFaces'].pop()
        with self.assertRaises(AssertionError):validate_grade(self.low,self.caps,self.components)
    def test_reject_unreviewed_nonwall(self):
        self.caps['rows'][0]['completeGroundClearancePartition']['negativeNonWallFaces'].append(44)
        with self.assertRaises(AssertionError):validate_grade(self.low,self.caps,self.components)
    def test_reject_detached_or_reclassified_slope(self):
        for field,value in [('wholeSharedEdgeComponentFaces',13),('downward',True),('exactlyHorizontal',True)]:
            context=deepcopy(self.components);context['rows'][0]['faces'][0][field]=value
            with self.subTest(field=field),self.assertRaises(AssertionError):validate_grade(self.low,self.caps,context)
    def test_reject_hidden_cap_failure(self):
        self.caps['allFourCompleteGroundClearCapPaths']=True
        with self.assertRaises(AssertionError):validate_grade(self.low,self.caps,self.components)
    def test_reject_hidden_literal_crossings(self):
        self.crossings['allFourWorldTransverseSegmentsStrictlySubgrade']=True
        with self.assertRaises(AssertionError):validate_lineage(self.lineage,self.crossings)
    def test_reject_new_crossing_pair(self):
        r=next(x for x in self.lineage['rows']if x['mode']=='literal');r['rows'][0]['originalPairContact']=None
        with self.assertRaises(AssertionError):validate_lineage(self.lineage,self.crossings)
    def test_reject_changed_literal_geometry_delta(self):
        self.lineage['completeCorrespondingVertexDeltas']['landsd/311317:0']['literal']['exactMaximumAbsoluteCoordinateDeltaM'][1]='1/1000'
        with self.assertRaises(AssertionError):validate_lineage(self.lineage,self.crossings)

if __name__=='__main__':unittest.main()
