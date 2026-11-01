"""Adversarial tests with synthetic receipts, never installation evidence."""
import copy,json,unittest
import test_basic_podium_footings as fixture
from basic_unsurveyed_foundations import POLICY,SOURCES,COMMON_PROOFS,stage_unsurveyed_foundations
from basic_podium_footings import terrain_geometry_sha,value_sha

class UnsurveyedTests(unittest.TestCase):
    enc=staticmethod(fixture.BasicFootingTests.enc)
    sha=staticmethod(fixture.BasicFootingTests.sha)
    load=staticmethod(fixture.BasicFootingTests.load)
    write=fixture.BasicFootingTests.write
    ref=fixture.BasicFootingTests.ref
    def setUp(self):
        fixture.BasicFootingTests.setUp(self)
        self.uid='landsd/309838:0';csuid,kind,structure=SOURCES[self.uid]
        self.b.update(uid=self.uid,buildingCSUID=csuid,kind=kind,structureType=structure,baseSource='terrain-estimated',heightSource='estimated',baseHeightHKPD=None,topHeightHKPD=None)
        self.write('3d-viewer/'+self.tile,self.data)
        renderer=self.write('renderer.js',{'version':1})
        self.proof=dict(governmentGeometryChanges=0,inputHashes={'renderer.js':self.sha(renderer)},originalBodyAndRoofPartsExactlyUnchanged=True,originalBodyVerticesAndWindowMasksExactlyUnchanged=True,allNewXZFromOriginalFootprint=True,collisionVolumesExactlyMatchRenderedParts=True,foundationOnlyBelowOriginalBase=True,newFoundationWindows=False)
        self.proofpath=self.write('proof.json',self.proof);receipt=self.write('receipt.json',{'synthetic':True})
        self.review=dict(status='approved-for-integration',policy=POLICY,uid=self.uid,sourceFormSHA256=value_sha(self.b),tileSHA256=self.sha(self.tilepath),foundationBase=4,minimumCoveredGroundHKPD=4,governmentGeometryChanges=0,sourcePoseChanges=0,aiGeometryModelling=False,nativeSupportCredit=False,renderProof=self.ref(self.proofpath),evidence={k:[self.ref(receipt)] for k in ['geometry','ground','collision','jointScene','desktop','mobile','fallback']},nativeTerrainDependencies=[dict(url=self.terrain_url,geometrySHA256=terrain_geometry_sha(self.terrain))],**{k:True for k in COMMON_PROOFS})
        self.update=dict(uid=self.uid,tile=self.tile,tileSHA256=self.sha(self.tilepath),before=copy.deepcopy(self.b),foundationBase=4);self.refresh()
    def refresh(self):
        self.write('review.json',self.review);self.update['evidence']=self.ref(self.reviewpath)
    def stage(self,updates=None):
        stage_unsurveyed_foundations(self.root,dict(unsurveyedBasicFoundations=[self.update] if updates is None else updates),self.manifest,self.edits,self.report,self.load,self.sha,self.enc)
    def rejects(self):
        before=self.tilepath.read_bytes()
        with self.assertRaises((AssertionError,KeyError)):self.stage()
        self.assertEqual(before,self.tilepath.read_bytes())
    def retain(self):
        self.stage()
        for p,b in self.edits.items():p.write_bytes(b)
        self.edits={}
    def test_stage_preserves_fields_without_live_write(self):
        before=self.tilepath.read_bytes();self.stage();self.assertEqual(before,self.tilepath.read_bytes())
        after=json.loads(self.edits[self.tilepath]);self.assertEqual(after['buildings'][0],{**self.b,'foundationBase':4,'foundationPolicy':POLICY});self.assertEqual(after['buildings'][1],self.data['buildings'][1])
    def test_all_acceptance_flags_required(self):
        for key in COMMON_PROOFS:
            with self.subTest(key=key):
                self.review[key]=False;self.refresh();self.rejects();self.review[key]=True
        self.review['status']='private-diagnostic';self.refresh();self.rejects()
    def test_stale_renderer_rejected(self):
        self.write('renderer.js',{'version':2});self.rejects()
    def test_missing_runtime_receipt_rejected(self):
        self.review['evidence']['mobile']=[];self.refresh();self.rejects()
    def test_native_activation_and_suppression_rejected(self):
        for m in [dict(uid=self.uid),dict(uid='other',suppressesBuildingUids=[self.uid])]:
            self.write('3d-viewer/'+self.cat_url,dict(models=[m]));self.rejects()
    def test_retained_native_activation_rejected(self):
        self.retain();self.write('3d-viewer/'+self.cat_url,dict(models=[dict(uid=self.uid)]))
        with self.assertRaises(AssertionError):self.stage([])
    def test_retained_terrain_change_rejected(self):
        self.retain();self.terrain['nativeMesh']['position'][1]=0;self.write('3d-viewer/'+self.terrain_url,self.terrain)
        with self.assertRaises(AssertionError):self.stage([])
    def test_retained_terrain_removal_rejected(self):
        self.retain();self.manifest['terrainPatches']=[]
        with self.assertRaises(AssertionError):self.stage([])
    def test_invented_depth_rejected(self):
        self.update['foundationBase']=3;self.review['foundationBase']=3;self.refresh();self.rejects()
    def test_geometry_change_rejected(self):
        self.proof['foundationOnlyBelowOriginalBase']=False;self.write('proof.json',self.proof);self.review['renderProof']=self.ref(self.proofpath);self.refresh();self.rejects()
    def test_source_kind_and_surveyed_height_rejected(self):
        for key,val in [('kind','roof'),('baseHeightHKPD',6),('baseSource','landsd')]:
            original=copy.deepcopy(self.b);self.b[key]=val;self.write('3d-viewer/'+self.tile,self.data)
            self.update.update(before=copy.deepcopy(self.b),tileSHA256=self.sha(self.tilepath));self.review.update(sourceFormSHA256=value_sha(self.b),tileSHA256=self.sha(self.tilepath));self.refresh();self.rejects();self.b.clear();self.b.update(original)
    def test_open_sided_requires_post_only_proof(self):
        self.uid='landsd/31181:0';csuid,kind,structure=SOURCES[self.uid];self.b.update(uid=self.uid,buildingCSUID=csuid,kind=kind,structureType=structure)
        self.write('3d-viewer/'+self.tile,self.data);self.update.update(uid=self.uid,before=copy.deepcopy(self.b),tileSHA256=self.sha(self.tilepath));self.review.update(uid=self.uid,sourceFormSHA256=value_sha(self.b),tileSHA256=self.sha(self.tilepath));self.refresh();self.rejects()
        self.proof.update(roofPartsExactlyUnchanged=True,allXZExactlyUnchanged=True,onlyIllustrativePostBottomVerticesChanged=True);self.write('proof.json',self.proof);self.review['renderProof']=self.ref(self.proofpath);self.refresh();self.stage()
if __name__=='__main__':unittest.main()
