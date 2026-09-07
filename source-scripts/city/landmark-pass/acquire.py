"""Bounded named-landmark source pass. Reuses the government range fetcher and stager.
No viewer writes, model shifts or AI calls. Repeat fetches reuse retained bytes.
"""
import argparse,gzip,hashlib,importlib.util,json,pathlib,sqlite3,sys,urllib.parse,urllib.request
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def read(p):return json.loads(p.read_bytes())
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def module(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def plan():
 from shapely.geometry import Polygon,box
 from pyproj import Transformer
 db=sqlite3.connect('file:'+str(HERE.parent/'building-batch/local/buildings.sqlite')+'?mode=ro',uri=True);db.row_factory=sqlite3.Row
 groups=read(HERE.parent/'building-batch/tourist-trial.json')['landmarks'];targets=[r for g in groups if g['id'] in ('po-lin','ngong-ping-village') for r in g['records']]
 # Select group by explicit IDs; fail closed if trial identifiers change.
 if not targets:raise ValueError('Missing landmark groups')
 bs=[dict(db.execute('select * from buildings where uid=? and active=1',(r['uid'],)).fetchone()) for r in targets]
 bounds=[min(b['x'] for b in bs)+834500-150,816500-max(b['z'] for b in bs)-150,max(b['x'] for b in bs)+834500+150,816500-min(b['z'] for b in bs)+150]
 params=dict(f='json',geometry=','.join(map(str,bounds)),geometryType='esriGeometryEnvelope',inSR=2326,outSR=2326,spatialRel='esriSpatialRelIntersects',outFields='*',returnGeometry='true')
 url='https://portal.csdi.gov.hk/server/rest/services/common/landsd_rcd_1742809441342_98380/FeatureServer/0/query?'+urllib.parse.urlencode(params)
 if not (HERE/'index.json').exists():
  with urllib.request.urlopen(url,timeout=60) as r:write(HERE/'index.json',json.load(r))
 index=read(HERE/'index.json');assert index.get('features') and not index.get('exceededTransferLimit'),index
 sheets=[f['attributes']['SHEETNO'] for f in index['features']];polygons=[Polygon(f['geometry']['rings'][0]) for f in index['features']]
 selected=[]
 for b in db.execute('select * from buildings where active=1'):
  if any(p.intersects(box(b['x']+834500-150,816500-b['z']-150,b['x']+834500+150,816500-b['z']+150)) for p in polygons):selected.append(dict(b))
 ids={b['object_id'] for b in selected if b['object_id'] is not None}
 sys.path.insert(0,str(HERE.parent/'landsd-territory'));from retain import iter_features
 source=HERE.parent/'landsd-territory/landsd-hong-kong-source.geojson.gz';project=Transformer.from_crs(4326,2326,always_xy=True);features=[]
 for f in iter_features(source):
  if f['properties']['OBJECTID'] not in ids:continue
  polygons=[f['geometry']['coordinates']] if f['geometry']['type']=='Polygon' else f['geometry']['coordinates']
  features.append({'attributes':f['properties'],'geometry':{'rings':[[list(project.transform(*p)) for p in ring] for polygon in polygons for ring in polygon]}})
 raw=json.dumps({'datasetVersion':'Building_Outline_Public_v20260819','derivation':'Retained official territory polygons projected to EPSG:2326; same existing selector method.','source':str(source.relative_to(ROOT)),'features':features},separators=(',',':')).encode()
 (HERE/'official-selection.json.gz').write_bytes(gzip.compress(raw,mtime=0))
 record=dict(groups=[g['id'] for g in groups if g['id'] in ('po-lin','ngong-ping-village')],targets=[r['uid'] for r in targets],prefixes=['BUILDING/B'+b['csuid'][:10] for b in bs]+['TERRAIN'],sheets=sheets,indexRequest=url,selectionForms=len(features),policy='Fetch only named landmark GeoRefNo entries and native terrain; nearby source footprints retained for ambiguity detection.')
 write(HERE/'acquisition-plan.json',record);print(json.dumps({k:v for k,v in record.items() if k not in ('prefixes','targets','indexRequest')}))

def run():
 p=read(HERE/'acquisition-plan.json');fetch=module('shared_landmark_fetch',HERE.parent/'mui-wo-models/fetch.py')
 fetch.fetch_tiles(HERE,p['sheets'],p['prefixes'])
 sys.path.insert(0,str(ROOT/'docs/astra-city/mui-wo-buildings/review'));from prepare_model_sample import stage
 for sheet in p['sheets']:
  folder=HERE/'sources'/sheet;d=read(folder/'download.json');archive=folder/(sheet+'.zip')
  assert hashlib.sha256(archive.read_bytes()).hexdigest()==d['sha256']
  m=stage(archive,d,HERE/'official-selection.json.gz',HERE/'staged'/sheet);print(sheet,m['counts'],flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('step',choices=['plan','run']);a=p.parse_args();plan() if a.step=='plan' else run()
