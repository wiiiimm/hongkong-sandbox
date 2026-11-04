import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from native_basic_fallback_ground import POLICY,RECIPE,REQUIRED,drawn_ground_sha,owner_contract_sha,stage_native_basic_fallback_ground
from basic_podium_footings import value_sha


class NativeBasicFallbackTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
        self.tile='city/data/tiles/test.json';self.terrain_url='city/data/test-terrain.json';self.cat_url='city/data/official-models/test/catalogue.json'
        self.b=dict(uid='landsd/10:0',objectId=10,buildingCSUID='test10',kind='yes',structureType='Tower',minimum=0,base=13.1,height=11.9,baseHeightHKPD=13.1,topHeightHKPD=25,baseSource='landsd',heightSource='landsd',rings=[[[0,0],[1,0],[1,1],[0,1],[0,0]]])
        self.data=dict(buildings=[self.b,dict(uid='untouched',base=9)])
        self.tilepath=self.write('3d-viewer/'+self.tile,self.data)
        self.terrain=dict(nativeMesh=dict(position=[0,4.5,0,1,4.5,0,1,5.4,1,0,4.5,1],index=[0,1,2,0,2,3]))
        self.terrainpath=self.write('3d-viewer/'+self.terrain_url,self.terrain)
        self.model=dict(uid=self.b['uid'],objectId=10,buildingCSUID='test10',sha256='a'*64,recordedBaseHeight=13.1,recordedTopHeight=25,worldBounds=[[0,4.8,0],[1,27,1]],activationGroup=[self.b['uid']])
        self.cat=dict(rootTranslation=[-834500,0,816500],crs='EPSG:2326',verticalDatum='Hong Kong Principal Datum',models=[self.model])
        self.catpath=self.write('3d-viewer/'+self.cat_url,self.cat)
        self.hint=dict(recipe=RECIPE,uid=self.b['uid'],sourceSHA256='a'*64,terrainSHA256=self.sha(self.terrainpath),drawnGroundSHA256=drawn_ground_sha(self.terrain),originalBottom=13.1,sourceMinimumY=4.8,base=4.5)
        self.review=dict(status='approved-for-integration',policy=POLICY,uid=self.b['uid'],buildingCSUID=self.b['buildingCSUID'],sourceFormSHA256=value_sha(self.b),tileSHA256=self.sha(self.tilepath),hint=self.hint,terrainURL=self.terrain_url,ownerPlacementAndAvailabilitySHA256=owner_contract_sha(self.model),sourceGeometryChanges=0,governmentGeometryChanges=0,aiGeometryModelling=False,groundRangeHKPD=[4.5,5.400000095367432],**{k:True for k in REQUIRED})
        self.reviewpath=self.write('review.json',self.review)
        self.update=dict(uid=self.b['uid'],tile=self.tile,tileSHA256=self.sha(self.tilepath),before=copy.deepcopy(self.b),hint=copy.deepcopy(self.hint),terrainURL=self.terrain_url,evidence=self.ref(self.reviewpath))
        self.manifest=dict(tiles=[dict(url=self.tile,bytes=self.tilepath.stat().st_size)],officialModelCatalogues=[self.cat_url],terrainPatches=[dict(url=self.terrain_url)])
        self.edits={};self.report={}

    @staticmethod
    def enc(value):return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
    @staticmethod
    def load(path):return json.loads(path.read_bytes())
    @staticmethod
    def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
    def write(self,path,data):
        p=self.root/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(self.enc(data));return p
    def ref(self,path):return dict(path=str(path.relative_to(self.root)),sha256=self.sha(path))
    def stage(self,updates=None):
        stage_native_basic_fallback_ground(self.root,dict(nativeBasicFallbackGrounds=[self.update]if updates is None else updates),self.manifest,self.edits,self.report,self.load,self.sha,self.enc)
    def rejects(self):
        old=self.tilepath.read_bytes();manifest=copy.deepcopy(self.manifest);edits=copy.deepcopy(self.edits)
        with self.assertRaises((AssertionError,KeyError,ValueError,OverflowError)):self.stage()
        self.assertEqual(old,self.tilepath.read_bytes());self.assertEqual(manifest,self.manifest);self.assertEqual(edits,self.edits)
    def retain(self):
        self.stage()
        for path,raw in self.edits.items():path.write_bytes(raw)
        self.edits={}
    def change_review(self,**changes):
        self.review.update(changes);self.write('review.json',self.review);self.update['evidence']=self.ref(self.reviewpath)

    def test_stage_changes_only_hint_in_memory_and_preserves_unrelated_body(self):
        old=self.tilepath.read_bytes();self.stage();self.assertEqual(old,self.tilepath.read_bytes());after=json.loads(self.edits[self.tilepath]);self.assertEqual(after['buildings'][0],dict(self.b,nativeFallbackGround=self.hint));self.assertEqual(after['buildings'][1],self.data['buildings'][1]);self.assertEqual(self.report['retainedNativeBasicFallbackGroundChecks'],[self.b['uid']])
    def test_unreviewed_or_missing_qualified_evidence_rejects(self):
        for key in REQUIRED:
            with self.subTest(key=key):
                old=copy.deepcopy(self.review);self.change_review(**{key:False});self.rejects();self.review=old;self.change_review()
        self.change_review(status='private-proposal');self.rejects()
    def test_wrong_source_identity_or_source_minimum_rejects(self):
        for changes in [dict(sourceSHA256='b'*64),dict(uid='landsd/99:0'),dict(sourceMinimumY=8)]:
            with self.subTest(changes=changes):
                old=copy.deepcopy(self.update['hint']);self.update['hint'].update(changes);self.rejects();self.update['hint']=old
    def test_wrong_or_stale_terrain_or_drawn_geometry_rejects(self):
        for key in ['terrainSHA256','drawnGroundSHA256']:
            old=self.update['hint'][key];self.update['hint'][key]='0'*64;self.rejects();self.update['hint'][key]=old
        self.terrain['nativeMesh']['position'][1]=4;self.write('3d-viewer/'+self.terrain_url,self.terrain);self.rejects()
    def test_upward_floor_deep_foundation_unknown_recipe_and_boolean_numbers_reject(self):
        for changes in [dict(base=1.199),dict(base=3),dict(base=13.09),dict(base=True),dict(originalBottom=13),dict(recipe='other'),dict(extra='geometry-change')]:
            old=copy.deepcopy(self.update['hint']);self.update['hint'].update(changes);self.rejects();self.update['hint']=old
    def test_source_fields_and_footprint_changes_reject(self):
        for key,value in [('base',8),('topHeightHKPD',35),('buildingCSUID','other'),('rings',[[[0,0],[2,0],[0,2],[0,0]]])]:
            old=copy.deepcopy(self.update['before']);self.update['before'][key]=value;self.rejects();self.update['before']=old
    def test_stale_evidence_and_tile_reject(self):
        old=self.update['evidence']['sha256'];self.update['evidence']['sha256']='0'*64;self.rejects();self.update['evidence']['sha256']=old
        self.tilepath.write_bytes(self.tilepath.read_bytes()+b' ');self.rejects()
    def test_canopy_existing_foundation_or_embedded_native_cannot_be_repurposed(self):
        for changes in [dict(structureType='Open-sided Structure'),dict(kind='roof'),dict(foundationBase=None),dict(foundationBase=4),dict(foundationPolicy='other'),dict(modelGeometry={'position':[0,0,0]})]:
            old=copy.deepcopy(self.data);self.data['buildings'][0].update(changes);self.write('3d-viewer/'+self.tile,self.data);self.update['tileSHA256']=self.sha(self.tilepath);self.update['before']=copy.deepcopy(self.data['buildings'][0]);self.rejects();self.data=old;self.write('3d-viewer/'+self.tile,self.data);self.update['tileSHA256']=self.sha(self.tilepath);self.update['before']=copy.deepcopy(self.b)
    def test_missing_native_or_suppressed_or_wrong_native_metadata_rejects(self):
        for models in [[],[dict(self.model,buildingCSUID='other')],[dict(self.model,objectId=11)],[dict(self.model,retainsBasicForm=True)],[self.model,dict(uid='other',suppressesBuildingUids=[self.b['uid']])]]:
            self.write('3d-viewer/'+self.cat_url,dict(self.cat,models=models));self.rejects()
    def test_native_pose_change_rejects(self):
        self.write('3d-viewer/'+self.cat_url,dict(self.cat,models=[dict(self.model,verticalPlacementOffsetHKPD=1)]));self.rejects()
    def test_duplicate_updates_reject_without_staged_mutation(self):
        before=copy.deepcopy(self.manifest)
        with self.assertRaises(AssertionError):self.stage([self.update,self.update])
        self.assertEqual(before,self.manifest);self.assertEqual(self.edits,{})
    def test_retained_registry_allows_original_native_and_rechecks_contract(self):
        self.retain();self.stage([]);self.assertEqual(self.report['retainedNativeBasicFallbackGroundChecks'],[self.b['uid']])
        self.write('3d-viewer/'+self.cat_url,dict(self.cat,models=[dict(self.model,activationGroup=[self.b['uid'],'landsd/11:0'])]));
        with self.assertRaisesRegex(AssertionError,'availability contract'):self.stage([])
    def test_retained_registry_rejects_changed_owner_or_terrain_or_form(self):
        self.retain();self.write('3d-viewer/'+self.cat_url,dict(self.cat,models=[dict(self.model,sha256='c'*64)]))
        with self.assertRaises(AssertionError):self.stage([])
        self.write('3d-viewer/'+self.cat_url,self.cat);self.terrainpath.write_bytes(self.terrainpath.read_bytes()+b' ')
        with self.assertRaises(AssertionError):self.stage([])
        self.write('3d-viewer/'+self.terrain_url,self.terrain);data=self.load(self.tilepath);data['buildings'][0]['height']=12;self.write('3d-viewer/'+self.tile,data)
        with self.assertRaises(AssertionError):self.stage([])
    def test_removed_terrain_owner_rejects(self):
        self.manifest['terrainPatches']=[];self.rejects()
    def test_path_escape_rejects(self):
        self.update['evidence']['path']='../outside.json';self.rejects()
    def test_staged_terrain_and_catalogue_bytes_are_checked_before_publication(self):
        self.edits[self.terrainpath]=self.terrainpath.read_bytes();self.edits[self.catpath]=self.catpath.read_bytes();self.stage();self.assertEqual(self.report['retainedNativeBasicFallbackGroundChecks'],[self.b['uid']])
    def test_future_registry_evidence_mutation_rejects(self):
        self.retain();self.reviewpath.write_bytes(self.reviewpath.read_bytes()+b' ')
        with self.assertRaises(AssertionError):self.stage([])


if __name__=='__main__':unittest.main()
