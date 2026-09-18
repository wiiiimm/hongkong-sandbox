"""Review one curved podium using its actual projected source triangles.
The existing convex hull screen is a false negative for this concave shape.
No shared importer changes and no live publication are performed.
"""
import gzip,hashlib,json,pathlib,sys
import numpy as np
from shapely import union_all
from shapely.geometry import Polygon,MultiPoint
from pack_models import HERE,ROOT,DOC,pack,sha,dump
from bake_model_geometry import bake

def main():
 folder=HERE/'staged/11-SW-9C';manifest=json.loads((folder/'manifest.json').read_text());georef='3511615681'
 specs=[m for m in manifest['models'] if m['geoRefNo']==georef];assert len(specs)==1;spec=specs[0]
 buildings=json.loads(gzip.decompress((HERE/'building-selection.json.gz').read_bytes()))['buildings'];matches=[b for b in buildings if b.get('sourceAttributes',{}).get('GeoRefNo')==georef];assert len(matches)==1;b=matches[0];assert b['uid']=='landsd/26195:0' and b['buildingCSUID']=='3511615681P20110704' and b['structureType']=='Podium'
 assert spec['id']=='B351161568102063C1' and spec['officialMatches']==[]
 for name,digest in spec['sourceHashes'].items():assert sha((folder/name).read_bytes())==digest
 baked=bake(spec,folder);positions=np.array(baked['position']).reshape(-1,3);triangles=positions.reshape(-1,3,3)[:,:,[0,2]]
 u=triangles[:,1]-triangles[:,0];v=triangles[:,2]-triangles[:,0];twice_area=np.abs(u[:,0]*v[:,1]-u[:,1]*v[:,0]);projected=union_all([Polygon(t) for t in triangles[twice_area>1e-8]])
 outline=Polygon(b['rings'][0],b['rings'][1:]);hull=MultiPoint(positions[:,[0,2]]).convex_hull
 def metrics(shape):
  overlap=shape.intersection(outline).area
  return {'area':shape.area,'centroid':list(shape.centroid.coords)[0],'centroidDistanceMetres':shape.centroid.distance(outline.centroid),'overlapOfSmallerFootprint':overlap/min(shape.area,outline.area),'intersectionOverUnion':overlap/shape.union(outline).area}
 precise=metrics(projected);old=metrics(hull);assert projected.is_valid and precise['overlapOfSmallerFootprint']>=.5 and precise['centroidDistanceMetres']<=10 and old['centroidDistanceMetres']>10
 raw,stats=pack(folder/spec['url']);compressed=gzip.compress(raw,mtime=0);dest=HERE/'compact-followup/models'/(spec['id']+'.glb.gz');dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(compressed)
 note='Exact unique GeoRefNo plus actual union of original projected source triangles. This replaces only the convex-hull approximation for this reviewed match; original source vertices, metadata, footprint and heights are untouched.'
 accepted={'uid':b['uid'],'buildingCSUID':b['buildingCSUID'],'objectId':b['objectId'],'modelId':spec['id'],'sourceTile':manifest['tile'],'sourceTileRevision':manifest['tileRevision'],'worldBounds':spec['worldBounds'],'triangles':spec['triangles'],'recordedBaseHeight':b['baseHeightHKPD'],'recordedTopHeight':b['topHeightHKPD'],'structureType':b['structureType'],'label':'West Wing podium','priority':'route-candidate','asset':'models/'+dest.name,'encoding':'gzip','bytes':len(compressed),'glbBytes':len(raw),'decodedGeometryBytes':stats['decodedGeometryBytes'],'indexedVertices':stats['vertices'],'sha256':sha(compressed),'placementReviewed':False,'matchReview':'west-wing-match.json'}
 counts={'catalogueModels':1,'packedModels':1,'compressedBytes':len(compressed),'decodedGeometryBytes':stats['decodedGeometryBytes'],'packedTriangles':spec['triangles']}
 catalogue={'schemaVersion':1,'kind':'staged-official-model-catalogue','area':'Central reviewed follow-up','datasetId':manifest['datasetId'],'crs':'EPSG:2326','verticalDatum':'Hong Kong Principal Datum','rootTranslation':[-834500,0,816500],'coordinatePolicy':note,'loadingPolicy':'Staging only. Source match approval does not approve public podium walking or suppress existing collisions.','counts':counts,'models':[accepted]};dump(HERE/'compact-followup/catalogue.json',catalogue)
 proof={'status':'source-match-accepted-runtime-unpublished','uid':b['uid'],'sourceAttributes':b['sourceAttributes'],'modelId':spec['id'],'sourceEntry':str((folder/spec['url']).relative_to(ROOT)),'sourceHashes':spec['sourceHashes'],'sourceCacheSha256':manifest['sourceCacheSha256'],'sourceOriginalDownload':manifest['sourceDownload'],'nativeGeometry':{'triangles':spec['triangles'],'worldBounds':spec['worldBounds']},'uniqueGeoRefMatch':True,'originalConvexHullScreen':old,'actualSourceProjection':precise,'matchingPolicy':note,'compressedSha256':sha(compressed),'glbSha256':sha(raw),**stats,'limits':['The projected union is evidence for identity/placement, not a replacement footprint or collision shape.','Source model top is 20.939 m HKPD; recorded outline top remains 16 m HKPD.','No public floor/roof access approval is inferred from matching the building.']};dump(DOC/'west-wing-match.json',proof)
 # Keep a compatible evidence wrapper for the existing actual-loader verifier.
 dump(DOC/'compact-followup-assets.json',{'counts':counts,'assets':[{'uid':b['uid'],'modelId':spec['id'],'sourceEntry':proof['sourceEntry'],'sourceHashes':spec['sourceHashes'],'glbSha256':sha(raw),**stats}]})
 print(json.dumps({'uid':b['uid'],'model':spec['id'],'triangles':spec['triangles'],'bytes':len(compressed),'match':precise,'oldHull':old},indent=2))
if __name__=='__main__':main()
