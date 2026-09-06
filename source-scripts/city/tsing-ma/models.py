"""Stage exact official deck halves and tower objects for the shared bridge layer."""
import gzip,hashlib,json,pathlib,sys,zipfile
import numpy as np
from shapely.geometry import MultiPoint,Polygon,LineString
from shapely.ops import unary_union
ROOT=pathlib.Path(__file__).resolve().parents[3];HERE=pathlib.Path(__file__).resolve().parent;DOC=ROOT/'docs/astra-city/tsing-ma'
sys.path.insert(0,str(ROOT/'docs/astra-city/mui-wo-buildings/review'))
from prepare_model_sample import model_geometry
from bake_model_geometry import bake
DECKS={'I244492317107063C0','I254702348107063C0'}
TOWERS={'B250112338101063C0':'landsd/193003:0','B250222334201063C0':'landsd/205933:0','B263302377501063C0':'landsd/194907:0','B263422373701063C0':'landsd/194906:0'}
def build():
 assets=HERE/'assets';models=[];projected=[];sources=[]
 buildings={b['uid']:b for b in json.loads((ROOT/'3d-viewer/city/data/tiles/-5_-4.json').read_text())['buildings']}
 for cache in [HERE/'sources',HERE/'towers/sources']:
  for folder in sorted(cache.iterdir()):
   archive=folder/(folder.name+'.zip');download=json.loads((folder/'download.json').read_text())
   assert hashlib.sha256(archive.read_bytes()).hexdigest()==download['sha256']
   with zipfile.ZipFile(archive) as z:
    for name in z.namelist():
     mid=pathlib.PurePosixPath(name).stem
     if not name.endswith('.gltf') or mid not in DECKS|TOWERS.keys():continue
     raw=z.read(name);d=json.loads(raw);parent=pathlib.PurePosixPath(name).parent;pos,t=model_geometry(d,lambda uri:z.read(str(parent/uri)));hashes={}
     for entry in [name]+[str(parent/b['uri']) for b in d['buffers']]:
      rel=pathlib.PurePosixPath(entry);assert not rel.is_absolute() and '..' not in rel.parts
      target=assets/folder.name/entry;target.parent.mkdir(parents=True,exist_ok=True);data=z.read(entry);target.write_bytes(data);hashes[entry]=hashlib.sha256(data).hexdigest()
     spec={'id':mid,'url':folder.name+'/'+name,'sourceEntry':name,'sourceHashes':hashes,'worldBounds':[pos.min(axis=0).tolist(),pos.max(axis=0).tolist()],'officialMatches':[]}
     shape=MultiPoint(pos[:,[0,2]]).convex_hull
     matches=[]
     if mid in TOWERS:
      b=buildings[TOWERS[mid]];poly=Polygon(b['rings'][0],b['rings'][1:]);assert b['buildingCSUID'].startswith(mid[1:11]);ratio=shape.intersection(poly).area/min(shape.area,poly.area);assert ratio>.75 and shape.centroid.distance(poly.centroid)<15
      matches=[{'uid':b['uid'],'buildingCSUID':b['buildingCSUID'],'objectId':b['objectId'],'sourceBaseHeightHKPD':b['baseHeightHKPD'],'sourceTopHeightHKPD':b['topHeightHKPD'],'overlapOfSmallerFootprint':ratio,'modelHullToFootprintCentroidMetres':shape.centroid.distance(poly.centroid),'policy':'Exact GeoRefNo/CSUID prefix and footprint overlap. Keep original footprint/elevation record; suppress its extrusion only after this exact model loads.'}]
      spec['officialMatches']=matches
     g=bake(spec,assets);assert 'colour' in g and g['colourItemSize']==3
     model={'id':'landsd-infrastructure/'+mid,'name':'Tsing Ma Bridge · '+('Ma Wan deck half' if mid.startswith('I24449') else 'Tsing Yi deck half' if mid.startswith('I25470') else 'source tower '+mid[1:11]),'zh':'青馬大橋','sheet':folder.name,'sourceUrl':download['source'],'sourceRevision':download['revisionDate'],'modelGeometry':g,'worldBounds':g['worldBounds'],'walkable':False,'walkTriangleIndices':[],'suppresses':[],'suppressesBuildingUids':[m['uid'] for m in matches],'buildingMatches':matches,'elevationBasis':'Exact original glTF hierarchy in Hong Kong Principal Datum; unchanged source positions.','accessNote':'Road/rail bridge; no public pedestrian access is inferred. Mapped motorway records prohibit foot access.'}
     models.append(model)
     if mid in DECKS:projected.append(shape)
     sources.append({'sheet':folder.name,'sourceUrl':download['source'],'sourceRevision':download['revisionDate'],'cacheSha256':download['sha256'],'cacheKind':download['cacheKind'],'sourceHashes':hashes})
 assert len(models)==6
 decks=unary_union(projected);bridgeRows=[];proxyClips=[]
 for b in json.loads((ROOT/'3d-viewer/city/data/bridges.json').read_text())['bridges']:
  if b.get('tags',{}).get('bridge:name:en')!='Tsing Ma Bridge':continue
  line=LineString(b['path']);inside=line.intersection(decks.buffer(1.5)).length/line.length
  bridgeRows.append({'id':b['id'],'length':line.length,'withinSourceDeckHullWith1_5mTolerance':inside,'foot':b.get('tags',{}).get('foot'),'source':b['source']})
  if inside>.9999:models[0]['suppresses'].append(b['id'])
  elif inside>.5:
   keep=line.difference(decks.buffer(1.5));parts=list(keep.geoms) if hasattr(keep,'geoms') else [keep]
   proxyClips.append({'id':b['id'],'source':b['source'],'keepPaths':[[[float(x),float(z)] for x,z in p.coords] for p in parts if p.length>1e-6],'originalLengthMetres':line.length,'retainedLengthMetres':keep.length,'replacedLengthMetres':line.length-keep.length,'policy':'After the whole valid source package loads, clip only the generic proxy portions within the union of the two source deck projected hulls plus1.5m explicit map tolerance. Retain original sourceID/tags and the unmatched TsingYi approach geometry. New clipping endpoints are derived, not new surveyed OSM nodes.'})
 out={'schemaVersion':1,'kind':'official-infrastructure','region':'tsing-ma','datasetId':'landsd_rcd_1742809441342_98380','crs':'EPSG:2326','verticalDatum':'Hong Kong Principal Datum','coordinatePolicy':'Original source hierarchy then city translation[-834500,0,816500]; no source movement, triangulation change or height adjustment.','models':models,'sources':sources,'proxyClips':proxyClips,'limits':['This package retains two official deck components and four separately classified tower objects.','High suspension cables are absent from the retained six source objects; any additional cable visual is a separate labelled approximation.','Source bridge geometry and tower-footprint records have different revision/elevation values; immutable source fields are not forced to agree.','No public walking permission, road traffic simulation or navigational bathymetry is provided.'],'counts':{'models':6,'sourceTriangles':sum(m['modelGeometry']['triangles'] for m in models),'publicWalkModels':0,'matchedBuildingExtrusions':4,'genericBridgeProxiesReplaced':len(models[0]['suppresses'])}}
 (HERE/'bridges-tsing-ma.json').write_text(json.dumps(out,ensure_ascii=False,separators=(',',':'))+'\n')
 brief={'counts':out['counts'],'items':[{k:v for k,v in m.items() if k!='modelGeometry'}|{'triangles':m['modelGeometry']['triangles']} for m in models],'bridgeProxyCoverage':bridgeRows,'proxyClips':proxyClips,'bytes':(HERE/'bridges-tsing-ma.json').stat().st_size}
 (DOC/'model-build.json').write_text(json.dumps(brief,indent=2)+'\n');print(json.dumps(out['counts']));print(json.dumps(bridgeRows,indent=2));return out
if __name__=='__main__':build()
