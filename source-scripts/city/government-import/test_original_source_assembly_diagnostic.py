import copy
import hashlib
import unittest
import numpy as np
from original_source_assembly_diagnostic import evaluate as pair_evaluate
TOWER, PODIUM = 'landsd/259613:0', 'landsd/259803:0'

def evaluate(*args):
    return pair_evaluate(*args, tower=TOWER, podium=PODIUM)


def fixture():
    def rectangle(x0, x1, z0, z1, y):
        return np.asarray([[[x0,y,z0],[x1,y,z0],[x1,y,z1]],
                           [[x0,y,z0],[x1,y,z1],[x0,y,z1]]], dtype=float)
    triangles = {PODIUM: rectangle(0,10,0,10,0), TOWER: rectangle(3,7,3,7,10)}
    rows, individual = [], {}
    for n, uid in enumerate([PODIUM,TOWER]):
        rings = [[0,0],[10,0],[10,10],[0,10],[0,0]] if uid == PODIUM else [[2,2],[8,2],[8,8],[2,8],[2,2]]
        rows.append({'uid':uid,'sourceSHA256':str(n)*64,'triangles':2,
                     'source':{'building':{'uid':uid,'parent':'way/shared','osmRefs':['way/shared'],
                                          'structureType':'Podium' if uid==PODIUM else 'Tower',
                                          'objectId':n+1,'buildingCSUID':'csuid'+str(n),'rings':[rings]}}})
        individual[uid] = {'sourceSHA256':str(n)*64,
                           'worldTrianglesSHA256':hashlib.sha256(triangles[uid].astype('<f8').tobytes()).hexdigest(),
                           'reasons':[] if uid==PODIUM else ['full-source-target-coverage'],
                           'geographicCell':{'targetCoversWholeCell':True,'originalProjectionCoversWholeCell':True}}
    interface = {'uid':TOWER,'supportUid':PODIUM,'sourceSHA256':'1'*64,'supportSHA256':'0'*64,
                 'interface':{'passed':True,'samples':6,'strictContacts':6,'wallIntersections':0,'unresolved':[]}}
    return rows,individual,triangles,interface,[]


class CompoundIdentity(unittest.TestCase):
    def test_complete_same_building_assembly_meets_existing_bounds(self):
        r=evaluate(*fixture())
        self.assertTrue(r['passed'],r['reasons'])
        self.assertEqual(r['measures']['targetCoveredBySourceProjection'],1)
        self.assertEqual(r['rawIndividualIdentity'][TOWER]['reasons'],['full-source-target-coverage'])
        self.assertFalse(r['installationApproved'])

    def test_unrelated_parent_or_missing_shared_reference_fails(self):
        for key,value in [('parent','way/other'),('osmRefs',[])]:
            a=fixture();a[0][1]['source']['building'][key]=value
            self.assertIn('different-or-missing-building-parent',evaluate(*a)['reasons'])

    def test_no_other_identity_failure_can_be_resolved(self):
        for reason in ['unique-viewerMatches','original-byte-integrity','original-world-pose-or-bounds',
                       'fresh-current-identity-differs:target']:
            a=fixture();a[1][TOWER]['reasons'].append(reason)
            self.assertIn(TOWER+':'+reason,evaluate(*a)['reasons'])

    def test_interface_must_be_complete_and_bound_to_same_sources(self):
        for key,value in [('sourceSHA256','bad'),('supportUid',TOWER)]:
            a=fixture();a[3][key]=value
            self.assertIn('exact-original-support-interface',evaluate(*a)['reasons'])
        for key,value in [('strictContacts',5),('samples',0),('wallIntersections',1),('unresolved',[{}]),('passed',False)]:
            a=fixture();a[3]['interface'][key]=value
            self.assertIn('exact-original-support-interface',evaluate(*a)['reasons'])

    def test_duplicate_ids_and_wrong_structure_types_fail(self):
        for key,value in [('objectId',1),('buildingCSUID','csuid0'),('structureType','Podium')]:
            a=fixture();a[0][1]['source']['building'][key]=value
            self.assertFalse(evaluate(*a)['passed'])

    def test_partial_whole_assembly_coverage_fails(self):
        a=fixture();a[0][0]['source']['building']['rings'][0]=[[0,0],[12,0],[12,10],[0,10],[0,0]]
        self.assertIn('compound-spatial-bound:targetCoveredBySourceProjection',evaluate(*a)['reasons'])

    def test_actual_extent_and_unrelated_overlap_still_fail(self):
        a=fixture();a[2][TOWER][:,:,0]+=30
        a[1][TOWER]['worldTrianglesSHA256']=hashlib.sha256(a[2][TOWER].astype('<f8').tobytes()).hexdigest()
        self.assertIn('compound-spatial-bound:sourceExcessMaximumDistanceFromTargetM',evaluate(*a)['reasons'])
        a=fixture();a[0][0]['source']['building']['rings'][0]=[[0,0],[9,0],[9,10],[0,10],[0,0]]
        a[4].append({'uid':'landsd/other:0','parent':'way/other','rings':[[[9,0],[10,0],[10,10],[9,10],[9,0]]]})
        self.assertIn('compound-spatial-bound:sourceExcessCoveredByUnrelatedFormsM2',evaluate(*a)['reasons'])

    def test_geometry_hash_cell_and_full_source_are_mandatory(self):
        a=fixture();a[2][TOWER][:,:,0]+=.1
        self.assertIn(TOWER+':individual-world-geometry-hash',evaluate(*a)['reasons'])
        a=fixture();a[1][TOWER]['geographicCell']['originalProjectionCoversWholeCell']=False
        self.assertIn(TOWER+':whole-georef-cell',evaluate(*a)['reasons'])
        a=fixture();a[2][TOWER][0,0,0]=float('nan')
        self.assertIn(TOWER+':invalid-full-source-geometry',evaluate(*a)['reasons'])

    def test_only_this_exact_pair_can_use_the_diagnostic(self):
        a=fixture();a[0][1]['uid']='landsd/other:0'
        self.assertEqual(evaluate(*a)['reasons'],['unscoped-source-group'])


if __name__=='__main__':unittest.main()
