"""Per-target original assembly coverage and source-only explanatory figures."""
from pathlib import Path
import numpy as np
import shapely
from shapely.geometry import Polygon,mapping
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';PRIOR=BASE/'government-xl-oi-sin-four-originals-physical-v1-20261017';BATCH='government-xl-oi-sin-assembly-coverage-v1-20261017';DOC=BASE/BATCH;RT=HERE/'local'/PRIOR.name/'runtime-geometry.json.gz'
def main():
 assert not DOC.exists();r=read(PRIOR/'result.json')
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for q in r['evidenceRefs']:assert digest((ROOT/q['path']).read_bytes())==q['sha256']
 selection=read(PRIOR/'selection.json.gz')['rows'];geo={g['uid']:g for g in read(RT)['rows']};tri={u:np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)]for u,g in geo.items()};proj={u:shapely.union_all(shapely.polygons(t[:,:,[0,2]]))for u,t in tri.items()};whole=shapely.union_all(list(proj.values()));targets={r['uid']:Polygon(r['source']['building']['rings'][0],r['source']['building']['rings'][1:])for r in selection};out=[];features=[]
 for row in selection:
  uid=row['uid'];target=targets[uid];missing=target.difference(proj[uid]);remaining=missing;credits=[]
  for other in sorted(set(proj)-{uid}):
   covered=remaining.intersection(proj[other]);credits.append(dict(uid=other,missingAreaCoveredM2=covered.area));remaining=remaining.difference(proj[other])
  assert abs(missing.area-sum(x['missingAreaCoveredM2']for x in credits)-remaining.area)<1e-6
  out.append(dict(uid=uid,sourceSHA256=row['sourceSHA256'],completeSourceFaces=len(tri[uid]),targetAreaM2=target.area,ownCoverageFraction=target.intersection(proj[uid]).area/target.area,assemblyCoverageFraction=target.intersection(whole).area/target.area,missingOwnM2=missing.area,remainingAssemblyMissingM2=remaining.area,sourceAttribution=credits));features.append(dict(type='Feature',properties={'uid':uid},geometry=mapping(remaining)))
 save(DOC/'coverage.json',dict(rows=out,identityAccepted=False,fullAcceptance=False,qualification='Each unchanged target is measured separately against complete exact source projections. No whole-assembly aggregate substitutes for per-target evidence; overlap attribution does not prove support or ownership.'));save(DOC/'remaining.geojson',dict(type='FeatureCollection',features=features))
 import matplotlib;matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 from matplotlib.patches import Polygon as Patch
 from mpl_toolkits.mplot3d.art3d import Poly3DCollection
 colors={'landsd/256280:0':'#287bb5','landsd/91128:0':'#a7adb5','landsd/254867:0':'#35a26f','landsd/256457:0':'#e79936'}
 fig=plt.figure(figsize=(15,7),dpi=160);ax=fig.add_subplot(121,projection='3d');origin=np.array([6850.,690.])
 for uid,t in tri.items():
  vertices=t.copy();vertices[:,:,0]-=origin[0];vertices[:,:,1]=-t[:,:,2]+origin[1];vertices[:,:,2]=t[:,:,1];ax.add_collection3d(Poly3DCollection(vertices,facecolors=colors[uid],edgecolors='none',alpha=1))
 ax.set(xlim=(0,145),ylim=(-90,0),zlim=(0,95),xlabel='East (m)',ylabel='North (m)',zlabel='HKPD (m)',title='Complete unchanged original assembly');ax.view_init(elev=25,azim=-55);ax.set_box_aspect((145,90,95))
 ax2=fig.add_subplot(122)
 def parts(g):
  if g.geom_type=='Polygon':return [g]
  return [p for z in getattr(g,'geoms',[])for p in parts(z)]
 for uid,p in proj.items():
  for poly in parts(p):ax2.add_patch(Patch(np.asarray(poly.exterior.coords),facecolor=colors[uid],edgecolor=colors[uid],alpha=.35))
 for uid,p in targets.items():
  for poly in parts(p):ax2.plot(*np.asarray(poly.exterior.coords).T,color=colors[uid],linewidth=1)
 ax2.autoscale_view();ax2.set_aspect('equal');ax2.invert_yaxis();ax2.set_title('Original projections and recorded footprints');ax2.set_xlabel('World east (m)');ax2.set_ylabel('World south (m)');fig.tight_layout();fig.savefig(DOC/'assembly-source-context.png');plt.close(fig)
 refs=[Path(__file__),PRIOR/'result.json',PRIOR/'selection.json.gz',RT];result=module('oi_coverage_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'oi-sin-four-originals-per-target-source-coverage-v1',refs,dict(uids=list(tri),rows=out,fullAcceptance=False,nextStep='Review complete source assembly and exact unresolved interfaces; coverage attribution alone does not resolve physical gates.'));print(dict(jobId=result['jobId'],rows=out),flush=True)
if __name__=='__main__':main()
