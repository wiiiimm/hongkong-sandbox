"""Source-specific Twin155 conditional visual roles; no root/bridge/current credit."""
from pathlib import Path
import importlib.util,time,uuid
from run import ROOT,HERE,read,save,digest,connect,reservations
from twin155_complete_boundary_actual_fixture_v1_20261011 import actual_fixture,DOCS
from twin155_named_complete_boundary_visual_assembly_proposal_v1_20261011 import verify
BATCH='xl-terrain-recovery-20261011-twin155-named-complete-boundary-visual-proposals-v1';DOC=ROOT/'docs/astra-city/government-import'/BATCH
UIDS=['landsd/222465:0','landsd/223206:0']
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();docs,packages,refs,receipts=actual_fixture()
 for r in receipts.values():
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 refs.extend(ref(HERE/n)for n in [Path(__file__).name,'twin155_complete_boundary_actual_fixture_v1_20261011.py','twin155_named_complete_boundary_visual_assembly_proposal_v1_20261011.py','test_twin155_named_complete_boundary_visual_assembly_proposal_v1_20261011.py','exact_original_shared_edge_component_census_v2_20261011.py','exact_original_body_boundary_group_census_v1_20261011.py','exact_original_edge_any_finite_distance_band_v2_20261010.py','exact_original_edge_any_finite_distance_band_v1_20261010.py','exact_original_perpendicular_any_facet_band_v1_20261010.py','xl-popcorn-source-investigations-checkpoints-20261009.py'])
 validation=ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261011-twin155-source-proposal-validation-v1';v=read(validation/'validation.json');assert v['passed']is True and v['actualAdverseTests']==13;refs.extend([ref(validation/'validation.json'),*v['evidenceRefs']])
 context=DOCS['bands'].parent/'xl-terrain-recovery-20261011-twin-regency-residual-representative-source-context-v3/context.json';data=read(context);refs.append(ref(context));refs.extend(data['images'])
 claim=reservations.claim('twin155-visual-proposals-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];last=time.monotonic();rows=[]
 def pulse(force=False):
  nonlocal last
  if force or time.monotonic()-last>=20:assert reservations.heartbeat(lease)['ok']and reservations.owns(lease);last=time.monotonic()
 try:
  for part,p in packages.items():rows.append(verify(**p));pulse()
  assert len(rows)==155;assert all(ref(ROOT/r['path'])==r for r in refs);pulse(True)
  out=dict(uids=UIDS,all155NamedSourceBodiesRetained=True,allFourCompleteBoundaryProofs=True,rows=rows,all138OtherVisualCandidatesUnqualified=True,fullInteriorFailuresPreserved=True,structuralRootCredit=False,structuralBridgeCredit=False,visualPartsNeverQualifyHosts=True,currentAcceptance=False,nativeReacceptance=False,sourceGeometryChanges=0,newlyInstalled=0,evidenceRefs=refs);save(DOC/'diagnostic.json.gz',out)
  spec=importlib.util.spec_from_file_location('twin155freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.freeze(BATCH,'twin155-original-complete-boundary-visual-assembly-conditional-proposals-v1',[ROOT/r['path']for r in refs]+[DOC/'diagnostic.json.gz'],dict(uids=UIDS,completeNamedSourceBodies=155,all138OtherCandidatesRemainUnqualified=True,currentAcceptance=False,nativeReacceptance=False,newlyInstalled=0))
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
