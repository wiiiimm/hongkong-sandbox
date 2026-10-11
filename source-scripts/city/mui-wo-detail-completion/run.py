"""Audit every retained Mui Wo form; stage exact government replacements only.
Reuse the validated source decoder, matching screen, byte-range fetcher and packer.
Live tiles/terrain remain untouched. Run fetch, then build.
"""
import argparse, collections, gzip, hashlib, importlib.util, json, pathlib, sys
from shapely.geometry import Polygon, Point
from pyproj import Transformer
HERE=pathlib.Path(__file__).resolve().parent; ROOT=HERE.parents[2]
DOC=ROOT/'docs/astra-city/mui-wo-detail-completion'
REVIEW=ROOT/'docs/astra-city/mui-wo-buildings/review'
sys.path.insert(0,str(REVIEW)); sys.path.insert(0,str(HERE.parent/'mui-wo-models'))
from prepare_model_sample import stage
from fetch import fetch_tiles

def load(path):
 raw=path.read_bytes(); return json.loads(gzip.decompress(raw) if path.suffix=='.gz' else raw)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def dump(path,data):
 path.parent.mkdir(parents=True,exist_ok=True);raw=(json.dumps(data,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode();path.write_bytes(gzip.compress(raw,mtime=0) if path.suffix=='.gz' else raw)
def verify_index():
 import datetime, urllib.request, urllib.parse
 url=(HERE/'index-request.txt').read_text().strip()
 raw=urllib.request.urlopen(url,timeout=60).read();current=json.loads(raw)
 assert 'error' not in current and not current.get('exceededTransferLimit')
 parts=urllib.parse.urlsplit(url);query=dict(urllib.parse.parse_qsl(parts.query));query['returnCountOnly']='true'
 count_url=urllib.parse.urlunsplit(parts._replace(query=urllib.parse.urlencode(query)))
 count=json.loads(urllib.request.urlopen(count_url,timeout=60).read())['count']
 retained=load(HERE/'index.json');a={f['attributes']['SHEETNO']:f['attributes']['REVISIONDATE'] for f in retained['features']};b={f['attributes']['SHEETNO']:f['attributes']['REVISIONDATE'] for f in current['features']}
 assert count==len(current['features'])
 (HERE/'index-current.json').write_bytes(raw)
 dump(HERE/'index-verification.json',{'url':url,'retrievedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sha256':sha(raw),'retainedSheets':len(a),'currentSheets':len(b),'sheetRevisionsUnchanged':a==b,'changedSheets':sorted(k for k in a.keys()|b.keys() if a.get(k)!=b.get(k)),'serviceCount':count,'countRequestUrl':count_url,'countMatchesReturnedFeatures':True})
 assert a==b,'Official sheet revisions changed: review new source before reusing cached matching'

def baseline():
 buildings=load(ROOT/'3d-viewer/city/data/mui-wo-buildings.json')['buildings']
 detail=load(HERE.parent/'mui-wo-models/model-geometries.json.gz')['byBuildingUid']
 return buildings,detail

def intersecting_sheets(buildings):
 tf=Transformer.from_crs(2326,4326,always_xy=True);result={}
 for f in load(HERE/'index.json')['features']:
  polygon=Polygon(f['geometry']['rings'][0]);uids=[]
  for b in buildings:
   # Whole footprint, not just centroid: retain boundary-crossing candidates.
   rings=[[(tf.transform(834500+x,816500-z)) for x,z in ring] for ring in b['rings']]
   shape=Polygon(rings[0],rings[1:])
   if not shape.is_valid:shape=shape.buffer(0)
   if shape.intersects(polygon):uids.append(b['uid'])
  if uids:result[f['attributes']['SHEETNO']]=uids
 return result

def existing_folders():return [REVIEW/'model-sample',*sorted((HERE.parent/'mui-wo-models/staged').iterdir())]
def fetch():
 buildings,detail=baseline();sheets=intersecting_sheets(buildings)
 existing={load(p/'manifest.json')['tile'] for p in existing_folders()}
 wanted=sorted(set(sheets)-existing)
 dump(HERE/'scope.json',{'baselineBuildings':len(buildings),'baselineDetailed':len(detail),'sourceFootprintSelection':'source-scripts/city/mui-wo-buildings/landsd-mui-wo.json.gz','sheetSelection':'Any unchanged Mui Wo footprint intersects the official sheet polygon. Includes boundary-crossing models.','sheets':sheets,'existingSheets':sorted(existing),'additionalSheets':wanted})
 fetch_tiles(HERE,wanted,member_prefixes=['BUILDING/','TERRAIN'])

def build():
 buildings,detail=baseline();scope=load(HERE/'scope.json');folders=existing_folders()
 for tile in scope['additionalSheets']:
  folder=HERE/'sources'/tile;download=load(folder/'download.json');archive=folder/(tile+'.zip')
  assert sha(archive.read_bytes())==download['sha256']
  out=HERE/'staged'/tile
  manifest=stage(archive,download,HERE.parent/'mui-wo-buildings/landsd-mui-wo.json.gz',out)
  folders.append(out);print(tile,manifest['counts']['buildingModels'],flush=True)
 by_csuid=collections.defaultdict(list);by_ref=collections.defaultdict(list)
 for b in buildings:by_csuid[b['buildingCSUID']].append(b)
 entries=[];groups=collections.defaultdict(list)
 for folder in folders:
  m=load(folder/'manifest.json')
  for s in m['models']:
   entry=(folder,m,s);entries.append(entry);by_ref[s['geoRefNo']].append(entry)
   if len(s['officialBuildingCSUIDs'])==1 and len(by_csuid[s['officialBuildingCSUIDs'][0]])==1:
    groups[by_csuid[s['officialBuildingCSUIDs'][0]][0]['uid']].append(entry)
 spec=importlib.util.spec_from_file_location('shared_packer',HERE.parent/'central-completion/pack_models.py');packer=importlib.util.module_from_spec(spec);spec.loader.exec_module(packer)
 rows=[];models=[];evidence=[]
 for b in buildings:
  uid=b['uid'];refs=by_ref[b['sourceAttributes']['GeoRefNo']];matches=groups.get(uid,[])
  row={'uid':uid,'buildingCSUID':b['buildingCSUID'],'geoRefNo':b['sourceAttributes']['GeoRefNo'],'structureType':b['structureType'],'centre':b['centre'],'baselineDetailed':uid in detail,'sheets':[k for k,v in scope['sheets'].items() if uid in v],'sameGeoRefModels':[{'id':s['id'],'sheet':m['tile'],'officialMatches':s['officialMatches']} for _,m,s in refs]}
  if uid in detail:row['reason']='already-detailed'
  elif not refs:row['reason']='no-building-model-with-source-georef-in-intersecting-sheets'
  elif not matches:row['reason']='source-georef-present-but-geometric-or-component-match-rejected'
  elif len({s['id'] for _,_,s in matches})!=1:row['reason']='multiple-distinct-models-match-one-uid-review-required'
  else:
   folder,m,s=sorted(matches,key=lambda e:(e[1]['tileRevision'],e[1]['tile']),reverse=True)[0]
   for rel,digest in s['sourceHashes'].items():assert sha((folder/rel).read_bytes())==digest
   raw,stats=packer.pack(folder/s['url']);compressed=gzip.compress(raw,mtime=0)
   assert stats['triangles']==s['triangles']
   dest=HERE/'compact/models'/(s['id']+'.glb.gz');dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(compressed)
   record={'uid':uid,'buildingCSUID':b['buildingCSUID'],'objectId':b['objectId'],'modelId':s['id'],'sourceTile':m['tile'],'sourceTileRevision':m['tileRevision'],'worldBounds':s['worldBounds'],'triangles':s['triangles'],'recordedBaseHeight':b.get('baseHeightHKPD'),'recordedTopHeight':b.get('topHeightHKPD'),'structureType':b['structureType'],'label':b.get('name') or s['id'],'priority':'regional-completion','asset':str(dest.relative_to(HERE/'compact')),'encoding':'gzip','bytes':len(compressed),'glbBytes':len(raw),'decodedGeometryBytes':stats['decodedGeometryBytes'],'indexedVertices':stats['vertices'],'sha256':sha(compressed),'placementReviewed':False}
   models.append(record);evidence.append({'uid':uid,'modelId':s['id'],'sourceEntry':str((folder/s['url']).relative_to(ROOT)),'sourceHashes':s['sourceHashes'],'sourceCacheSha256':m['sourceCacheSha256'],'sourceOriginalDownload':m['sourceDownload'],'sourceMatches':s['officialMatches'],'compressedSha256':sha(compressed),'glbSha256':sha(raw),**stats})
   row['reason']='new-exact-match-packed-awaiting-placement-review';row['stagedModelId']=s['id']
  rows.append(row)
 counts={'forms':len(buildings),'baselineDetailed':len(detail),'baselineFallback':len(buildings)-len(detail),'additionalSheets':len(scope['additionalSheets']),'inspectedSheets':len(folders),'sourceModelEntries':len(entries),'newExactModels':len(models),'packedModels':len(models),'catalogueModels':len(models),'potentialDetailed':len(detail)+len(models),'remainingFallback':len(buildings)-len(detail)-len(models),'compressedBytes':sum(m['bytes'] for m in models),'decodedGeometryBytes':sum(m['decodedGeometryBytes'] for m in models),'triangles':sum(m['triangles'] for m in models),'reasons':dict(collections.Counter(r['reason'] for r in rows))}
 catalogue={'schemaVersion':1,'kind':'staged-official-model-catalogue','area':'Mui Wo completion','datasetId':'landsd_rcd_1742809441342_98380','crs':'EPSG:2326','verticalDatum':'Hong Kong Principal Datum','rootTranslation':[-834500,0,816500],'coordinatePolicy':'Unmodified native source transforms; index only byte-identical full vertex tuples. No draping, height fitting or procedural geometry.','loadingPolicy':'Staged only. Keep fallback until the verified model loads. Root must review placement and integrate shared registry.','counts':counts,'models':models}
 dump(HERE/'compact/catalogue.json',catalogue);dump(DOC/'ledger.json',{'counts':counts,'rows':rows});dump(DOC/'compact-assets.json',{'counts':counts,'assets':evidence});dump(DOC/'summary.json',counts)
 print(json.dumps(counts,indent=2))
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('step',choices=['verify_index','fetch','build']);args=parser.parse_args();globals()[args.step]()
