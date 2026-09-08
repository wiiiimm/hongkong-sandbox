"""Bounded native triangle patches: keep core facets, join parent outside the core."""
import json,math
from pathlib import Path
import numpy as np
import shapely
import native_terrain as n
import terrain_patches as t
ROOT=n.ROOT;HERE=Path(__file__).resolve().parent;OUT=n.OUT

def clip(poly, axis, value, greater):
 out=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  da=(a[axis]-value)*(1 if greater else -1);db=(b[axis]-value)*(1 if greater else -1)
  if da>=-1e-10:out.append(a)
  if (da<0 and db>0) or (da>0 and db<0):out.append(a+(b-a)*(da/(da-db)))
 return out

def rect(poly,bb):
 for axis,value,greater in [(0,bb[0],True),(2,bb[1],True),(0,bb[2],False),(2,bb[3],False)]:
  if not poly:return []
  poly=clip(poly,axis,value,greater)
 return poly

def cross2(a,b):return a[0]*b[1]-a[1]*b[0]

def parent_clip(poly,tri):
 # Counter-clockwise XZ clipping; linear interpolation preserves native Y.
 area=cross2(tri[1]-tri[0],tri[2]-tri[0])
 if area<0:tri=tri[::-1]
 for a,b in zip(tri,np.roll(tri,-1,axis=0)):
  out=[]
  for p,q in zip(poly,poly[1:]+poly[:1]):
   dp=cross2(b-a,p[[0,2]]-a);dq=cross2(b-a,q[[0,2]]-a)
   if dp>=-1e-9:out.append(p)
   if (dp<0 and dq>0)or(dp>0 and dq<0):out.append(p+(q-p)*dp/(dp-dq))
  poly=out
  if not poly:break
 return poly

def main():
 report=n.read(OUT/'report.json');models={x['uid']:x for x in report['rows']};bundle=n.read(OUT/'terrain-patches.json');rows=[];folder=HERE/'exact-tin';folder.mkdir(exist_ok=True)
 for baseid in ['103538-0','257313-0']:
  patch=n.read(HERE/'terrain-patches'/('support-native-'+baseid+'.json'));parent=n.read(ROOT/'3d-viewer'/patch['meta']['parentTerrain']);sampler=t.fine.DemSampler(parent,rendered=True);bb=t.bounds(patch);core=[bb[0]+10,bb[1]+10,bb[2]-10,bb[3]-10];regions=[(core,False),([bb[0],bb[1],bb[2],core[1]],True),([bb[0],core[3],bb[2],bb[3]],True),([bb[0],core[1],core[0],core[3]],True),([core[2],core[1],bb[2],core[3]],True)]
  pg=parent['meta']['georef'];cell=abs(pg['aE']);pcells=[]
  c0,r0,c1,r1=patch['coarseCells']
  for r in range(r0,r1):
   for c in range(c0,c1):
    x=pg['bE']+c*cell-834500;z=816500-pg['bN']+r*cell;a=np.array([x,z]);b=a+[cell,0];d=a+[0,cell];e=a+[cell,cell];pcells.extend([np.array([a,b,d]),np.array([b,e,d])])
  output=[];coverage=[];sourcefacets=0;vertical=0;coreunchanged=0
  for source in patch['meta']['source']['nativeSources']:
   assert n.sha(ROOT/source['manifest'])==source['manifestSha256']
   for f in source['files']:assert n.sha(ROOT/f['path'])==f['sha256']
   _,_,alltri,_,_,_=n.terrain_index((ROOT/source['manifest']).parent)
   hits=alltri[(alltri[:,:,0].max(axis=1)>=bb[0])&(alltri[:,:,0].min(axis=1)<=bb[2])&(alltri[:,:,2].max(axis=1)>=bb[1])&(alltri[:,:,2].min(axis=1)<=bb[3])]
   for tri in hits:
    sourcefacets+=1
    for region,transition in regions:
     p=rect(list(tri),region)
     if len(p)<3:continue
     groups=[parent_clip(p,pt) for pt in pcells] if transition else [p]
     for points in groups:
      if len(points)<3:continue
      vs=[]
      for v in points:
       v=v.copy()
       if transition:
        alpha=max(0,min(1,min(v[0]-bb[0],bb[2]-v[0],v[2]-bb[1],bb[3]-v[2])/10));v[1]=v[1]*alpha+sampler.ground(v[0],v[2])*(1-alpha)
       vs.append(v)
      for i in range(1,len(vs)-1):
       f=np.array([vs[0],vs[i],vs[i+1]])
       if np.linalg.norm(np.cross(f[1]-f[0],f[2]-f[0]))<1e-8:continue
       output.append(f)
       if not transition:coreunchanged+=1
  triangles=np.array(output);polys=shapely.polygons(triangles[:,:,[0,2]]);valid=shapely.area(polys)>1e-10;vertical=int((~valid).sum());usable=triangles[valid];tree=shapely.STRtree(polys[valid]);missing=shapely.area(shapely.difference(shapely.box(*bb),shapely.union_all(polys[valid])));boundary=[]
  for f in triangles:
   for v in f:
    if min(abs(v[0]-bb[0]),abs(v[0]-bb[2]),abs(v[2]-bb[1]),abs(v[2]-bb[3]))<1e-7:boundary.append(abs(v[1]-sampler.ground(v[0],v[2])))
  checks=[]
  for uid in patch['meta']['targetUids']:
   pts=np.array([s['position'] for s in models[uid]['rim']]);ys=n.samples(pts[:,[0,2]],usable,tree);gaps=pts[:,1]-ys;checks.append({'uid':uid,'rimSamples':len(gaps),'covered':int(np.isfinite(ys).sum()),'within2m':int((abs(gaps)<=2).sum()),'gapRange':[float(gaps.min()),float(gaps.max())]})
  patch['id']='support-exact-tin-'+baseid;patch['nativeMesh']={'position':triangles.reshape(-1).tolist(),'index':list(range(len(triangles)*3)),'source':{'nativeSources':patch['meta']['source']['nativeSources'],'policy':'Native source facets retained in core, including vertical retaining faces. Outer 10m transition split on exact parent triangle edges; parent boundary heights unchanged. Highest projected triangle is the collision surface.','verticalDatum':'HKPD','verticalScale':1}}
  path=folder/(patch['id']+'.json');path.write_text(json.dumps(patch,separators=(',',':'))+'\n');result={'path':str(path.relative_to(ROOT)),'sha256':n.sha(path),'parentTerrainURL':patch['meta']['parentTerrain'],'parentSha256':n.sha(ROOT/'3d-viewer'/patch['meta']['parentTerrain']),'coarseCells':patch['coarseCells'],'triangles':len(triangles),'verticalFacets':vertical,'coreFacets':coreunchanged,'missingProjectedAreaM2':float(missing),'boundaryMaxError':max(boundary),'rows':checks,'publicationApproved':False};rows.append(result);print(json.dumps(result),flush=True)
 (OUT/'exact-tin.json').write_text(json.dumps({'issue':'HKS-214','patches':rows,'runtimeBrowserChecksPending':True},indent=2)+'\n')
if __name__=='__main__':main()
