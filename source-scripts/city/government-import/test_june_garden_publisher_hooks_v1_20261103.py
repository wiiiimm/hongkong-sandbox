"""Publisher composition must preserve canonical failures and exact source scope."""
import copy
import hashlib
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch
from contextlib import nullcontext
import june_garden_publisher_hooks_v1_20261103 as hooks


class PublisherGuards(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        for name in ['manifest.json','terrain.json']:
            p = self.root/'3d-viewer/city/data'/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b'{}')
        self.sha = hashlib.sha256(b'{}').hexdigest()
        self.original = {u:dict(uid=u,sha256=s,buildingCSUID='cs-'+u,rootTranslation=[-834500,0,816500]) for u,s in hooks.SOURCES.items()}
        self.models = copy.deepcopy(self.original)
        for u,m in self.models.items():
            m.update(asset='assets/'+m['sha256']+'.glb.gz',priority='landmark',proceduralWindows=False,activationGroup=sorted(hooks.SOURCES))
            if u in hooks.SUPPORTS:
                m['supportDependencies']=[dict(uid=hooks.P,state='installed',buildingCSUID=self.original[hooks.P]['buildingCSUID'],sha256=hooks.SOURCES[hooks.P])]
        members=[]
        for name in ['south','middle','north']:
            path=self.root/('candidate-'+name+'.json');path.write_bytes(b'{}')
            members.append(dict(member=name,candidate=dict(path=path.name,sha256=self.sha),replaces=dict(url='city/data/government-native-north-pair-'+name+'-v1-20261027.json',sha256=self.sha)))
        self.surface=dict(allEffectiveMembersRequired=True,members=members)
        self.plan=dict(topLevelTerrainPatches=[dict(source=m['candidate']['path'],sha256=self.sha,destination=m['replaces']['url'],replaces=m['replaces']) for m in members])
        self.guard=object();self.dependencies=Mock(return_value='canonical-support-result');self.terrain=Mock(return_value='canonical-terrain-result')
        self.pub=SimpleNamespace(read_bytes=lambda p:Path(p).read_bytes(),stage_dependencies=self.dependencies,stage_top_level_terrain=self.terrain,PUBLICATION_GUARD=self.guard)
    def install(self):
        hooks.install(self.pub,self.root,self.surface,self.original,self.sha)
    def call_dependencies(self):
        return self.pub.stage_dependencies(self.root,self.plan,{}, {},self.models,{})
    def test_canonical_support_checks_still_run(self):
        self.install();self.assertEqual(self.call_dependencies(),'canonical-support-result');self.dependencies.assert_called_once();self.assertIs(self.pub.PUBLICATION_GUARD,self.guard)
    def test_canonical_support_failure_propagates(self):
        self.dependencies.side_effect=RuntimeError('retained support guard')
        self.install()
        with self.assertRaisesRegex(RuntimeError,'retained support guard'):self.call_dependencies()
    def test_wrong_original_bytes_rejected(self):
        self.original[hooks.SMALL]['sha256']='wrong'
        with self.assertRaises(AssertionError):self.install()
    def test_source_pose_change_rejected(self):
        self.install();self.models[hooks.SMALL]['verticalPlacementOffsetHKPD']=1
        with self.assertRaises(AssertionError):self.call_dependencies()
        self.dependencies.assert_not_called()
    def test_support_metadata_migration_rejected(self):
        self.install();self.plan['dependencyReviews']=['unexpected']
        with self.assertRaises(AssertionError):self.call_dependencies()
    def test_wrong_terrain_destination_rejected(self):
        self.install();self.plan['topLevelTerrainPatches'][0]['destination']='elsewhere.json'
        with self.assertRaises(AssertionError):self.pub.stage_top_level_terrain(self.plan,{}, {},{}, {})
        self.terrain.assert_not_called()
    def test_all_three_terrain_members_go_through_canonical_validator(self):
        self.install()
        with patch.object(hooks,'private_validator',return_value=nullcontext()) as dispatch:
            self.assertEqual(self.pub.stage_top_level_terrain(self.plan,{}, {},{}, {}),'canonical-terrain-result')
        dispatch.assert_called_once();self.terrain.assert_called_once()
    def test_changed_root_terrain_rejected(self):
        self.install();(self.root/'3d-viewer/city/data/terrain.json').write_bytes(b'changed')
        with self.assertRaises(AssertionError):self.pub.stage_top_level_terrain(self.plan,{}, {},{}, {})


if __name__ == '__main__': unittest.main()
