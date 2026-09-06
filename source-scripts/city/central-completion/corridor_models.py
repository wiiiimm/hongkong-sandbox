"""Reuse retained native sheets for the Wan Chai–Central–Sheung Wan corridor.
This stages compact assets only; it does not edit sources, city tiles or manifests.
"""
import collections,gzip,hashlib,json,pathlib,sys
import numpy as np
from shapely.geometry import MultiPoint,Polygon
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[2];DOC=ROOT/'docs/astra-city/central-completion'
sys.path.insert(0,str(HERE));from pack_models import pack,sha,dump
sys.path.insert(0,str(ROOT/'docs/astra-city/mui-wo-buildings/review'));from prepare_model_sample import model_geometry
TARGETS={
 '01.4':{94583:'Shun Tak Centre',94974:'Shun Tak Centre West Tower',1307:'Western Market',67579:'The Center',254567:'Man Mo Temple'},
 '02.1':{98449:'Central Plaza',125801:'Immigration Tower',125577:'Revenue Tower',265525:'Hopewell Centre',145002:'Blue House',145223:'Blue House',180759:'Blue House',180764:'Blue House',10114:'Southorn Stadium',107308:'Southorn Centre',7163:'Three Pacific Place'},
 '02.2':{124803:'Hong Kong Convention and Exhibition Centre',123020:'Hong Kong Arts Centre',337711:'HKAPA Theatre Block',337830:'HKAPA Academy Block',69025:'HKAPA Administration Block',42369:'HKAPA ancillary form'},
}
def main():
 targets={f'landsd/{oid}:0':(section,label) for section,items in TARGETS.items() for oid,label in items.items()}
 manifest=json.loads((ROOT/'3d-viewer/city/data/manifest.json').read_text());buildings={};source_files=[];csuid_counts=collections.Counter()
 for tile in manifest['tiles']:
  b=tile['bounds']
  if b[0]>2300 or b[2]<-1800 or b[1]>1800 or b[3]<-400:continue
  path=ROOT/'3d-viewer'/tile['url'];data=json.loads(path.read_text());source_files.append({'path':str(path.relative_to(ROOT)),'sha256':sha(path.read_bytes())})
  for b in data['buildings']:
   if b.get('buildingCSUID'):csuid_counts[b['buildingCSUID']]+=1
   if b['uid'] in targets:buildings[b['uid']]=b
 assert set(buildings)==set(targets)
 sources=collections.defaultdict(list)
 for path in sorted((HERE/'staged').glob('*/manifest.json')):
  source=json.loads(path.read_text())
  for spec in source['models']:sources[spec.get('geoRefNo')].append((path.parent,source,spec))
 records=[];evidence=[];gaps=[]
 for uid,(section,label) in targets.items():
  b=buildings[uid];candidates=sources.get(b['buildingCSUID'][:10],[])
  if not candidates:gaps.append({'uid':uid,'name':label,'section':section,'reason':'No native model with this exact GeoRefNo in the retained source sheets.'});continue
  if csuid_counts[b['buildingCSUID']]!=1 or len({s['id'] for _,_,s in candidates})!=1:
   gaps.append({'uid':uid,'name':label,'section':section,'reason':'Ambiguous source component/model identity; original footprint retained.'});continue
  folder,source,spec=sorted(candidates,key=lambda e:(e[1]['tileRevision'],e[1]['tile']),reverse=True)[0];path=folder/spec['url']
  for rel,digest in spec['sourceHashes'].items():assert sha((folder/rel).read_bytes())==digest
  native=json.loads(path.read_text());positions,triangles=model_geometry(native,lambda uri:(path.parent/uri).read_bytes());bounds=[positions.min(axis=0).tolist(),positions.max(axis=0).tolist()]
  assert np.max(np.abs(np.asarray(bounds)-spec['worldBounds']))<1e-8
  hull=MultiPoint(positions[:,[0,2]]).convex_hull;footprint=Polygon(b['rings'][0],b['rings'][1:]);overlap=hull.intersection(footprint).area/min(hull.area,footprint.area);distance=hull.centroid.distance(footprint.centroid)
  match={'uid':uid,'buildingCSUID':b['buildingCSUID'],'objectId':b['objectId'],'exactGeoRefNo':spec['geoRefNo'],'overlapOfSmallerFootprint':overlap,'footprintCentroidDistanceMetres':distance,'policy':'Unchanged shared importer rules: exact GeoRefNo and a unique source model/component; projected convex hull overlaps at least 50% of the smaller footprint and centroids are within 10 m.'}
  if overlap<.5 or distance>10:
   gaps.append({'uid':uid,'name':label,'section':section,'reason':'Existing conservative source geometry match failed; no threshold relaxation or source adjustment.',**match});continue
  glb,stats=pack(path);assert stats['triangles']==triangles
  raw=gzip.compress(glb,mtime=0);out=HERE/'compact-corridor';dest=out/'models'/(spec['id']+'.glb.gz');dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw)
  record={'uid':uid,'objectId':b['objectId'],'buildingCSUID':b['buildingCSUID'],'modelId':spec['id'],'sourceTile':source['tile'],'sourceTileRevision':source['tileRevision'],'worldBounds':bounds,'triangles':triangles,'recordedBaseHeight':b.get('baseHeightHKPD'),'recordedTopHeight':b.get('topHeightHKPD'),'structureType':b.get('structureType'),'label':label,'sectionId':section,'priority':'landmark','placementReviewed':False,'asset':str(dest.relative_to(out)),'encoding':'gzip','bytes':len(raw),'glbBytes':len(glb),'decodedGeometryBytes':stats['decodedGeometryBytes'],'indexedVertices':stats['vertices'],'sha256':sha(raw)}
  records.append(record);evidence.append({'uid':uid,'sourceEntry':str(path.relative_to(ROOT)),'sourceHashes':spec['sourceHashes'],'sourceOriginalDownload':source['sourceDownload'],'sourceCacheSha256':source['sourceCacheSha256'],'sourceMatch':match,'originalFootprintRingsSHA256':sha(json.dumps(b['rings'],separators=(',',':')).encode()),'recordedBaseHeight':b.get('baseHeightHKPD'),'recordedTopHeight':b.get('topHeightHKPD'),'compressedSha256':sha(raw),'glbSha256':sha(glb),**stats})
  print(uid,label,triangles,len(raw),flush=True)
 counts={'requestedForms':len(targets),'packedModels':len(records),'unresolvedForms':len(gaps),'compressedBytes':sum(r['bytes'] for r in records),'glbBytes':sum(r['glbBytes'] for r in records),'decodedGeometryBytes':sum(r['decodedGeometryBytes'] for r in records),'packedTriangles':sum(r['triangles'] for r in records)}
 catalogue={'schemaVersion':1,'kind':'staged-official-model-catalogue','area':'Wan Chai to Sheung Wan corridor','datasetId':'landsd_rcd_1742809441342_98380','crs':'EPSG:2326','verticalDatum':'Hong Kong Principal Datum','rootTranslation':[-834500,0,816500],'coordinatePolicy':'Original native glTF positions/normals/colours/materials and node matrices; only bit-identical complete vertex tuples are indexed. Apply one city root translation; no terrain lifting or height correction.','counts':counts,'models':records}
 dump(HERE/'compact-corridor/catalogue.json',catalogue);dump(DOC/'corridor-models.json',{'counts':counts,'sourceFiles':source_files,'assets':evidence,'gaps':gaps,'limits':['Staged compact assets, not a live publication or complete section review.','No downloads, relaxed match thresholds, building geometry moves or recorded-height changes.','Missing/ambiguous matches retain their original footprint; no public-access inference.','Architectural placement, source/terrain disagreement and continuous route acceptance remain separate checks.']});print(json.dumps(counts,indent=2))
if __name__=='__main__':main()
