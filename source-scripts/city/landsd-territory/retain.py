"""Validate/reuse original public LandsD GeoJSON bytes; no renderer/importer copy."""
from __future__ import annotations
import argparse,collections,concurrent.futures,datetime,gzip,hashlib,json,math,pathlib,re,sys,time
from shapely.geometry import shape
from shapely.ops import transform
from shapely.validation import explain_validity
from pyproj import Transformer
from source import HERE,ROOT,DOCS,BASE,DATASET,META,SPEC,utc,digest,encode,atomic,save_json,read_json,request,retained,version

DEFAULT=pathlib.Path('/Users/williamli/projects/wiiiimm/hongkong-sandbox/.claude/worktrees/hong-kong-3d-city-buildings-b86a93/source-scripts/hk-buildings/cache/Building_Outline_Public_v20260819_Building_converted.geojson')
DOWNLOAD=f'https://portal.csdi.gov.hk/csdi-webpage/file-api?dataset_id={DATASET}&format=geojson&layer_name=Building'

def iter_features(path):
 """Incremental standard-library GeoJSON reader; never retain the whole file."""
 opener=gzip.open if pathlib.Path(path).suffix=='.gz' else open
 decoder=json.JSONDecoder();chunk_size=1024*1024
 with opener(path,'rt',encoding='utf-8') as file:
  buffer='';start=None
  while start is None:
   part=file.read(chunk_size)
   if not part:raise ValueError('No GeoJSON features array')
   buffer+=part;match=re.search(r'"features"\s*:\s*\[',buffer)
   if match:start=match.end()
  position=start;ended=False
  while not ended:
   while position<len(buffer) and (buffer[position].isspace() or buffer[position]==','):position+=1
   if position<len(buffer) and buffer[position]==']':ended=True;break
   try:feature,next_position=decoder.raw_decode(buffer,position)
   except json.JSONDecodeError:
    part=file.read(chunk_size)
    if not part:raise ValueError('Incomplete or malformed feature JSON')
    buffer=buffer[position:]+part;position=0;continue
   if not isinstance(feature,dict) or feature.get('type')!='Feature':raise ValueError('Invalid GeoJSON feature')
   yield feature;position=next_position
  trailer=buffer[position:]+file.read()
  if not re.fullmatch(r'\]\s*}\s*',trailer):raise ValueError('Malformed GeoJSON footer')


def compress_source(path):
 target=HERE/'landsd-hong-kong-source.geojson.gz';temp=target.with_name(target.name+'.tmp');h=hashlib.sha256();count=0
 with path.open('rb') as src,temp.open('wb') as dest,gzip.GzipFile(fileobj=dest,mode='wb',filename='',mtime=0,compresslevel=6) as zipped:
  while block:=src.read(1024*1024):h.update(block);zipped.write(block);count+=len(block)
 temp.replace(target)
 return {'file':str(target.relative_to(ROOT)),'originalBytes':count,'uncompressedSHA256':h.hexdigest(),'compressedBytes':target.stat().st_size,'compressedSHA256':digest(target.read_bytes())}


def live_membership():
 def get(name,extra):
  params={'f':'json','where':'1=1',**extra}
  raw,info=request(BASE+'/0/query',params);atomic(HERE/name,raw);save_json(HERE/(name+'.request.json'),info);return json.loads(raw)
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
  ids_future=pool.submit(get,'query-object-ids.json',{'returnIdsOnly':'true','returnGeometry':'false'})
  count_future=pool.submit(get,'query-count.json',{'returnCountOnly':'true','returnGeometry':'false'})
  ids_data,count=ids_future.result(),count_future.result()['count']
 ids=sorted(ids_data['objectIds'])
 if ids_data['objectIdFieldName']!='OBJECTID' or len(ids)!=len(set(ids)) or len(ids)!=count:raise ValueError('Live advertised ID list/count mismatch')
 print(json.dumps({'liveCount':count,'liveIDs':len(ids)}),flush=True)
 return ids


def validate(source):
 stats={'featureCount':0,'geometryTypes':collections.Counter(),'buildingTypes':collections.Counter(),'status':collections.Counter(),'nullFields':collections.Counter(),'invalidGeometries':[],'missingGeometries':[],'unclosedRings':[],'nonFiniteCoordinates':[],'rings':0,'vertices':0,'holes':0,'components':0,'nullBaseHeight':0,'nullTopHeight':0,'bothHeightsPresent':0,'nonPositiveHeights':0,'boundsWGS84':[math.inf,math.inf,-math.inf,-math.inf]}
 ids=[];samples={};sample_ids={1,2,3,1000,10000,50000,100000,150000,200000,250000,300000,342223};saw_types=set();field_sets=collections.Counter()
 for feature in iter_features(source):
  attrs=feature['properties'];oid=attrs['OBJECTID'];ids.append(oid);stats['featureCount']+=1;kind=attrs.get('BuildingBlockType');stats['buildingTypes'][str(kind)]+=1;stats['status'][str(attrs.get('Status'))]+=1;field_sets[tuple(sorted(attrs))]+=1
  for key,value in attrs.items():
   if value is None:stats['nullFields'][key]+=1
  base,top=attrs.get('BaseHeight'),attrs.get('TopHeight');stats['nullBaseHeight']+=base is None;stats['nullTopHeight']+=top is None
  if base is not None and top is not None:
   stats['bothHeightsPresent']+=1;stats['nonPositiveHeights']+=top<=base
  geometry=feature.get('geometry')
  if not geometry:stats['missingGeometries'].append(oid);continue
  typ=geometry['type'];stats['geometryTypes'][typ]+=1
  if typ not in ['Polygon','MultiPolygon']:raise ValueError('Unexpected geometry '+typ)
  polygons=[geometry['coordinates']] if typ=='Polygon' else geometry['coordinates'];stats['components']+=len(polygons)
  for polygon in polygons:
   stats['holes']+=max(0,len(polygon)-1)
   for ring in polygon:
    stats['rings']+=1;stats['vertices']+=len(ring)
    if not ring or ring[0]!=ring[-1]:stats['unclosedRings'].append(oid)
    if not all(isinstance(n,(int,float)) and math.isfinite(n) for point in ring for n in point):stats['nonFiniteCoordinates'].append(oid)
  shp=shape(geometry)
  if not shp.is_valid:stats['invalidGeometries'].append({'OBJECTID':oid,'reason':explain_validity(shp)})
  if not shp.is_empty:
   x0,y0,x1,y1=shp.bounds;b=stats['boundsWGS84'];b[0]=min(b[0],x0);b[1]=min(b[1],y0);b[2]=max(b[2],x1);b[3]=max(b[3],y1)
  key=(kind,base is None,top is None,typ)
  if oid in sample_ids or key not in saw_types:samples[oid]=feature;saw_types.add(key)
  if stats['featureCount']%50000==0:print(json.dumps({'validatedFeatures':stats['featureCount']}),flush=True)
 if len(ids)!=len(set(ids)):raise ValueError('Duplicate source OBJECTIDs')
 stats['uniqueIDs']=len(set(ids));stats['idMin']=min(ids);stats['idMax']=max(ids);stats['propertySchemas']=[{'fields':list(fields),'count':count} for fields,count in field_sets.items()]
 return stats,sorted(ids),samples


def geometry_sample(samples):
 ids=sorted(samples);params={'f':'json','objectIds':','.join(map(str,ids)),'outFields':'*','returnGeometry':'true','outSR':2326,'orderByFields':'OBJECTID'}
 raw,info=request(BASE+'/0/query',params,method='POST');data=json.loads(raw);atomic(HERE/'native-coordinate-sample.json',raw);save_json(HERE/'native-coordinate-sample.json.request.json',info)
 native={f['attributes']['OBJECTID']:f for f in data['features']}
 if set(native)!=set(ids) or data.get('exceededTransferLimit'):raise ValueError('Native sample is incomplete')
 # Reuse Astra's already-tested LandsD ring converter instead of implementing
 # a second polygon/holes/staging policy. It returns world coordinates.
 import importlib.util
 script=ROOT/'source-scripts/city/mui-wo-buildings/build.py';spec=importlib.util.spec_from_file_location('astra_muiwo_buildings',script);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 projector=Transformer.from_crs(4326,2326,always_xy=True);rows=[];mismatches=[]
 for oid in ids:
  feature=samples[oid];a=transform(projector.transform,shape(feature['geometry']));world,repaired=module.official_geometry(native[oid]);b=transform(lambda x,y:(x+834500,816500-y),world);error=a.hausdorff_distance(b)
  keys=['GeoRefNo','BuildingBlockType','BuildingCSUID','BuildingID','Status','BuildingNameEN','BuildingNameTC','BaseHeight','TopHeight','Storeys','StoreysInBasement']
  bad=[key for key in keys if feature['properties'].get(key)!=native[oid]['attributes'].get(key)]
  if bad:mismatches.append({'OBJECTID':oid,'fields':bad})
  rows.append({'OBJECTID':oid,'type':feature['properties'].get('BuildingBlockType'),'vertices':sum(len(r) for p in ([feature['geometry']['coordinates']] if feature['geometry']['type']=='Polygon' else feature['geometry']['coordinates']) for r in p),'hausdorffMetres':error,'propertyMismatches':bad,'nativeRepairForComparison':repaired})
 curve_ids=[r['OBJECTID'] for r in rows if r['hausdorffMetres']>.02]
 if curve_ids:
  curve_params={'f':'json','objectIds':','.join(map(str,curve_ids)),'outFields':'OBJECTID','returnGeometry':'true','returnTrueCurves':'true','outSR':2326}
  curve_raw,curve_info=request(BASE+'/0/query',curve_params,method='POST');atomic(HERE/'native-true-curves-sample.json',curve_raw);save_json(HERE/'native-true-curves-sample.json.request.json',curve_info)
  curved={f['attributes']['OBJECTID'] for f in json.loads(curve_raw)['features'] if 'curveRings' in f.get('geometry',{})}
  if curved!=set(curve_ids):raise ValueError('Unexplained native geometry discrepancy')
 for row in rows:
  row['nativeTrueCurves']=row['OBJECTID'] in curve_ids
  row['comparisonToleranceMetres']=1.0 if row['nativeTrueCurves'] else .02
 if mismatches or any(r['hausdorffMetres']>r['comparisonToleranceMetres'] for r in rows):raise ValueError('Native CRS/attribute sample differs from retained source: '+str(mismatches))
 return {'sourceCRS':'OGC:CRS84 (GeoJSON longitude, latitude)','nativeCRS':'EPSG:2326','transformer':projector.description,'samples':rows,'maximumHausdorffMetres':max(r['hausdorffMetres'] for r in rows),'ordinaryPolygonToleranceMetres':.02,'curveDensificationToleranceMetres':1.0,'curveNote':'The retained official GeoJSON and REST polygon response independently linearise native curveRings; the curved sample has a measured sub-metre boundary difference, preserved and identified. This is not a projection-accuracy claim.','attributeComparison':'Identity, type, status, names, both elevations and storeys; original date strings retained (ArcGIS REST uses epoch milliseconds).'}


def main():
 parser=argparse.ArgumentParser();parser.add_argument('--source',type=pathlib.Path,default=DEFAULT);args=parser.parse_args();DOCS.mkdir(parents=True,exist_ok=True)
 source=args.source
 if not source.is_file():parser.error('Provide the already-retained official GeoJSON with --source; official download URL is '+DOWNLOAD)
 started=utc()
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
  ids_future=pool.submit(live_membership);compression_future=pool.submit(compress_source,source);stats_future=pool.submit(validate,source)
  stats,ids,samples=stats_future.result();print(json.dumps({'allSourceFeatures':stats['featureCount'],'samples':len(samples)}),flush=True)
  live_ids=ids_future.result();snapshot=compression_future.result()
 if ids!=live_ids:raise ValueError('Retained source IDs differ from live official membership')
 html,metadata=retained('dataset-metadata.html',META,json_expected=False);dataset_version=version(html.decode())
 if dataset_version not in source.name:raise ValueError('Retained filename does not match live advertised version')
 coordinate_sample=geometry_sample(samples)
 manifest={'schemaVersion':1,'datasetId':DATASET,'datasetVersion':dataset_version,'sourceURL':DOWNLOAD,'serviceURL':BASE+'/0','metadataURL':META,'specificationURL':SPEC,'reuse':{'origin':'Existing original public source bytes reused from the repository comparison worktree cache. No other-model implementation or rendered output was copied.','originalPath':str(source),'originalFilesystemModifiedAtUTC':datetime.datetime.fromtimestamp(source.stat().st_mtime,datetime.timezone.utc).isoformat(),'originalDownloadTimestamp':'Not recorded by the retained cache; file modification time is not asserted to be the download timestamp.'},'validationStartedAtUTC':started,'validatedAtUTC':utc(),'sourceCRS':{'name':'OGC:CRS84','axes':['longitude','latitude'],'units':'degrees','nativeServiceCRS':'EPSG:2326'},'verticalDatum':{'name':'Hong Kong Principal Datum','units':'metres','fields':['BaseHeight','TopHeight'],'precision':'Approximate source elevations, preserved without terrain lifting or substituted values','source':SPEC},'snapshot':snapshot,'completeness':{'sourceCount':len(ids),'sourceUniqueIDs':len(set(ids)),'liveCount':len(live_ids),'liveUniqueIDs':len(set(live_ids)),'exactIDsMatch':True,'objectIdSHA256':digest(encode(ids)),'allTypesAndNullsRetained':True,'bytePreservingCompression':True},'validation':stats,'nativeCoordinateCheck':coordinate_sample,'integration':'Read compressed features incrementally with iter_features(); project via existing pyproj and reuse source-scripts/city/mui-wo-buildings/build.py stage_feature(). No live city tiles changed.'}
 save_json(HERE/'manifest.json',manifest);save_json(DOCS/'verification.json',manifest);print(json.dumps({'complete':True,'count':len(ids),'snapshot':snapshot,'maximumCoordinateErrorMetres':coordinate_sample['maximumHausdorffMetres'],'invalidGeometries':len(stats['invalidGeometries'])}),flush=True)

if __name__=='__main__':main()
