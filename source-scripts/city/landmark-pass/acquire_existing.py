"""Bounded IFC podium / Tai O hotel pass, using retained source IDs and shared tools.
Stage only: never mutate live viewer, shared inventory or original manifests.
"""
import argparse,gzip,hashlib,importlib.util,json,pathlib,sqlite3,sys
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[2];WORK=HERE/'existing-work'
def read(p):return json.loads(p.read_bytes())
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
def module(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
TARGETS={'landsd/232441:0':'B342191624502063C0','landsd/257115:0':'B342851634802063C0','landsd/170271:0':'B029581275901063C0','landsd/170357:0':'B029511275801063C0','landsd/239278:0':'B029241272701063C0','landsd/67478:0':'B029351274901063C0'}
def main():
 from shapely.geometry import Polygon,MultiPoint
 from pyproj import Transformer
 WORK.mkdir(parents=True,exist_ok=True)
 c=sqlite3.connect('file:'+str(HERE.parent/'building-batch/local/buildings.sqlite')+'?mode=ro',uri=True);c.row_factory=sqlite3.Row
 bs={uid:dict(c.execute('select * from buildings where uid=? and active=1',(uid,)).fetchone()) for uid in TARGETS}
 # Keep neighbour identities as well: no matching against an artificially isolated target.
 neighbours=[dict(b) for b in c.execute('select * from buildings where active=1 and ((x between -31800 and -31200 and z between 3500 and 4000) or (x between -600 and 200 and z between -100 and 600))')]
 ids={b['object_id'] for b in neighbours};sys.path.insert(0,str(HERE.parent/'landsd-territory'));from retain import iter_features
 source=HERE.parent/'landsd-territory/landsd-hong-kong-source.geojson.gz';project=Transformer.from_crs(4326,2326,always_xy=True);features=[]
 for f in iter_features(source):
  if f['properties']['OBJECTID'] not in ids:continue
  polys=[f['geometry']['coordinates']] if f['geometry']['type']=='Polygon' else f['geometry']['coordinates']
  features.append({'attributes':f['properties'],'geometry':{'rings':[[list(project.transform(*p)) for p in ring] for poly in polys for ring in poly]}})
 raw=json.dumps({'datasetVersion':'Building_Outline_Public_v20260819','source':str(source.relative_to(ROOT)),'derivation':'Retained official WGS84 polygons projected with established EPSG:2326 transformer; neighbouring records included.','features':features},separators=(',',':')).encode();(WORK/'official-selection.json.gz').write_bytes(gzip.compress(raw,mtime=0))
 write(WORK/'index.json',read(HERE.parent/'tai-o-detail-completion/index.json'))
 prefixes=['BUILDING/'+mid+'/' for uid,mid in TARGETS.items() if uid not in ('landsd/232441:0','landsd/257115:0')]+['TERRAIN']
 fetch=module('shared_existing_fetch',HERE.parent/'mui-wo-models/fetch.py');fetch.fetch_tiles(WORK,['9-SW-22B'],prefixes)
 sys.path.insert(0,str(ROOT/'docs/astra-city/mui-wo-buildings/review'));from prepare_model_sample import stage,model_geometry
 folder=WORK/'sources/9-SW-22B';download=read(folder/'download.json');archive=folder/'9-SW-22B.zip';assert hashlib.sha256(archive.read_bytes()).hexdigest()==download['sha256']
 stage(archive,download,WORK/'official-selection.json.gz',HERE/'staged-existing/9-SW-22B')
 pack=module('shared_existing_pack',HERE.parent/'central-completion/pack_models.py').pack
 out=HERE/'compact-existing';models=[];evidence=[]
 for uid,mid in TARGETS.items():
  b=bs[uid];sf=HERE.parent/'central-completion/staged/11-SW-8B' if uid in ('landsd/232441:0','landsd/257115:0') else HERE/'staged-existing/9-SW-22B'
  manifest=read(sf/'manifest.json');spec=next(s for s in manifest['models'] if s['id']==mid);path=sf/spec['sourceEntry']
  for rel,sha in spec['sourceHashes'].items():assert hashlib.sha256((sf/rel).read_bytes()).hexdigest()==sha
  assert spec['geoRefNo']==b['csuid'][:10];v,tri=model_geometry(read(path),lambda u:(path.parent/u).read_bytes());hull=MultiPoint(v[:,[0,2]]).convex_hull;rs=json.loads(b['rings_json']);poly=Polygon(rs[0],rs[1:]);ov=hull.intersection(poly).area/min(hull.area,poly.area);dist=hull.centroid.distance(poly.centroid)
  matches=spec['officialBuildingCSUIDs'];status='standard-source-match' if matches==[b['csuid']] else 'explicit-landmark-match-review-required'
  # Waiver is requested, never implicit: no change to shared <=10m matcher.
  data,stats=pack(path);compressed=gzip.compress(data,mtime=0);asset=out/'models'/(mid+'.glb.gz');asset.parent.mkdir(parents=True,exist_ok=True);asset.write_bytes(compressed)
  record={'uid':uid,'buildingCSUID':b['csuid'],'objectId':b['object_id'],'modelId':mid,'sourceTile':manifest['tile'],'sourceTileRevision':manifest['tileRevision'],'worldBounds':spec['worldBounds'],'triangles':tri,'recordedBaseHeight':b['source_base'],'recordedTopHeight':b['source_top'],'structureType':b['structure_type'],'label':b['name'],'priority':'landmark','placementReviewed':False,'sourceMatchReview':status,'asset':str(asset.relative_to(out)),'encoding':'gzip','bytes':len(compressed),'glbBytes':len(data),'decodedGeometryBytes':stats['decodedGeometryBytes'],'indexedVertices':stats['vertices'],'sha256':hashlib.sha256(compressed).hexdigest()}
  models.append(record);evidence.append({'uid':uid,'modelId':mid,'sourceManifest':str((sf/'manifest.json').relative_to(ROOT)),'sourceEntry':str(path.relative_to(ROOT)),'sourceHashes':spec['sourceHashes'],'sourceArchiveSHA256':manifest['sourceArchiveSha256'],'officialMatches':spec['officialMatches'],'matchStatus':status,'exactGeoRef':True,'overlapOfSmallerFootprint':ov,'centroidDistanceMetres':dist,'nativeBaseTop':[float(v[:,1].min()),float(v[:,1].max())],'sourceBaseTop':[b['source_base'],b['source_top']],'baseDelta':float(v[:,1].min())-b['source_base'] if b['source_base'] is not None else None,'topDelta':float(v[:,1].max())-b['source_top'] if b['source_top'] is not None else None,'qualification':'Candidate only. No height, position, source identity, threshold or viewer changes.'})
 counts={'catalogueModels':len(models),'packedModels':len(models),'compressedBytes':sum(m['bytes'] for m in models),'packedTriangles':sum(m['triangles'] for m in models)}
 write(out/'catalogue-index.json',{'models':len(models),'catalogues':['catalogue.json']});write(out/'catalogue.json',{'schemaVersion':1,'kind':'staged-official-model-catalogue','datasetId':'landsd_rcd_1742809441342_98380','area':'IFC podiums and Tai O Heritage Hotel','crs':'EPSG:2326','verticalDatum':'Hong Kong Principal Datum','rootTranslation':[-834500,0,816500],'models':models,'counts':counts,'loadingPolicy':'Staging only. Explicit source-match exceptions and terrain/browser review required before publication.'});write(out/'proofs.json',{'counts':counts,'models':evidence,'aiCalls':0});print(json.dumps({'counts':counts,'evidence':evidence},indent=2))
if __name__=='__main__':main()
