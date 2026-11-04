"""Fetch only four missing-reference model candidates; preserve original geometry."""
import sys,collections,gzip,json,hashlib,pathlib,importlib.util,zipfile
import numpy as np
from shapely.geometry import MultiPoint
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[2];BASE=HERE.parent/'pui-o-completion';DOC=ROOT/'docs/astra-city/pui-o-detail-completion'
def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
sys.path.insert(0,str(ROOT/'docs/astra-city/mui-wo-buildings/review'))
from prepare_model_sample import model_geometry
from compare_official import official_shape
sha=lambda b:hashlib.sha256(b).hexdigest()
def main():
 audit=json.loads((DOC/'audit.json').read_text());candidates=[r for r in audit['ledger'] if r['status']=='candidate-requires-exact-geometry-check'];bytile=collections.defaultdict(list)
 for r in candidates:
  for c in r['candidates']:bytile[c['tile']].append(c)
 fetch=module('shared_fetch',HERE.parent/'mui-wo-models/fetch.py').fetch_tiles
 for tile,items in bytile.items():fetch(HERE,[tile],['BUILDING/'+c['modelId']+'/' for c in items])
 official=json.loads(gzip.decompress((BASE/'official-selection.json.gz').read_bytes()));features=collections.defaultdict(list)
 for f in official['features']:features[f['attributes']['GeoRefNo']].append(f)
 buildings={b['uid']:b for b in json.loads(gzip.decompress((BASE/'building-selection.json.gz').read_bytes()))['buildings']};pack=module('shared_pack',HERE.parent/'central-completion/pack_models.py').pack
 records=[];screens=[];evidence=[];output=HERE/'compact';(output/'models').mkdir(parents=True,exist_ok=True)
 for r in candidates:
  assert len(r['candidates'])==1;c=r['candidates'][0];tile=c['tile'];modelId=c['modelId'];download=json.loads((HERE/'sources'/tile/'download.json').read_text());folder=HERE/'staged'/tile;folder.mkdir(parents=True,exist_ok=True)
  with zipfile.ZipFile(HERE/'sources'/tile/(tile+'.zip')) as z:
   original=z.read(c['path']);data=json.loads(original);parent=pathlib.PurePosixPath(c['path']).parent;positions,triangles=model_geometry(data,lambda uri:z.read(str(parent/uri)));hashes={}
   for rel in [c['path']]+[str(parent/b['uri']) for b in data['buffers']]:
    assert '..' not in pathlib.PurePosixPath(rel).parts;raw=z.read(rel);dest=folder/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw);hashes[rel]=sha(raw)
  hull=MultiPoint(positions[:,[0,2]]).convex_hull;matches=[];checks=[]
  for f in features[r['geoRefNo']]:
   shape=official_shape(f);overlap=hull.intersection(shape).area/max(.001,min(hull.area,shape.area));distance=hull.centroid.distance(shape.centroid);passed=overlap>=.5 and distance<=10
   checks.append({'buildingCSUID':f['attributes']['BuildingCSUID'],'overlap':overlap,'centroidDistanceMetres':distance,'passed':passed})
   if passed:matches.append(f['attributes']['BuildingCSUID'])
  screen={'uid':r['uid'],'modelId':modelId,'sourceTile':tile,'checks':checks,'safeIdentityMatch':matches==[r['buildingCSUID']]};screens.append(screen)
  if not screen['safeIdentityMatch']:continue
  b=buildings[r['uid']];raw,stats=pack(folder/c['path']);assert triangles==stats['triangles'];compressed=gzip.compress(raw,mtime=0);asset='models/'+modelId+'.glb.gz';(output/asset).write_bytes(compressed)
  record={'uid':r['uid'],'buildingCSUID':b['buildingCSUID'],'objectId':b['objectId'],'modelId':modelId,'sourceTile':tile,'sourceTileRevision':download['revisionDate'],'worldBounds':[positions.min(axis=0).tolist(),positions.max(axis=0).tolist()],'triangles':triangles,'recordedBaseHeight':b['baseHeightHKPD'],'recordedTopHeight':b['topHeightHKPD'],'structureType':b['structureType'],'label':b.get('name') or modelId,'priority':'unreviewed','placementReviewed':False,'asset':asset,'encoding':'gzip','bytes':len(compressed),'glbBytes':len(raw),'decodedGeometryBytes':stats['decodedGeometryBytes'],'indexedVertices':stats['vertices'],'sha256':sha(compressed)};records.append(record);evidence.append({'uid':r['uid'],'sourceHashes':hashes,'sourceEntry':str((folder/c['path']).relative_to(ROOT)),'sourceCacheSha256':download['sha256'],'compressedSha256':sha(compressed),'glbSha256':sha(raw),**stats})
 counts={'models':len(records),'packedModels':len(records),'catalogueModels':len(records),'glbBytes':sum(r['glbBytes'] for r in records),'packedTriangles':sum(r['triangles'] for r in records),'compressedBytes':sum(r['bytes'] for r in records),'triangles':sum(r['triangles'] for r in records),'decodedGeometryBytes':sum(r['decodedGeometryBytes'] for r in records)}
 catalogue={'schemaVersion':1,'kind':'staged-official-model-catalogue','area':'Pui O detail completion','datasetId':'landsd_rcd_1742809441342_98380','crs':'EPSG:2326','verticalDatum':'Hong Kong Principal Datum','rootTranslation':[-834500,0,816500],'coordinatePolicy':'Original nodes and bit-identical source attributes through existing packer. No height or footprint edits.','loadingPolicy':'Staged only. Root must verify terrain and browser before publication; retain existing outlines until a successful asset load.','counts':counts,'models':records}
 (output/'catalogue.json').write_text(json.dumps(catalogue,separators=(',',':'))+'\n');report={'counts':counts,'screens':screens,'assets':evidence,'catalogueSha256':sha((output/'catalogue.json').read_bytes()),'sourceTransferredBytes':sum(json.loads((HERE/'sources'/t/'download.json').read_text())['transferredBytes'] for t in bytile),'limits':['Identity and attribute validation are not placement or architectural acceptance.','No shared runtime, building source fields, terrain, live catalogue or manifest is changed.','Known buffer terrain conflicts require terrain/source validation before publication.']};(DOC/'prepared.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
