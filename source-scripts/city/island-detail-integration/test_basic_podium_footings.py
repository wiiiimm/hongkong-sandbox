"""Publication-contract tests using synthetic qualified evidence in temporary files."""
import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from basic_podium_footings import POLICY, stage_basic_podium_footings, terrain_geometry_sha, value_sha


class BasicFootingTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.tile = 'city/data/tiles/test.json'
        self.terrain_url = 'city/data/test-terrain.json'
        self.cat_url = 'city/data/official-models/test/catalogue.json'
        self.b = dict(uid='podium', buildingCSUID='testP', kind='yes', structureType='Podium',
                      minimum=0, baseSource='landsd', heightSource='landsd', base=6, height=8,
                      baseHeightHKPD=6, topHeightHKPD=14, rings=[[[0,0],[1,0],[1,1],[0,1],[0,0]]])
        self.data = dict(buildings=[self.b, dict(uid='untouched', base=9)])
        self.tilepath = self.write('3d-viewer/'+self.tile, self.data)
        self.terrain = dict(coarseCells=[0,0,1,1], w=2, h=2, elev=[4,4,4,4.5],
                            renderedElev=[4,4,4,4.5], meta=dict(georef=dict(aE=1,aN=-1,bE=0,bN=0)),
                            nativeMesh=dict(position=[0,4,0,1,4,0,1,4.5,1,0,4,1],index=[0,1,2,0,2,3]))
        self.terrainpath = self.write('3d-viewer/'+self.terrain_url, self.terrain)
        self.catpath = self.write('3d-viewer/'+self.cat_url, dict(models=[]))
        self.proposalpath = self.write('proposal.json', dict(uid='podium',originalBase=6,foundationBase=3.98,surveyedElevationsUnchanged=True))
        self.review = dict(status='approved-for-integration',policy=POLICY,uid='podium',buildingCSUID='testP',
                           sourceFormSHA256=value_sha(self.b),tileSHA256=self.sha(self.tilepath),proposalSHA256=self.sha(self.proposalpath),
                           foundationBase=3.98,completeBasicBodyAndIndicesExactlyUnchanged=True,surveyedElevationsAndRoofUnchanged=True,
                           fullFootprintCovered=True,fullPositiveAreaGroundWithinFooting=True,nativeCoverageMatchesActualDrawnGround=True,
                           collisionReviewApproved=True,visualReviewApproved=True,verticalGroundContactsRequireReview=0,
                           sourceGeometryChanges=0,governmentGeometryChanges=0,aiGeometryModelling=False,
                           nativeCoverageUncoveredAreaM2=0,groundRange=[4,4.5],
                           nativeTerrainDependencies=[dict(url=self.terrain_url,geometrySHA256=terrain_geometry_sha(self.terrain))])
        self.reviewpath = self.write('review.json',self.review)
        self.update = dict(uid='podium',tile=self.tile,tileSHA256=self.sha(self.tilepath),before=copy.deepcopy(self.b),foundationBase=3.98,
                           proposal=self.ref(self.proposalpath),evidence=self.ref(self.reviewpath))
        self.manifest = dict(tiles=[dict(url=self.tile,bytes=self.tilepath.stat().st_size)],
                             officialModelCatalogues=[self.cat_url],terrainPatches=[dict(url=self.terrain_url)])
        self.edits = {}; self.report = {}

    @staticmethod
    def enc(value): return json.dumps(value,sort_keys=True,separators=(',',':')).encode()
    @staticmethod
    def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
    @staticmethod
    def load(path): return json.loads(path.read_bytes())
    def write(self, rel, value):
        p=self.root/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(self.enc(value));return p
    def ref(self,p):return dict(path=str(p.relative_to(self.root)),sha256=self.sha(p))
    def review_change(self,**changes):
        self.review.update(changes);self.write('review.json',self.review);self.update['evidence']=self.ref(self.reviewpath)
    def stage(self,updates=None):
        stage_basic_podium_footings(self.root,dict(basicPodiumFootings=[self.update]if updates is None else updates),
                                   self.manifest,self.edits,self.report,self.load,self.sha,self.enc)
    def retain(self):
        self.stage()
        for p,value in self.edits.items():p.write_bytes(value)
        self.edits={}
    def rejects(self):
        before=self.tilepath.read_bytes()
        with self.assertRaises((AssertionError,KeyError)):self.stage()
        self.assertEqual(before,self.tilepath.read_bytes())

    def test_stage_preserves_source_body_and_unrelated_records_without_live_write(self):
        before=self.tilepath.read_bytes();self.stage();self.assertEqual(before,self.tilepath.read_bytes())
        after=json.loads(self.edits[self.tilepath]);self.assertEqual(after['buildings'][0],{**self.b,'foundationBase':3.98,'foundationPolicy':POLICY})
        self.assertEqual(after['buildings'][1],self.data['buildings'][1]);self.assertEqual(self.report['retainedBasicOnlyFootingChecks'],['podium'])
    def test_private_unreviewed_proposal_is_not_publishable(self):
        self.review_change(status='private-proposal',collisionReviewApproved=False,visualReviewApproved=False);self.rejects()
    def test_visual_or_collision_or_coverage_failure_rejected(self):
        for key in ['collisionReviewApproved','visualReviewApproved','nativeCoverageMatchesActualDrawnGround','completeBasicBodyAndIndicesExactlyUnchanged']:
            with self.subTest(key=key):
                old=copy.deepcopy(self.review);self.review_change(**{key:False});self.rejects();self.review=old;self.review_change()
    def test_changed_form_rejected(self):
        self.update['before']['topHeightHKPD']=20;self.rejects()
    def test_changed_evidence_rejected(self):
        self.update['evidence']['sha256']='0'*64;self.rejects()
    def test_new_native_or_suppression_rejected(self):
        for model in [dict(uid='podium'),dict(uid='other',suppressesBuildingUids=['podium'])]:
            with self.subTest(model=model):
                self.write('3d-viewer/'+self.cat_url,dict(models=[model]));self.rejects()
    def test_retained_native_activation_and_suppression_rejected(self):
        self.retain()
        for model in [dict(uid='podium'),dict(uid='other',suppressesBuildingUids=['podium'])]:
            with self.subTest(model=model):
                self.write('3d-viewer/'+self.cat_url,dict(models=[model]))
                with self.assertRaises(AssertionError):self.stage([])
    def test_changed_local_native_terrain_rejected(self):
        self.retain();t=copy.deepcopy(self.terrain);t['nativeMesh']['position'][1]=0
        self.write('3d-viewer/'+self.terrain_url,t)
        with self.assertRaises(AssertionError):self.stage([])
    def test_removed_local_terrain_owner_rejected(self):
        self.retain();self.manifest['terrainPatches']=[]
        with self.assertRaises(AssertionError):self.stage([])
    def test_unrelated_future_models_and_terrain_do_not_invalidate_footing(self):
        self.retain();self.write('3d-viewer/'+self.cat_url,dict(models=[dict(uid='elsewhere')]))
        url='city/data/elsewhere-terrain.json';t=copy.deepcopy(self.terrain);t['coarseCells']=[100,100,101,101]
        self.write('3d-viewer/'+url,t);self.manifest['terrainPatches'].append(dict(url=url));self.stage([])
        self.assertEqual(self.report['retainedBasicOnlyFootingChecks'],['podium'])
    def test_nonfinite_or_excessive_depth_rejected(self):
        self.update['foundationBase']=float('nan');self.rejects()
        self.update['foundationBase']=-100;self.write('proposal.json',dict(uid='podium',originalBase=6,foundationBase=-100,surveyedElevationsUnchanged=True))
        self.update['proposal']=self.ref(self.proposalpath);self.review_change(foundationBase=-100,proposalSHA256=self.sha(self.proposalpath));self.rejects()
    def test_vertical_contacts_and_uncovered_ground_rejected(self):
        self.review_change(verticalGroundContactsRequireReview=1);self.rejects()
        self.review_change(verticalGroundContactsRequireReview=0,nativeCoverageUncoveredAreaM2=.01);self.rejects()
    def test_duplicate_uid_rejected(self):
        before=self.tilepath.read_bytes()
        with self.assertRaises(AssertionError):self.stage([self.update,self.update])
        self.assertEqual(before,self.tilepath.read_bytes())

if __name__=='__main__':unittest.main()
