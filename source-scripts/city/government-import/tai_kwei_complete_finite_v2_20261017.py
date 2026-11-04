"""Complete finite terrain clearance for Tai Kwei and all affected current actors."""
from pathlib import Path
from fractions import Fraction as F
import numpy as np,uuid,time
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
from exact_closed_ground_aabb_pruning_v1_20261011 import CompleteGround
from exact_finite_combined_coverage_cache_v1_draft_20261014 import executor
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';CAP=BASE/'government-xl-tai-kwei-runtime-capture-v1-20261017';BATCH='government-xl-tai-kwei-complete-finite-v2-20261017';DOC=BASE/BATCH;OWN='landsd/106413:0'
def main():
 assert not DOC.exists();r=read(CAP/'result.json');pins={e['path']:e['sha256']for e in r['evidenceRefs']}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 report=read(CAP/'capture-report.json.gz');assert report['strictExteriorUnchanged'];attrs=read(CAP/'attributes.json.gz');inputs={r['uid']:r for r in read(CAP/'attributes-input.json.gz')['rows']};basic=read(CAP/'basic-actors.json.gz');ground={label:np.asarray(read(CAP/(label+'-ground.json.gz'))['completeRelevantDrawnTriplets'],float).reshape(-1,3,3)for label in ['before','after']};selectors={k:CompleteGround(g)for k,g in ground.items()};finite,memo=executor();cache={};summary=[];actors=[];refs=[Path(__file__),CAP/'result.json']+[ROOT/p for p in pins]
 for g in attrs['rows']:
  source=inputs[g['uid']];asset=ROOT/source['path'];assert digest(asset.read_bytes())==g['sourceSHA256'];idx=np.asarray(g['completeOriginalIndex']).reshape(-1,3)
  modes={'original':decode_original_world_triangles(asset.read_bytes()),'literal':np.asarray(g['completeLiteralWorldPosition']).reshape(-1,3)[idx],'leftF32':np.asarray(g['completeExplicitLeftAssociatedFloat32WorldPosition']).reshape(-1,3)[idx],'balancedF32':np.asarray(g['completeExplicitBalancedFloat32WorldPosition']).reshape(-1,3)[idx]};actors.append((g['uid'],modes))
 for g in basic['rows']:
  assert g['identityArithmeticAllThreeExactlyEqual'];t=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];actors.append((g['uid'],{'basicLiteralAndBothF32':t}))
 claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];DOC.mkdir();last_heartbeat=time.monotonic()
 try:
  for uid,modes in actors:
   world_cache={}
   for mode,tri in modes.items():
    sha=digest(tri.tobytes())
    if sha in world_cache:
     previous=world_cache[sha];summary.append({**previous,'mode':mode,'exactWorldReuse':previous['mode']});continue
    details=[];phases=['after']if uid==OWN else ['before','after'];unproved={p:[]for p in phases};uncovered={p:[]for p in phases};introduced=[]
    for i,face in enumerate(tri):
     checks={}
     for phase in phases:
      ids,selection=selectors[phase].select([[F(float(v))for v in p]for p in face]);selected=ground[phase][ids];key=(digest(face.tobytes()),digest(selected.tobytes()))
      if key not in cache:cache[key]=finite(face,selected)
      proof=cache[key];checks[phase]=dict(selection=selection,finite=proof)
      if not proof['ordinaryBoundProved']:unproved[phase].append(i)
      if not proof['projectionCovered']:uncovered[phase].append(i)
     if uid!=OWN and checks['before']['finite']['ordinaryBoundProved']and not checks['after']['finite']['ordinaryBoundProved']:introduced.append(i)
     details.append(dict(face=i,sourceFaceSHA256=digest(face.tobytes()),checks=checks))
     if time.monotonic()-last_heartbeat>=20:
      assert reservations.heartbeat(lease,ttl=3600)['ok'];last_heartbeat=time.monotonic()
    item=dict(uid=uid,mode=mode,worldSHA256=sha,faces=len(tri),unproved=unproved,uncovered=uncovered,introducedUnproved=introduced);summary.append(item);world_cache[sha]=item;save(DOC/(uid.replace('/','-').replace(':','-')+'-'+mode+'.json.gz'),dict(**item,rows=details));print(dict(uid=uid,mode=mode,faces=len(tri),unproved={p:len(v)for p,v in unproved.items()},uncovered={p:len(v)for p,v in uncovered.items()},introduced=len(introduced)),flush=True)
   save(DOC/'progress.json',dict(completedModes=len(summary),rows=summary,complete=False))
  assert reservations.heartbeat(lease,ttl=3600)['ok']
  for s in selectors.values():s.verify_binding()
  for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
  result=dict(rows=summary,ownAllStrict=all(not r['unproved']['after']and not r['uncovered']['after']for r in summary if r['uid']==OWN),neighbourNoIntroducedFailures=all(not r['introducedUnproved']and not r['uncovered']['after']for r in summary if r['uid']!=OWN),actors=len(actors),complete=True,fullAcceptance=False);save(DOC/'summary.json',result)
  refs +=[HERE/n for n in ['exact_closed_ground_aabb_pruning_v1_20261011.py','exact_finite_combined_coverage_cache_v1_draft_20261014.py','exact_finite_coverage_cache_v1_draft_20261014.py','exact_coverage_strict_bounds_cache_v1_draft_20261014.py','exact_packed_world_geometry_20261009.py']]
  out=module('tai_kwei_finite_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'tai-kwei-complete-all-worlds-all-affected-actors-finite-clearance-v2',list(set(refs)),dict(uids=[u for u,_ in actors],**result));print(out['jobId'],flush=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
