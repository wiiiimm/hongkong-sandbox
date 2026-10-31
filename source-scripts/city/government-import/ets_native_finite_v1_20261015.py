"""Full affected native source before/after; exact unchanged ground reuse."""
from pathlib import Path
from fractions import Fraction as F
import uuid,numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
from exact_closed_ground_aabb_pruning_v1_20261011 import CompleteGround
from exact_finite_combined_coverage_cache_v1_draft_20261014 import executor
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-ets-native-finite-v1-20261015';DOC=BASE/BATCH
CAP=BASE/'government-xl-ets-native-ground-capture-v1-20261015';ATTR=BASE/'government-xl-ets-current-native-attributes-v1-20261015'
def main():
 assert not DOC.exists();pins={};refs=[Path(__file__)]
 for folder in [CAP,ATTR]:
  r=read(folder/'result.json');refs.append(folder/'result.json')
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  for q in r['evidenceRefs']:
   assert q['path']not in pins or pins[q['path']]==q['sha256'];pins[q['path']]=q['sha256']
 for path,h in pins.items():assert digest((ROOT/path).read_bytes())==h;refs.append(ROOT/path)
 report=read(CAP/'capture-report.json.gz');assert report['strictExteriorUnchanged']
 a=next(r for r in read(ATTR/'attributes.json.gz')['rows']if r['uid']=='landsd/159863:0');inp=next(r for r in read(ATTR/'input.json.gz')['rows']if r['uid']==a['uid']);raw=(ROOT/inp['path']).read_bytes();assert digest(raw)==a['sourceSHA256']
 ix=np.asarray(a['completeOriginalIndex']).reshape(-1,3);worlds={'original':decode_original_world_triangles(raw)}
 for mode,key in [('literal','completeLiteralWorldPosition'),('leftF32','completeExplicitLeftAssociatedFloat32WorldPosition'),('balancedF32','completeExplicitBalancedFloat32WorldPosition')]:worlds[mode]=np.asarray(a[key]).reshape(-1,3)[ix]
 grounds=[np.asarray(read(CAP/(label+'-ground.json.gz'))['completeRelevantDrawnTriplets'],float).reshape(-1,3,3)for label in ['before','after']];selectors=[CompleteGround(g)for g in grounds];finite,memo=executor();cache={};worldcache={};summary=[]
 claim=reservations.claim('ets-native-finite-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  DOC.mkdir()
  for mode,tri in worlds.items():
   assert len(tri)==32225;wh=digest(tri.astype('<f8').tobytes())
   if wh in worldcache:summary.append({**worldcache[wh],'mode':mode,'exactWholeWorldReuse':True});continue
   rows=[];introduced=[];coverage=[];same=0
   for i,face in enumerate(tri):
    selected=[];selections=[]
    for ground,selector in zip(grounds,selectors):
     ids,selection=selector.select([[F(float(v))for v in p]for p in face]);selected.append(ground[ids]);selections.append(selection)
    if np.array_equal(selected[0],selected[1]):
     same+=1;rows.append({'sourceFace':i,'sourceFaceSHA256':digest(face.tobytes()),'exactUnchangedGroundSHA256':digest(selected[0].tobytes()),'completeSelections':selections})
    else:
     findings=[]
     for g in selected:
      key=(digest(face.tobytes()),digest(g.tobytes()))
      if key not in cache:cache[key]=finite(face,g)
      findings.append(cache[key])
     rows.append({'sourceFace':i,'sourceFaceSHA256':digest(face.tobytes()),'completeSelections':selections,'before':findings[0],'after':findings[1]})
     if findings[0]['ordinaryBoundProved']and not findings[1]['ordinaryBoundProved']:introduced.append(i)
     if findings[0]['projectionCovered']and not findings[1]['projectionCovered']:coverage.append(i)
    if i%1000==0:assert reservations.heartbeat(lease)['ok'];print(mode,i,'unchanged',same,'regressions',len(introduced),flush=True)
   s={'mode':mode,'completeFaces':len(tri),'exactUnchangedGroundFaces':same,'introducedUnproved':introduced,'introducedUncovered':coverage,'fullAcceptance':False};summary.append(s);worldcache[wh]=s;save(DOC/(mode+'-faces.json.gz'),{'worldSHA256':wh,'rows':rows})
  for selector in selectors:selector.verify_binding()
  for path,h in pins.items():assert digest((ROOT/path).read_bytes())==h
  save(DOC/'summary.json',{'uid':a['uid'],'rows':summary,'noIntroducedFailures':all(not r['introducedUnproved']and not r['introducedUncovered']for r in summary),'fullAcceptance':False,'newlyInstalled':0})
  refs.extend(HERE/n for n in ['exact_closed_ground_aabb_pruning_v1_20261011.py','exact_finite_combined_coverage_cache_v1_draft_20261014.py','exact_finite_coverage_cache_v1_draft_20261014.py','exact_coverage_strict_bounds_cache_v1_draft_20261014.py','exact_packed_world_geometry_20261009.py'])
  r=module('ets_native_finite_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-K11-four-world-before-after-ground-regression',refs,{'uids':[a['uid']],'rows':summary,'fullAcceptance':False,'newlyInstalled':0});print('Neon verified',r['jobId'],flush=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
