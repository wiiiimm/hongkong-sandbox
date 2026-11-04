"""Render unchanged source facets for below-grade wall interpretation."""
from pathlib import Path
import numpy as np
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from run import ROOT,HERE,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';DOC=BASE/'government-xl-villa-podium-wall-review-v2-20261015'
def main():
 assert not DOC.exists();DOC.mkdir();source=BASE/'government-xl-villa-five-current-physical-v4-20261015/selection.json.gz';row=next(r for r in read(source)['rows']if r['uid']=='landsd/89917:0');asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256'];tri=decode_original_world_triangles(asset.read_bytes());wall=BASE/'government-xl-villa-five-original-and-rendered-finite-wall-contexts-v3-20261010/diagnostic.json.gz';context=read(wall)['rows'][0]['completeOriginal'];ids=context['affectedFaces'];assert len(ids)==24 and not context['unresolvedWallConditions']and not context['buriedUpwardFaces'];roof=sorted({p['wallToRoofPath'][-1]for p in context['wallPaths']['faces']});origin=tri.min((0,1));render=tri[:,:,[0,2,1]]-origin[[0,2,1]];norm=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);stats=[]
 for i in ids:
  n=norm[i];stats.append(dict(face=i,bounds=[tri[i].min(0).tolist(),tri[i].max(0).tolist()],normal=n.tolist(),vertical=bool(n[1]==0),roofPath=next(p['wallToRoofPath']for p in context['wallPaths']['faces']if p['sourceFace']==i)))
 fig=plt.figure(figsize=(18,12));
 for j,(az,el)in enumerate([(25,25),(125,25),(220,25),(310,20)]):
  ax=fig.add_subplot(2,2,j+1,projection='3d');ax.add_collection3d(Poly3DCollection(render,facecolor='#9caab5',edgecolor='none',alpha=.16));ax.add_collection3d(Poly3DCollection(render[roof],facecolor='#f5c84b',edgecolor='#705500',linewidth=.3));ax.add_collection3d(Poly3DCollection(render[ids],facecolor='#d33131',edgecolor='#720000',linewidth=.4));ext=render.max((0,1));ax.set_xlim(0,ext[0]);ax.set_ylim(0,ext[1]);ax.set_zlim(0,ext[2]);ax.set_box_aspect(ext);ax.view_init(el,az);ax.set_xlabel('East (m)');ax.set_ylabel('South (m)');ax.set_zlabel('Height above source minimum (m)');ax.set_title('Complete unchanged podium: red=24 affected wall records; gold=connected exposed roof')
 fig.tight_layout();fig.savefig(DOC/'complete-podium-wall-views-2700x1800.png',dpi=150);plt.close(fig)
 save(DOC/'face-review-inputs.json',dict(uid=row['uid'],sourceSHA256=row['sourceSHA256'],sourceFaces=len(tri),affectedFaces=stats,roofFaces=roof,sourceMinimum=origin.tolist(),primaryCSUID=row['source']['building']['buildingCSUID'],inputRefs=[dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))for p in [Path(__file__),source,asset,wall]]))
if __name__=='__main__':main()
