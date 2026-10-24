"""UNEXECUTED six synthetic preservation/historical/schema fixtures."""
import copy,hashlib,tempfile,unittest
from pathlib import Path
from polyu_compact_runtime_mesh_projection_v1_draft_20261014 import mesh_binding
import polyu_append_historical_capture_binding_v1_draft_20261014 as h
class BindingFixtures(unittest.TestCase):
    def setUp(self):
        self.old=dict(position=[-0.0,1,0,1,1,0,0,1,1,99,88,77],index=[0,1,2]);self.new=copy.deepcopy(self.old)
        t=[[0,1,0],[1,1,0],[0,1,1]];self.new['position']+=sum(t,[]);self.new['index']+=[4,5,6]
        pointer=dict(oldPrivateFace=0,outsidePolygon=0,field='completeExactMaskPartition.outside',mapping='completeOldPrivateMapping')
        piece=dict(idealSourcePlanePoints=t,packedPieceTriplet=t,exactVerticalSourcePlaneResidualM=['0','0','0'])
        self.nom=dict(schema='private-polyu-append-complete-legacy-source-region-nomination-v1',currentAcceptance=False,physicalAccepted=False,installationApproved=False,
            previousCompleteMeshBinding=mesh_binding(self.old),newCompleteMeshBinding=mesh_binding(self.new),newNativeMesh=self.new,oldFaceProvenanceRange=[0,1],originalPositionBufferAndIndexPrefixUnchanged=True,
            sourceRegionAccounts=[dict(target=dict(sourcePointer=pointer),exactOwnPlaneCellEnclosure=dict(triangles=[piece]))],
            appendAccount=dict(appendedFaces=[dict(candidateFace=1,kind='appendedLegacyExactSourceRegionOwnPlaneCellEnclosure',physicalAccepted=False,originalBuildingGeometryPoseUnchanged=True,sourcePointer=copy.deepcopy(pointer),localTriangle=0,packedTriplet=t,completeIdealSourcePlanePoints=t,exactVerticalSourcePlaneResidualM=['0','0','0'])],exactExistingRepresentations=[]))
    def check(self):return h.validate_append(self.nom,self.old,mesh_binding(self.old),mesh_binding(self.new))
    def test_complete_unused_prefix_and_appended_source_pointer_valid(self):self.assertEqual(self.check().shape,(2,3,3))
    def test_unused_signed_zero_change_rejected_even_with_new_valid_hash(self):
        self.new['position'][0]=0.0;self.nom['newCompleteMeshBinding']=mesh_binding(self.new)
        with self.assertRaises(AssertionError):self.check()
    def test_old_index_and_append_source_plane_provenance_tamper_rejected(self):
        self.new['index'][0]=1;self.nom['newCompleteMeshBinding']=mesh_binding(self.new)
        with self.assertRaises(AssertionError):self.check()
        self.new['index'][0]=0;self.nom['newCompleteMeshBinding']=mesh_binding(self.new);self.nom['appendAccount']['appendedFaces'][0]['sourcePointer']['outsidePolygon']=1
        with self.assertRaises((AssertionError,KeyError)):self.check()
    def test_wrong_count_or_new_face_index_rejected(self):
        self.nom['appendAccount']['appendedFaces'][0]['candidateFace']=2
        with self.assertRaises(AssertionError):self.check()
    def test_full_grid_width_domain_contract_not_description_only(self):
        p=dict(w=3,h=2,meta=dict(georef=dict(W=3,H=2,aE=5,aN=-5,bE=834500,bN=816500)),elev=[0]*6,renderedElev=[0]*6,vegetation=[0]*6)
        self.assertEqual(h.grid_domain(p),[0,0,10,5]);p['w']=4
        with self.assertRaises(AssertionError):h.grid_domain(p)
    def test_only_exact_named_manifest_archive_resolves_missing_old_live_input(self):
        context=dict(mutableCurrentByteSnapshots=[dict(original=dict(path=h.MANIFEST,sha256=h.HISTORICAL),savedHistoricalBytes=dict(path='archive.json',sha256=h.HISTORICAL))])
        archive=h.historical_manifest(context)
        with tempfile.TemporaryDirectory()as folder:
            root=Path(folder);data=b'fixture';q=dict(path='source.bin',sha256=hashlib.sha256(data).hexdigest());(root/'source.bin').write_bytes(data)
            self.assertEqual(h.resolve_source_ref(q,archive,root),q)
            with self.assertRaises(AssertionError):h.resolve_source_ref(dict(path='missing-source.bin',sha256=q['sha256']),archive,root)
            with self.assertRaises(AssertionError):h.resolve_source_ref(dict(path=h.MANIFEST,sha256=q['sha256']),archive,root)
        context['mutableCurrentByteSnapshots'].append(copy.deepcopy(context['mutableCurrentByteSnapshots'][0]))
        with self.assertRaises(AssertionError):h.historical_manifest(context)
if __name__=='__main__':unittest.main(verbosity=2)
