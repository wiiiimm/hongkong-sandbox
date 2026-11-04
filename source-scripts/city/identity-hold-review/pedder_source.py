"""Review Pedder native source extent and heights without moving or trimming it."""
import pathlib,json,sys,sqlite3,hashlib,argparse,urllib.request,urllib.parse,datetime
import numpy as np
from shapely.geometry import Polygon
from shapely import make_valid,union_all
ROOT=pathlib.Path(__file__).resolve().parents[3];HERE=pathlib.Path(__file__).resolve().parent;DOC=ROOT/'docs/astra-city/identity-hold-review'
sys.path.insert(0,str(ROOT/'docs/astra-city/mui-wo-buildings/review'));from bake_model_geometry import bake
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
parser=argparse.ArgumentParser();parser.add_argument('--refresh',action='store_true');args=parser.parse_args()
if args.refresh:
 url='https://portal.csdi.gov.hk/server/rest/services/common/landsd_rcd_1637211194312_35158/MapServer/0/query?'+urllib.parse.urlencode({'f':'json','objectIds':'69002','outFields':'OBJECTID,BuildingCSUID,GeoRefNo,BuildingID,BuildingBlockType,BaseHeight,TopHeight','returnGeometry':'true','outSR':'2326'})
 with urllib.request.urlopen(url,timeout=45)as response:raw=response.read(200001)
 assert len(raw)<=200000
 live=json.loads(raw);assert len(live['features'])==1 and not live.get('exceededTransferLimit')
 (DOC/'pedder-live-source.json').write_bytes(raw)
 (DOC/'pedder-live-source-provenance.json').write_text(json.dumps({'url':url,'fetchedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)},indent=2)+'\n')
live=json.loads((DOC/'pedder-live-source.json').read_text());attrs=live['features'][0]['attributes']
assert [attrs['OBJECTID'],attrs['BuildingCSUID'],attrs['BaseHeight'],attrs['TopHeight']]==[69002,'3420215907T20050430',5.5,43.8]

p=ROOT/'source-scripts/city/central-completion/staged/11-SW-8D/manifest.json';m=next(m for m in json.loads(p.read_text())['models']if m['id']=='B342021590701063C0')
for f,h in m['sourceHashes'].items():assert sha(p.parent/f)==h
v=np.array(bake(m,p.parent)['position']).reshape(-1,3);t=v.reshape(-1,3,3)
c=sqlite3.connect(f'file:{ROOT}/source-scripts/city/building-batch/local/buildings.sqlite?mode=ro',uri=True);c.row_factory=sqlite3.Row;c.execute('PRAGMA query_only=ON')
bs=[dict(r) for r in c.execute('select uid,name,source_base,source_top,csuid,rings_json,x,z from buildings where active=1 and x between -400 and -150 and z between 500 and 750')];c.close()
def poly(b):
 r=json.loads(b['rings_json']);return make_valid(Polygon(r[0],r[1:]))
def projection(ts):return union_all([p for tri in ts if (p:=Polygon(tri[:,[0,2]])).area>1e-8])
pr=projection(t);target=poly(next(b for b in bs if b['uid']=='landsd/69002:0'))
near=[]
for b in bs:
 f=poly(b);area=pr.intersection(f).area
 if area>.01:near.append({k:b[k]for k in ['uid','name','csuid','source_base','source_top']}|{'sourceFootprintArea':f.area,'nativeIntersectedArea':area,'footprintCovered':area/f.area,'nativeProjectionInsideFootprint':area/pr.area})
ys,counts=np.unique(np.round(v[:,1],3),return_counts=True)
levels=[]
for level in [35,39,43.8,45,47.8,48,50,52]:
 high=projection(t[t[:,:,1].min(axis=1)>=level]);levels.append({'minTriangleY':level,'projectedArea':high.area,'fractionOfTargetFootprint':high.intersection(target).area/target.area})
up=[]
for tri in t:
 n=np.cross(tri[1]-tri[0],tri[2]-tri[0]);area=np.linalg.norm(n)/2
 if area>0 and n[1]/(area*2)>.95:up.append({'meanY':float(tri[:,1].mean()),'area':float(area)})
roof={}
for r in up:
 k=str(round(r['meanY'],2));roof[k]=roof.get(k,0)+r['area']
out={'issue':'HKS-214','uid':'landsd/69002:0','sourceModel':m['id'],'sourceManifest':str(p.relative_to(ROOT)),'sourceHashes':m['sourceHashes'],'verticalScale':1,'sourceGeometryEdited':False,'nativeBounds':m['worldBounds'],'triangles':len(t),'sourceBaseTop':[5.5,43.8],'nativeProjectionArea':pr.area,'targetFootprintArea':target.area,'nearbyFootprintIntersections':near,'vertexYFrequency':sorted([{'y':float(y),'count':int(n)}for y,n in zip(ys,counts)],key=lambda r:-r['count'])[:30],'elevatedTriangleProjections':levels,'largestUpwardSurfaceElevations':sorted([{'y':float(y),'area':a}for y,a in roof.items()],key=lambda r:-r['area'])[:20],'status':'held-source-height-and-architecture-conflict','currentGovernmentAttributes':attrs,'currentGovernmentSHA256':sha(DOC/'pedder-live-source.json'),'dbWrites':0}
(DOC/'pedder-source.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:out[k]for k in ['nearbyFootprintIntersections','elevatedTriangleProjections','largestUpwardSurfaceElevations']}))
