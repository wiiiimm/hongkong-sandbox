"""Compare both mall originals before deciding whether they are complementary."""
from pathlib import Path
import numpy as np
import shapely
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-mount-sterling-two-source-comparison-v1-20261020';DOC=BASE/BATCH;SRC=BASE/'government-xl-mount-sterling-nine-original-recovery-v1-20261020'
def main():
 assert not DOC.exists();r=read(SRC/'result.json');refs=[Path(__file__),SRC/'result.json',HERE/'exact_packed_world_geometry_20261009.py'];pins={e['path']:e['sha256']for e in r['evidenceRefs']}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 p=SRC/'recovery.json';assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p);rows=[r for r in read(p)['rows']if r['uid']=='landsd/289787:0'];assert len(rows)==2;meshes=[];projections=[];stats=[]
 for row in rows:
  p=ROOT/row['assetPath'];assert digest(p.read_bytes())==row['sourceSHA256']==pins[str(p.relative_to(ROOT))];refs.append(p);t=decode_original_world_triangles(p.read_bytes());meshes.append(t);polys=shapely.polygons(t[:,:,[0,2]]);proj=shapely.union_all(polys[shapely.area(polys)>1e-10]);projections.append(proj);stats.append(dict(modelId=row['modelId'],sourceSHA256=row['sourceSHA256'],triangles=len(t),bounds=[t.min((0,1)).tolist(),t.max((0,1)).tolist()],projectionArea=float(proj.area)))
 DOC.mkdir(parents=True);fig,axes=plt.subplots(2,3,figsize=(18,10));lo=np.concatenate(meshes).min((0,1));hi=np.concatenate(meshes).max((0,1))
 for j,(row,t)in enumerate(zip(rows,meshes)):
  for ax,dims,label in zip(axes[j],[(0,2),(0,1),(2,1)],['Plan','X/Y elevation','Z/Y elevation']):
   ax.add_collection(PolyCollection(t[:,:,dims],facecolors=['#3f8298','#aa7755'][j],edgecolors='#213d47',linewidths=.12,alpha=.24));ax.set_xlim(lo[dims[0]]-3,hi[dims[0]]+3);ax.set_ylim(lo[dims[1]]-1,hi[dims[1]]+1);ax.set_title(f'{row["modelId"]}: {len(t)} faces — {label}')
   if dims==(0,2):ax.set_aspect('equal')
 fig.suptitle('Two unchanged government sources mapped to Mount Sterling Mall\nComparison only: do not assume the smaller source must be added to the larger source.');fig.tight_layout();fig.savefig(DOC/'two-originals.png',dpi=160);plt.close(fig)
 intersection=projections[0].intersection(projections[1]);summary=dict(uids=['landsd/289787:0'],sources=stats,projectionIntersectionArea=float(intersection.area),firstCoveredBySecond=float(intersection.area/projections[0].area),secondCoveredByFirst=float(intersection.area/projections[1].area),firstOnlyArea=float(projections[0].difference(projections[1]).area),secondOnlyArea=float(projections[1].difference(projections[0]).area),sourceGeometryChanges=0,installationApproved=False,sourceRelationship='Uninterpreted: overlap does not establish duplicate or complementary geometry.')
 save(DOC/'comparison.json',summary);module('mount_sterling_pair_compare',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'two-original-projection-and-elevation-comparison',refs,summary);print(summary,flush=True)
if __name__=='__main__':main()
