"""Prepare source-coordinate Tai O tidal water; no bathymetric measurements are inferred."""
import datetime,gzip,hashlib,json,pathlib,subprocess,xml.etree.ElementTree as ET,zipfile
from shapely.geometry import Polygon,box,mapping
from shapely.ops import unary_union
from shapely import make_valid
from hydro_prepare import HERE,ROOT,DOC,G,BOUNDS,positions,local,load
INDEX='https://portal.csdi.gov.hk/server/rest/services/common/landsd_rcd_1637224243141_96556/MapServer/0/query'
LAYERS=['Relief/ContourPoly','Hydrography/HydrographyPoly','Hydrography/HydrographyLine','Transportation/RoadPoly','Transportation/PedNBikePoly']
def fetch():
 index=HERE/'hydro-ib5000-index.json'
 if not index.exists():
  subprocess.run(['curl','-fLsS','--get',INDEX,'--data-urlencode','f=json','--data-urlencode','geometry='+','.join(map(str,BOUNDS)),'--data-urlencode','geometryType=esriGeometryEnvelope','--data-urlencode','inSR=2326','--data-urlencode','outSR=2326','--data-urlencode','outFields=*','--data-urlencode','returnGeometry=true','-o',str(index)],check=True)
 records=[]
 for f in json.loads(index.read_text())['features']:
  a=f['attributes'];sheet=a['SHEETNO'];folder=HERE/'hydro-sources';archive=folder/f'iB5000-{sheet}.zip';meta=folder/f'iB5000-{sheet}-download.json'
  if not archive.exists():subprocess.run(['curl','-fLsS','--max-time','120',a['GML'],'-o',str(archive)],check=True)
  entries=[]
  with zipfile.ZipFile(archive) as z:
   for name in LAYERS:
    source=f'{sheet}/Layers/{name}.gml'
    if source not in z.namelist():continue
    raw=z.read(source);dest=folder/f'iB5000-{sheet}-{name.split("/")[-1]}.gml.gz';dest.write_bytes(gzip.compress(raw,mtime=0));entries.append({'file':dest.name,'sourceEntry':source,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
  r={'sheet':a,'downloadURL':a['GML'],'archiveBytes':archive.stat().st_size,'archiveSha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'fetchedAtUTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'entries':entries}
  if meta.exists():r['fetchedAtUTC']=json.loads(meta.read_text())['fetchedAtUTC']
  meta.write_text(json.dumps(r,indent=2)+'\n');records.append(r)
 return records

def ib5000():
 rows=[]
 for path in sorted((HERE/'hydro-sources').glob('iB5000-*.gml.gz')):
  raw=gzip.decompress(path.read_bytes())
  for m in ET.fromstring(raw).findall(G+'featureMember'):
   f=list(m)[0];a={local(t.tag):t.text for t in f if not list(t)};parts=[]
   if a.get('DATASTATUS')!='E':continue
   for p in f.findall('.//'+G+'PolygonPatch'):
    parts.append(make_valid(Polygon(positions(p.find(G+'exterior/.//'+G+'posList')),[positions(n) for n in p.findall(G+'interior/.//'+G+'posList')])))
   if not parts:continue
   g=unary_union(parts);rows.append(({'id':local(f.tag)+'/'+a['FEATURE_ID'],'layer':local(f.tag),'attributes':a,'sourceFile':str(path.relative_to(ROOT)),'sourceSha256':hashlib.sha256(raw).hexdigest()},g))
 return rows

def polys(g):
 if g.geom_type=='Polygon':yield g
 elif hasattr(g,'geoms'):
  for p in g.geoms:yield from polys(p)

def build():
 sources=fetch();rows=ib5000();x0,n0,x1,n1=BOUNDS;clip=box(x0-834500,816500-n1,x1-834500,816500-n0)
 landrows=[(r,g) for r,g in rows if r['layer']=='ContourPoly' and g.intersects(clip)]
 land=unary_union([g for r,g in landrows]).intersection(clip)
 # Only explicit surface rivers/channels supplement the mapped coast. Culverts, ponds,
 # catchwaters, breakwaters and cartographic zero-Z values do not become tidal water.
 rivers=[(r,g) for r,g in load() if r['layer']=='HydroPolygon' and r['attributes'].get('HYDROPOLYGONTYPE') in ['RIV','CHA','NUL'] and g.intersects(clip)]
 ocean=clip.difference(land)
 # Retain connected tidal rivers only, excluding disconnected uphill inland streams.
 connected=[(r,g) for r,g in rivers if g.intersects(ocean)]
 water=make_valid(unary_union([ocean,*[g for r,g in connected]]).intersection(clip))
 out={'schemaVersion':1,'region':'tai-o','bounds':list(clip.bounds),'boundsHK1980':BOUNDS,'illustrativeBed':-4,'source':{'provider':'Lands Department / HKSAR Government','dataset':'iB5000 closed ContourPoly land extent; connected iB1000 HydroPolygon rivers/channels','derivation':'Sea is the bounded complement of original closed land polygons, plus intersecting explicit RIV/CHA/NUL polygons. No manual shoreline gap closure or raster tracing.','coordinatePrecision':'Original GML coordinates retained; precision is not a survey accuracy claim.','verticalNote':'The -4m render bed is illustrative and is not bathymetry. Raw source elevation arrays and source building geometry remain unchanged.','sources':sources,'landFeatures':[r for r,g in landrows],'riverFeatures':[r for r,g in connected],'currentReference':'https://www.landsd.gov.hk/doc/en/mapping/ehkg/MapPages/GeoPDF/IS08_TaiO.pdf'},'water':[]}
 for i,p in enumerate(polys(water)):
  out['water'].append({'id':f'tai-o-tidal-water-{i}','rings':[[[round(x,5),round(z,5)] for x,z in ring.coords] for ring in [p.exterior,*p.interiors]],'area':p.area})
 (HERE/'hydro-tai-o.json').write_text(json.dumps(out,separators=(',',':'))+'\n')
 report={'landSourceFeatures':len(landrows),'connectedRiverFeatures':len(connected),'waterPolygons':len(out['water']),'waterAreaM2':water.area,'landAreaM2':clip.area-water.area,'vertices':sum(len(r) for p in out['water'] for r in p['rings']),'bounds':list(clip.bounds),'sourceBuildingGeometryChanged':False}
 DOC.mkdir(parents=True,exist_ok=True);(DOC/'hydro-source-audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
 # Retain directly sourced land/water for independent route/infrastructure audits.
 (HERE/'hydro-land.geojson.gz').write_bytes(gzip.compress(json.dumps({'type':'FeatureCollection','features':[{'type':'Feature','properties':r,'geometry':mapping(g.intersection(clip))} for r,g in landrows]},separators=(',',':')).encode(),mtime=0))
 return out,water,land,rows
if __name__=='__main__':build()
