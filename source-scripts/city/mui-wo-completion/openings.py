"""Candidate physical openings in the exact public promenade floor boundary."""
import gzip,json,pathlib,math
import numpy as np
from shapely.geometry import Polygon,Point
from shapely.ops import unary_union
HERE=pathlib.Path(__file__).resolve().parent
j=json.loads(gzip.decompress((HERE/'infrastructure-models.json.gz').read_bytes()));m=next(m for m in j['models'] if m['id'].endswith('/I178711420803063C0'));tri=np.array(m['modelGeometry']['position']).reshape(-1,3,3);floor=unary_union([Polygon(tri[i][:,[0,2]]) for i in m['walkTriangleIndices']]);rows=[]
for p in (list(floor.geoms) if hasattr(floor,'geoms') else [floor]):
 coords=list(p.exterior.coords)
 for a,b in zip(coords,coords[1:]):
  d=math.dist(a,b)
  if d<.2:continue
  n=[-(b[1]-a[1])/d,(b[0]-a[0])/d]
  for q in np.linspace(.05,.95,max(2,math.ceil(d))):
   c=[a[k]+(b[k]-a[k])*q for k in [0,1]]
   if c[0]<-16520:continue
   if not floor.contains(Point(c[0]+n[0]*.8,c[1]+n[1]*.8)):n=[-v for v in n]
   inside=[c[k]+n[k] for k in [0,1]];outside=[c[k]-n[k]*1.2 for k in [0,1]]
   if floor.contains(Point(inside)) and not floor.intersects(Point(outside)):rows.append({'inside':inside,'outside':outside,'edge':c})
(HERE/'opening-candidates.json').write_text(json.dumps(rows,separators=(',',':'))+'\n');print(len(rows))
