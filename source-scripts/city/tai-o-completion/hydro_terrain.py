"""Clip existing rendered triangles by mapped water, preserving all source elevation arrays."""
import argparse,hashlib,json,math,pathlib
import numpy as np
from shapely import constrained_delaunay_triangles
from shapely.geometry import Polygon,Point,box
from shapely.ops import unary_union
from hydro_build import HERE,ROOT,DOC,polys
OUT=ROOT/'3d-viewer/city/data';ORIGIN=[834500,816500]
def render_value(data,i):
 v=(data.get('renderedElev') or [])[i] if data.get('renderedElev') else None
 return float(v) if isinstance(v,(int,float)) else max(1.2,data['elev'][i]) if data['elev'][i]>0 else -4.
def vertex(data,c,r):
 g=data['meta']['georef'];return (g['bE']+c*g['aE']-ORIGIN[0],render_value(data,r*data['w']+c),ORIGIN[1]-(g['bN']+r*g['aN']))
def height(data,x,z):
 g=data['meta']['georef'];c=(x+ORIGIN[0]-g['bE'])/g['aE'];r=(ORIGIN[1]-z-g['bN'])/g['aN'];c=max(0,min(data['w']-1,c));r=max(0,min(data['h']-1,r));i=min(data['w']-2,math.floor(c));j=min(data['h']-2,math.floor(r));u=c-i;v=r-j
 a,b,d,e=[render_value(data,k) for k in [j*data['w']+i,j*data['w']+i+1,(j+1)*data['w']+i,(j+1)*data['w']+i+1]]
 return a+(b-a)*u+(d-a)*v if u+v<=1 else e+(d-e)*(1-u)+(b-e)*(1-v)
def contains(data,x,z):
 g=data['meta']['georef'];c=(x+ORIGIN[0]-g['bE'])/g['aE'];r=(ORIGIN[1]-z-g['bN'])/g['aN'];return 0<=c<data['w']-1 and 0<=r<data['h']-1
def triangles(poly):
 for p in polys(poly):
  if p.area<1e-10:continue
  for t in constrained_delaunay_triangles(p).geoms:yield list(t.exterior.coords)[:3]
def clip_grid(data,water,patches=()):
 w=data['w'];g=data['meta']['georef'];x0,z0,x1,z1=water.bounds;cs=[(x+ORIGIN[0]-g['bE'])/g['aE'] for x in [x0,x1]];rs=[(ORIGIN[1]-z-g['bN'])/g['aN'] for z in [z0,z1]];out=[];cut_area=0.
 for r in range(max(0,math.floor(min(rs))),min(data['h']-1,math.ceil(max(rs)))):
  for c in range(max(0,math.floor(min(cs))),min(w-1,math.ceil(max(cs)))):
   if any(p['coarseCells'][0]<=c<p['coarseCells'][2] and p['coarseCells'][1]<=r<p['coarseCells'][3] for p in patches):continue
   a=r*w+c
   if all(not data['elev'][i] for i in [a,a+1,a+w,a+w+1]):continue
   va,vb,vd,ve=[vertex(data,cc,rr) for cc,rr in [(c,r),(c+1,r),(c,r+1),(c+1,r+1)]]
   cell=Polygon([(v[0],v[2]) for v in [va,vb,ve,vd]])
   if not water.intersects(cell) or water.intersection(cell).area<1e-9:continue
   flat=[]
   for tri in [[va,vd,vb],[vb,vd,ve]]:
    polygon=Polygon([(v[0],v[2]) for v in tri]);cut=polygon.intersection(water);cut_area+=cut.area
    for t in triangles(polygon.difference(water)):
     # Enforce upward-facing winding in the city's x/z plane.
     if (t[1][0]-t[0][0])*(t[2][1]-t[0][1])-(t[1][1]-t[0][1])*(t[2][0]-t[0][0])>0:t=t[::-1]
     for x,z in t:flat.extend([round(x,5),round(height(data,x,z),5),round(z,5)])
   out.append({'c':c,'r':r,'x':va[0],'z':va[2],'land':flat})
 return {'georef':g,'w':data['w'],'h':data['h'],'cells':out,'removedAreaM2':cut_area}
def main(publish=False):
 hydro=json.loads((HERE/'hydro-tai-o.json').read_text());water=unary_union([Polygon(p['rings'][0],p['rings'][1:]) for p in hydro['water']]);manifest=json.loads((OUT/'manifest.json').read_text());base=json.loads((OUT/'terrain.json').read_text());patches=[json.loads((ROOT/'3d-viewer'/p['url']).read_text()) for p in manifest.get('terrainPatches',[])];base.pop('hydro',None)
 cuts=[clip_grid(base,water,patches)]+[clip_grid(p,water) for p in patches if Polygon([(vertex(p,c,r)[0],vertex(p,c,r)[2]) for c,r in [(0,0),(p['w']-1,0),(p['w']-1,p['h']-1),(0,p['h']-1)]]).intersects(water)]
 hydro['terrainCuts']=cuts;bed=[]
 for t in triangles(water):
  if (t[1][0]-t[0][0])*(t[2][1]-t[0][1])-(t[1][1]-t[0][1])*(t[2][0]-t[0][0])>0:t=t[::-1]
  for x,z in t:bed.extend([round(x,5),hydro['illustrativeBed'],round(z,5)])
 hydro['bedTriangles']=bed;walls=[];boundary=box(*hydro['bounds']).boundary
 def bank(x,z):
  p=next((p for p in patches if contains(p,x,z)),base);return height(p,x,z)
 for p in polys(water):
  for ring in [p.exterior,*p.interiors]:
   coords=list(ring.coords)
   for a,b in zip(coords,coords[1:]):
    if boundary.distance(Point((a[0]+b[0])/2,(a[1]+b[1])/2))<1e-6:continue
    # Subdivide at <=2.5m solely to follow the existing terrain interpolation.
    n=max(1,math.ceil(math.dist(a,b)/2.5));points=[(a[0]+(b[0]-a[0])*i/n,a[1]+(b[1]-a[1])*i/n) for i in range(n+1)]
    for aa,bb in zip(points,points[1:]):
     ha,hb=bank(*aa),bank(*bb)
     if max(ha,hb)<=hydro['illustrativeBed']+.001:continue
     for v in [(aa[0],ha,aa[1]),(aa[0],-4,aa[1]),(bb[0],hb,bb[1]),(bb[0],hb,bb[1]),(aa[0],-4,aa[1]),(bb[0],-4,bb[1])]:walls.extend(round(k,5) for k in v)
 hydro['bankTriangles']=walls;base['hydro']=hydro
 staged=HERE/'hydro-terrain.json';staged.write_text(json.dumps(base,separators=(',',':'))+'\n')
 report={'originalElevationSha256':hashlib.sha256(json.dumps(base['elev']).encode()).hexdigest(),'terrainGrids':[{k:v for k,v in c.items() if k!='cells'}|{'removedCells':len(c['cells']),'replacementLandTriangles':sum(len(x['land'])//9 for x in c['cells'])} for c in cuts],'bedTriangles':len(bed)//9,'bankTriangles':len(walls)//9,'outputBytes':staged.stat().st_size,'hydroBytes':len(json.dumps(hydro,separators=(',',':'))),'rawSourceElevationsChanged':False,'sourceModelsChanged':False,'illustrativeBed':-4,'terrainSha256':hashlib.sha256(staged.read_bytes()).hexdigest()}
 (DOC/'hydro-terrain-audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
 if publish:(OUT/'terrain.json').write_bytes(staged.read_bytes())
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--publish',action='store_true');main(p.parse_args().publish)
