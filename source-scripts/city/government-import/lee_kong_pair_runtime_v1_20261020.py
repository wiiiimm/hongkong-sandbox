"""Fresh paired original identity/runtime diagnostics, no admission or source edits."""
from pathlib import Path
import subprocess,sys,uuid,json
import numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_georef_cell_identity_20261009 import verify_files
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-lee-kong-pair-runtime-v1-20261020';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
UIDS=['landsd/72296:0','landsd/253697:0']
def owned():
 assert reservations.owns(read(LOCAL/'reservation.json'));assert not DOC.exists();pins={};refs=[Path(__file__)]
 old=BASE/'government-xl-lee-kong-pair-support-v2-20261020';r=read(old/'result.json')
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 pins={e['path']:e['sha256'] for e in r['evidenceRefs']};refs.append(old/'result.json')
 def pin(p):
  assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))],p
  refs.append(p)
 sel=BASE/'government-xl-lee-kong-four-original-source-recovery-v1-20261011/selection.json.gz';pin(sel)
 rows=[x for x in read(sel)['rows'] if x['uid'] in UIDS];assert len(rows)==2
 manifest=ROOT/'3d-viewer/city/data/manifest.json';fresh={str(manifest.relative_to(ROOT)):digest(manifest.read_bytes())}
 final=module('lee_pair_context',HERE/'xl-final-script-pass.py');identities=[]
 for row in rows:
  uid=row['uid'];key=uid.split('/')[1];asset=ROOT/row['candidate']['path'];pin(asset);row['triangles']=row['native']['model']['triangles']
  tile=ROOT/'3d-viewer'/row['source']['tile'];current=next(b for b in read(tile)['buildings'] if b['uid']==uid);assert current==row['source']['building'];fresh[str(tile.relative_to(ROOT))]=digest(tile.read_bytes())
  tri=decode_original_world_triangles(asset.read_bytes());lo,hi=tri.min((0,1)),tri.max((0,1));near=final.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2]);tiles={t:digest((ROOT/'3d-viewer'/t).read_bytes()) for _,_,t in near}
  context=dict(sourceSHA256=row['sourceSHA256'],identity=final.identity_context(row,tri,near),neighbourTileHashes=tiles);save(DOC/key/'context.json',context);proof=verify_files(row,context,LOCAL/key);save(DOC/key/'identity.json',proof);identities.append(dict(uid=uid,passed=proof['passed'],reasons=proof['reasons']))
  for t,h in tiles.items():fresh[str((ROOT/'3d-viewer'/t).relative_to(ROOT))]=h
  entry=row['candidate']['entry'];entry.update(placementReviewed=False,publicationApproved=False);dest=LOCAL/entry['asset'];dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(asset.read_bytes());row['candidate']['path']=str(dest.relative_to(ROOT));refs.append(dest)
 prior=BASE/'government-xl-lee-kong72296-candidate-runtime-v1-20261020';pr=read(prior/'result.json')
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(pr['jobId'],)).fetchone()==('complete',pr)
 for e in pr['evidenceRefs']:
  assert digest((ROOT/e['path']).read_bytes())==e['sha256'];fresh[e['path']]=e['sha256']
 refs.append(prior/'result.json');terrain=read(prior/'terrain-candidates.json');terrain[0]['uids']=UIDS;save(DOC/'terrain-candidates.json',terrain)
 save(DOC/'selection.json.gz',dict(rows=rows,manifestSHA256=fresh[str(manifest.relative_to(ROOT))]))
 cmd=['node',str(HERE/'acceptance-metrics-multi-retained.mjs'),'--selection',str((DOC/'selection.json.gz').relative_to(ROOT)),'--candidates',str(LOCAL.relative_to(ROOT)),'--terrain-candidates',str((DOC/'terrain-candidates.json').relative_to(ROOT)),'--out',str((DOC/'metrics.json').relative_to(ROOT)),'--geometry-out',str((LOCAL/'runtime-geometry.json.gz').relative_to(ROOT))]
 with (DOC/'worker.log').open('w') as log:subprocess.run(cmd,cwd=ROOT,check=True,stdout=log,stderr=subprocess.STDOUT)
 metrics=read(DOC/'metrics.json');assert all(not x.get('error') for x in metrics['rows']),metrics['rows']
 geometry={x['uid']:x for x in read(LOCAL/'runtime-geometry.json.gz')['rows']};world={u:np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)] for u,g in geometry.items()};foundations=[]
 for row in rows:
  u=row['uid'];ground=np.asarray(geometry[u]['drawnGroundGeometry']).reshape(-1,3,3);support=ground if u==UIDS[0] else np.concatenate([ground,world[UIDS[0]]]);b=row['source']['building'];f=final.foundation_context(world[u],support,Polygon(b['rings'][0],b['rings'][1:]));foundations.append(dict(uid=u,foundation=f))
 save(DOC/'summary.json',dict(identities=identities,foundations=foundations,installationApproved=False))
 for p,h in {**fresh,**metrics['inputHashes']}.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 refs.extend([HERE/'acceptance-metrics-multi-retained.mjs',HERE/'xl-final-script-pass.py',HERE/'exact_original_georef_cell_identity_20261009.py',LOCAL/'runtime-geometry.json.gz'])
 module('lee_pair_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'fresh-original-pair-identity-runtime-foundations',list(dict.fromkeys(refs)),dict(uids=UIDS,identities=identities,foundations=foundations,installationApproved=False))
def main():
 if '--owned' in sys.argv:return owned()
 assert not DOC.exists();claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['building:'+u for u in UIDS],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];p=LOCAL/'reservation.json';save(p,json.loads(json.dumps(lease,default=str)))
 try:subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(p),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
