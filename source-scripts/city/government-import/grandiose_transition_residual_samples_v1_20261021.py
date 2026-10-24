"""Attribute all remaining terrain depth failures after the private boundary transition."""
from pathlib import Path
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';PRIOR=BASE/'government-xl-grandiose-terrain-boundary-transition-v2-20261021';BATCH='government-xl-grandiose-transition-residual-samples-v1-20261021';DOC=BASE/BATCH
assert not DOC.exists();r=read(PRIOR/'result.json');refs=[Path(__file__),PRIOR/'result.json'];pins={e['path']:e['sha256']for e in r['evidenceRefs']}
with connect() as db:
 db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
def take(p):
 assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p);return read(p)
row=take(BASE/'government-xl-grandiose-podium-current-terrain-v1-20261021/selection.json.gz')['rows'][0];asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256'];refs.append(asset);t=decode_original_world_triangles(asset.read_bytes())
g=np.asarray(take(HERE/'local'/PRIOR.name/'private-terrain.json.gz')['triangles']);p=shapely.polygons(g[:,:,[0,2]]);valid=shapely.area(p)>1e-10;g,p=g[valid],p[valid];points=np.concatenate([t,t.mean(1)[:,None,:]],1);m=module('transition_residual',HERE/'xl-final-script-pass.py');h=m.s.context.shared.samples(points[:,:,[0,2]].reshape(-1,2),g,shapely.STRtree(p)).reshape(-1,4);gap=points[:,:,1]-h
assert np.isfinite(h).all();rows=[dict(faceIndex=int(i),sampleIndex=int(j),position=points[i,j].tolist(),gapM=float(gap[i,j]),vertices=t[i].tolist())for i,j in np.argwhere(gap<-.5)]
save(DOC/'samples.json.gz',dict(rows=rows,sourceSHA256=row['sourceSHA256'],installationApproved=False))
summary=dict(uids=[row['uid']],completeSourceFaces=len(t),failedSamples=len(rows),failedFaces=len({r['faceIndex']for r in rows}),minimumGapM=float(gap.min()),installationApproved=False,newlyInstalled=0)
save(DOC/'summary.json',summary);refs.extend(HERE/n for n in ['xl-final-script-pass.py','exact_packed_world_geometry_20261009.py'])
module('transition_residual_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-source-private-terrain-residual-attribution',refs,summary);print(summary)
