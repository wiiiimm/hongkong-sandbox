"""View full original West Wing projection against unchanged current official rings."""
from pathlib import Path
import json,gzip,hashlib
import numpy as np
from shapely.geometry import Polygon
from shapely.ops import unary_union
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.path import Path as PlotPath
from matplotlib.patches import PathPatch
from shapely.geometry.polygon import orient
ROOT=Path(__file__).resolve().parents[3];BASE=ROOT/'docs/astra-city/government-import';CAP=BASE/'government-xl-west-wing26195-complete-current-runtime-capture-v2-20261012';OUT=BASE/'government-xl-west-wing26195-current-projection-context-v2-20261015'
def read(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b)if p.suffix=='.gz'else b)
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def main():
 assert not OUT.exists();uid='landsd/26195:0';manifest=ROOT/'3d-viewer/city/data/manifest.json';m=read(manifest);refs=[ref(manifest)];saved=read(CAP/'literal-source-inputs.json.gz');forms={b['uid']:b for b in saved['completeCurrentForms']};current={}
 for t in m['tiles']:
  if t['url']!='city/data/tiles/0_0.json':continue
  p=ROOT/'3d-viewer'/t['url'];refs.append(ref(p));current={b['uid']:b for b in read(p)['buildings']}
 for u,b in forms.items():assert {k:v for k,v in b.items()if k!='tile'}=={k:v for k,v in current[u].items()if k!='tile'},u
 capture=read(CAP/'actual-render-geometry.json.gz');entry=next(x for x in capture['rows']if x['uid']==uid)['rawInstalledEntry'];matches=[]
 for url in m['officialModelCatalogues']:
  p=ROOT/'3d-viewer'/url
  for e in read(p)['models']:
   if e['uid']==uid:matches.append(e);refs.extend([ref(p),ref(p.parent/e['asset'])]);assert refs[-1]['sha256']==e['sha256']
 assert matches==[entry]
 original=read(CAP/'original-full-source-root-context.json.gz');a=np.asarray(original['completeOriginalBinary64WorldTriangles']);assert a.shape==(46918,3,3)
 polygons=[Polygon(t[:,[0,2]])for t in a];area=[p for p in polygons if p.area>0];projection=unary_union(area);target=Polygon(forms[uid]['rings'][0],forms[uid]['rings'][1:]);excess=projection.difference(target)
 fig,ax=plt.subplots(figsize=(12,12));
 def draw(g,**kw):
  if g.is_empty:return
  if g.geom_type=='Polygon':
   g=orient(g,sign=1);vertices=[];codes=[]
   for ring in [g.exterior,*g.interiors]:
    points=list(ring.coords);vertices.extend(points);codes.extend([PlotPath.MOVETO]+[PlotPath.LINETO]*(len(points)-2)+[PlotPath.CLOSEPOLY])
   ax.add_patch(PathPatch(PlotPath(vertices,codes),**kw))
  elif hasattr(g,'geoms'):
   for q in g.geoms:draw(q,**kw)
 draw(projection,color='#b8cbd8',alpha=.7);draw(excess,color='#ef9c36',alpha=.9)
 rows=[]
 for u in [uid,'landsd/322270:0','landsd/315069:0','landsd/319534:0']:
  f=forms[u];p=Polygon(f['rings'][0],f['rings'][1:]);x,y=p.exterior.xy;ax.plot(x,y,label=u+' '+str(f.get('name')),linewidth=1.4)
  if u!=uid:
   intersection=projection.intersection(p);indices=[i for i,q in enumerate(polygons)if q.area>0 and q.intersection(p).area>0];rows.append(dict(uid=u,sourceIntersectionArea=intersection.area,sourceFaceIds=indices,sourceYRange=[float(a[indices,:,1].min()),float(a[indices,:,1].max())]if indices else None))
  if u in ['landsd/315069:0','landsd/319534:0']:draw(excess.intersection(p),color='#bd354c',alpha=1)
 ax.set_aspect('equal');ax.invert_yaxis();ax.legend(fontsize=8);ax.set_title('West Wing: whole original source projection and official footprints\nOrange: source outside own footprint; red: excess overlapping unrelated forms');ax.set_xlabel('Viewer X (m)');ax.set_ylabel('Viewer Z (m)');fig.tight_layout();OUT.mkdir();fig.savefig(OUT/'whole-source-official-footprints.png',dpi=160);plt.close(fig)
 refs.extend(ref(CAP/f)for f in ['literal-source-inputs.json.gz','actual-render-geometry.json.gz','original-full-source-root-context.json.gz']);refs.append(ref(Path(__file__)))
 for q in refs:assert ref(ROOT/q['path'])==q
 (OUT/'context.json').write_text(json.dumps(dict(inputs=refs,sourceOnly=True,installationApproved=False,newlyInstalled=0,currentFormsVerified=len(forms),currentRuntimeEntryUnchanged=True,completeOriginalFaces=len(a),areaBearingFaces=len(area),zeroProjectedAreaFaces=len(a)-len(area),sourceProjectionArea=projection.area,sourceOutsideTargetArea=excess.area,targetCoverage=projection.intersection(target).area/target.area,intersections=rows,geometryChanges=0),indent=2)+'\n');print(json.dumps(dict(currentFormsVerified=len(forms),sourceFaces=len(a),targetCoverage=projection.intersection(target).area/target.area)))
if __name__=='__main__':main()
