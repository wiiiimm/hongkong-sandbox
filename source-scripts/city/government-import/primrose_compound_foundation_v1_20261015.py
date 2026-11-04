"""Check unchanged Primrose originals against corrected terrain and original podium."""
from pathlib import Path
import importlib.util, uuid
import numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,reservations,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-primrose-compound-foundation-v1-20261015'
DOC=BASE/BATCH
CAPTURE=BASE/'government-xl-primrose-actual-render-attributes-v1-20261015'
SOURCE=BASE/'government-xl-primrose-remaining-original-components-v2-20261015'
GROUND=BASE/'government-xl-primrose-join-runtime-capture-v4-20261015'
PODIUM='landsd/74573:0'
def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def main():
 assert not DOC.exists()
 refs={}
 for folder in [CAPTURE,SOURCE,GROUND]:
  receipt=read(folder/'result.json')
  with connect() as db:
   db.execute('SET TRANSACTION READ ONLY')
   assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
  for q in receipt['evidenceRefs']:
   assert q['path'] not in refs or refs[q['path']]==q['sha256']
   refs[q['path']]=q['sha256']
  refs[str((folder/'result.json').relative_to(ROOT))]=digest((folder/'result.json').read_bytes())
 for p,h in refs.items():assert digest((ROOT/p).read_bytes())==h,p
 selection=read(SOURCE/'selection.json.gz')['rows'];captured=read(CAPTURE/'attributes.json.gz')['rows']
 assert {r['uid']for r in selection}=={'landsd/74568:0','landsd/74569:0','landsd/74570:0',PODIUM}
 worlds={'original':{}};paths=[Path(__file__),HERE/'xl-final-script-pass.py',HERE/'exact_packed_world_geometry_20261009.py']+[ROOT/p for p in refs]
 for row in selection:
  p=ROOT/row['candidate']['path'];assert digest(p.read_bytes())==row['sourceSHA256']
  worlds['original'][row['uid']]=decode_original_world_triangles(p.read_bytes());paths.append(p)
 for mode,key in [('literal','completeLiteralWorldPosition'),('left','completeExplicitLeftAssociatedFloat32WorldPosition'),('balanced','completeExplicitBalancedFloat32WorldPosition')]:
  worlds[mode]={r['uid']:np.asarray(r[key],float).reshape(-1,3)[np.asarray(r['completeOriginalIndex']).reshape(-1,3)] for r in captured}
 ground=np.asarray(read(GROUND/'after-ground.json.gz')['completeRelevantDrawnTriplets'],float).reshape(-1,3,3)
 assert len(ground)==2076
 f=module('primrose_existing_foundation',HERE/'xl-final-script-pass.py')
 claim=reservations.claim('primrose-compound-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 rows=[]
 try:
  DOC.mkdir()
  for mode,world in worlds.items():
   for source in selection:
    uid=source['uid'];tri=world[uid];assert len(tri)==source['triangles']
    support=ground if uid==PODIUM else np.concatenate([ground,world[PODIUM]])
    b=source['source']['building'];poly=Polygon(b['rings'][0],b['rings'][1:])
    foundation=f.foundation_context(tri,support,poly)
    strict=foundation['completeTerrainTriangles']==len(tri) and not foundation['fullyBuriedUpwardTriangles'] and foundation['fullyBuriedAreaFraction']==0
    row=dict(uid=uid,mode=mode,worldSHA256=digest(tri.tobytes()),supportSHA256=digest(support.tobytes()),foundation=foundation,strictFoundationAccepted=strict)
    rows.append(row);save(DOC/(uid.replace('/','-').replace(':','-')+'-'+mode+'.json'),row)
    assert reservations.heartbeat(lease)['ok']
    print(uid,mode,'accepted',strict,'buried',foundation['fullyBuriedTriangles'],'upward',foundation['fullyBuriedUpwardTriangles'],flush=True)
  for p,h in refs.items():assert digest((ROOT/p).read_bytes())==h,p
  save(DOC/'summary.json',dict(rows=rows,allStrictPass=all(r['strictFoundationAccepted']for r in rows),fullAcceptance=False))
  module('primrose_compound_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-original-compound-foundation-four-representations-v1',paths,dict(uids=[r['uid']for r in selection],rows=rows,fullAcceptance=False))
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
