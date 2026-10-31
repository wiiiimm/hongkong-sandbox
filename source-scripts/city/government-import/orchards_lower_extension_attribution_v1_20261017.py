"""Attribute unchanged far-extension faces to current forms; diagnostic only."""
from pathlib import Path
import numpy as np
import shapely
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';PRIOR=BASE/'government-xl-three-current-originals-v1-20261017';BATCH='government-xl-orchards-lower-extension-attribution-v1-20261017';DOC=BASE/BATCH;UID='landsd/254629:0'
def main():
 assert not DOC.exists()
 r=read(PRIOR/'result.json')
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for e in r['evidenceRefs']:assert digest((ROOT/e['path']).read_bytes())==e['sha256']
 row=next(x for x in read(PRIOR/'selection.json.gz')['rows']if x['uid']==UID)
 rt=HERE/'local'/PRIOR.name/'runtime-geometry.json.gz';g=next(x for x in read(rt)['rows']if x['uid']==UID)
 t=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];assert len(t)==11517
 b=row['source']['building'];target=Polygon(b['rings'][0],b['rings'][1:]);dist=shapely.distance(shapely.points(t[:,:,[0,2]].reshape(-1,2)),target).reshape(-1,3)
 ids=np.flatnonzero(dist.max(axis=1)>10);far=t[ids];assert len(far)>0
 projection=shapely.union_all(shapely.polygons(far[:,:,[0,2]]));final=module('orchards_extension_forms',HERE/'xl-final-script-pass.py');lo,hi=t.min(axis=(0,1)),t.max(axis=(0,1));forms=final.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2]);attribution=[];same=[];refs=[Path(__file__),PRIOR/'result.json',PRIOR/'selection.json.gz',rt,HERE/'xl-final-script-pass.py']
 for f,_,tile in forms:
  refs.append(ROOT/'3d-viewer'/tile);p=Polygon(f['rings'][0],f['rings'][1:]);intersection=projection.intersection(p)
  if intersection.area>1e-10:
   attribution.append(dict(uid=f['uid'],name=f.get('name'),parent=f.get('parent'),sameParent=f.get('parent')==b['parent'],base=f['base'],top=f['base']+f['height'],projectedIntersectionM2=intersection.area))
  if f.get('parent')==b['parent']:same.append(p)
 uncovered=projection.difference(shapely.union_all(same))
 out=dict(uid=UID,sourceSHA256=row['sourceSHA256'],selectionRule='Whole original faces with any XZ vertex more than the existing 10m identity extent from target; no clipping or edits',sourceFaces=ids.tolist(),faceCount=len(ids),worldBounds=[far.min(axis=(0,1)).tolist(),far.max(axis=(0,1)).tolist()],projectionAreaM2=projection.area,notCoveredBySameParentM2=uncovered.area,forms=attribution,installationApproved=False,qualification='Current GIS attribution and heights only; shared parent does not grant source identity or physical acceptance.')
 save(DOC/'attribution.json.gz',out)
 import matplotlib;matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 from mpl_toolkits.mplot3d.art3d import Poly3DCollection
 fig=plt.figure(figsize=(12,7),dpi=140);ax=fig.add_subplot(111,projection='3d')
 # Local axes X/Z/Y keep elevation vertical. All complete far faces retained.
 ax.add_collection3d(Poly3DCollection(far[:,:,[0,2,1]],facecolors='#6aa5bf',edgecolors='#23495c',linewidths=.2,alpha=.8))
 bounds=np.array(out['worldBounds'])[:,[0,2,1]];ax.set_xlim(bounds[:,0]);ax.set_ylim(bounds[:,1]);ax.set_zlim(bounds[:,2]);ax.set_box_aspect(np.maximum(bounds[1]-bounds[0],.1));ax.set_xlabel('World X');ax.set_ylabel('World Z');ax.set_zlabel('HKPD height');ax.set_title('Orchards Tower 2: unchanged faces responsible for >10m extent');fig.tight_layout();fig.savefig(DOC/'extension.png');plt.close(fig)
 summary={k:out[k]for k in ['faceCount','worldBounds','projectionAreaM2','notCoveredBySameParentM2','forms']}
 result=module('orchards_extension_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'orchards-lower-extension-current-form-attribution-v1',list(set(refs)),dict(uids=[UID],summary=summary,fullAcceptance=False,nextStep='Review precise extension shape and government source provenance before resolving identity; full contact and neighbour requirements remain.'))
 print(dict(jobId=result['jobId'],summary=summary),flush=True)
if __name__=='__main__':main()
