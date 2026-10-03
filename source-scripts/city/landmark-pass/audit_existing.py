"""Read-only landmark gap audit. Source parts are not whole architectural landmarks.
Reuses the retained inventory, complete ZIP directories and native model decoder.
"""
import collections,io,json,pathlib,sqlite3,struct,sys,zipfile
HERE=pathlib.Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def read(p):return json.loads(p.read_bytes())
def triangle_evidence(path, positions, footprint, model_base, estimated_base, estimated_height):
 import numpy as np
 from shapely.geometry import Point,Polygon
 from shapely import union_all
 d=read(path);pieces=[];offset=0
 def indices(a):
  v=d['bufferViews'][a['bufferView']];raw=(path.parent/d['buffers'][v['buffer']]['uri']).read_bytes();dtype={5121:'u1',5123:'<u2',5125:'<u4'}[a['componentType']]
  return np.ndarray((a['count'],),dtype=dtype,buffer=raw,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',np.dtype(dtype).itemsize),))
 def visit(i):
  nonlocal offset
  node=d['nodes'][i]
  if 'mesh' in node:
   for primitive in d['meshes'][node['mesh']]['primitives']:
    assert primitive.get('mode',4)==4
    count=d['accessors'][primitive['attributes']['POSITION']]['count'];local=positions[offset:offset+count];offset+=count
    order=indices(d['accessors'][primitive['indices']]) if 'indices' in primitive else np.arange(count)
    pieces.append(local[order].reshape((-1,3,3)))
  for child in node.get('children',[]):visit(child)
 for node in d['scenes'][d.get('scene',0)]['nodes']:visit(node)
 assert offset==len(positions)
 triangles=np.concatenate(pieces);xz=triangles[:,:,[0,2]]
 xmin,zmin,xmax,zmax=footprint.bounds;keep=(xz[:,:,0].max(1)>=xmin)&(xz[:,:,0].min(1)<=xmax)&(xz[:,:,1].max(1)>=zmin)&(xz[:,:,1].min(1)<=zmax)
 triangles=triangles[keep];xz=triangles[:,:,[0,2]]
 a=xz[:,0];ab=xz[:,1]-a;ac=xz[:,2]-a;det=ab[:,0]*ac[:,1]-ab[:,1]*ac[:,0];keep=np.abs(det)>1e-9
 triangles=triangles[keep];xz=xz[keep];a=a[keep];ab=ab[keep];ac=ac[keep];det=det[keep]
 projected=union_all([Polygon(t).intersection(footprint) for t in xz]);fraction=projected.area/footprint.area
 points=[footprint.representative_point()]
 for x in np.arange(xmin+0.5,xmax,1):
  for z in np.arange(zmin+0.5,zmax,1):
   pt=Point(x,z)
   if footprint.contains(pt):points.append(pt)
 rays=[];near_estimate=0
 for pt in points:
  ap=np.array([pt.x,pt.y])-a;u=(ap[:,0]*ac[:,1]-ap[:,1]*ac[:,0])/det;v=(ab[:,0]*ap[:,1]-ab[:,1]*ap[:,0])/det;hit=(u>=-1e-8)&(v>=-1e-8)&(u+v<=1+1e-8)
  y=triangles[:,0,1]+u*(triangles[:,1,1]-triangles[:,0,1])+v*(triangles[:,2,1]-triangles[:,0,1]);levels=sorted(set(round(float(q),3) for q in y[hit]));near=any(estimated_base-1<=q<=estimated_base+estimated_height+2 for q in levels)
  near_estimate+=near;rays.append({'x':round(pt.x,3),'z':round(pt.y,3),'surfaceHeightsHKPD':levels,'withinEstimatedFallbackBand':near})
 hit_rays=[r for r in rays if r['surfaceHeightsHKPD']];mins=[r['surfaceHeightsHKPD'][0] for r in hit_rays];maxs=[r['surfaceHeightsHKPD'][-1] for r in hit_rays]
 return {'method':'Native indexed glTF triangles decoded with shared node transforms. Exact horizontal triangle-union intersection and 1m interior vertical-ray samples. No convex-hull proxy.','trianglesInFootprintBounds':len(triangles),'projectedTriangleCoverageFraction':round(fraction,6),'interiorSamples':len(rays),'samplesWithActualTriangle':len(hit_rays),'minimumSurfaceHeightRangeHKPD':[min(mins),max(mins)] if mins else None,'maximumSurfaceHeightRangeHKPD':[min(maxs),max(maxs)] if maxs else None,'samplesInEstimatedFallbackBand':near_estimate,'estimatedFallbackBandHKPD':[estimated_base-1,estimated_base+estimated_height+2],'sourceBaseHeightHKPD':model_base,'rays':rays,'qualification':'Triangle presence can be another storey or underside. The canopy has no surveyed height, so correspondence and suppression still require explicit source/visual review.'}

def main():
 from shapely.geometry import Polygon,MultiPoint
 sys.path.insert(0,str(ROOT/'docs/astra-city/mui-wo-buildings/review'));from prepare_model_sample import model_geometry
 c=sqlite3.connect('file:'+str(HERE.parent/'building-batch/local/buildings.sqlite')+'?mode=ro',uri=True);c.row_factory=sqlite3.Row
 groups=read(HERE.parent/'building-batch/tourist-trial.json')['landmarks'][:6];refs={r['csuid'][:10] for g in groups for r in g['records']};sources=collections.defaultdict(list);models=[]
 manifests=list(ROOT.glob('source-scripts/city/*/staged/*/manifest.json'))+list((HERE/'staged-existing').glob('*/manifest.json'))
 for p in manifests:
  d=read(p)
  for m in d['models']:
   if m.get('geoRefNo') in refs:models.append((p,d,m))
 # These are complete native archive directories even where payload caches are filtered.
 paths=[ROOT/'source-scripts/city/central-completion/sources/11-SW-8B/zip-directory.bin',ROOT/'source-scripts/city/central-completion/sources/11-SW-14A/zip-directory.bin',ROOT/'source-scripts/city/mui-wo-models/sources/10-SW-18A/zip-directory.bin',ROOT/'source-scripts/city/tai-o-detail-completion/directories/9-SW-22B.bin']
 checked=[]
 for p in paths:
  if not p.exists():continue
  raw=p.read_bytes();end=raw.rfind(b'PK\x05\x06');e=struct.unpack('<4s4H2LH',raw[end:end+22]);assert e[1]==e[2]==0 and e[3]==e[4]
  # Stored bin begins at the directory's native offset.
  buf=bytearray(e[6]+len(raw));buf[e[6]:]=raw
  with zipfile.ZipFile(io.BytesIO(buf)) as z:names=z.namelist()
  checked.append({'path':str(p.relative_to(ROOT)),'entries':len(names),'completeDirectory':len(names)==e[4]})
  assert len(names)==e[4]
  for n in names:
   if n.endswith('.gltf'):
    for ref in refs:
     if ref in n:sources[ref].append({'directory':str(p.relative_to(ROOT)),'entry':n})
 rows=[]
 for group in groups:
  for target in group['records']:
   b=dict(c.execute('SELECT b.*,m.asset AS progressive_asset FROM buildings b LEFT JOIN models m ON m.uid=b.uid WHERE b.uid=?',(target['uid'],)).fetchone());rs=json.loads(b['rings_json']);foot=Polygon(rs[0],rs[1:]);candidates=[];related=[]
   for path,d,m in models:
    if m.get('geoRefNo') != b['csuid'][:10] and not any(set(m.get('officialBuildingCSUIDs',[]))&{r['csuid'] for r in group['records']}):continue
    source=path.parent/m['sourceEntry'];v,_=model_geometry(read(source),lambda u:(source.parent/u).read_bytes());hull=MultiPoint(v[:,[0,2]]).convex_hull
    overlap=hull.intersection(foot).area/max(.001,min(hull.area,foot.area));coverage=hull.intersection(foot).area/max(.001,foot.area)
    rec={'id':m['id'],'manifest':str(path.relative_to(ROOT)),'exactGeoRef':m.get('geoRefNo')==b['csuid'][:10],'officialMatches':m['officialBuildingCSUIDs'],'overlapOfSmallerFootprint':round(overlap,6),'targetWithinConvexHullFraction':round(coverage,6),'centroidDistanceMetres':round(hull.centroid.distance(foot.centroid),4),'nativeBaseTop':[float(v[:,1].min()),float(v[:,1].max())]}
    if b['uid'] in ('landsd/93196:0','landsd/185493:0','landsd/240278:0') and not rec['exactGeoRef'] and coverage>.5:
     rec['actualTriangleEvidence']=triangle_evidence(source,v,foot,b['source_base'],b['base'],b['height'])
    (candidates if rec['exactGeoRef'] else related).append(rec)
   detailed=bool(b['embedded'] or b['progressive_asset'])
   if detailed:status='already-detailed'
   elif any(b['csuid'] in m['officialMatches'] for m in candidates):status='matched-candidate-awaiting-placement-and-browser'
   elif candidates:status='exact-reference-candidate-requires-explicit-match-review'
   elif sources[b['csuid'][:10]]:status='available-source-member-not-staged'
   else:status='no-separate-exact-reference-entry-in-checked-directories'
   rows.append({'landmark':group['id'],'uid':b['uid'],'objectId':b['object_id'],'csuid':b['csuid'],'name':b['name'],'structureType':b['structure_type'],'currentDetailed':detailed,'sourceBaseTop':[b['source_base'],b['source_top']],'renderedBaseHeight':[b['base'],b['height']],'footprintArea':round(foot.area,4),'status':status,'sourceEntries':sources[b['csuid'][:10]],'candidates':candidates,'relatedModelOverlaps':[r for r in related if r['targetWithinConvexHullFraction']>.01],'qualification':'Convex-hull overlap alone does not prove a roof/part is actually represented. Do not hide its fallback using this report.'})
 out={'scope':'Six named landmark groups, excluding Ngong Ping which has separate acquisition pass.','aiCalls':0,'networkRequests':0,'checkedDirectories':checked,'counts':dict(collections.Counter(r['status'] for r in rows)),'rows':rows,'limits':['Directory absence is qualified to checked source revisions and sheets; not a claim of dataset-wide unavailability.','Script completion means all candidates have a disposition, not all buildings have detailed models.','Source structures include podiums and canopies; tallying parts is not architectural completeness.','No automatic threshold relaxation, source height changes, viewer replacement or source-ID suppression.']};(HERE/'existing-audit.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out['counts']));print(json.dumps([{k:r[k] for k in ('uid','structureType','status','relatedModelOverlaps')} for r in rows if not r['currentDetailed']],indent=2))
if __name__=='__main__':main()
