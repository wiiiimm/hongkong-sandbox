"""Unexecuted source-only placement proposal, pinned to completed actual ground.

No fresh current capture/reacceptance, no mounting/support/bridge/function claim.
Root must review source views and full method before canonical execution. A later
whole-pair adapter must independently fence/replay current physical obligations.
"""
from pathlib import Path
import importlib.util,time,uuid
from run import ROOT,HERE,read,save,digest,connect,reservations
from twin138_source_placement_actual_fixture_v1_20261011 import actual_fixture
import twin138_named_original_source_placement_proposal_v1_20261011 as k
BATCH='xl-terrain-recovery-20261011-twin138-named-original-source-placement-proposals-v1';DOC=ROOT/'docs/astra-city/government-import'/BATCH
VALIDATION=DOC.parent/'xl-terrain-recovery-20261011-twin138-source-placement-validation-v1'
UIDS=['landsd/222465:0','landsd/223206:0']
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();docs,packages,refs,receipts=actual_fixture()
 for r in receipts.values():
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 refs.extend(ref(HERE/n)for n in [Path(__file__).name,'twin138_named_original_source_placement_proposal_v1_20261011.py','twin138_original_source_placement_pins_v1_20261011.json','twin138_source_placement_actual_fixture_v1_20261011.py','test_twin138_named_original_source_placement_proposal_v1_20261011.py','twin155_complete_boundary_actual_fixture_v1_20261011.py','twin155_named_complete_boundary_visual_assembly_proposal_v1_20261011.py','exact_packed_world_geometry_20261009.py','exact_original_shared_edge_component_census_v2_20261011.py','xl-popcorn-source-investigations-checkpoints-20261009.py'])
 validation=read(VALIDATION/'validation.json');assert validation['passed']is True and validation['actualAdverseTests']==16
 refs.extend([ref(VALIDATION/'validation.json'),*validation['evidenceRefs']])
 # Explicitly bind the frozen candidate/actual-ground/raw physical provenance.
 physical=ROOT/'docs/astra-city/government-import/government-xl-terrain-recovery-twin-regency-pair-authentic-current-v1-20261011/result.json';raw=read(physical)
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(raw['jobId'],)).fetchone()==('complete',raw)
 refs.append(ref(physical));refs.extend(raw['evidenceRefs'])
 refs=list({(r['path'],r['sha256']):r for r in refs}.values());assert all(ref(ROOT/r['path'])==r for r in refs)
 claim=reservations.claim('twin138-source-placement-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];last=time.monotonic();rows=[]
 def pulse(force=False):
  nonlocal last
  if force or time.monotonic()-last>=20:assert reservations.heartbeat(lease)['ok']and reservations.owns(lease);last=time.monotonic()
 try:
  for body in sorted(packages):rows.append(k.verify(**packages[body]));pulse()
  assert len(rows)==138 and sum(len(r['completeOriginalFaces'])for r in rows)==1521
  assert all(ref(ROOT/r['path'])==r for r in refs);pulse(True)
  save(DOC/'diagnostic.json.gz',dict(uids=UIDS,rows=rows,completeNamedSourceBodies=138,completeOriginalFaces=1521,completeFourArithmeticStreams=True,sourceOnly=True,frozenActualGroundBaselineOnly=True,noFreshCurrentCapture=True,currentAcceptance=False,finiteMountingCertified=False,structuralRootCredit=False,structuralBridgeCredit=False,visualPartsNeverQualifyHosts=True,nativeReacceptance=False,sourceGeometryChanges=0,newlyInstalled=0,evidenceRefs=refs))
  spec=importlib.util.spec_from_file_location('twin138_source_placement_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
  m.freeze(BATCH,'twin138-named-original-source-placement-conditional-visual-proposals-v1',[ROOT/r['path']for r in refs]+[DOC/'diagnostic.json.gz'],dict(uids=UIDS,completeNamedSourceBodies=138,completeOriginalFaces=1521,currentAcceptance=False,finiteMountingCertified=False,structuralRootCredit=False,structuralBridgeCredit=False,nativeReacceptance=False,newlyInstalled=0))
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
