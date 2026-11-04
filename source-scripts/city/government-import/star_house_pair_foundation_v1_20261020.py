"""Complete literal Star House pair foundations; diagnostic, not acceptance."""
from pathlib import Path
import numpy as np,shapely
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';PRIOR=BASE/'government-xl-star-parkview-support-v1-20261020';BATCH='government-xl-star-house-pair-foundation-v1-20261020';DOC=BASE/BATCH
assert not DOC.exists()
receipt=read(PRIOR/'result.json')
with connect() as c:
 c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
pins={e['path']:e['sha256'] for e in receipt['evidenceRefs']}
def verified(p):
 assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))],p
 return read(p)
rows=verified(PRIOR/'selection.json.gz')['rows'];geometry=verified(HERE/'local'/PRIOR.name/'runtime-geometry.json.gz')['rows'];uids=['landsd/231484:0','landsd/33396:0'];g={r['uid']:r for r in geometry if r['uid'] in uids}
world={u:np.asarray(r['position']).reshape(-1,3)[np.asarray(r['index']).reshape(-1,3)] for u,r in g.items()}
final=module('star_pair_foundation',HERE/'xl-final-script-pass.py');out=[]
for u in uids:
 r=next(r for r in rows if r['uid']==u);tri=world[u];ground=np.asarray(g[u]['drawnGroundGeometry']).reshape(-1,3,3);support=ground if u==uids[0] else np.concatenate([ground,world[uids[0]]]);b=r['source']['building'];f=final.foundation_context(tri,support,Polygon(b['rings'][0],b['rings'][1:]));buried=[]
 if f['fullyBuriedTriangles']:
  polys=shapely.polygons(support[:,:,[0,2]]);valid=shapely.area(polys)>1e-10;native,polys=support[valid],polys[valid];points=np.concatenate([tri,tri.mean(1)[:,None,:]],axis=1);heights=final.s.context.shared.samples(points[:,:,[0,2]].reshape(-1,2),native,shapely.STRtree(polys)).reshape(-1,4);gaps=points[:,:,1]-heights;ids=np.flatnonzero(np.isfinite(heights).all(1)&(gaps<-.5).all(1));assert len(ids)==f['fullyBuriedTriangles'];buried=[dict(faceId=int(i),vertices=tri[i].tolist(),gaps=gaps[i].tolist())for i in ids]
 evidence=dict(uid=u,sourceSHA256=r['sourceSHA256'],foundation=f,buriedFaces=buried,installationApproved=False);save(DOC/(u.split('/')[1]+'.json'),evidence);summary=dict(uid=u,triangles=len(tri),covered=f['completeTerrainTriangles'],buried=f['fullyBuriedTriangles'],buriedAreaFraction=f['fullyBuriedAreaFraction']);out.append(summary);print(summary,flush=True)
refs=[Path(__file__),PRIOR/'result.json',PRIOR/'selection.json.gz',HERE/'local'/PRIOR.name/'runtime-geometry.json.gz',HERE/'xl-final-script-pass.py']
for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
module('star_pair_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-literal-original-pair-foundations',refs,dict(uids=uids,rows=out,installationApproved=False,modelGeometryChanges=0))
