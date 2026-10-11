"""Exact untouched podium surfaces supplying the commercial outline omissions."""
import json,numpy as np,shapely
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from source_closed_components import components
DOC=ROOT/'docs/astra-city/government-import/government-xl-tung-sing-commercial-missing-original-platform-surfaces-20261010';BASE=DOC.parent

def main():
 assert not DOC.exists();selectionpath=BASE/'government-xl-tung-sing-interior-current-identity-inputs-v2-20261010/selection.json.gz';contextpath=BASE/'government-xl-tung-sing-commercial-complete-coverage-context-20261010/diagnostic.json.gz';row=next(r for r in read(selectionpath)['rows'] if r['uid']=='landsd/126434:0');path=ROOT/row['candidate']['path'];raw=path.read_bytes();assert digest(raw)==row['sourceSHA256'];a=decode_original_world_triangles(raw);assert len(a)==432;top=components(a);ownership={i:ci for ci,c in enumerate(top['components']) for i in c['faceIndices']};normals=np.cross(a[:,1]-a[:,0],a[:,2]-a[:,0]);parts=[]
 for index,m in enumerate(read(contextpath)['allMissingTargetPolygons']):
  q=shapely.from_geojson(json.dumps(m['fullExactReportedGeoJSON']));hits=[]
  for i,t in enumerate(a):
   p=shapely.Polygon(t[:,[0,2]]);area=p.intersection(q).area
   if area>0:hits.append({'faceId':i,'componentId':ownership[i],'originalTriangle':t.tolist(),'normal':normals[i].tolist(),'normalYPositive':bool(normals[i,1]>0),'projectedOverlapAreaM2':float(area),'sourceFaceYRangeHKPD':[float(t[:,1].min()),float(t[:,1].max())]})
  up=[h['faceId'] for h in hits if h['normalYPositive']];positive=shapely.union_all(shapely.polygons(a[up][:,:,[0,2]])) if up else shapely.GeometryCollection();groups=[]
  for ci in sorted({h['componentId'] for h in hits}):
   c=top['components'][ci];ids=c['faceIndices'];groups.append({'componentId':ci,'completeOriginalPartFaceIds':ids,'completeOriginalPartTriangles':a[ids].tolist(),'wholeOriginalComponent':c,'supplyingFaceIds':[h['faceId'] for h in hits if h['componentId']==ci]})
  parts.append({'missingPolygonIndex':index,'completeMissingCurrentTargetGeoJSON':m['fullExactReportedGeoJSON'],'missingAreaM2':q.area,'allOriginalPodiumSupplyingFaces':hits,'supplyingCompleteOriginalParts':groups,'ordinaryUpwardOriginalSurfacesCoverMissingAreaM2':float(q.intersection(positive).area),'missingAreaNotCoveredByOriginalUpwardSurfacesM2':float(q.difference(positive).area)})
 out={'uid':'landsd/254604:0','relatedPodiumUid':row['uid'],'podiumSourceSHA256':row['sourceSHA256'],'podiumWholeOriginalWorldSHA256':digest(a.astype('<f8').tobytes()),'podiumWholeOriginalFaces':len(a),'podiumWholeOriginalParts':len(top['components']),'allMissingRegionOriginalSurfaceDispositions':parts,'missingTotalM2':sum(p['missingAreaM2'] for p in parts),'sourceSurfaceUncoveredM2':sum(p['missingAreaNotCoveredByOriginalUpwardSurfacesM2'] for p in parts),'exactOriginalPartAccounting':top,'inputHashes':{str(p.relative_to(ROOT)):digest(p.read_bytes()) for p in [Path(__file__),selectionpath,contextpath,path,HERE/'source_closed_components.py',HERE/'exact_packed_world_geometry_20261009.py']},'identityAccepted':False,'physicalAccepted':False,'sourceGeometryChanges':0,'qualification':'Every original podium face supplying the commercial missing footprint is retained with original height/normals/complete part topology. Float planar area reports only; no95% waiver, whole-family identity, physical support or installation credit.'}
 save(DOC/'diagnostic.json.gz',out);print(json.dumps({'missingTotalM2':out['missingTotalM2'],'upwardUncoveredM2':out['sourceSurfaceUncoveredM2'],'regions':[{'id':p['missingPolygonIndex'],'parts':[x['componentId'] for x in p['supplyingCompleteOriginalParts']],'upFaces':[h['faceId'] for h in p['allOriginalPodiumSupplyingFaces'] if h['normalYPositive']],'heights':sorted({tuple(h['sourceFaceYRangeHKPD']) for h in p['allOriginalPodiumSupplyingFaces'] if h['normalYPositive']})} for p in parts]}),flush=True)
if __name__=='__main__':main()
