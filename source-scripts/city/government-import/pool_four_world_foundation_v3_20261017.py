"""Complete pool foundation checks in original, literal and both Float32 worlds."""
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-sham-shui-po-pool-four-world-foundation-v3-20261017';DOC=BASE/BATCH

def main():
 assert not DOC.exists();refs=[Path(__file__),HERE/'exact_packed_world_geometry_20261009.py'];pins={}
 names=['government-xl-sham-shui-po-pool-original-group-v1-20261016','government-xl-sham-shui-po-pool-actual-render-attributes-v1-20261017','government-xl-sham-shui-po-pool-basic-ground-capture-v4-20261017']
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  for name in names:
   p=BASE/name/'result.json';r=read(p);assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(p)
   for q in r['evidenceRefs']:
    assert q['path'] not in pins or pins[q['path']]==q['sha256'];pins[q['path']]=q['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 selection=read(BASE/names[0]/'selection.json.gz')['rows'];captured=read(BASE/names[1]/'attributes.json.gz')['rows'];worlds={'original':{r['uid']:decode_original_world_triangles((ROOT/r['candidate']['path']).read_bytes()) for r in selection}}
 for mode,key in [('literal','completeLiteralWorldPosition'),('left','completeExplicitLeftAssociatedFloat32WorldPosition'),('balanced','completeExplicitBalancedFloat32WorldPosition')]:worlds[mode]={r['uid']:np.asarray(r[key]).reshape(-1,3)[np.asarray(r['completeOriginalIndex']).reshape(-1,3)] for r in captured}
 gpath=BASE/names[2]/'after-ground.json.gz';ground=np.asarray(read(gpath)['completeRelevantDrawnTriplets']).reshape(-1,3,3);f=module('pool_four_foundation',HERE/'xl-final-script-pass.py');rows=[];DOC.mkdir()
 for mode,world in worlds.items():
  for source in selection:
   uid=source['uid'];t=world[uid];assert len(t)==source['triangles'];support=ground if uid=='landsd/265480:0' else np.concatenate([ground,world['landsd/265480:0']]);b=source['source']['building'];proof=f.foundation_context(t,support,Polygon(b['rings'][0],b['rings'][1:]))
   rows.append(dict(uid=uid,mode=mode,foundation=proof,strictFoundationAccepted=proof['completeTerrainTriangles']==len(t) and not proof['fullyBuriedUpwardTriangles'] and proof['fullyBuriedAreaFraction']==0));print(mode,uid,rows[-1]['strictFoundationAccepted'],flush=True)
 save(DOC/'summary.json',dict(rows=rows,allStrictPass=all(r['strictFoundationAccepted'] for r in rows),fullAcceptance=False));save(DOC/'world-triangles.json.gz',{mode:{uid:t.tolist() for uid,t in world.items()} for mode,world in worlds.items()});refs += [gpath,HERE/'xl-final-script-pass.py']
 out=module('pool_four_foundation_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-pool-complete-four-world-foundation-v1',list(dict.fromkeys(refs)),dict(uids=[r['uid'] for r in selection],rows=rows,fullAcceptance=False,newlyInstalled=0));print(dict(jobId=out['jobId'],allStrictPass=all(r['strictFoundationAccepted'] for r in rows)),flush=True)
if __name__=='__main__':main()
