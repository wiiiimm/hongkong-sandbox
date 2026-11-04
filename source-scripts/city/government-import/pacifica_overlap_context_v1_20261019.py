"""Read-only exact-source overlap context; no identity or installation approval."""
from pathlib import Path
import numpy as np,shapely
from shapely.geometry import Polygon
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-pacifica-overlap-context-v1-20261019';DOC=BASE/BATCH;CAP=BASE/'government-xl-pacifica-expanded-grid-v4-20261018'
def main():
 assert not DOC.exists();receipt=read(CAP/'result.json');refs=[Path(__file__),CAP/'result.json',HERE/'exact_packed_world_geometry_20261009.py'];pins={e['path']:e['sha256'] for e in receipt['evidenceRefs']}
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 row=read(CAP/'selection.json.gz')['rows'][0];raw=(ROOT/row['candidate']['path']).read_bytes();assert digest(raw)==row['sourceSHA256'];t=np.asarray(decode_original_world_triangles(raw));xz=t[:,:,[0,2]];projection=shapely.union_all(shapely.polygons(xz));manifestpath=ROOT/'3d-viewer/city/data/manifest.json';manifest=read(manifestpath);refs.append(manifestpath);entries={}
 for u in manifest['officialModelCatalogues']:
  p=ROOT/'3d-viewer'/u;refs.append(p)
  for e in read(p)['models']:entries[e['uid']]=(e,p.parent/e['asset'])
 tile=ROOT/'3d-viewer/city/data/tiles/-1_-3.json';refs.append(tile);forms={b['uid']:b for b in read(tile)['buildings']};summary=[];fig,axes=plt.subplots(1,2,figsize=(16,9))
 for ax,uid in zip(axes,['landsd/265478:0','landsd/283034:0']):
  e,p=entries[uid];r=p.read_bytes();assert digest(r)==e['sha256'];refs.append(p);other=np.asarray(decode_original_world_triangles(r));op=shapely.union_all(shapely.polygons(other[:,:,[0,2]]));form=forms[uid];fp=Polygon(form['rings'][0],form['rings'][1:]);hit=shapely.intersects(shapely.polygons(xz),fp);ids=np.flatnonzero(hit);joint=projection.intersection(op)
  def signature(face):return tuple(sorted(tuple(map(float,v))for v in face))
  otherfaces={signature(f)for f in other};duplicates=[int(i)for i,f in enumerate(t)if signature(f)in otherfaces]
  info=dict(uid=uid,name=form['name'],sourceSHA256=row['sourceSHA256'],otherSourceSHA256=e['sha256'],otherCSUID=e['buildingCSUID'],otherModelId=e.get('modelId'),sourceFaces=len(t),otherFaces=len(other),sharedExactWorldTriangles=duplicates,sourceProjectionInOtherFootprintM2=projection.intersection(fp).area,sourceProjectionInOtherNativeProjectionM2=joint.area,intersectingSourceFaceIds=ids.tolist(),intersectingWholeFaceYBounds=[float(t[ids,:,1].min()),float(t[ids,:,1].max())],projectedOverlapWKT=joint.wkt,installationApproved=False,identityApproved=False)
  save(DOC/(uid.split('/')[1]+'.json'),info);summary.append({k:v for k,v in info.items()if k not in ['intersectingSourceFaceIds','projectedOverlapWKT','sharedExactWorldTriangles']});summary[-1]['sharedExactWorldTriangleCount']=len(duplicates)
  ax.add_collection(PolyCollection(xz,facecolors='#cccccc',edgecolors='none',alpha=.2));ax.add_collection(PolyCollection(other[:,:,[0,2]],facecolors='#4696ca',edgecolors='none',alpha=.12));ax.add_collection(PolyCollection(xz[ids],facecolors='#e66a2b',edgecolors='none',alpha=.3))
  for ring in [fp.exterior,*fp.interiors]:a=np.asarray(ring.coords);ax.plot(a[:,0],a[:,1],color='blue',lw=1)
  ax.autoscale();ax.set_aspect('equal');ax.set_title(uid+' '+form['name']+'\nGrey candidate, blue installed, orange candidate faces touching footprint');ax.set_xlabel('world X');ax.set_ylabel('world Z')
 fig.tight_layout();fig.savefig(DOC/'overlaps.png',dpi=130);plt.close(fig);save(DOC/'summary.json',dict(rows=summary,installationApproved=False,sourceGeometryChanges=0));print(summary,flush=True)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 module('pacifica_overlap_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-original-neighbour-overlap-context',list(dict.fromkeys(refs)),dict(uids=[row['uid']],installationApproved=False))
if __name__=='__main__':main()
