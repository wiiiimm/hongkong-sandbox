"""Exact original companion extent/coverage diagnostics; no acceptance or geometry edits."""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from shapely.geometry import Polygon
import shapely
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';SRC=BASE/'government-xl-next-five-original-identity-v1-20261018';BATCH='government-xl-next-five-original-extent-context-v1-20261018';DOC=BASE/BATCH

def main():
 assert not DOC.exists()
 receipt=read(SRC/'result.json')
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 refs=[Path(__file__),SRC/'result.json']
 for e in receipt['evidenceRefs']:
  p=ROOT/e['path'];assert digest(p.read_bytes())==e['sha256'];refs.append(p)
 rows=read(SRC/'selection.json.gz')['rows'];summaries=[]
 for row in rows:
  uid=row['uid'];key=uid.split('/')[1];raw=(ROOT/row['candidate']['path']).read_bytes();assert digest(raw)==row['sourceSHA256'];t=np.asarray(decode_original_world_triangles(raw),dtype='<f8');identity=read(SRC/key/'identity.json');assert digest(t.tobytes())==identity['worldTrianglesSHA256']
  form=row['source']['building'];poly=Polygon(form['rings'][0],form['rings'][1:]);xz=t[:,:,[0,2]];dist=np.asarray(shapely.distance(shapely.points(xz.reshape(-1,2)),poly)).reshape(-1,3);far=np.flatnonzero(dist.max(1)>10);outside=np.flatnonzero(dist.max(1)>1e-8)
  projected=shapely.union_all(shapely.polygons(xz));missing=poly.difference(projected);excess=projected.difference(poly)
  info=dict(uid=uid,sourceSHA256=row['sourceSHA256'],worldSHA256=digest(t.tobytes()),completeFaceCount=len(t),completeOver10mFaceIds=far.tolist(),outsideFaceIds=outside.tolist(),maximumDistanceM=float(dist.max()),targetAreaM2=poly.area,sourceProjectionAreaM2=projected.area,missingTargetAreaM2=missing.area,excessSourceAreaM2=excess.area,missingTargetWKT=missing.wkt,excessSourceWKT=excess.wkt,farFaceTriangles=t[far].tolist(),rawReasons=identity['reasons'],installationApproved=False)
  save(DOC/(key+'.json'),info)
  fig=plt.figure(figsize=(16,8));ax=fig.add_subplot(121);ax.add_collection(PolyCollection(xz,facecolors='#aaa',edgecolors='none',alpha=.25));ax.add_collection(PolyCollection(xz[far],facecolors='red',edgecolors='red',linewidths=.25,alpha=.8))
  for ring in [poly.exterior,*poly.interiors]:a=np.asarray(ring.coords);ax.plot(a[:,0],a[:,1],color='blue',lw=1)
  ax.autoscale();ax.set_aspect('equal');ax.set_title('Original projection; target blue; >10m faces red');ax.set_xlabel('world X');ax.set_ylabel('world Z')
  ax=fig.add_subplot(122,projection='3d');display=t[:,:,[0,2,1]];ax.add_collection3d(Poly3DCollection(display,facecolor='grey',edgecolor='none',alpha=.08));ax.add_collection3d(Poly3DCollection(display[far],facecolor='red',edgecolor='darkred',linewidth=.3,alpha=.9));lo=display.min((0,1));hi=display.max((0,1));ax.set_xlim(lo[0],hi[0]);ax.set_ylim(lo[1],hi[1]);ax.set_zlim(lo[2],hi[2]);ax.set_box_aspect(np.maximum(hi-lo,.1));ax.view_init(25,-55);ax.set_title('Complete unchanged original / extent context');fig.suptitle(uid);fig.tight_layout();fig.savefig(DOC/(key+'.png'),dpi=140);plt.close(fig)
  summaries.append({k:info[k] for k in ['uid','completeFaceCount','maximumDistanceM','missingTargetAreaM2','excessSourceAreaM2']});print(summaries[-1],flush=True)
 save(DOC/'summary.json',dict(rows=summaries,installationApproved=False,geometryChanges=0))
 result=module('companion_extent_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-companion-original-extent-context',list(dict.fromkeys(refs)),dict(uids=[r['uid'] for r in rows],installationApproved=False,newlyInstalled=0));print(result['jobId'],flush=True)
if __name__=='__main__':main()
