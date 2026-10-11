"""Complete source/literal/two Float32 projection against three actual neighbours."""
from fractions import Fraction as F
from pathlib import Path
import importlib.util,json
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from lippo_actual_render_float32_diagnostic_20261010 import reconstruct
BATCH='government-xl-lippo-three-basic-neighbour-complete-projection-context-v1-20261011';DOC=ROOT/'docs/astra-city/government-import'/BATCH
CAPTURE=DOC.parent/'government-xl-lippo-current-bound-six-roof-inputs-v4-20261011'
PHYS=DOC.parent/'government-xl-lippo-two-original-disjoint-current-parent-physical-v3-20261011'
RUNTIME=HERE/'local'/PHYS.name/'runtime-geometry.json.gz'
INPUT=DOC.parent/'government-xl-lippo-two-original-current-physical-inputs-v2-20261011'
UIDS={'landsd/231645:0','landsd/239465:0'};NEIGHBOURS={'landsd/156599:0','landsd/237843:0','landsd/239032:0'}
def form_polygon(rings):
 result=shapely.GeometryCollection()
 for ring in rings:result=result.symmetric_difference(shapely.Polygon(ring))
 assert result.is_valid and not result.is_empty
 return result

def closed_projection(triangles):
 pieces=[];counts={0:0,1:0,2:0}
 for triangle in triangles:
  points=[tuple(v) for v in triangle[:,[0,2]]];a,b,c=[[F(float(v)) for v in point] for point in points]
  area=(b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]);unique=list(dict.fromkeys(points))
  if area:geometry=shapely.Polygon(points);assert geometry.area>0;dim=2
  elif len(unique)>1:geometry=shapely.LineString(unique);dim=1
  else:geometry=shapely.Point(unique[0]);dim=0
  counts[dim]+=1;pieces.append(geometry)
 assert sum(counts.values())==len(triangles)
 return shapely.union_all(pieces),counts

def main():
 assert not DOC.exists();manifest=ROOT/'3d-viewer/city/data/manifest.json';before=manifest.read_bytes();capture=read(CAPTURE/'current-inputs.json.gz');assert digest(before)==capture['manifestSHA256']
 rows=[r for r in read(INPUT/'check-selection.json.gz')['rows'] if r['uid'] in UIDS];assert len(rows)==2
 assets=[ROOT/r['candidate']['path'] for r in rows]
 for r,p in zip(rows,assets):assert digest(p.read_bytes())==r['sourceSHA256']
 runtime=read(RUNTIME);assert {r['uid'] for r in runtime['rows']}==UIDS
 actual={r['uid']:np.asarray(r['position'],dtype='<f8').reshape(-1,3)[np.asarray(r['index'],dtype=np.int64).reshape(-1,3)] for r in runtime['rows']}
 export=read(CAPTURE/'actual-render-attribute-geometry.json.gz');literal=read(CAPTURE/'literal-production-geometry.json.gz');f32,pins=reconstruct(export,literal)
 representations={'completeOriginal':{r['uid']:decode_original_world_triangles(p.read_bytes()) for r,p in zip(rows,assets)},'actualRuntimeLiteralFloat64':actual}
 representations.update({k:{uid:tri for uid,tri in data.items() if uid in UIDS} for k,data in f32.items()})
 neighbourhood=read(PHYS/'neighbour-inputs.json.gz');neighbours=[r for r in neighbourhood['rows'] if r['building']['uid'] in NEIGHBOURS];assert {r['building']['uid'] for r in neighbours}==NEIGHBOURS and all(not r['existingNative'] for r in neighbours)
 checks=[]
 for kind,actors in sorted(representations.items()):
  assert set(actors)==UIDS;whole=np.concatenate([actors[u] for u in sorted(UIDS)]);assert len(whole)==17322 and np.isfinite(whole).all();projection,census=closed_projection(whole)
  outcomes=[]
  for n in sorted(neighbours,key=lambda r:r['building']['uid']):
   b=n['building'];polygon=form_polygon(b['rings']);overlap=projection.intersection(polygon)
   outcomes.append(dict(uid=b['uid'],name=b.get('name'),completeCurrentForm=b,currentNative=False,sourceProjectionDisjoint=projection.disjoint(polygon),projectionOverlapM2=overlap.area,minimumClosedProjectionDistanceM=projection.distance(polygon),currentFormWKB_SHA256=digest(polygon.wkb)))
  checks.append(dict(representation=kind,completeSourceFaces=len(whole),worldSHA256=digest(whole.tobytes()),projectedPrimitiveDimensionCensus={str(k):v for k,v in census.items()},completeClosedProjectionWKB_SHA256=digest(projection.wkb),rows=outcomes))
 assert all({r['uid'] for r in c['rows'] if r['sourceProjectionDisjoint']}=={'landsd/156599:0','landsd/239032:0'} for c in checks)
 assert all(next(r for r in c['rows'] if r['uid']=='landsd/237843:0')['projectionOverlapM2']>1700 for c in checks)
 save(DOC/'diagnostic.json.gz',dict(completeRepresentations=checks,completeActualFloat32WorldBindings=pins,manifestSHA256=digest(before),sourceGeometryChanges=0,terrainAccepted=False,physicalAccepted=False,installationApproved=False,qualification='Every original/literal/F32 face closed projection retained, including exact dimension0/1 primitives; no zero-area discarded. Two actual BASIC forms are genuinely source-disjoint in every declared complete representation. Langham is positively overlapping and cannot use disjoint-retention credit. This diagnosis alone supplies no terrain preservation, current ground/surface-equivalence, role/ownership/support/collision or installation acceptance.'))
 assert manifest.read_bytes()==before
 refs=[Path(__file__),CAPTURE/'result.json',CAPTURE/'actual-render-attribute-geometry.json.gz',CAPTURE/'literal-production-geometry.json.gz',CAPTURE/'current-inputs.json.gz',PHYS/'result.json',PHYS/'neighbour-inputs.json.gz',RUNTIME,INPUT/'check-selection.json.gz',HERE/'lippo_actual_render_float32_diagnostic_20261010.py',HERE/'exact_packed_world_geometry_20261009.py',manifest,*assets]
 sp=importlib.util.spec_from_file_location('lippo_neighbour_context_fence',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
 receipt=m.freeze(BATCH,'three-basic-neighbour-complete-source-literal-f32-projection-context-v1',refs,dict(uids=sorted(UIDS|NEIGHBOURS),completeSourceFaces=17322,completeRepresentations=4,sourceDisjointCurrentBasicUIDs=['landsd/156599:0','landsd/239032:0'],genuinelyOverlappingBasicUID='landsd/237843:0',physicalAccepted=False,installationApproved=False))
 print(json.dumps(dict(jobId=receipt['jobId'],sourceDisjointCurrentBasicUIDs=receipt['sourceDisjointCurrentBasicUIDs'])),flush=True)
if __name__=='__main__':main()
