"""Rebind exact complete current CITIC clearance, refining conservative negatives."""
from pathlib import Path
import numpy as np,uuid
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_paired_finite_clearance_v3_20261011 import verify
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-citic-current-finite-v1-20261017';DOC=BASE/BATCH;CURRENT=BASE/'government-xl-citic-current-pair-v1-20261017';OLD=BASE/'xl-terrain-recovery-20261010-citic-current-original-literal-complete-finite-v1'
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for d in [CURRENT,OLD]:
   r=read(d/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(d/'result.json')
   for q in r['evidenceRefs']:pins.setdefault(q['path'],set()).add(q['sha256'])
 def consume(p):
  assert digest(p.read_bytes())in pins[str(p.relative_to(ROOT))];refs.append(p);return read(p)
 prior={r['uid']:r for r in consume(OLD/'diagnostic.json.gz')['rows']};geo=consume(HERE/'local'/CURRENT.name/'runtime-geometry.json.gz');rows=consume(CURRENT/'selection.json.gz')['rows'];selection={r['uid']:r for r in rows};summary=[];details=[]
 claim=reservations.claim('citic-current-finite-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  DOC.mkdir()
  for g in geo['rows']:
   uid=g['uid'];old=prior[uid];r=selection[uid];asset=ROOT/r['candidate']['path'];assert digest(asset.read_bytes())==r['sourceSHA256']==old['sourceSHA256'];refs.append(asset)
   worlds=dict(completeOriginal=decode_original_world_triangles(asset.read_bytes()),actualRendered=np.asarray(g['position'],float).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)]);ground=np.asarray(g['drawnGroundGeometry'],float).reshape(-1,3,3)
   for mode,tri in worlds.items():
    worldkey='completeOriginalWorldSHA256'if mode=='completeOriginal'else'completeActualRenderedWorldSHA256';same=digest(tri.tobytes())==old[worldkey]and digest(ground.tobytes())==old['completeGroundSHA256'];unproved=[];uncovered=[];refined=[];reused=0
    assert len(tri)==old['completeOriginalFaces']==len(old['allFaces'])
    for i,t in enumerate(tri):
     priorproof=old['allFaces'][i][mode]
     if same and priorproof['groundProjectionCovered']and priorproof['existingOrdinaryClearanceBoundProved']:
      assert priorproof['sourceFaceSHA256']==digest(t.tobytes());reused+=1;continue
     proof=verify(t,ground);refined.append(dict(face=i,proof=proof))
     if not proof['existingOrdinaryClearanceBoundProved']:unproved.append(i)
     if not proof['groundProjectionCovered']:uncovered.append(i)
     if len(refined)%25==0:assert reservations.heartbeat(lease)['ok']
    summary.append(dict(uid=uid,mode=mode,faces=len(tri),exactHistoricalSourceAndGroundEqual=same,reusedStrictFaces=reused,freshFiniteFaces=len(refined),unproved=unproved,uncovered=uncovered));details.append(dict(uid=uid,mode=mode,worldSHA256=digest(tri.tobytes()),groundSHA256=digest(ground.tobytes()),refined=refined));print(summary[-1],flush=True)
  save(DOC/'proofs.json.gz',dict(rows=details));save(DOC/'summary.json',dict(rows=summary,allFacesCovered=all(not r['uncovered']for r in summary),allStrict=all(not r['unproved']for r in summary),sourceGeometryChanges=0,fullAcceptance=False))
  for p,h in geo['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
  refs.extend(HERE/n for n in ['exact_original_paired_finite_clearance_v3_20261011.py','exact_original_paired_finite_clearance_v2_20261010.py','exact_original_projection_coverage_v2_20261010.py','exact_original_closed_projection_intersection_20261010.py','exact_packed_world_geometry_20261009.py'])
  result=module('citic_current_finite_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'current-complete-citic-original-and-rendered-finite-clearance-v1',list(dict.fromkeys(refs)),dict(uids=list(selection),rows=summary,fullAcceptance=False,newlyInstalled=0));print(dict(jobId=result['jobId']),flush=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
