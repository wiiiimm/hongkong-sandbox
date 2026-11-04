"""Complete original and literal podium finite bounds; unchanged sources, no approval."""
import importlib.util,uuid
import numpy as np
from run import ROOT,HERE,read,save,digest,reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_paired_finite_clearance_v3_20261011 import verify
BATCH='government-xl-esplanade-podium-finite-v1-20261015';BASE=ROOT/'docs/astra-city/government-import';DOC=BASE/BATCH;PREV=BASE/'government-xl-esplanade-pair-current-physical-v3-20261015';LOCAL=HERE/'local'/PREV.name

def main():
 assert not DOC.exists();receipt=read(PREV/'result.json')
 for r in receipt['evidenceRefs']:assert digest((ROOT/r['path']).read_bytes())==r['sha256']
 row=next(r for r in read(PREV/'selection.json.gz')['rows']if r['uid']=='landsd/309385:0');runtime=next(r for r in read(LOCAL/'runtime-geometry.json.gz')['rows']if r['uid']==row['uid']);raw=(ROOT/row['candidate']['path']).read_bytes();assert digest(raw)==row['sourceSHA256'];original=decode_original_world_triangles(raw);literal=np.asarray(runtime['position'],float).reshape(-1,3)[np.asarray(runtime['index']).reshape(-1,3)];ground=np.asarray(runtime['drawnGroundGeometry'],float).reshape(-1,3,3);assert len(original)==len(literal)==1476
 claim=reservations.claim('esplanade-finite-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];results=[]
 try:
  DOC.mkdir();save(DOC/'binding.json',dict(uid=row['uid'],sourceSHA256=row['sourceSHA256'],originalWorldSHA256=digest(original.tobytes()),literalWorldSHA256=digest(literal.tobytes()),groundSHA256=digest(ground.tobytes())))
  for name,tri in [('original',original),('literal',literal)]:
   faces=[]
   for i,face in enumerate(tri):
    proof=verify(face,ground);faces.append(dict(sourceFace=i,proof=proof))
    if i%50==0:assert reservations.heartbeat(lease)['ok'];print(name,i,len(tri),flush=True)
   save(DOC/(name+'.json.gz'),dict(faces=faces,worldSHA256=digest(tri.tobytes()),groundSHA256=digest(ground.tobytes()),installationApproved=False));results.append(dict(mode=name,faces=len(faces),unproved=[r['sourceFace']for r in faces if not r['proof']['existingOrdinaryClearanceBoundProved']],uncovered=[r['sourceFace']for r in faces if not r['proof']['groundProjectionCovered']]))
  for r in receipt['evidenceRefs']:assert digest((ROOT/r['path']).read_bytes())==r['sha256']
  paths=[__import__('pathlib').Path(__file__),PREV/'result.json',PREV/'selection.json.gz',LOCAL/'runtime-geometry.json.gz',ROOT/row['candidate']['path']]+[HERE/n for n in ['exact_original_paired_finite_clearance_v3_20261011.py','exact_original_paired_finite_clearance_v2_20261010.py','exact_original_triangle_pair_column_gap_20261010.py','exact_original_projection_coverage_v2_20261010.py']]
  spec=importlib.util.spec_from_file_location('esplanade_finite_checkpoint',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f);f.freeze(BATCH,'complete-podium-original-literal-finite-v1',paths,dict(uids=[row['uid']],rows=results,fullAcceptance=False,qualification='Complete original and literal worlds only; no other Float32 representations or source-role approval claimed.'))
  print(results,flush=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
