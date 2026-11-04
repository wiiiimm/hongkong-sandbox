"""Fenced complete original+literal+two explicitF32 backing role PROPOSALS.

No current ground/host qualification, root, role acceptance or installation.
Every complete source/capture stream pinned; failed lowerloops/facets retained.
"""
from pathlib import Path
import importlib.util
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from mount_verdant_original_two_back_mounted_visual_proposals_v1_20261011 import verify,sha,canonical,SOURCE,UID
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261011-mount-verdant-four-stream-back-visual-proposals-v1';DOC=BASE/BATCH
CAPTURE=BASE/'xl-terrain-recovery-20261011-mount-verdant-two-current-render-attribute-capture-v1'
GRADE=BASE/'xl-terrain-recovery-20261011-mount-verdant-podium-grade-cap-lower-loops-v2'
BACK=BASE/'xl-terrain-recovery-20261011-mount-verdant-specific-back-attachments-v2'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();refs=[ref(Path(__file__))]
 for folder,name in ((CAPTURE,'actual-render-attributes.json.gz'),(GRADE,'diagnostic.json.gz'),(BACK,'diagnostic.json.gz')):
  receipt=read(folder/'result.json')
  with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
  assert ref(folder/name)in receipt['evidenceRefs'];refs.extend([ref(folder/'result.json'),ref(folder/name)])
 inputs=read(CAPTURE/'literal-source-inputs.json.gz');assert inputs['currentManifest']['sha256']=='4a6756a928b11a781d5eca86a22278994441985f532dba40a973f46df2902285';row=next(r for r in inputs['rows']if r['uid']==UID);source=ROOT/row['path'];assert digest(source.read_bytes())==row['entry']['sha256']==SOURCE and row['entry']['triangles']==641;original=decode_original_world_triangles(source.read_bytes());grade=read(GRADE/'diagnostic.json.gz');assert digest(original.tobytes())==grade['completeOriginalWorldSHA256'];actual=next(r for r in read(CAPTURE/'actual-render-attributes.json.gz')['rows']if r['uid']==UID);assert actual['sourceSHA256']==SOURCE
 index=np.asarray(actual['completeOriginalIndex'],np.uint32).reshape(-1,3);assert len(index)==641
 fields=[('captured-actual-literal','completeLiteralWorldPosition'),('captured-explicit-left-associated-float32','completeExplicitLeftAssociatedFloat32WorldPosition'),('captured-explicit-balanced-float32','completeExplicitBalancedFloat32WorldPosition')]
 worlds=[('untouched-provider-original',original)]+[(mode,np.asarray(actual[field],float).reshape(-1,3)[index])for mode,field in fields];assert all(w.shape==(641,3,3)and np.isfinite(w).all()for _,w in worlds)
 helpers=['mount_verdant_original_two_back_mounted_visual_proposals_v1_20261011.py','test_mount_verdant_original_two_back_mounted_visual_proposals_v1_20261011.py','exact_original_shared_edge_component_census_v2_20261011.py','exact_original_edge_finite_facade_distance_band_v2_20261010.py','exact_original_edge_finite_facade_distance_band_20261010.py','exact_original_facet_orthogonal_finite_host_band_diagnostic_v1_20261011.py','exact_original_surface_coordinate_band_20261010.py','exact_original_projection_coverage_20261009.py','exact_packed_world_geometry_20261009.py','xl-popcorn-source-investigations-checkpoints-20261009.py'];refs.extend(ref(p)for p in [source,CAPTURE/'literal-source-inputs.json.gz',*[HERE/n for n in helpers]])
 hostids=grade['completeMainBody576OriginalFaces'];rows=[]
 for mode,world in worlds:
  binding=dict(uid=UID,sourceSHA256=SOURCE,completeWorldTrianglesSHA256=sha(world),completeHostSourceFaceIdsSHA256=canonical(hostids));proposal=verify(world,hostids,expected_binding=binding,current_binding=binding);rows.append(dict(mode=mode,completeWorldTrianglesSHA256=sha(world),complete641Faces=True,conditionalVisualProposal=proposal));print(dict(mode=mode,parts=2,allWholeBackMountAssociations=True),flush=True)
 assert all(ref(ROOT/r['path'])==r for r in refs);out=dict(uids=[UID],sourceSHA256=SOURCE,completeOriginal641FacesRetained=True,completeFourStreamRows=rows,rawFailures=ref(BACK/'diagnostic.json.gz'),frozenCapturedManifestSHA256=inputs['currentManifest']['sha256'],freshCurrentAcceptance=False,sourceOnly=True,conditionalGroundedHostNotAccepted=True,explicitFloat32ArithmeticOnlyNotUniversalGPUCameraGuarantee=True,visualRoleAccepted=False,structuralRootOrBridgeCredit=False,wholeNativeReacceptance=False,newlyInstalled=0,evidenceRefs=refs);save(DOC/'diagnostic.json.gz',out)
 spec=importlib.util.spec_from_file_location('freeze',HERE/helpers[-1]);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.freeze(BATCH,'mount641-original-literal-two-explicit-f32-named-full-back-visual-proposals-v1',[ROOT/r['path']for r in refs]+[DOC/'diagnostic.json.gz'],dict(uids=[UID],allFourStreamsCompleteBackMountProposals=True,originalDetailFaces=22,sourceOnly=True,currentAcceptance=False,visualRoleAccepted=False,structuralRootCredit=False,newlyInstalled=0))
if __name__=='__main__':main()
