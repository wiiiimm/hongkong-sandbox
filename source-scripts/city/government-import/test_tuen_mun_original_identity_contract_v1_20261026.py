"""Adversarial identity-only checks using the twelve sealed source fixtures."""
import unittest
from copy import deepcopy
from pathlib import Path
from run import ROOT,read
from tuen_mun_original_identity_contract_v1_20261026 import verify,OWNER,MAIN,CELL_PROVIDER

BASE=ROOT/'docs/astra-city/government-import'
PREFIX='government-xl-after-pok-oi-tuen-mun-'
def fixture():
    def take(name):return read(BASE/(PREFIX+name+'-20261026')/'summary.json')
    rows=read(BASE/(PREFIX+'twelve-runtime-evidence-v1-20261026')/'selection.json.gz')['rows']
    identities={}
    for n in ['eight-identity-v1','four-neighbour-identity-v1']:
        d=BASE/(PREFIX+n+'-20261026')
        for row in read(d/'summary.json')['rows']:identities[row['uid']]=read(d/(row['uid'].split('/')[1])/'identity.json')
    return [rows,identities,take('twelve-family-spatial-v1'),take('main-cell-companion-d-v1'),take('proposed-dependency-coverage-v1'),deepcopy(OWNER)]


class ExactHospitalIdentityTests(unittest.TestCase):
    def setUp(self):self.args=fixture()
    def rejects(self):
        with self.assertRaises(AssertionError):verify(*self.args)
    def test_actual_sources_identity_only(self):
        result=verify(*self.args)
        self.assertTrue(result['identityAccepted']);self.assertEqual(len(result['identityProofByUid']),12)
        self.assertFalse(result['physicalAcceptance']);self.assertFalse(result['installationApproved']);self.assertFalse(result['publication'])
        self.assertEqual(result['rawIndividualIdentityReasons'][MAIN],self.args[1][MAIN]['reasons'])
    def test_changed_source_rejected(self):self.args[0][0]['sourceSHA256']='0'*64;self.rejects()
    def test_unknown_failure_rejected(self):self.args[1][MAIN]['reasons'].append('unreviewed-source-graph-failure');self.rejects()
    def test_failed_exact_route_rejected(self):self.args[1][MAIN]['exactCurrentComponentRoute']['qualified']=False;self.rejects()
    def test_changed_object_rejected(self):self.args[1][MAIN]['exactCurrentComponentRoute']['official']['objectId']=1;self.rejects()
    def test_failed_companion_cell_rejected(self):self.args[3]['allFourWorldTargetCellsCovered']=False;self.rejects()
    def test_missing_cell_provider_dependency_rejected(self):
        next(r for r in self.args[4]['rows']if r['uid']==MAIN)['completeDependencyClosure'].remove(CELL_PROVIDER);self.rejects()
    def test_unknown_external_overlap_rejected(self):self.args[2]['outsideGroupIntersections'][0]['uid']='landsd/1:0';self.rejects()
    def test_insufficient_compound_coverage_rejected(self):self.args[2]['sources'][0]['combinedTargetCoverage']=.949;self.rejects()
    def test_insufficient_dependency_coverage_rejected(self):self.args[4]['rows'][0]['closureCoverageFraction']=.949;self.rejects()
    def test_changed_owner_evidence_rejected(self):self.args[5]['official-site-plan-20150518.pdf']='0'*64;self.rejects()
    def test_duplicate_source_rejected(self):self.args[0].append(deepcopy(self.args[0][0]));self.rejects()
    def test_changed_source_graph_rejected(self):self.args[1][MAIN]['originalOwnership']['sourceGraphVerified']=False;self.rejects()


if __name__=='__main__':unittest.main()
