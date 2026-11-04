"""Full-source foundation diagnostic preserving the installed terrain domain."""
from pathlib import Path
import json, subprocess, sys, uuid
import numpy as np, shapely
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from native_patch_resolution import _faces
from source_surface_inset import plane,lift
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-yoho-mall-i-retained-ground-v1-20261020';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
SCOPE=BASE/'government-xl-yoho-mall-i-regional-scope-v1-20261020';GROUND=BASE/'government-xl-next-twenty-original-ground-v3-20261020';SELECTION=BASE/'government-xl-next-twenty-current-terrain-v2-20261020'
def owned():
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease) and not DOC.exists()
 refs=[Path(__file__)];pins={}
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY')
  for folder in [SCOPE,GROUND,SELECTION]:
   r=read(folder/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
   refs.append(folder/'result.json');pins[folder]={e['path']:e['sha256']for e in r['evidenceRefs']}
 def take(folder,p):
  assert digest(p.read_bytes())==pins[folder][str(p.relative_to(ROOT))],p
  refs.append(p);return read(p)
 scope=take(SCOPE,SCOPE/'scope.json');take(SCOPE,ROOT/'3d-viewer/city/data/manifest.json')
 row=next(r for r in take(SELECTION,SELECTION/'selection.json.gz')['rows']if r['uid']=='landsd/189427:0')
 asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256'];refs.append(asset)
 model=decode_original_world_triangles(asset.read_bytes());assert len(model)==21928
 groundfile=HERE/'local'/GROUND.name/'189427:0-ground.json.gz';ground=np.asarray(take(GROUND,groundfile)['completeOriginalTerrain'],dtype='float64')
 assert digest(ground.astype('<f8').tobytes())==take(GROUND,GROUND/'189427:0.json')['terrainWorldSHA256']
 assert len(scope['retainedPatches'])==1;record=scope['retainedPatches'][0];oldpath=ROOT/'3d-viewer'/record['url'];oldpatch=take(SCOPE,oldpath);old=_faces(oldpatch);domain=shapely.box(*record['extent'])
 # Foundation sampler only considers positive projected-area surfaces. Record
 # verticals separately; this diagnostic is never a publishable terrain asset.
 polys=shapely.polygons(ground[:,:,[0,2]]);areas=shapely.area(polys);vertical=np.flatnonzero(areas<=1e-12)
 output=list(old);untouched=[];clipped=[];removed=[]
 for i in np.flatnonzero(areas>1e-12):
  p=polys[i]
  if not p.intersects(domain): output.append(ground[i]);untouched.append(int(i));continue
  part=p.difference(domain)
  if part.area<=1e-12: removed.append(int(i));continue
  faces=lift(part,plane(ground[i]));output.extend(faces);clipped.append(dict(sourceFace=int(i),fragments=len(faces)))
 output=np.asarray(output,dtype='float64');assert np.array_equal(output[:len(old)],old);assert np.isfinite(output).all()
 b=row['source']['building'];final=module('yoho_retained_foundation',HERE/'xl-final-script-pass.py')
 result=final.foundation_context(model,output,Polygon(b['rings'][0],b['rings'][1:]))
 save(LOCAL/'diagnostic-height-surfaces.json.gz',dict(triangles=output.tolist(),notPublishable=True,excludedOriginalVerticalFaceIds=vertical.tolist()))
 save(DOC/'foundation.json',result)
 summary=dict(uids=[row['uid']],sourceSHA256=row['sourceSHA256'],completeSourceFaces=len(model),retainedTerrainSHA256=record['sha256'],retainedFacesUnchanged=len(old),originalGroundFaces=len(ground),excludedZeroProjectedAreaFaces=len(vertical),untouchedSourceFaces=len(untouched),clippedSourceFaces=len(clipped),removedWithinRetainedDomainFaces=len(removed),diagnosticFaces=len(output),foundation={k:v for k,v in result.items()if k!='components'},installationApproved=False,productionChanges=0,qualification='Height-surface diagnostic only, no parent-edge transition or final renderer validation; not a terrain publication candidate.')
 save(DOC/'lineage.json.gz',dict(untouched=untouched,clipped=clipped,removed=removed,excludedZeroProjectedArea=vertical.tolist()));save(DOC/'summary.json',summary)
 for folder in pins:
  for p in refs:
   key=str(p.relative_to(ROOT))
   if key in pins[folder]: assert digest(p.read_bytes())==pins[folder][key],p
 assert reservations.owns(lease)
 refs.extend([LOCAL/'diagnostic-height-surfaces.json.gz',HERE/'xl-final-script-pass.py',HERE/'source_surface_inset.py',HERE/'native_patch_resolution.py',HERE/'exact_packed_world_geometry_20261009.py'])
 r=module('yoho_retained_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'full-original-on-exact-retained-domain-ground',list(dict.fromkeys(refs)),summary)
 print(json.dumps(dict(jobId=r['jobId'],**summary)),flush=True)
def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists();claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['building:landsd/189427:0'],batch=BATCH,ttl=3600);assert claim['ok'],claim
 lease=claim['reservation'];p=LOCAL/'reservation.json';save(p,json.loads(json.dumps(lease,default=str)))
 try:subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(p),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
