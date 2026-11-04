"""Synthetic coarse-domain and complete-source scope fixtures; no production geometry."""
import copy,unittest
from pathlib import Path
from unittest.mock import patch
import heritage165054_authentic_tin_nomination_v1_20261014 as a
class NominationScope(unittest.TestCase):
    def test_saved_whole_bounds_select_complete_parent_cells(self):
        g=dict(aE=70,aN=-70,bE=800032.5,bN=847967.5)
        cells,bb=a.nominated_domain([[2558.94140625,4.85,-10014.753913879395],[2715.0546875,44.73,-9860.49609375]],dict(meta=dict(georef=g)))
        self.assertEqual(cells,[528,306,532,309]);self.assertEqual(bb,[2492.5,-10047.5,2772.5,-9837.5])
    def test_closed_boundary_touch_and_disjoint(self):
        self.assertTrue(a.closed_touch([0,0,1,1],[1,1,2,2]));self.assertFalse(a.closed_touch([0,0,1,1],[1.01,0,2,2]))
    def fixture(self):
        own=a.UID; native=[dict(uid='landsd/'+str(500000+i)+':0',sha256='s',modelId='m',worldBounds=[[10,0,10],[11,1,11]]) for i in range(6653)]
        row=dict(uid=native[0]['uid'],sourceSHA256='s',rawCurrentEntry=copy.deepcopy(native[0]),source=dict(path='original',sha256='s'),completeOriginalPOSITIONProof=dict(allOriginalPositionVerticesAccounted=True,originalWholeSourceBounds=[[0,0,0],[1,1,1]]))
        lit=dict(uid=row['uid'],sourceSHA256='s',wholeUnusedPositionVerticesIncluded=True,sourceFacesOmitted=0,completeLiteralBounds=[[0,0,0],[1,1,1]],completeLeftAssociatedF32Bounds=[[0,0,0],[1,1,1]],completeBalancedF32Bounds=[[0,0,0],[1,1,1]])
        form=dict(uid=own,rings=[[[0,0],[1,0],[1,1],[0,0]]],modelGeometry=None)
        def read(p):
            if p==a.POSITION:return dict(rows=[row])
            if p==a.LITERAL:return dict(rows=[lit])
            if p.name=='catalogue.json':return dict(models=native)
            return dict(buildings=[form])
        return native,row,lit,form,read
    def scope(self,read):
        with patch.object(a,'read',read),patch.object(a,'ref',lambda p:dict(path=str(p),sha256='fixture')):
            return a.scope_metadata(dict(officialModelCatalogues=['catalogue.json'],tiles=[dict(url='tile.json')]),[0,0,1,1])[0]
    def test_missing_current_actor_never_silently_omitted(self):
        native,row,lit,form,read=self.fixture();s=self.scope(read)
        self.assertEqual(len(s['missingOrChangedWholeBoundsActorsRetained']),6652);self.assertIn(native[-1]['uid'],s['allActorsForNominationLease']);self.assertIn(a.UID,s['allActorsForNominationLease'])
    def test_whole_source_and_float32_touching_included_even_when_catalogue_far(self):
        native,row,lit,form,read=self.fixture();s=self.scope(read)
        self.assertEqual([v['uid'] for v in s['knownNativeWholeBoundsTouching']],[native[0]['uid']]);self.assertTrue(s['fullCurrentOriginalLiteralFloat32ParentDomainRegressionAndExteriorStillRequired'])
    def test_changed_source_pose_field_becomes_unresolved_scoped_actor(self):
        native,row,lit,form,read=self.fixture();native[0]['rootTranslation']=[1,0,0];s=self.scope(read)
        self.assertEqual(len(s['missingOrChangedWholeBoundsActorsRetained']),6653);self.assertEqual(s['knownNativeWholeBoundsTouching'],[])
    def test_model_geometry_outside_footprint_cannot_escape_scope(self):
        native,row,lit,form,read=self.fixture();form['rings']=[[[10,10],[11,10],[10,11],[10,10]]];form['modelGeometry']=dict(position=[1,0,1,2,0,1,1,0,2]);s=self.scope(read)
        self.assertEqual(len(s['currentProjectedFormsTouching']),1)
if __name__=='__main__':unittest.main()
