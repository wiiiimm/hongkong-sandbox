"""Recheck companion against all actual prepared patch faces, preserving old failures."""
from pathlib import Path
import subprocess,uuid
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
from exact_original_paired_finite_clearance_v3_20261011 import verify
from require_remaining_xl import require_remaining
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-opus-companion-complete-patch-v1-20261017';DOC=BASE/BATCH
OLD=BASE/'government-xl-opus-companion-finite-walls-v1-20261017';GROUND=BASE/'government-xl-opus-preserved-neighbours-v1-20261016';WORLD=BASE/'government-xl-opus-four-world-contacts-v1-20261017'
def main():
 assert not DOC.exists();count=BASE/'government-xl-sham-shui-po-pool-original-installed-v1-20261017/full-xl-current-count.json'
 require_remaining(count,'landsd/322573:0','e3c4ad4fff2acda8844233c83b6885dbbd73c1da9acb0a0efc7ec9778f57d764')
 refs=[Path(__file__),count,HERE/'require_remaining_xl.py'];pins={}
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  for d in [OLD,GROUND,WORLD]:
   r=read(d/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(d/'result.json')
   for x in r['evidenceRefs']:pins.setdefault(x['path'],set()).add(x['sha256'])
 def consume(p):
  assert digest(p.read_bytes()) in pins[str(p.relative_to(ROOT))];refs.append(p);return read(p)
 worlds=consume(WORLD/'world-triangles.json.gz');tri=np.array(worlds['original']['landsd/319559:0']);assert len(tri)==208 and all(np.array_equal(tri,w['landsd/319559:0']) for w in worlds.values());old=consume(OLD/'original.json.gz');patch=GROUND/'private-terrain.json';consume(patch)
 claim=reservations.claim('opus-full-patch-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  DOC.mkdir();tool=HERE/'opus_complete_patch_capture_v1_20261017.mjs';capture=DOC/'drawn-patch.json.gz'
  subprocess.run(['node',str(tool),str(patch.relative_to(ROOT)),str(capture.relative_to(ROOT))],cwd=ROOT,check=True)
  cap=read(capture);assert cap['patchSHA256']==digest(patch.read_bytes());ground=np.array(cap['position']).reshape(-1,3)[np.array(cap['index']).reshape(-1,3)]
  rows=[]
  for i,t in enumerate(tri):
   rows.append(dict(sourceFace=i,proof=verify(t,ground)))
   if i%25==0:assert reservations.heartbeat(lease)['ok'];print(i,len(tri),flush=True)
  before=[r['sourceFace'] for r in old['faces'] if not r['proof']['groundProjectionCovered']];after=[r['sourceFace'] for r in rows if not r['proof']['groundProjectionCovered']]
  summary=dict(originalFaces=208,drawnPatchFaces=len(ground),previousUncovered=before,currentUncovered=after,ordinaryFailures=[r['sourceFace'] for r in rows if not r['proof']['existingOrdinaryClearanceBoundProved']],fourWorldGeometryByteIdentical=True,sourceGeometryChanges=0,terrainChanges=0,fullAcceptance=False,newlyInstalled=0)
  save(DOC/'proofs.json.gz',dict(rows=rows,worldSHA256=digest(tri.tobytes()),groundSHA256=digest(ground.tobytes())));save(DOC/'summary.json',summary)
  refs += [tool,HERE/'exact_literal_dynamic_production_dependency_closure_v1_20261012.mjs']
  for path,h in cap['closure']['inputHashes'].items():assert digest((ROOT/path).read_bytes())==h;refs.append(ROOT/path)
  for x in read(OLD/'result.json')['evidenceRefs']:
   if x['path'].endswith('.py'):assert digest((ROOT/x['path']).read_bytes())==x['sha256'];refs.append(ROOT/x['path'])
  result=module('opus_complete_patch_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-opus-complete-prepared-patch-companion-clearance-v1',refs,dict(uids=['landsd/319559:0','landsd/322573:0'],**summary));print(dict(jobId=result['jobId'],**summary),flush=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
