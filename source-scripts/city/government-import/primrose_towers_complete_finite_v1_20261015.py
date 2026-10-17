"""Complete original tower clearance against corrected ground and original podium."""
from pathlib import Path
from fractions import Fraction as F
import uuid,numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import BASE,CAPTURE,SOURCE,GROUND,PODIUM,module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_closed_ground_aabb_pruning_v1_20261011 import CompleteGround
from exact_finite_combined_coverage_cache_v1_draft_20261014 import executor
BATCH='government-xl-primrose-towers-complete-finite-v1-20261015';DOC=BASE/BATCH

def main():
 assert not DOC.exists();refs={}
 for folder in [CAPTURE,GROUND,SOURCE,BASE/'government-xl-primrose-compound-foundation-v2-20261015']:
  r=read(folder/'result.json')
  with connect()as db:
   db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  for q in r['evidenceRefs']:
   assert q['path']not in refs or refs[q['path']]==q['sha256'];refs[q['path']]=q['sha256']
  refs[str((folder/'result.json').relative_to(ROOT))]=digest((folder/'result.json').read_bytes())
 for p,h in refs.items():assert digest((ROOT/p).read_bytes())==h,p
 sources=read(SOURCE/'selection.json.gz')['rows'];captured=read(CAPTURE/'attributes.json.gz')['rows'];worlds={'original':{}}
 for r in sources:
  raw=(ROOT/r['candidate']['path']).read_bytes();assert digest(raw)==r['sourceSHA256'];worlds['original'][r['uid']]=decode_original_world_triangles(raw)
 for mode,key in [('literal','completeLiteralWorldPosition'),('left','completeExplicitLeftAssociatedFloat32WorldPosition'),('balanced','completeExplicitBalancedFloat32WorldPosition')]:worlds[mode]={r['uid']:np.asarray(r[key],float).reshape(-1,3)[np.asarray(r['completeOriginalIndex']).reshape(-1,3)]for r in captured}
 ground=np.asarray(read(GROUND/'after-ground.json.gz')['completeRelevantDrawnTriplets'],float).reshape(-1,3,3)
 claim=reservations.claim('primrose-full-tower-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];summaries=[];completed={}
 try:
  DOC.mkdir()
  for mode,world in worlds.items():
   support=np.concatenate([ground,world[PODIUM]]);supportsha=digest(support.tobytes());selector=CompleteGround(support);finite,memo=executor()
   for source in sources:
    uid=source['uid']
    if uid==PODIUM:continue
    tri=world[uid];assert len(tri)==source['triangles'];key=(uid,digest(tri.tobytes()),supportsha)
    if key in completed:
     prior=completed[key];summaries.append({**prior,'mode':mode,'reusedExactWorldAndSupportFromMode':prior['mode']});continue
    item=dict(uid=uid,mode=mode,completeFaces=len(tri),worldSHA256=key[1],supportSHA256=supportsha,chunks=[],unproved=[],uncovered=[]);chunk=[]
    for i,face in enumerate(tri):
     ids,selection=selector.select([[F(float(v))for v in p]for p in face]);proof=finite(face,support[ids]);chunk.append(dict(sourceFace=i,sourceFaceSHA256=digest(face.tobytes()),completeSupportSelection=selection,finite=proof))
     if not proof['ordinaryBoundProved']:item['unproved'].append(i)
     if not proof['projectionCovered']:item['uncovered'].append(i)
     if (i+1)%128==0 or i+1==len(tri):
      name=uid.replace('/','-').replace(':','-')+'-'+mode+'-'+str(i+1)+'.json.gz';save(DOC/name,dict(uid=uid,mode=mode,worldSHA256=key[1],supportSHA256=supportsha,rows=chunk));item['chunks'].append(dict(path=str((DOC/name).relative_to(ROOT)),sha256=digest((DOC/name).read_bytes())));chunk=[]
      assert reservations.heartbeat(lease)['ok'];print(uid,mode,i+1,len(tri),flush=True)
    completed[key]=item;summaries.append(item);save(DOC/(uid.replace('/','-').replace(':','-')+'-'+mode+'-summary.json'),item)
   selector.verify_binding()
  for p,h in refs.items():assert digest((ROOT/p).read_bytes())==h,p
  save(DOC/'summary.json',dict(rows=summaries,fullAcceptance=False))
  paths=[ROOT/p for p in refs]+[Path(__file__)]+[HERE/n for n in ['primrose_compound_foundation_v2_20261015.py','exact_closed_ground_aabb_pruning_v1_20261011.py','exact_finite_combined_coverage_cache_v1_draft_20261014.py','exact_finite_coverage_cache_v1_draft_20261014.py','exact_coverage_strict_bounds_cache_v1_draft_20261014.py']]
  module('towers_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-three-original-towers-four-world-compound-clearance-v1',paths,dict(uids=[r['uid']for r in sources],rows=summaries,fullAcceptance=False))
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
