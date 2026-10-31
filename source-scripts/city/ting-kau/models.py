"""Stage the original Ting Kau bridge mesh; separate tower assets are identity evidence only."""
import hashlib,json,pathlib,sys,zipfile
import numpy as np
from shapely.geometry import MultiPoint,Polygon,LineString
ROOT=pathlib.Path(__file__).resolve().parents[3];HERE=pathlib.Path(__file__).resolve().parent;DOC=ROOT/'docs/astra-city/ting-kau'
sys.path.insert(0,str(ROOT/'docs/astra-city/mui-wo-buildings/review'))
from prepare_model_sample import model_geometry
from bake_model_geometry import bake
MID='I259872443407063C0';TOWERS={'B260722538701063C0':'landsd/219323:0','B262702498501063C0':'landsd/219830:0','B264802455801063C0':'landsd/221079:0'}
def original(folder,mid,assets=None):
 meta=json.loads((folder/'download.json').read_text());archive=folder/(folder.name+'.zip');assert hashlib.sha256(archive.read_bytes()).hexdigest()==meta['sha256']
 with zipfile.ZipFile(archive) as z:
  entry=next(n for n in z.namelist() if pathlib.PurePosixPath(n).stem==mid and n.endswith('.gltf'));raw=z.read(entry);d=json.loads(raw);parent=pathlib.PurePosixPath(entry).parent;p,t=model_geometry(d,lambda uri:z.read(str(parent/uri)));hashes={}
  for name in [entry]+[str(parent/b['uri']) for b in d['buffers']]:
   data=z.read(name);hashes[name]=hashlib.sha256(data).hexdigest()
   if assets:
    target=assets/folder.name/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
 return p,t,{'id':mid,'url':folder.name+'/'+entry,'sourceEntry':entry,'sourceHashes':hashes,'worldBounds':[p.min(axis=0).tolist(),p.max(axis=0).tolist()],'officialMatches':[]},meta

def build():
 assets=HERE/'assets';p,t,spec,meta=original(HERE/'sources/6-SE-23B',MID,assets);hull=MultiPoint(p[:,[0,2]]).convex_hull
 buildings={}
 for tile in json.loads((ROOT/'3d-viewer/city/data/manifest.json').read_text())['tiles']:
  if tile['bounds'][2]<-8600 or tile['bounds'][0]>-7800 or tile['bounds'][3]<-9100 or tile['bounds'][1]>-7900:continue
  for b in json.loads((ROOT/'3d-viewer'/tile['url']).read_text())['buildings']:
   if b['uid'] in TOWERS.values():buildings[b['uid']]=b
 proofs=[]
 for mid,uid in TOWERS.items():
  folder=next(f for f in (HERE/'towers/sources').iterdir() if any(mid in n for n in zipfile.ZipFile(f/(f.name+'.zip')).namelist()))
  tower,tt,ts,tm=original(folder,mid,assets);b=buildings[uid];assert b['buildingCSUID'].startswith(mid[1:11]);poly=Polygon(b['rings'][0],b['rings'][1:]);th=MultiPoint(tower[:,[0,2]]).convex_hull;ratio=poly.intersection(th).area/min(poly.area,th.area);assert ratio>.8 and hull.intersection(poly).area/poly.area>.95
  # The main infrastructure already has tall source faces at each recorded tower position.
  mask=np.linalg.norm(p[:,[0,2]]-np.array(b['centre']),axis=1)<15;assert mask.any() and p[mask,1].max()>150
  proofs.append({'uid':uid,'buildingCSUID':b['buildingCSUID'],'objectId':b['objectId'],'sourceBaseHeightHKPD':b['baseHeightHKPD'],'sourceTopHeightHKPD':b['topHeightHKPD'],'identityModel':mid,'identitySourceUrl':tm['source'],'identityHashes':ts['sourceHashes'],'identityWorldBounds':ts['worldBounds'],'overlapOfSmallerFootprint':ratio,'mainInfrastructureTowerTopHKPD':float(p[mask,1].max()),'policy':'Exact CSUID/GeoRefNo prefix and overlapping source footprints; the full infrastructure already includes this tower. Keep the original building source record; suppress its extrusion only after the full valid bridge package loads. Do not overlay the separate tower model.'})
 spec['officialMatches']=proofs;g=bake(spec,assets);assert g['triangles']==16995
 suppressed=[];clips=[];coverage=[]
 for b in json.loads((ROOT/'3d-viewer/city/data/bridges.json').read_text())['bridges']:
  if b.get('name')!='Ting Kau Bridge':continue
  line=LineString(b['path']);keep=line.difference(hull.buffer(1.5));ratio=1-keep.length/line.length;coverage.append({'id':b['id'],'length':line.length,'sourceHullCoverageWith1_5mTolerance':ratio,'source':b['source'],'foot':b.get('tags',{}).get('foot')})
  if keep.length<.001:suppressed.append(b['id'])
  elif ratio>.5:
   parts=list(keep.geoms) if hasattr(keep,'geoms') else [keep];clips.append({'id':b['id'],'source':b['source'],'keepPaths':[[list(q) for q in part.coords] for part in parts if part.length>1e-6],'originalLengthMetres':line.length,'retainedLengthMetres':keep.length,'replacedLengthMetres':line.length-keep.length,'policy':'Replace only the part covered by the source bridge projected hull plus 1.5 m explicit map tolerance; retain the unmatched original approach path and source identity.'})
 model={'id':'landsd-infrastructure/'+MID,'name':'Ting Kau Bridge · original deck and three towers','zh':'汀九橋','sheet':'6-SE-23B','sourceUrl':meta['source'],'sourceRevision':meta['revisionDate'],'modelGeometry':g,'worldBounds':g['worldBounds'],'walkable':False,'walkTriangleIndices':[],'suppresses':suppressed,'suppressesBuildingUids':list(TOWERS.values()),'buildingMatches':proofs,'elevationBasis':'Unchanged original glTF transform in Hong Kong Principal Datum. Source towers are already part of this infrastructure mesh.','accessNote':'Motorway bridge; no public pedestrian access is inferred.'}
 out={'schemaVersion':1,'kind':'official-infrastructure','region':'ting-kau','datasetId':'landsd_rcd_1742809441342_98380','crs':'EPSG:2326','verticalDatum':'Hong Kong Principal Datum','coordinatePolicy':'Original source hierarchy then city translation [-834500,0,816500]; no source geometry or elevation adjustment.','models':[model],'sources':[{'sourceUrl':meta['source'],'sourceRevision':meta['revisionDate'],'cacheSha256':meta['sha256'],'cacheKind':meta['cacheKind'],'sourceHashes':spec['sourceHashes']}],'proxyClips':clips,'counts':{'models':1,'sourceTriangles':16995,'publicWalkModels':0,'matchedBuildingExtrusions':3,'genericBridgeProxiesReplaced':len(suppressed),'partiallyReplacedProxies':len(clips)},'limits':['The original infrastructure contains the complete deck and three towers, but no diagonal stay cables.','Separate tower model files are retained as identity evidence and not rendered twice.','No public walking permission, traffic simulation or bathymetric clearance is inferred.']}
 (HERE/'bridges-ting-kau.json').write_text(json.dumps(out,ensure_ascii=False,separators=(',',':'))+'\n')
 report={'counts':out['counts'],'sourceModelId':MID,'bounds':g['worldBounds'],'towerMatches':proofs,'proxyCoverage':coverage,'proxyClips':clips,'sourceCableGeometry':'Absent in both retained non-textured and individualised versions of the infrastructure; both have 16,995 triangles. The separate individualised generic object is a low coastal surface, not bridge cables.'}
 (DOC/'model-build.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(out['counts']));return out
if __name__=='__main__':build()
