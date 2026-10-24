"""Original wall paths, upper-surface coverage and inspectable local source views."""
from pathlib import Path
import numpy as np,matplotlib,shapely
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from primrose_podium_remaining_roles_v1_20261015 import paths_to,trace
BASE=ROOT/'docs/astra-city/government-import';FINITE=BASE/'government-xl-opus-podium-finite-walls-v1-20261017';WORLD=BASE/'government-xl-opus-four-world-contacts-v1-20261017';GROUND=BASE/'government-xl-opus-preserved-neighbours-v1-20261016';BATCH='government-xl-opus-podium-local-roles-v1-20261017';DOC=BASE/BATCH;UID='landsd/248432:0'
def main():
 assert not DOC.exists();r=read(FINITE/'result.json');pins={x['path']:x['sha256'] for x in r['evidenceRefs']};refs=[Path(__file__),FINITE/'result.json']
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 def consume(p):
  assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p);return read(p)
 worlds=consume(WORLD/'world-triangles.json.gz');tri=np.array(worlds['original'][UID]);assert all(np.array_equal(tri,w[UID]) for w in worlds.values());finite=consume(FINITE/'original.json.gz');records=finite['faces'];assert len(records)==len(tri)==967
 gpath=HERE/'local'/GROUND.name/'runtime-geometry.json.gz';ground=np.concatenate([np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3) for g in consume(gpath)['rows']]);assert finite['groundSHA256']==digest(ground.tobytes()) and finite['worldSHA256']==digest(tri.tobytes())
 normals=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);length=np.linalg.norm(normals,axis=1);ratio=np.divide(normals[:,1],length,out=np.zeros_like(length),where=length>0);bad={i for i,x in enumerate(records) if not x['proof']['existingOrdinaryClearanceBoundProved']};walls={i for i in bad if length[i]>0 and abs(ratio[i])<=.25};assert bad-walls=={619}
 eligible={i for i in range(len(tri)) if length[i]>0 and (abs(ratio[i])<=.25 or records[i]['proof']['existingOrdinaryClearanceBoundProved'])};roofs={i for i in eligible if ratio[i]>.25};parents=paths_to(tri,sorted(eligible),sorted(roofs));wallpaths=[dict(sourceFace=i,pathToStrictClearRoof=trace(i,parents)) for i in sorted(walls)]
 target=Polygon(tri[619][:,[0,2]]);height=tri[619,0,1];assert np.all(tri[619,:,1]==height) and ratio[619]==-1;cover=[]
 for i,t in enumerate(tri):
  if ratio[i]<=.25 or t[:,1].min()<=height:continue
  p=Polygon(t[:,[0,2]]);q=p.intersection(target)
  if q.area>0:cover.append(dict(faceIndex=i,overlapM2=q.area,minimumHeightM=float(t[:,1].min()),polygon=q))
 union=shapely.union_all([x['polygon'] for x in cover]);coverage=dict(faceIndex=619,faceAreaM2=target.area,coveredByHigherUpwardFacesM2=union.area,uncoveredM2=target.difference(union).area,higherOriginalFaces=[{k:v for k,v in x.items() if k!='polygon'} for x in cover],qualification='Projected coverage by wholly higher upward original faces; source context only, not a closed-solid or support proof.')
 DOC.mkdir();ids=[599,610,611,618,619];centre=tri[ids].mean(axis=(0,1));lo=tri[ids].min(axis=(0,1))-2;hi=tri[ids].max(axis=(0,1))+3;near=np.all(tri.max(axis=1)>=lo,axis=1)&np.all(tri.min(axis=1)<=hi,axis=1);ng=np.all(ground[:,:,[0,2]].max(axis=1)>=lo[[0,2]],axis=1)&np.all(ground[:,:,[0,2]].min(axis=1)<=hi[[0,2]],axis=1)
 for label,withground in [('source',False),('ground',True)]:
  fig=plt.figure(figsize=(15,7))
  for j,az in enumerate([-55,125]):
   ax=fig.add_subplot(1,2,j+1,projection='3d')
   parts=[(tri[near],'#b8c8d8',.18),(tri[[610,611]],'#d75035',.85),(tri[[618,619]],'#8852b7',.85)]+([(ground[ng],'#3e984d',.25)] if withground else [])
   for t,color,alpha in parts:ax.add_collection3d(Poly3DCollection((t-centre)[:,:,[0,2,1]],facecolor=color,edgecolor='#303030',alpha=alpha,linewidths=.4))
   for i in ids:
    c=tri[i].mean(axis=0)-centre;ax.text(c[0],c[2],c[1],str(i),fontsize=8)
   ax.set(xlim=(lo[0]-centre[0],hi[0]-centre[0]),ylim=(lo[2]-centre[2],hi[2]-centre[2]),zlim=(lo[1]-centre[1],hi[1]-centre[1]),xlabel='X metres',ylabel='Z metres',zlabel='Height metres');ax.set_box_aspect((hi-lo)[[0,2,1]]);ax.view_init(elev=25,azim=az)
  fig.suptitle('Opus original podium: red wall 610/611, purple horizontal faces 618/619'+(' with prepared terrain' if withground else ''));fig.tight_layout();fig.savefig(DOC/(label+'.png'),dpi=140);plt.close(fig)
 summary=dict(wallFaces=len(walls),wallsWithStrictClearRoofPath=sum(bool(x['pathToStrictClearRoof']) for x in wallpaths),missingRoofPaths=[x['sourceFace'] for x in wallpaths if not x['pathToStrictClearRoof']],downwardFace=coverage,fullAcceptance=False,newlyInstalled=0);save(DOC/'context.json',dict(wallPaths=wallpaths,localOriginalFaces={str(i):tri[i].tolist() for i in ids},worldSHA256=finite['worldSHA256'],groundSHA256=finite['groundSHA256'],**summary))
 refs += [HERE/'primrose_podium_remaining_roles_v1_20261015.py'];out=module('opus_local_roles_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-opus-wall-roof-paths-and-local-downward-context-v1',refs,dict(uids=[UID],**summary));print(dict(jobId=out['jobId'],**summary),flush=True)
if __name__=='__main__':main()
