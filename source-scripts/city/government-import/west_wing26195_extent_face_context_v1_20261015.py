"""Attribute every original outside-footprint patch; diagnostic, never approval."""
from pathlib import Path
import numpy as np,shapely
from shapely.geometry import Polygon
from shapely.ops import unary_union
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from run import ROOT,read,save,digest
BASE=ROOT/'docs/astra-city/government-import';CAP=BASE/'government-xl-west-wing26195-complete-current-runtime-capture-v2-20261012';OUT=BASE/'government-xl-west-wing26195-extent-face-context-v1-20261015'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not OUT.exists();paths=[CAP/'original-full-source-root-context.json.gz',CAP/'literal-source-inputs.json.gz',Path(__file__)];refs=[ref(p)for p in paths]
 a=np.asarray(read(paths[0])['completeOriginalBinary64WorldTriangles']);assert a.shape==(46918,3,3)
 forms={b['uid']:b for b in read(paths[1])['completeCurrentForms']};f=forms['landsd/26195:0'];target=Polygon(f['rings'][0],f['rings'][1:]);ps=[Polygon(t[:,[0,2]])for t in a];projection=unary_union([p for p in ps if p.area>0]);excess=projection.difference(target);parts=sorted(list(excess.geoms)if hasattr(excess,'geoms')else[excess],key=lambda p:-p.area)
 distances=np.asarray(shapely.distance(shapely.points(a[:,:,[0,2]].reshape(-1,2)),target)).reshape(-1,3);far=np.flatnonzero(distances.max(axis=1)>10).tolist();rows=[]
 for i,g in enumerate(parts):
  ids=[j for j,p in enumerate(ps)if p.area>0 and p.intersection(g).area>1e-9]
  rows.append(dict(region=i,areaM2=g.area,bounds=list(g.bounds),sourceFaceIds=ids,over10mFaceIds=sorted(set(ids)&set(far)),sourceYRange=[float(a[ids,:,1].min()),float(a[ids,:,1].max())]if ids else None))
 fig,axes=plt.subplots(1,2,figsize=(15,11))
 for ax in axes:
  ax.add_collection(PolyCollection([t[:,[0,2]]for t in a],facecolors='#b9cad4',edgecolors='none',alpha=.3));x,z=target.exterior.xy;ax.plot(x,z,'k-',lw=1)
  ax.add_collection(PolyCollection([a[i][:,[0,2]]for i in far],facecolors='#b42f2f',edgecolors='#721717',linewidths=.3,alpha=.8));ax.autoscale();ax.set_aspect('equal');ax.invert_yaxis();ax.set_xlabel('Viewer X (m)');ax.set_ylabel('Viewer Z (m)')
 for r,g in zip(rows,parts):
  if r['areaM2']>1:
   c=g.representative_point();axes[0].text(c.x,c.y,str(r['region']),fontsize=9,color='darkblue')
 q=a[far][:,:,[0,2]];lo=q.min(axis=(0,1));hi=q.max(axis=(0,1));axes[1].set_xlim(lo[0]-10,hi[0]+10);axes[1].set_ylim(hi[1]+10,lo[1]-10)
 axes[0].set_title('Complete original and official footprint; outside-region labels');axes[1].set_title('Original faces with any vertex >10m outside footprint');fig.tight_layout();OUT.mkdir();fig.savefig(OUT/'extent-context.png',dpi=140);plt.close(fig)
 for q in refs:assert ref(ROOT/q['path'])==q
 save(OUT/'context.json',dict(sourceOnly=True,newlyInstalled=0,installationApproved=False,sourceGeometryChanges=0,completeSourceFaces=len(a),sourceOutsideTargetArea=excess.area,regions=rows,completeOver10mFaceIds=far,maximumVertexDistanceM=float(distances.max()),inputRefs=refs))
 print(dict(regions=len(rows),over10mFaces=len(far),materialRegions=[{k:v for k,v in r.items()if k!='sourceFaceIds'}for r in rows if r['areaM2']>1]))
if __name__=='__main__':main()
