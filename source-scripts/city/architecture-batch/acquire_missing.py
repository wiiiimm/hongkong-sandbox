"""HKS-208 bounded missing landmark source pass. Stages only, 20 MB range cap."""
import gzip,hashlib,importlib.util,io,json,pathlib,sqlite3,struct,sys,urllib.parse,urllib.request,zipfile
H=pathlib.Path(__file__).resolve().parent;R=H.parents[2];W=H/'sources/acquisition';CAP=20_000_000
TARGET_IDS=[324948,322573,252035,319803,246271,246272,248218]
def read(p):return json.loads(p.read_bytes())
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
def module(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def main():
 from shapely.geometry import Polygon,Point
 from pyproj import Transformer
 W.mkdir(parents=True,exist_ok=True);c=sqlite3.connect('file:'+str(H.parent/'building-batch/local/buildings.sqlite')+'?mode=ro',uri=True);c.row_factory=sqlite3.Row
 targets=[dict(c.execute('select * from buildings where object_id=? and active=1',(i,)).fetchone()) for i in TARGET_IDS];nearby=[dict(b) for b in c.execute('select * from buildings where active=1') if any(abs(b['x']-t['x'])<200 and abs(b['z']-t['z'])<200 for t in targets)]
 # This similarly named source record is geographically unrelated to Victoria Peak.
 excluded=dict(c.execute('select uid,csuid,name,x,z from buildings where object_id=329094 and active=1').fetchone())
 if not (W/'index.json').exists():
  features={};requests=[]
  for t in targets:
   e=t['x']+834500;n=816500-t['z'];params=dict(f='json',geometry=f'{e-80},{n-80},{e+80},{n+80}',geometryType='esriGeometryEnvelope',inSR=2326,outSR=2326,spatialRel='esriSpatialRelIntersects',outFields='*',returnGeometry='true')
   url='https://portal.csdi.gov.hk/server/rest/services/common/landsd_rcd_1742809441342_98380/FeatureServer/0/query?'+urllib.parse.urlencode(params)
   with urllib.request.urlopen(url,timeout=60) as response:d=json.load(response)
   assert d.get('features') and not d.get('exceededTransferLimit'),d
   requests.append({'uid':t['uid'],'url':url})
   for f in d['features']:features[f['attributes']['SHEETNO']]=f
  write(W/'index.json',{'features':list(features.values()),'requests':requests})
 index=read(W/'index.json');tile_targets={}
 for f in index['features']:
  poly=Polygon(f['geometry']['rings'][0]);ts=[t for t in targets if poly.intersects(Point(t['x']+834500,816500-t['z']).buffer(80))]
  if ts:tile_targets[f['attributes']['SHEETNO']]=ts
 ids={b['object_id']for b in nearby};sys.path.insert(0,str(H.parent/'landsd-territory'));from retain import iter_features
 source=H.parent/'landsd-territory/landsd-hong-kong-source.geojson.gz';project=Transformer.from_crs(4326,2326,always_xy=True);features=[]
 for f in iter_features(source):
  if f['properties']['OBJECTID']not in ids:continue
  polygons=[f['geometry']['coordinates']]if f['geometry']['type']=='Polygon'else f['geometry']['coordinates'];features.append({'attributes':f['properties'],'geometry':{'rings':[[list(project.transform(*p))for p in ring]for poly in polygons for ring in poly]}})
 (W/'official-selection.json.gz').write_bytes(gzip.compress(json.dumps({'datasetVersion':'Building_Outline_Public_v20260819','source':str(source.relative_to(R)),'features':features},separators=(',',':')).encode(),mtime=0))
 fetch=module('shared_architecture_fetch',H.parent/'mui-wo-models/fetch.py');original=urllib.request.urlopen;transferred=max(sum(read(p).get('transferredBytes',0)for p in (W/'sources').glob('*/download.json')),read(W/'transfer-ledger.json')['bytes'] if (W/'transfer-ledger.json').exists() else 0);new=0
 def bounded(request,*args,**kwargs):
  nonlocal transferred,new
  span=request.get_header('Range') if isinstance(request,urllib.request.Request) else None
  assert span and span.startswith('bytes='),'Only explicit bounded byte-range model calls allowed'
  value=span[6:];maximum=int(value[1:])if value.startswith('-')else int(value.split('-')[1])-int(value.split('-')[0])+1
  if transferred+maximum>CAP:raise RuntimeError(f'20 MB cumulative acquisition cap; used {transferred}, next {maximum}')
  response=original(request,*args,**kwargs);actual=int(response.headers['Content-Length']);assert actual<=maximum;transferred+=actual;new+=actual;write(W/'transfer-ledger.json',{'bytes':transferred,'limit':CAP,'includesPriorDirectoryOnlyRequests':True});return response
 urllib.request.urlopen=bounded
 try:
  for sheet,ts in tile_targets.items():fetch.fetch_tiles(W,[sheet],['BUILDING/B'+t['csuid'][:10] for t in ts])
 finally:urllib.request.urlopen=original
 sys.path.insert(0,str(R/'docs/astra-city/mui-wo-buildings/review'));from prepare_model_sample import stage
 matches={t['uid']:[]for t in targets};archives=[]
 for sheet in tile_targets:
  folder=W/'sources'/sheet;d=read(folder/'download.json');archive=folder/(sheet+'.zip');assert hashlib.sha256(archive.read_bytes()).hexdigest()==d['sha256'];m=stage(archive,d,W/'official-selection.json.gz',H/'staged'/sheet);archives.append({'sheet':sheet,'sourceCache':str(archive.relative_to(R)),'sourceCacheSHA256':d['sha256'],'transferredBytes':d['transferredBytes'],'sourceTileRevision':d['revisionDate'],'prefixes':d.get('memberPrefixes'),'sourceEntries':len(d['entries'])})
  for t in targets:
   for s in m['models']:
    if s['geoRefNo']==t['csuid'][:10]:matches[t['uid']].append({'sheet':sheet,'modelId':s['id'],'manifest':str((H/'staged'/sheet/'manifest.json').relative_to(R)),'officialBuildingCSUIDs':s['officialBuildingCSUIDs'],'officialMatches':s['officialMatches'],'standardMatch':t['csuid']in s['officialBuildingCSUIDs'],'nativeBounds':s['worldBounds']})
 directory_checks=[];directory_entries={t['uid']:[] for t in targets}
 for p in (W/'sources').glob('*/zip-directory.bin'):
  raw=p.read_bytes();end=raw.rfind(b'PK\x05\x06');assert end>=0;header=struct.unpack('<4s4H2LH',raw[end:end+22]);assert header[1]==header[2]==0 and header[3]==header[4]
  buffer=bytearray(header[6]+len(raw));buffer[header[6]:]=raw
  with zipfile.ZipFile(io.BytesIO(buffer)) as z:names=z.namelist()
  assert len(names)==header[4];directory_checks.append({'sheet':p.parent.name,'completeEntries':len(names),'directorySHA256':hashlib.sha256(raw).hexdigest()})
  for t in targets:
   directory_entries[t['uid']].extend({'sheet':p.parent.name,'entry':n}for n in names if n.endswith('.gltf') and t['csuid'][:10]in n)
 rows=[{'uid':t['uid'],'name':t['name'],'buildingCSUID':t['csuid'],'sourceBaseTop':[t['source_base'],t['source_top']],'outcome':'staged-standard-match'if any(m['standardMatch']for m in matches[t['uid']])else 'staged-exact-reference-requires-match-review'if matches[t['uid']]else 'no-exact-reference-model-in-checked-source-sheets','models':matches[t['uid']],'completeDirectoryExactReferences':directory_entries[t['uid']]}for t in targets]
 report={'issue':'HKS-208','policy':'No model vertical multiplier or coordinate adjustments; native HKPD 1x retained. Staging only.','requestedRecords':8,'targetedRecords':7,'neighbouringFootprints':len(features),'rows':rows,'excluded':[dict(excluded,reason='Namesake outside Victoria Peak; not the requested Peak Tower landmark.')],'archives':archives,'completeDirectoryChecks':directory_checks,'cumulativeTransferBytes':transferred,'newTransferBytes':new,'transferCapBytes':CAP,'aiCalls':0}
 write(H/'missing-source-report.json',report);print(json.dumps(report,indent=2))
if __name__=='__main__':main()
