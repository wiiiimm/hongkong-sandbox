"""Complete 13-neighbour finite comparison on captured actual terrain."""
from pathlib import Path
from fractions import Fraction as F
import importlib.util,uuid
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_closed_ground_aabb_pruning_v1_20261011 import CompleteGround
from exact_finite_combined_coverage_cache_v1_draft_20261014 import executor
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-stanford-basic-finite-v1-20261015';DOC=BASE/BATCH;CAPTURE=BASE/'government-xl-stanford-basic-ground-capture-v1-20261015'
def main():
 assert not DOC.exists();receipt=read(CAPTURE/'result.json')
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for q in receipt['evidenceRefs']:assert digest((ROOT/q['path']).read_bytes())==q['sha256']
 original_capture=BASE/'government-xl-stanford-basic-ground-capture-v1-20261015';actors=read(original_capture/'basic-actors.json.gz');report=read(CAPTURE/'capture-report.json.gz');assert len(actors['rows'])==13 and report['strictExteriorUnchanged'];grounds=[np.asarray(read((original_capture if label=='before'else CAPTURE)/(label+'-ground.json.gz'))['completeRelevantDrawnTriplets'],float).reshape(-1,3,3)for label in ['before','after']];selectors=[CompleteGround(g)for g in grounds];finite,memo=executor();cache={}
 claim=reservations.claim('primrose-join-basic-finite-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];summary=[]
 try:
  DOC.mkdir()
  for actor in actors['rows']:
   assert actor['identityArithmeticAllThreeExactlyEqual'];tri=np.asarray(actor['position'],float).reshape(-1,3)[np.asarray(actor['index']).reshape(-1,3)];rows=[]
   for i,face in enumerate(tri):
    findings=[]
    for ground,selector in zip(grounds,selectors):
     ids,selection=selector.select([[F(float(v))for v in p]for p in face]);key=(digest(face.tobytes()),digest(ground[ids].tobytes()))
     if key not in cache:cache[key]=finite(face,ground[ids])
     findings.append(dict(completeGroundSelection=selection,finite=cache[key]))
    rows.append(dict(sourceFace=i,sourceFaceSHA256=digest(face.tobytes()),before=findings[0],after=findings[1]))
    if i%32==0:assert reservations.heartbeat(lease)['ok']
   output=DOC/(actor['uid'].replace('/','-').replace(':','-')+'.json.gz');save(output,dict(uid=actor['uid'],worldSHA256=digest(tri.tobytes()),completeFaces=len(tri),modes=['actualLiteral','explicitLeftF32','explicitBalancedF32'],modeReuseExactCompletePositionEquality=True,rows=rows))
   item=dict(uid=actor['uid'],completeFaces=len(tri),beforeUnproved=[r['sourceFace']for r in rows if not r['before']['finite']['ordinaryBoundProved']],afterUnproved=[r['sourceFace']for r in rows if not r['after']['finite']['ordinaryBoundProved']],introducedUnproved=[r['sourceFace']for r in rows if r['before']['finite']['ordinaryBoundProved']and not r['after']['finite']['ordinaryBoundProved']],afterUncovered=[r['sourceFace']for r in rows if not r['after']['finite']['projectionCovered']]);summary.append(item);print({k:v for k,v in item.items()if k not in ['beforeUnproved','afterUnproved']},flush=True)
  for s in selectors:s.verify_binding()
  for q in receipt['evidenceRefs']:assert digest((ROOT/q['path']).read_bytes())==q['sha256']
  save(DOC/'summary.json',dict(rows=summary,all13ActorsComplete=True,modeCount=3,allOriginalNegativesPreserved=True,noIntroducedFailures=all(not r['introducedUnproved']and not r['afterUncovered']for r in summary),installationApproved=False))
  paths=[Path(__file__),CAPTURE/'result.json']+[ROOT/q['path']for q in receipt['evidenceRefs']]+[HERE/n for n in ['exact_closed_ground_aabb_pruning_v1_20261011.py','exact_finite_combined_coverage_cache_v1_draft_20261014.py','exact_finite_coverage_cache_v1_draft_20261014.py','exact_coverage_strict_bounds_cache_v1_draft_20261014.py']]
  spec=importlib.util.spec_from_file_location('primrose-join_basic_finite_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.freeze(BATCH,'13-complete-current-basic-before-after-finite-v1',paths,dict(uids=[r['uid']for r in summary],rows=summary,fullAcceptance=False))
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
