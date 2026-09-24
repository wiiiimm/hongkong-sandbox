"""Stage the existing source-mesh package with bounded generic bridge replacements."""
import gzip,hashlib,json,pathlib
import numpy as np
from shapely.geometry import Polygon,LineString
from shapely.ops import unary_union
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[2];DOC=ROOT/'docs/astra-city/mui-wo-completion'
def main():
 source=json.loads(gzip.decompress((HERE/'infrastructure-models.json.gz').read_bytes()));models=source['models'];polygons=[]
 for m in models:
  for t in np.asarray(m['modelGeometry']['position']).reshape(-1,3,3):
   p=Polygon(t[:,[0,2]])
   if p.area>1e-8:polygons.append(p)
 footprint=unary_union(polygons);tolerance=footprint.buffer(1.5);rows=[];clips=[];suppressed=[]
 for b in json.loads((ROOT/'3d-viewer/city/data/bridges.json').read_text())['bridges']:
  line=LineString(b['path']);exact=line.intersection(footprint).length
  # Positive overlap with actual projected source triangles is required. Nearby
  # parallel paths are never selected solely because they enter the tolerance.
  if exact<.01:continue
  keep=line.difference(tolerance);replaced=line.length-keep.length
  row={'id':b['id'],'source':b['source'],'originalLengthMetres':line.length,'withinExactSourceProjectionMetres':exact,'replacedLengthMetres':replaced,'retainedLengthMetres':keep.length}
  rows.append(row)
  if keep.length<1e-6:suppressed.append(b['id'])
  else:
   parts=list(keep.geoms) if hasattr(keep,'geoms') else [keep]
   clips.append({**row,'keepPaths':[[[float(x),float(z)] for x,z in p.coords] for p in parts if p.length>1e-6],'policy':'After this complete valid source package loads, replace only generic proxy portions within exact source triangle projections plus 1.5 m explicit map-alignment tolerance. Positive exact source overlap is required before applying tolerance. Original source IDs/tags and outside approaches remain; clipping endpoints are derived, not surveyed OSM nodes.'})
 models[0]['suppresses']=suppressed
 source.update(approaches=json.loads((HERE/'approaches.json').read_text())['records'],proxyClips=clips)
 source['counts']={**source['counts'],'estimatedPublicApproaches':len(source['approaches']),'genericBridgeProxiesReplaced':len(suppressed),'genericBridgeProxiesPartlyReplaced':len(clips)}
 source['limits']=['Ten exact infrastructure meshes are the retained INFRASTRUCTURE set in the existing Mui Wo model sheets; they do not establish complete infrastructure coverage.','Selected original public floor triangles and continuous walking have separate source/Navigation evidence.','Four visible public approach profiles have estimated widths/intermediate heights; original mesh triangles and source elevations remain unchanged.','Source depicts overlapping old/new Wang Tong components; only the upper western pedestrian floor is walkable. The cycle floor is not a public walking substitute.','Illustrative underwater terrain is not surveyed bathymetry.']
 raw=json.dumps(source,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode();(HERE/'bridges-mui-wo.json').write_bytes(raw)
 report={'schemaVersion':1,'staged':True,'counts':source['counts'],'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'sourceGeometryUnchanged':True,'proxyCoverage':rows,'fullSuppressionIds':suppressed,'partialClips':clips,'modelIds':[m['id'] for m in models]};(DOC/'infrastructure-package.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ('proxyCoverage','partialClips')},indent=2))
if __name__=='__main__':main()
