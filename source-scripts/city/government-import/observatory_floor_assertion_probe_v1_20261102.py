"""Observe the unchanged floor-kernel assertion; no geometry or acceptance change."""
import sys,uuid
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from north_pair_nonwall_topology_v1_20261027 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from retained_native_floor_domains_v1_20261102 import inset
import bounded_original_upward_floor_return_v3_20261102 as kernel
BATCH='government-xl-observatory252988-floor-assertion-probe-v1-20261102';BASE=ROOT/'docs/astra-city/government-import';RUNTIME='government-xl-observatory252988-after-yoho-current-v1-20261102-runtime';LOW='government-xl-observatory252988-current-low-faces-v1-20261102';ENVELOPE='government-xl-observatory252988-full-native-envelope-v1-20261102';UID='landsd/252988:0';URL='city/data/government-native-118475-0.json'
def main():
 out=BASE/BATCH;lp=HERE/'local'/BATCH/'reservation.json';assert not out.exists();pins={};refs=[Path(__file__)]
 def take(batch,path):
  if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
  assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 forms=take(ENVELOPE,BASE/ENVELOPE/'form-obligations.json.gz');resources={'building:'+f['uid']for f in forms}|{'building:'+UID,'terrain:city/data/terrain.json','terrain:'+URL}
 if '--owned'not in sys.argv:
  assert not lp.parent.exists();c=reservations.claim('observatory-floor-probe-'+str(uuid.uuid4()),sorted(resources),batch=BATCH,ttl=3600);assert c['ok'],c
  return execute_reserved(c['reservation'],lp,[sys.executable,__file__,'--owned'])
 lease=read(lp);assert reservations.owns(lease)and set(lease['resources'])==resources
 sel=take(RUNTIME,BASE/RUNTIME/'selection.json.gz')['rows'][0];asset=ROOT/sel['candidate']['path'];assert digest(asset.read_bytes())==sel['sourceSHA256'];refs.append(asset);tri=decode_original_world_triangles(asset.read_bytes());low=take(LOW,BASE/LOW/'original.json.gz');assert low['sourceWorldSHA256']==digest(tri.astype('<f8').tobytes());ids=[]
 for r in low['rows']:
  t=tri[r['sourceFace']];assert np.array_equal(t,np.asarray(r['vertices']));n=np.cross(t[1]-t[0],t[2]-t[0]);length=np.linalg.norm(n)
  if length and n[1]/length>=.25:ids.append(r['sourceFace'])
 assert ids==[11997,11998];node=take(RUNTIME,ROOT/'3d-viewer'/URL);vertices=np.asarray(node['nativeMesh']['position'],dtype='<f4').astype('<f8').reshape(-1,3);terrain=vertices[np.asarray(node['nativeMesh']['index']).reshape(-1,3)];observed=[];source=Path(kernel.__file__);lines=source.read_text().splitlines();line=next(i+1 for i,s in enumerate(lines)if 'assert abs(removed-inserted)'in s)
 def tracer(frame,event,arg):
  if event=='line'and frame.f_code.co_filename==str(source)and frame.f_lineno==line:
   v=frame.f_locals;observed.append(dict(originalTerrainFaces=len(v['terrain']),outputFaces=len(v['output']),changedParentFaces=len(v['changed']),removedAreaM2=v['removed'],insertedAreaM2=v['inserted'],signedAreaDifferenceM2=v['removed']-v['inserted'],areaCheckPassed=abs(v['removed']-v['inserted'])<1e-6,budgetCheckPassed=len(v['output'])<=25000,thresholdsChanged=False))
  return tracer
 error=None;sys.settrace(tracer)
 try:inset(terrain,tri[ids])
 except AssertionError as e:error=type(e).__name__
 finally:sys.settrace(None)
 assert error and observed and reservations.owns(lease);save(out/'summary.json',dict(uid=UID,sourceSHA256=sel['sourceSHA256'],sourceFloorFaceIndices=ids,observed=observed,originalKernelAssertionRetained=True,sourceGeometryChanges=0,terrainGeometryChanges=0,installationApproved=False,publication=False));refs.extend([source,HERE/'retained_native_floor_domains_v1_20261102.py',HERE/'source_floor_return_with_existing_seabed_v1_20261102.py']);module('observatory_floor_probe_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'unchanged-floor-kernel-exact-assertion-diagnostic',refs,read(out/'summary.json'));print(observed,flush=True)
if __name__=='__main__':main()
