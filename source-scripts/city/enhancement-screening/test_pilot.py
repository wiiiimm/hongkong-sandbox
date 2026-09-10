import copy
import unittest
from pilot import classify, select


class PilotTests(unittest.TestCase):
    def setUp(self):
        self.row = {'geometry':'footprint','state':'unassessed'}
        self.b = {'kind':'house','structureType':'Tower','heightSource':'landsd','height':9,'rings':[[]]}
        self.audit = {'flags':[],'terrain':{'state':'sampled-source-footprint-envelope'},'areaM2':100}
        self.native = {'matches':1,'identityMatches':True,'recordedHeightsMatch':True,
            'state':'packed-needs-placement-review','cachedOverlap':1,
            'cachedCentroidDistanceMetres':.1,'maxBoundsDeltaMetres':.2,
            'baseDeltaMetres':.1,'topDeltaMetres':.5,'triangles':32}

    def verdict(self):
        return classify(self.row,self.b,self.audit,self.native)[0]

    def test_low_complexity_is_only_provisional(self):
        self.assertEqual(self.verdict(),'likely-skip')

    def test_unknown_native_does_not_become_skip(self):
        self.native={'matches':0}
        self.assertEqual(self.verdict(),'review')

    def test_identity_or_height_change_blocks_candidate(self):
        for field in ('identityMatches','recordedHeightsMatch'):
            with self.subTest(field=field):
                saved=copy.deepcopy(self.native);self.native[field]=False
                self.assertEqual(self.verdict(),'review');self.native=saved

    def test_clean_metadata_does_not_override_terrain_issue(self):
        self.audit['flags']=['sampled-base-above-terrain']
        self.assertEqual(self.verdict(),'review')

    def test_estimated_height_is_not_automatic_adequacy(self):
        self.b['heightSource']='estimated'
        self.assertEqual(self.verdict(),'review')

    def test_stadium_flag_does_not_depend_on_name_or_uid(self):
        self.b['kind']='grandstand'
        self.assertEqual(self.verdict(),'enhancement-candidate')

    def test_stadium_with_detail_remains_review(self):
        self.b['kind']='grandstand';self.row['geometry']='native'
        self.assertEqual(self.verdict(),'review')

    def test_explicit_rework_takes_precedence(self):
        self.row['state']='enhancement-required'
        self.assertEqual(self.verdict(),'enhancement-candidate')

    def test_existing_acceptance_is_the_only_confirmed_skip(self):
        self.row['state']='enhanced'
        self.assertEqual(self.verdict(),'confirmed-skip')

    def test_sample_independent_of_input_order(self):
        rows=[{'uid':str(i)} for i in range(50)]
        self.assertEqual(select(rows,10),select(list(reversed(rows)),10))
        self.assertEqual(len({r['uid'] for r in select(rows,10)}),10)

    def test_duplicate_population_rejected(self):
        with self.assertRaises(ValueError):select([{'uid':'1'},{'uid':'1'}],1)


if __name__=='__main__':unittest.main()
