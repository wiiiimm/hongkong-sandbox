"""HKS-207: reuse retained government geometry for the Tsim Sha Tsui cultural pair.
Staging only: no live asset, inventory, transform, terrain or height mutations.
"""
import gzip,hashlib,importlib.util,json,pathlib,sqlite3,sys,zipfile
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def read(p):return json.loads(p.read_bytes())
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
def module(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def main():
 from shapely.geometry import Polygon,MultiPoint
 from pyproj import Transformer
 c=sqlite3.connect('file:'+str(HERE.parent/'building-batch/local/buildings.sqlite')+'?mode=ro',uri=True);c.row_factory=sqlite3.Row
 nearby=[dict(r) for r in c.execute('select * from buildings where active=1 and x between 850 and 1450 and z between -1100 and -400')]
 targets=[b for b in nearby if b['name'].upper().startswith('HONG KONG CULTURAL CENTRE') or b['name'].upper()=='HONG KONG SPACE MUSEUM' or b['uid'] in ('landsd/211702:0','landsd/251819:0')]
 assert len(targets)==16,len(targets)
 ids={b['object_id'] for b in nearby};sys.path.insert(0,str(HERE.parent/'landsd-territory'));from retain import iter_features
 source=HERE.parent/'landsd-territory/landsd-hong-kong-source.geojson.gz';project=Transformer.from_crs(4326,2326,always_xy=True);features=[]
 for f in iter_features(source):
  if f['properties']['OBJECTID'] not in ids:continue
  polys=[f['geometry']['coordinates']] if f['geometry']['type']=='Polygon' else f['geometry']['coordinates']
  features.append({'attributes':f['properties'],'geometry':{'rings':[[list(project.transform(*p)) for p in ring] for poly in polys for ring in poly]}})
 raw=json.dumps({'datasetVersion':'Building_Outline_Public_v20260819','source':str(source.relative_to(ROOT)),'derivation':'Retained official WGS84 polygons projected with established EPSG:2326 transformer; neighbouring identities included.','features':features},separators=(',',':')).encode();(HERE/'official-selection.json.gz').write_bytes(gzip.compress(raw,mtime=0))
 folder=HERE.parent/'central-completion/sources/11-SW-4D';archive=folder/'11-SW-4D.zip';download=read(folder/'download.json');assert hashlib.sha256(archive.read_bytes()).hexdigest()==download['sha256'];assert not download.get('memberPrefixes')
 sys.path.insert(0,str(ROOT/'docs/astra-city/mui-wo-buildings/review'));from prepare_model_sample import stage,model_geometry
 staged=HERE/'staged/11-SW-4D';manifest=stage(archive,download,HERE/'official-selection.json.gz',staged)
 pack=module('cultural_shared_pack',HERE.parent/'central-completion/pack_models.py').pack
 out=HERE/'compact';models=[];proofs=[];missing=[]
 def shape(b):
  rs=json.loads(b['rings_json']);return Polygon(rs[0],rs[1:])
 for b in targets:
  specs=[s for s in manifest['models'] if s['geoRefNo']==b['csuid'][:10]]
  if not specs:missing.append({'uid':b['uid'],'buildingCSUID':b['csuid'],'label':b['name'],'structureType':b['structure_type'],'reason':'No BUILDING model with this exact GeoRefNo in the complete retained geometry cache.'});continue
  assert len(specs)==1,specs
  spec=specs[0];path=staged/spec['sourceEntry'];mid=spec['id']
  for rel,sha in spec['sourceHashes'].items():assert hashlib.sha256((staged/rel).read_bytes()).hexdigest()==sha
  v,tri=model_geometry(read(path),lambda u:(path.parent/u).read_bytes());hull=MultiPoint(v[:,[0,2]]).convex_hull;poly=shape(b);ov=hull.intersection(poly).area/min(hull.area,poly.area);dist=hull.centroid.distance(poly.centroid)
  assert ov>=.5,(b['uid'],ov)
  status='standard-source-match' if spec['officialBuildingCSUIDs']==[b['csuid']] else 'explicit-landmark-match-review-required'
  data,stats=pack(path);compressed=gzip.compress(data,mtime=0);asset=out/'models'/(mid+'.glb.gz');asset.parent.mkdir(parents=True,exist_ok=True);asset.write_bytes(compressed)
  record={'uid':b['uid'],'buildingCSUID':b['csuid'],'objectId':b['object_id'],'modelId':mid,'sourceTile':manifest['tile'],'sourceTileRevision':manifest['tileRevision'],'worldBounds':spec['worldBounds'],'triangles':tri,'recordedBaseHeight':b['source_base'],'recordedTopHeight':b['source_top'],'structureType':b['structure_type'],'label':b['name'] or 'Unnamed Cultural Centre podium-associated structure','priority':'landmark','placementReviewed':False,'sourceMatchReview':status,'asset':str(asset.relative_to(out)),'encoding':'gzip','bytes':len(compressed),'glbBytes':len(data),'decodedGeometryBytes':stats['decodedGeometryBytes'],'indexedVertices':stats['vertices'],'sha256':hashlib.sha256(compressed).hexdigest()};models.append(record)
  proofs.append({'uid':b['uid'],'label':record['label'],'modelId':mid,'sourceManifest':str((staged/'manifest.json').relative_to(ROOT)),'sourceEntry':str(path.relative_to(ROOT)),'sourceHashes':spec['sourceHashes'],'sourceCacheSHA256':manifest['sourceCacheSha256'],'officialMatches':spec['officialMatches'],'matchStatus':status,'exactGeoRef':True,'overlapOfSmallerFootprint':ov,'centroidDistanceMetres':dist,'nativeBaseTop':[float(v[:,1].min()),float(v[:,1].max())],'sourceBaseTop':[b['source_base'],b['source_top']],'baseDelta':float(v[:,1].min())-b['source_base'] if b['source_base'] is not None else None,'topDelta':float(v[:,1].max())-b['source_top'] if b['source_top'] is not None else None,'qualification':'Candidate only. Native absolute HKPD geometry preserved at 1x. Space Museum roof geometry legitimately extends above the block survey top; requires visual review, never flattening.'})
 # Inventory every infrastructure mesh in this complete source cache; never pretend
 # a nearby infrastructure identity is an exact building identity.
 infrastructure=[]
 with zipfile.ZipFile(archive) as z:
  for entry in sorted(n for n in z.namelist() if n.startswith('INFRASTRUCTURE/') and n.endswith('.gltf')):
   folder=pathlib.PurePosixPath(entry).parent;v,tri=model_geometry(json.loads(z.read(entry)),lambda u:z.read(str(folder/u)));hull=MultiPoint(v[:,[0,2]]).convex_hull
   infrastructure.append({'sourceEntry':entry,'triangles':tri,'worldBounds':[v.min(axis=0).tolist(),v.max(axis=0).tolist()],'intersectingHeldFootprints':[b['uid'] for b in targets if any(m['uid']==b['uid'] for m in missing) and hull.intersects(shape(b))]})
 counts={'sourceForms':len(targets),'catalogueModels':len(models),'packedModels':len(models),'heldSourceForms':len(missing),'compressedBytes':sum(m['bytes'] for m in models),'packedTriangles':sum(m['triangles'] for m in models)}
 write(out/'catalogue-index.json',{'models':len(models),'catalogues':['catalogue.json'],'counts':counts});write(out/'catalogue.json',{'schemaVersion':1,'kind':'staged-official-model-catalogue','datasetId':'landsd_rcd_1742809441342_98380','area':'Hong Kong Space Museum and Hong Kong Cultural Centre','crs':'EPSG:2326','verticalDatum':'Hong Kong Principal Datum','rootTranslation':[-834500,0,816500],'models':models,'counts':counts,'loadingPolicy':'Staging only. Exact source identities retained, full terrain and browser review required before publication.'})
 write(HERE/'report.json',{'issue':'HKS-207','counts':counts,'models':proofs,'held':missing,'infrastructure':infrastructure,'aiCalls':0,'sourceNetworkBytes':0,'sourceCache':str(archive.relative_to(ROOT)),'sourceCacheSHA256':download['sha256'],'sourceTileRevision':download['revisionDate'],'selectionForms':len(features),'scopeRules':['Names identify cultural complexes inside a bounded Tsim Sha Tsui neighbourhood only.','Auditoria Building included through government venue identity and adjacent footprint; no name-only search omission.','Unnamed landsd/251819:0 retained inside Cultural Centre podium footprint; identity does not claim an architectural function.','Museum of Art podium, Clock Tower, Star Ferry Pier and 1881 Heritage are distinct neighbouring landmarks and are not reassigned to these two complexes.','Six open-sided Cultural Centre source records retained and reported; no guessed or fabricated model identity.'],'references':['https://www.lcsd.gov.hk/en/hkcc/contactus.html','https://www.gov.hk/en/residents/culture/performart/venues/performancevenues.htm','https://hk.space.museum/en/web/spm/about-us.html']})
 print(json.dumps({'counts':counts,'matches':[(r['uid'],r['matchStatus'],r['topDelta']) for r in proofs],'held':missing,'infrastructure':infrastructure},indent=2))
if __name__=='__main__':main()
