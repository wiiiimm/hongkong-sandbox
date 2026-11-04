"""Exact-source, peer-graph and canonical installer guard regression checks."""
import ast
import copy
import os
import unittest
from run import ROOT, HERE, read
from pok_oi_original_admission_v1_20261026 import MAIN, PODIUM, SOURCES, verify_closed_contract

CONFIG_PATH = 'docs/astra-city/government-import/government-xl-pok-oi-original-install-config-v1-20261026.json'
os.environ['ORIGINAL_INSTALL_CONFIG'] = CONFIG_PATH
from pok_oi_original_stage_v1_20261026 import expected_dependencies


class ClosedPairAdmission(unittest.TestCase):
    def setUp(self):
        self.cfg = read(ROOT/CONFIG_PATH)
        self.review = read(ROOT/'docs/astra-city/government-import'/self.cfg['review']/'ROOT-PHYSICAL-REVIEW.json')

    def test_exact_pair_and_directed_availability(self):
        self.assertTrue(verify_closed_contract(self.cfg,self.review))
        self.assertEqual(expected_dependencies(MAIN,self.review),[])
        self.assertEqual(expected_dependencies(PODIUM,self.review),[
            dict(uid=MAIN,state='installed',buildingCSUID='2237034007T20060123',sha256=SOURCES[MAIN])])

    def test_changed_source_revision_rejected(self):
        self.review['sourceSHA256ByUid'][MAIN]='0'*64
        with self.assertRaises(AssertionError): verify_closed_contract(self.cfg,self.review)

    def test_missing_or_cyclic_peer_graph_rejected(self):
        for graph in [{},{MAIN:PODIUM},{MAIN:PODIUM,PODIUM:MAIN}]:
            with self.subTest(graph=graph):
                altered=copy.deepcopy(self.review);altered['supportByUid']=graph
                with self.assertRaises(AssertionError): verify_closed_contract(self.cfg,altered)

    def test_unreviewed_face_never_inherits_exception(self):
        self.review['acceptedGroundWallFacesByUid'][PODIUM].append(2702)
        with self.assertRaises(AssertionError): verify_closed_contract(self.cfg,self.review)

    def test_availability_does_not_grant_physical_support(self):
        self.review['physicalSupportByUid']={MAIN:PODIUM}
        with self.assertRaises(AssertionError): verify_closed_contract(self.cfg,self.review)

    def test_basic_support_cannot_replace_exact_source(self):
        self.review['retainedBasicSupportDependencies']=[dict(uid=PODIUM,supportUid=MAIN)]
        with self.assertRaises(AssertionError): expected_dependencies(PODIUM,self.review)

    def test_geometry_or_terrain_edits_rejected(self):
        for field,value in [('terrainEdits',True),('sourceGeometryChanges',1),('sourcePoseChanges',1)]:
            altered=copy.deepcopy(self.review);altered[field]=value
            with self.subTest(field=field),self.assertRaises(AssertionError): verify_closed_contract(self.cfg,altered)

    def test_unrelated_source_is_rejected(self):
        with self.assertRaises(AssertionError): expected_dependencies('landsd/336667:0',self.review)

    def test_installer_function_bodies_match_canonical(self):
        def functions(path):
            return {n.name:ast.dump(n,include_attributes=False) for n in ast.parse(path.read_text()).body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
        self.assertEqual(functions(HERE/'pok_oi_original_install_v1_20261026.py'),
                         functions(HERE/'independent_model_only_live_install_v1_20261024.py'))

    def test_publication_lock_and_lease_functions_match_canonical(self):
        def functions(path):
            return {n.name:ast.dump(n,include_attributes=False) for n in ast.parse(path.read_text()).body if isinstance(n,ast.FunctionDef)}
        adapted=functions(HERE/'pok_oi_original_publish_v1_20261026.py')
        canonical=functions(HERE/'ying_hoi_native_floor_publish_v1_20261026.py')
        for name in ['check','assert_publication_idle','main']:
            self.assertEqual(adapted[name],canonical[name])


if __name__=='__main__':
    unittest.main()
