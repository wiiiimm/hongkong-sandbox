"""Private source-anchored terrain boundary transition; government buildings untouched."""
from pathlib import Path
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from source_surface_inset import plane,lift
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from china_ferry_current_foundations_v1_20261020 import face_diagnostics
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-grandiose-terrain-boundary-transition-v4-20261021';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
PRIOR=BASE/'government-xl-grandiose-terrain-boundary-transition-v3-20261021';RES=BASE/'government-xl-grandiose-runtime-failure-samples-v1-20261021';SRC=BASE/'government-xl-grandiose-podium-current-terrain-v1-20261021'
assert not DOC.exists();refs=[Path(__file__)];pins={}
with connect()as db:
 db.execute('SET TRANSACTION READ ONLY')
 for folder in [PRIOR,RES,SRC]:
  r=read(folder/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
  for e in r['evidenceRefs']:
   assert e['path'] not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
def take(p):
 assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p);return read(p)
row=take(SRC/'selection.json.gz')['rows'][0];ap=ROOT/row['candidate']['path'];assert digest(ap.read_bytes())==row['sourceSHA256'];refs.append(ap);model=decode_original_world_triangles(ap.read_bytes())
failed=take(RES/'samples.json')['rows'][0]['failures'];assert len(failed)==30 and all(f['kind']=='edge' for f in failed)
keys=sorted({(f['face'],f['edge']) for f in failed});assert len(keys)==3
residual=[dict(faceIndex=i,edge=e) for i,e in keys];faces=np.asarray([[model[i,e],model[i,(e+1)%3]]for i,e in keys])
for f in failed:
 expected=model[f['face'],f['edge']]*(1-f['step']/f['steps'])+model[f['face'],(f['edge']+1)%3]*(f['step']/f['steps'])
 assert np.max(np.abs(expected-f['position']))<1e-8,'Runtime/source edge attribution mismatch'
shapes=[shapely.LineString(t[:,[0,2]])for t in faces]
core=shapely.union_all(shapes).buffer(.25,join_style='mitre');regions=list(core.geoms) if hasattr(core,'geoms') else [core]
ground=np.asarray(take(HERE/'local'/PRIOR.name/'private-terrain.json.gz')['triangles']);changed=[];regionRecords=[];output=ground
for region in regions:
 localIds=[i for i,p in enumerate(shapes) if p.intersects(region)];floor=float(faces[localIds,:,1].min());outer=region.buffer(1,join_style='mitre');ring=outer.difference(region)
 regionRecords.append(dict(sourceFaces=[residual[i]['faceIndex']for i in localIds],floorM=floor,coreWKT=region.wkt,outerWKT=outer.wkt))
 baseline=output;output=[];unchanged=0
 for i,t in enumerate(baseline):
  p=shapely.Polygon(t[:,[0,2]])
  if p.area<=1e-10 or p.disjoint(outer):output.append(t);unchanged+=1;continue
  coeff=plane(t);changed.append(dict(region=len(regionRecords)-1,inputFace=i));output.extend(lift(p.difference(outer),coeff))
  for part,isCore in [(p.intersection(region),True),(p.intersection(ring),False)]:
   for face in lift(part,coeff):
    for v in face:
     point=shapely.Point(v[[0,2]]);inside=point.distance(region);outside=point.distance(outer.boundary);w=1 if isCore else outside/(inside+outside)
     v[1]=min(v[1],(1-w)*v[1]+w*floor)
    output.append(face)
 output=np.asarray(output)
output=np.asarray(output);assert np.isfinite(output).all()
save(LOCAL/'private-terrain.json.gz',dict(triangles=output.tolist(),notPublishable=True));refs.append(LOCAL/'private-terrain.json.gz')
helper=module('grandiose_transition_foundation',HERE/'xl-final-script-pass.py');b=row['source']['building'];f=helper.foundation_context(model,output,shapely.Polygon(b['rings'][0],b['rings'][1:]));save(DOC/'foundation.json',f);save(DOC/'residual-faces.json.gz',face_diagnostics(helper,model,output))
result=dict(uids=[row['uid']],sourceSHA256=row['sourceSHA256'],sourceGeometryChanges=0,regions=regionRecords,innerBufferM=.25,transitionWidthM=1,terrainChangedFaceIndices=changed,unchangedTerrainFaces=unchanged,terrainFaces=len(output),foundation={k:v for k,v in f.items()if k!='components'},installationApproved=False,newlyInstalled=0,qualification='Private compute terrain proposal. Source-anchored collar interpolates to previous terrain; it is not original government terrain. All regional coverage, seams, actual runtime, neighbours and support checks remain required. No building geometry or placement changes.')
save(DOC/'summary.json',result);refs.extend(HERE/n for n in ['source_surface_inset.py','exact_packed_world_geometry_20261009.py','china_ferry_current_foundations_v1_20261020.py','xl-final-script-pass.py'])
module('grandiose_transition_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'private-terrain-boundary-transition',refs,result)
print({k:v for k,v in result.items()if not k.endswith('WKT')})
