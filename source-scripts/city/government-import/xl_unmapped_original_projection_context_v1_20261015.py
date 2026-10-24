"""Complete recovered source projections vs current provider footprints; no approval."""
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon,GeometryCollection
from shapely.ops import unary_union
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';REC=BASE/'government-xl-unmapped-exact-source-recovery-v1-20261015';QUERY=BASE/'government-xl-unmapped-full-bounds-provider-v1-20261015';OUT=BASE/'government-xl-unmapped-original-projection-context-v1-20261015'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not OUT.exists();OUT.mkdir();out=[];refs=[ref(Path(__file__)),ref(REC/'result.json'),ref(QUERY/'result.json')]
 for row in read(REC/'recovery.json')['rows']:
  path=ROOT/row['asset']['path'];assert ref(path)==row['asset'];a=decode_original_world_triangles(path.read_bytes());assert a.shape==(row['triangles'],3,3);ps=[Polygon(t[:,[0,2]])for t in a];projection=unary_union([p for p in ps if p.area>0]);qp=QUERY/(row['modelId']+'.json');features=read(qp)['features'];refs.extend([ref(path),ref(qp)]);measurements=[]
  fig=plt.figure(figsize=(14,8));ax=fig.add_subplot(1,2,1);ax.add_collection(PolyCollection([t[:,[0,2]]for t in a],facecolors='#9ab9cc',edgecolors='none',alpha=.45))
  for feature in features:
   attr=feature['attributes'];target=GeometryCollection()
   for ring in feature['geometry']['rings']:
    points=np.asarray(ring)[:,:2];points[:,0]-=834500;points[:,1]=816500-points[:,1];p=Polygon(points);assert p.is_valid;target=target.symmetric_difference(p);ax.plot(points[:,0],points[:,1],linewidth=.8)
   assert target.is_valid and target.area>0;inter=projection.intersection(target).area;c=target.representative_point();ax.text(c.x,c.y,str(attr['OBJECTID']),fontsize=6)
   measurements.append(dict(objectId=attr['OBJECTID'],CSUID=attr['BuildingCSUID'],name=attr.get('BuildingNameEN'),type=attr['BuildingBlockType'],intersectionAreaM2=inter,sourceCoverage=inter/projection.area,targetCoverage=inter/target.area,intersectionOverUnion=inter/projection.union(target).area))
  ax.autoscale();ax.set_aspect('equal');ax.invert_yaxis();ax.set_title('Original projection (blue) / current government rings')
  ax=fig.add_subplot(1,2,2,projection='3d');lo=a.min(axis=(0,1));hi=a.max(axis=(0,1));origin=np.array([lo[0],0,lo[2]]);b=(a-origin)[:,:,[0,2,1]];ax.add_collection3d(Poly3DCollection(b,facecolors='#a6bcca',edgecolors='#526575',linewidths=.06));ax.set_xlim(0,hi[0]-lo[0]);ax.set_ylim(0,hi[2]-lo[2]);ax.set_zlim(lo[1],hi[1]);ax.set_box_aspect(np.maximum(hi-lo,.01)[[0,2,1]]);ax.view_init(elev=25,azim=-60);ax.set_zlabel('HKPD m');ax.set_title('Complete unchanged original')
  fig.suptitle(row['modelId']+' — identity context only');fig.tight_layout();png=OUT/(row['modelId']+'.png');fig.savefig(png,dpi=130);plt.close(fig)
  out.append(dict(sourceKey=row['sourceKey'],sourceSHA256=row['sourceSHA256'],completeFaces=len(a),worldSHA256=digest(np.asarray(a,dtype='<f8').tobytes()),sourceAreaM2=projection.area,sourceBounds=[lo.tolist(),hi.tolist()],candidates=sorted(measurements,key=lambda x:-x['sourceCoverage']),image=ref(png),identityAccepted=False,installationApproved=False))
 for q in refs:assert ref(ROOT/q['path'])==q
 save(OUT/'context.json',dict(rows=out,inputRefs=refs,sourceOnly=True,newlyInstalled=0,geometryChanges=0,qualification='Complete original triangle projection and current public provider geometry. Overlap and visual resemblance are identity leads, not authoritative historical-ID lineage or installation approval.'))
 print([(r['sourceKey'].split('/')[1],[(c['objectId'],round(c['sourceCoverage'],3),round(c['targetCoverage'],3))for c in r['candidates'][:3]])for r in out])
if __name__=='__main__':main()
