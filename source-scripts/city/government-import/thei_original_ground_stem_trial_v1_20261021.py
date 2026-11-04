"""Private THEi original-TIN/local low-stem feasibility; never publish or approve."""
import json, subprocess, sys, uuid
from pathlib import Path
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from china_merchants_finite_inset_v4_20261021 import plane,lift
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-thei-original-ground-stem-trial-v1-20261021'
DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
CURRENT=BASE/'government-xl-thei-current-runtime-v1-20261021'
OLD=BASE/'government-xl-259803-independent-original-ground-20261008'
UIDS=['landsd/259613:0','landsd/259803:0']
def owned():
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease)
 refs=[Path(__file__)];consumed={}
 def take(folder,path):
  receipt,pins=authenticate(folder);refs.append(folder/'result.json')
  key=str(path.relative_to(ROOT));assert digest(path.read_bytes())==pins[key]
  consumed[key]=pins[key];refs.append(path);return read(path)
 selection=take(CURRENT,CURRENT/'selection.json.gz');rows=selection['rows'];assert {r['uid']for r in rows}==set(UIDS)
 manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256'];refs.append(manifest)
 meta=take(OLD,OLD/'terrain.json');patchpath=ROOT/meta['patch']['path'];assert digest(patchpath.read_bytes())==meta['patch']['sha256'];refs.append(patchpath)
 patch=read(patchpath);mesh=patch['nativeMesh'];ground=np.asarray(mesh['position']).reshape(-1,3)[np.asarray(mesh['index']).reshape(-1,3)]
 world={}
 for r in rows:
  asset=ROOT/r['candidate']['path'];assert digest(asset.read_bytes())==r['sourceSHA256'];refs.append(asset)
  world[r['uid']]=decode_original_world_triangles(asset.read_bytes());assert len(world[r['uid']])==r['triangles']
 tower=world[UIDS[0]];floor=float(tower[:,:,1].min());feet=tower.reshape(-1,3);feet=feet[feet[:,1]<=floor+.001]
 core=shapely.MultiPoint(feet[:,[0,2]]).convex_hull.buffer(.25,join_style='mitre');outer=core.buffer(3,join_style='mitre')
 polygons=shapely.polygons(ground[:,:,[0,2]]);assert outer.difference(shapely.union_all(polygons)).area<1e-8
 output=[];lineage=[]
 for i,(face,poly) in enumerate(zip(ground,polygons)):
  if poly.area<=1e-10 or poly.disjoint(outer):output.append(face.copy());lineage.append(i);continue
  coeff=plane(face)
  for region in [poly.intersection(core),poly.intersection(outer).difference(core),poly.difference(outer)]:
   for fragment in lift(region,coeff):
    for vertex in fragment:
     weight=max(0.,1-shapely.Point(vertex[[0,2]]).distance(core)/3)
     vertex[1]=min(vertex[1],vertex[1]+weight*(floor-vertex[1]))
    output.append(fragment);lineage.append(i)
 output=np.asarray(output);assert np.isfinite(output).all()
 final=module('thei_stem_foundation',HERE/'xl-final-script-pass.py');results=[]
 for r in rows:
  b=r['source']['building'];foundation=final.foundation_context(world[r['uid']],output,shapely.Polygon(b['rings'][0],b['rings'][1:]))
  save(DOC/(r['uid'].split('/')[1]+'.json'),foundation)
  results.append(dict(uid=r['uid'],foundation={k:v for k,v in foundation.items()if k!='components'}));print(results[-1],flush=True)
 save(LOCAL/'private-ground.json.gz',dict(triangles=output.tolist(),notPublishable=True))
 save(DOC/'lineage.json.gz',dict(originalFaceIds=lineage,coreWKT=core.wkt,outerWKT=outer.wkt,sourceMinimumY=floor))
 summary=dict(uids=UIDS,rows=results,originalGroundFaces=len(ground),trialFaces=len(output),installationApproved=False,productionChanges=0,nextStep='Check actual contact warnings, complete current replacement scope and neighbours before any terrain acceptance.')
 save(DOC/'summary.json',summary)
 for key,h in consumed.items():assert digest((ROOT/key).read_bytes())==h
 assert digest(manifest.read_bytes())==selection['manifestSHA256'] and reservations.owns(lease)
 refs += [LOCAL/'private-ground.json.gz',HERE/'xl-final-script-pass.py',HERE/'exact_packed_world_geometry_20261009.py',HERE/'china_merchants_finite_inset_v4_20261021.py']
 module('thei_stem_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-tin-local-stem-private-feasibility',list(dict.fromkeys(refs)),summary)
def main():
 if '--owned' in sys.argv:return owned()
 assert not DOC.exists() and not LOCAL.exists()
 claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['building:'+u for u in UIDS],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];save(LOCAL/'reservation.json',json.loads(json.dumps(lease,default=str)))
 try:subprocess.run([sys.executable,str(HERE/'harbourfront_reserved_runner_v1_20261021.py'),str(LOCAL/'reservation.json'),sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
