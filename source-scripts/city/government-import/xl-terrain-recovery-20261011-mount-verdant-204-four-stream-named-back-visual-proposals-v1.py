"""Conditional exact source204 visual backing proposals in all four streams.

Full main podium grade/cap and restricted nonvisual body graph remain separately
bound source evidence, not current available hosts or acceptance. Every original
face/zero/body is retained. The three horizontal open bottoms use a distinct
existing roof perimeter contract, never this vertical backing interpretation.
"""
from pathlib import Path
import importlib.util,json,time,uuid
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
import mount_verdant_204_original_complete_back_visual_proposals_v1_20261011 as kernel
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261011-mount-verdant-204-four-stream-named-back-visual-proposals-v1';DOC=BASE/BATCH
CAPTURE=BASE/'xl-terrain-recovery-20261011-mount-verdant-two-current-render-attribute-capture-v1'; BACKS=BASE/'xl-terrain-recovery-20261011-mount-verdant-207-four-stream-complete-back-associations-v1'; GRADE=BASE/'xl-terrain-recovery-20261011-mount-verdant-podium-four-stream-authentic-grade-cap-v1'; GRAPH=BASE/'xl-terrain-recovery-20261011-mount-verdant-four-stream-restricted-source-contacts-v1'; FINITE=BASE/'xl-terrain-recovery-20261011-mount-verdant-tower-authentic-four-stream-finite-v1'; BOTTOM=BASE/'xl-terrain-recovery-20261011-mount-verdant-three-open-bottom-four-stream-roof-perimeters-v1'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();refs=[ref(Path(__file__))];receipts={}
 for folder in [CAPTURE,BACKS,GRADE,GRAPH,FINITE,BOTTOM]:
  r=read(folder/'result.json')
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  receipts[folder.name]=r;refs.append(ref(folder/'result.json'))
 def bound(folder,name):
  p=folder/name;assert ref(p)in receipts[folder.name]['evidenceRefs'];refs.append(ref(p));return read(p)
 source=bound(CAPTURE,'literal-source-inputs.json.gz');actual=bound(CAPTURE,'actual-render-attributes.json.gz');back=bound(BACKS,'diagnostic.json.gz');grade=bound(GRADE,'diagnostic.json.gz');graph=bound(GRAPH,'diagnostic.json.gz');finite=bound(FINITE,'diagnostic.json.gz');bottom=bound(BOTTOM,'diagnostic.json.gz');uids=['landsd/261717:0','landsd/75782:0'];assert [r['uid']for r in source['rows']]==[r['uid']for r in actual['rows']]==uids;worlds=[[],[],[],[]]
 for row,record,count in zip(source['rows'],actual['rows'],[14938,641]):
  asset=ROOT/row['path'];assert digest(asset.read_bytes())==row['entry']['sha256']==record['sourceSHA256'];refs.append(ref(asset));tri=decode_original_world_triangles(asset.read_bytes());index=np.asarray(record['completeOriginalIndex'],np.uint32).reshape(-1,3);assert tri.shape==(count,3,3)and len(index)==count;worlds[0].append(tri)
  for k,field in enumerate(['completeLiteralWorldPosition','completeExplicitLeftAssociatedFloat32WorldPosition','completeExplicitBalancedFloat32WorldPosition'],1):worlds[k].append(np.asarray(record[field],float).reshape(-1,3)[index])
 worlds=[np.concatenate(w)for w in worlds];data=kernel.membership();progress=ROOT/data['completeMappingOriginalInput']['path'];assert ref(progress)==data['completeMappingOriginalInput']and ref(progress)in receipts[BACKS.name]['evidenceRefs'];refs.extend([ref(progress),ref(kernel.MEMBERSHIP)]);mapping=read(progress)['binding']['completeBodyAndBackingMappings'];expected={k:v for k,v in mapping.items()if int(k)not in [311,312,313]};assert expected==data['exactOriginalMembership']and data['sourceMembershipReceipt']==ref(BACKS/'result.json');assert read(progress)['binding']['completeHostGlobalFaces']==data['conditionalHostGlobalFaces'];assert len(expected)==204
 assert len(graph['rows'])==len(grade['rows'])==len(finite['rows'])==4 and all(len(r['conditionalReachedComponents'])==764 and not r['unresolvedNonvisualComponents']for r in graph['rows']);assert all(r['strictClearCapWallPaths']['allAffectedHavePaths']and len(r['completeMainBodyGradeInterfaces'])==183 and not r['nonwallRawFailures']for r in grade['rows']);assert all(not r['unprovedFaces']for r in finite['rows']);assert all(not r['negativeBodies']for r in bottom['summary'])
 helpers=['mount_verdant_204_original_complete_back_visual_proposals_v1_20261011.py','test_mount_verdant_204_original_complete_back_visual_proposals_v1_20261011.py','exact_packed_world_geometry_20261009.py','exact_original_shared_edge_component_census_v2_20261011.py','exact_original_edge_finite_facade_distance_band_v2_20261010.py','exact_original_edge_finite_facade_distance_band_20261010.py','exact_original_facet_orthogonal_finite_host_band_diagnostic_v1_20261011.py','exact_original_surface_coordinate_band_20261010.py','exact_original_projection_coverage_20261009.py','xl-popcorn-source-investigations-checkpoints-20261009.py'];refs.extend(ref(HERE/n)for n in helpers);claim=reservations.claim('mount204-named-source-proposal-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];rows=[]
 try:
  for mode,world,grow,frow in zip(kernel.SOURCE_WORLDS,worlds,grade['rows'],finite['rows']):
   assert digest(world[14938:].tobytes())==grow['complete641WorldSHA256']and digest(world[:14938].tobytes())==frow['completeWorldSHA256'];binding=dict(sourceSHA256ByUID={u:r['entry']['sha256']for u,r in zip(uids,source['rows'])},complete15579WorldSHA256=kernel.sha(world),membershipBytesSHA256=kernel.MEMBERSHIP_SHA256,completeHostFaceIdsSHA256=kernel.canonical(data['conditionalHostGlobalFaces']));assert reservations.heartbeat(lease)['ok'];proof=kernel.verify(world,mode,expected_binding=binding,current_binding=binding);assert len(proof['rows'])==204;rows.append(proof);assert reservations.heartbeat(lease)['ok'];print(json.dumps(dict(mode=mode,completeConditionalVisualAssociations=len(proof['rows']),structuralCredit=False)),flush=True)
  DOC.mkdir(parents=True);testlog=DOC/'actual-source-and-adverse-tests.log';testlog.write_bytes(Path('/tmp/mount-verdant-204-source-role-tests-v1-20261011.log').read_bytes());assert b'Ran 16 tests'in testlog.read_bytes()and testlog.read_bytes().rstrip().endswith(b'OK');refs.append(ref(testlog));assert all(ref(ROOT/r['path'])==r for r in refs);out=dict(uids=uids,all204NamedConditionalVisualAssociationsEveryFourStreams=rows,full15579Faces973NonzeroBodiesAndThreeZerosPreserved=True,completeOriginalClearanceGradeAndGraphEvidence=[ref(GRADE/'diagnostic.json.gz'),ref(GRAPH/'diagnostic.json.gz'),ref(FINITE/'diagnostic.json.gz')],threeHorizontalOpenBottomFootingsRemainSeparate=ref(BOTTOM/'diagnostic.json.gz'),sourceOnly=True,independentlyCurrentHostQualificationStillRequired=True,visualRoleAccepted=False,structuralRootCredit=False,structuralBridgeCredit=False,currentAcceptance=False,newlyInstalled=0,evidenceRefs=refs);save(DOC/'diagnostic.json.gz',out)
  spec=importlib.util.spec_from_file_location('freeze',HERE/helpers[-1]);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.freeze(BATCH,'mount204-complete-backing-four-stream-exact-source-named-visual-proposals-v1',[ROOT/r['path']for r in refs]+[DOC/'diagnostic.json.gz'],dict(uids=uids,completeConditionalVisualAssociations=204,sourceOnly=True,currentAcceptance=False,newlyInstalled=0))
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
