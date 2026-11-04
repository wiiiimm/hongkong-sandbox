"""Stage an exact bounded marine cut using existing hydro triangle helpers.
Raw elevation arrays and source model geometry are left intact.
"""
import math,gzip,hashlib,json,pathlib,sys,xml.etree.ElementTree as ET
from shapely.geometry import Polygon,Point,box
from shapely.ops import unary_union
from shapely import make_valid
ROOT=pathlib.Path(__file__).resolve().parents[3];HERE=pathlib.Path(__file__).resolve().parent;DOC=ROOT/'docs/astra-city/tsing-ma'
sys.path.insert(0,str(HERE.parent/'tai-o-completion'))
from hydro_prepare import positions,local,G
from hydro_terrain import clip_grid,triangles,height,contains
BOUNDS=[824200,823000,826900,824000]
def stage(*,here=HERE,doc=DOC,bounds=BOUNDS,region='tsing-ma',sample_points=None,terrain_path=None):
 HERE=pathlib.Path(here);DOC=pathlib.Path(doc);BOUNDS=bounds
 rows=[]
 for p in sorted((HERE/'hydro-sources').glob('*-ContourPoly.gml.gz')):
  raw=gzip.decompress(p.read_bytes())
  for m in ET.fromstring(raw).findall(G+'featureMember'):
   f=list(m)[0];a={local(t.tag):t.text for t in f if not list(t)}
   if a.get('DATASTATUS')!='E':continue
   parts=[make_valid(Polygon(positions(q.find(G+'exterior/.//'+G+'posList')),[positions(n) for n in q.findall(G+'interior/.//'+G+'posList')])) for q in f.findall('.//'+G+'PolygonPatch')]
   if parts:rows.append(({'id':local(f.tag)+'/'+a['FEATURE_ID'],'attributes':a,'file':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(raw).hexdigest()},unary_union(parts)))
 E0,N0,E1,N1=BOUNDS;scope=box(E0-834500,816500-N1,E1-834500,816500-N0)
 selected=[(r,g) for r,g in rows if g.intersects(scope)];land=unary_union([g for r,g in selected]).intersection(scope);water=scope.difference(land)
 polys=list(water.geoms) if hasattr(water,'geoms') else [water]
 base=json.loads((ROOT/'3d-viewer/city/data/terrain.json').read_text());patch=json.loads(pathlib.Path(terrain_path or HERE/f'terrain-{region}.json').read_text());cuts=[clip_grid(base,water,[patch]),clip_grid(patch,water)]
 bed=[]
 for tri in triangles(water):
  if (tri[1][0]-tri[0][0])*(tri[2][1]-tri[0][1])-(tri[1][1]-tri[0][1])*(tri[2][0]-tri[0][0])>0:tri=tri[::-1]
  for x,z in tri:bed.extend([round(x,5),-4,round(z,5)])
 walls=[];boundary=scope.boundary
 for p in polys:
  for ring in [p.exterior,*p.interiors]:
   for a,b in zip(list(ring.coords),list(ring.coords)[1:]):
    if boundary.distance(Point((a[0]+b[0])/2,(a[1]+b[1])/2))<1e-6:continue
    n=max(1,math.ceil(math.dist(a,b)/2.5));pts=[(a[0]+(b[0]-a[0])*i/n,a[1]+(b[1]-a[1])*i/n) for i in range(n+1)]
    for aa,bb in zip(pts,pts[1:]):
     ha=height(patch if contains(patch,*aa) else base,*aa);hb=height(patch if contains(patch,*bb) else base,*bb)
     if max(ha,hb)<=-3.999:continue
     for v in [(aa[0],ha,aa[1]),(aa[0],-4,aa[1]),(bb[0],hb,bb[1]),(bb[0],hb,bb[1]),(aa[0],-4,aa[1]),(bb[0],-4,bb[1])]:walls.extend(round(k,5) for k in v)
 out={'schemaVersion':1,'region':region,'bounds':list(scope.bounds),'boundsHK1980':BOUNDS,'illustrativeBed':-4,'source':{'provider':'Lands Department / HKSAR Government','dataset':'iB5000 closed ContourPoly','datasetId':'landsd_rcd_1637224243141_96556','derivation':'Bounded complement of original existing-land polygons. No bridge-axis buffer or invented coastline. Land and tower-foundation islet preserved exactly in plan.','verticalNote':'-4m is an illustrative render bed, not surveyed bathymetry. Original DTM elevation arrays and bridge HKPD coordinates are unchanged.','features':[r for r,g in selected],'downloads':[json.loads(p.read_text()) for p in sorted((HERE/'hydro-sources').glob('*-download.json'))]},'water':[{'id':region+'-channel-'+str(i),'rings':[[[round(x,5),round(z,5)] for x,z in r.coords] for r in [p.exterior,*p.interiors]],'area':p.area} for i,p in enumerate(polys)],'terrainCuts':cuts,'bedTriangles':bed,'bankTriangles':walls}
 (HERE/f'hydro-{region}.json').write_text(json.dumps(out,separators=(',',':'))+'\n')
 samples=[{'world':[x,z],'mappedWater':water.covers(Point(x,z))} for x,z in (sample_points if sample_points is not None else [(-9800,-6770),(-9500,-6860),(-9250,-6940),(-9000,-7010),(-8750,-7090),(-8500,-7160),(-8250,-7240)])]
 report={'landFeatures':len(selected),'waterAreaM2':water.area,'landAreaM2':land.area,'waterPolygons':len(polys),'waterVertices':sum(len(r) for p in out['water'] for r in p['rings']),'removedTerrainCells':sum(len(cut['cells']) for cut in cuts),'removedTriangleAreaM2':sum(cut['removedAreaM2'] for cut in cuts),'replacementLandTriangles':sum(len(c['land'])//9 for cut in cuts for c in cut['cells']),'bedTriangles':len(bed)//9,'bankTriangles':len(walls)//9,'terrainGrids':[{k:v for k,v in cut.items() if k!='cells'}|{'cutCells':len(cut['cells'])} for cut in cuts],'sourceElevationsSha256':hashlib.sha256(json.dumps(base['elev']).encode()).hexdigest(),'ridgeSamples':samples,'note':'Only bounded mapped water is cut. No walking permission or measured bathymetry is inferred.'}
 (DOC/'hydro-audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));return out,land,water
if __name__=='__main__':stage()
