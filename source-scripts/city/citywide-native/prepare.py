"""Partition retained official footprints once for every indexed government model sheet."""
import collections,gzip,hashlib,json,pathlib,sys
from pyproj import Transformer
ROOT=pathlib.Path(__file__).resolve().parents[3];HERE=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'landsd-territory'))
from retain import iter_features
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=HERE/'local';out.mkdir(parents=True,exist_ok=True)
 catalogue=ROOT/'docs/astra-city/citywide-source/directories.json.gz';data=json.loads(gzip.decompress(catalogue.read_bytes()))
 assert data['summary']['status']=='complete' and len(data['directories'])==3456
 viewer=collections.defaultdict(list);manifest=json.loads((ROOT/'3d-viewer/city/data/manifest.json').read_text());viewer_hashes=[]
 for tile in manifest['tiles']:
  p=ROOT/'3d-viewer'/tile['url'];viewer_hashes.append([tile['url'],sha(p)])
  for b in json.loads(p.read_text())['buildings']:
   if b.get('buildingCSUID'):viewer[b['buildingCSUID']].append({k:b[k] for k in ['uid','rings','base','height']})
 refs=collections.defaultdict(set);sheets={r['sheet']:r for r in data['directories']};official=collections.defaultdict(list)
 for sheet,row in sheets.items():
  for model in row['models']:refs[model['geoRefNo']].add(sheet)
 source=HERE.parent/'landsd-territory/landsd-hong-kong-source.geojson.gz';projection=Transformer.from_crs(4326,2326,always_xy=True);matched_records=0;total_records=0
 for f in iter_features(source):
  total_records+=1;attrs=f['properties'];selected=refs.get(str(attrs.get('GeoRefNo','')))
  if not selected:continue
  geom=f['geometry'];assert geom['type'] in ('Polygon','MultiPolygon')
  polygons=[geom['coordinates']] if geom['type']=='Polygon' else geom['coordinates'];rings=[[list(projection.transform(*point)) for point in ring] for poly in polygons for ring in poly]
  feature={'attributes':attrs,'geometry':{'rings':rings},'viewerUids':viewer.get(attrs.get('BuildingCSUID'),[])}
  for sheet in selected:official[sheet].append(feature)
  matched_records+=1
 source_sha=sha(source);rows=[]
 for sheet,row in sorted(sheets.items()):
  folder=out/'inputs'/sheet;folder.mkdir(parents=True,exist_ok=True)
  selection={'datasetVersion':'Building_Outline_Public_v20260819','sourceSHA256':source_sha,'features':official[sheet]};p=folder/'official.json.gz';p.write_bytes(gzip.compress(json.dumps(selection,separators=(',',':')).encode(),mtime=0))
  q=folder/'directory.json';q.write_text(json.dumps(row,separators=(',',':'))+'\n')
  raw_directory=HERE.parent/'citywide-source/cache'/data['summary']['indexSHA256'][:16]/sheet/'zip-directory.bin';assert sha(raw_directory)==row['directorySHA256']
  rows.append({'sheet':sheet,'models':len(row['models']),'directory':str(q.relative_to(ROOT)),'rawDirectory':str(raw_directory.relative_to(ROOT)),'official':str(p.relative_to(ROOT)),'footprintSha256':sha(p),'sourceSha256':hashlib.sha256(json.dumps([row['sourceURL'],row['etag'],row['directorySHA256']],separators=(',',':')).encode()).hexdigest()})
 plan={'issue':'HKS-222','indexSHA256':data['summary']['indexSHA256'],'sourceSHA256':source_sha,'viewerInputsSHA256':hashlib.sha256(json.dumps(viewer_hashes).encode()).hexdigest(),'sourceRecords':total_records,'recordsWithGeographicReferenceCandidate':matched_records,'sheets':rows,'expectedModels':sum(r['models'] for r in rows),'qualification':'Exact government reference candidates only; geometric matching and model validation remain required.'}
 (out/'plan.json').write_text(json.dumps(plan,indent=2)+'\n');print(json.dumps({k:v for k,v in plan.items() if k!='sheets'}))
if __name__=='__main__':main()
