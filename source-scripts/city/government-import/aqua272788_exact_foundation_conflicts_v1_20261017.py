"""Trace every failed canonical foundation face against unchanged original support."""
from pathlib import Path
import uuid,numpy as np,shapely
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
from exact_original_paired_finite_clearance_v3_20261011 import verify
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-aqua272788-exact-foundation-conflicts-v1-20261017';DOC=BASE/BATCH
PAIR=BASE/'government-xl-aqua272788-current-pair-v1-20261017';PHYSICAL=BASE/'government-xl-aqua272788-current-physical-v2-20261017'
T='landsd/272788:0';P='landsd/193086:0'
def main():
 assert not DOC.exists();pins={};refs=[Path(__file__)]
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for d in [PAIR,PHYSICAL]:
   r=read(d/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(d/'result.json')
   for q in r['evidenceRefs']:pins.setdefault(q['path'],set()).add(q['sha256'])
 def consume(p):
  assert digest(p.read_bytes())in pins[str(p.relative_to(ROOT))];refs.append(p);return read(p)
 g={r['uid']:r for r in consume(HERE/'local'/PAIR.name/'runtime-geometry.json.gz')['rows']};tri={u:np.asarray(r['position'],float).reshape(-1,3)[np.asarray(r['index']).reshape(-1,3)]for u,r in g.items()};ground=np.asarray(g[T]['drawnGroundGeometry'],float).reshape(-1,3,3);combined=np.concatenate([ground,tri[P]])
 claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  final=module('aqua_exact_foundation',HERE/'xl-final-script-pass.py');native=combined;polys=shapely.polygons(native[:,:,[0,2]]);valid=shapely.area(polys)>1e-10
  points=np.concatenate([tri[T],tri[T].mean(axis=1)[:,None,:]],axis=1);heights=final.s.context.shared.samples(points[:,:,[0,2]].reshape(-1,2),native[valid],shapely.STRtree(polys[valid])).reshape(-1,4);gaps=points[:,:,1]-heights;failed=np.flatnonzero(np.isfinite(heights).all(axis=1)&(gaps<-.5).all(axis=1));expected=consume(PHYSICAL/'foundation.json')['rows'][0]['foundation'];assert len(failed)==expected['fullyBuriedTriangles']==2
  rows=[]
  for i in failed:
   t=tri[T][i];lo,hi=t[:,[0,2]].min(0),t[:,[0,2]].max(0);sxz=tri[P][:,:,[0,2]];ids=np.flatnonzero((sxz.max(1)>=lo).all(1)&(sxz.min(1)<=hi).all(1));proof=verify(t,combined)
   rows.append(dict(sourceFace=int(i),sourceFaceSHA256=digest(t.tobytes()),originalWorldTriangle=t.tolist(),sampledGaps=gaps[i].tolist(),podiumBoundingCandidateFaceIds=ids.tolist(),exactProof=proof));assert reservations.heartbeat(lease)['ok'];print(dict(face=int(i),strictClearanceProved=proof['existingOrdinaryClearanceBoundProved'],coverage=proof['groundProjectionCovered']),flush=True)
  save(DOC/'conflicts.json.gz',dict(uid=T,supportUid=P,completeSourceFaces=len(tri[T]),completePodiumFaces=len(tri[P]),allCanonicalFailedFaces=failed.tolist(),rows=rows,wholeModelAccepted=False,sourceGeometryChanges=0))
  for u,r in g.items():
   for p,h in r.get('inputHashes',{}).items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
  for p,hs in pins.items():
   if p.startswith('3d-viewer/'):
    assert digest((ROOT/p).read_bytes())in hs;refs.append(ROOT/p)
  refs.extend(HERE/n for n in ['xl-final-script-pass.py','exact_original_paired_finite_clearance_v3_20261011.py','exact_original_paired_finite_clearance_v2_20261010.py','exact_original_projection_coverage_v2_20261010.py','exact_original_closed_projection_intersection_20261010.py'])
  result=module('aqua_conflict_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-current-original-compound-foundation-conflicts-v1',list(dict.fromkeys(refs)),dict(uids=[T],failedFoundationFaces=failed.tolist(),exactConflictCount=sum(not r['exactProof']['existingOrdinaryClearanceBoundProved']for r in rows),requiresHumanDecision=False,requiresAIGeometry=False,nextStep='Inspect the recorded exact tower/podium face intersections; retain hold until canonical whole-source foundation passes.'))
  print(dict(jobId=result['jobId']),flush=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
