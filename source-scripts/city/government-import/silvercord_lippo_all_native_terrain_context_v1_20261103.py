"""Exhaustive full-bounds terrain delta routing for all required installed natives.

An exact unchanged terrain context is evidence only. Intersecting actors remain
pending full mesh/support checks; no source, support or installation reapproval.
"""
import sys,uuid,subprocess
from pathlib import Path
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from observed_reserved_runner_v4_20261103 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-silvercord-lippo-all-native-terrain-context-v1-20261103'
SCOPE='government-xl-silvercord-lippo-full-current-parent-scope-v3-20261103'
CANDIDATE='government-xl-silvercord-lippo-complete-floor-candidate-v4-20261103'
LOCAL=HERE/'local'/BATCH;UIDS=['landsd/233997:0','landsd/231645:0']

def canonical(tri):
 tri=np.asarray(tri,dtype='<f4');assert np.isfinite(tri).all()
 order=np.lexsort((tri[:,:,2],tri[:,:,1],tri[:,:,0]),axis=1)
 ordered=np.take_along_axis(tri,order[:,:,None],axis=1);ordered[ordered==0]=0
 return np.ascontiguousarray(ordered).reshape(-1,9).view(np.dtype('V36')).ravel()

def owned():
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease);refs=[Path(__file__)];pins={}
 def take(batch,name):
  if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
  path=BASE/batch/name;assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 scope=take(SCOPE,'summary.json');proposal=take(CANDIDATE,'summary.json');inventory=take(SCOPE,'complete-current-actor-bounds.json.gz')['rows'];by={r['uid']:r for r in inventory}
 required=set(scope['affectedNativeUids']);assert required<=by.keys() and len(required)==1228
 manifest_path=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest_path.read_bytes())==scope['currentManifestSHA256']==proposal['currentManifestSHA256'];refs.append(manifest_path)
 models={};form_tiles={}
 for url in read(manifest_path)['officialModelCatalogues']:
  path=ROOT/'3d-viewer'/url;assert digest(path.read_bytes())==pins[SCOPE][str(path.relative_to(ROOT))];refs.append(path)
  for m in read(path)['models']:assert m['uid']not in models;models[m['uid']]=m
 assert set(models)==set(by)
 # Preserve complete native dependency closure as additional terrain-context
 # obligations without rewriting original installed/fallback support contracts.
 closure=set(required);todo=list(required);basic=set()
 while todo:
  uid=todo.pop()
  for dependency in models[uid].get('supportDependencies',[]):
   other=dependency['uid']if isinstance(dependency,dict)else dependency
   if other in models:
    if other not in closure:closure.add(other);todo.append(other)
   else:basic.add(other)
 fresh=ROOT/proposal['currentFloorCapture']['path'];assert digest(fresh.read_bytes())==proposal['currentFloorCapture']['sha256'];refs.append(fresh)
 north_ref=proposal['additionalTopLevelPatch'];north_path=ROOT/north_ref['path'];assert digest(north_path.read_bytes())==north_ref['sha256'];north=read(north_path);refs.append(north_path)
 g=north['meta']['georef'];lo=np.array([g['bE']-834500,816500-g['bN']]);hi=lo+np.array([(north['w']-1)*g['aE'],-(north['h']-1)*g['aN']])
 root_before=[r['triangle']for r in read(fresh)['rows']if r['url']=='city/data/terrain.json'and np.array_equal(np.asarray(r['triangle'])[:,[0,2]].min(0),lo)and np.array_equal(np.asarray(r['triangle'])[:,[0,2]].max(0),hi)]
 assert len(root_before)==2
 old=proposal['replacedParent'];old_path=ROOT/'3d-viewer'/old['url'];assert digest(old_path.read_bytes())==old['sha256'];refs.append(old_path)
 candidate=proposal['candidate'];candidate_path=ROOT/candidate['path'];assert digest(candidate_path.read_bytes())==candidate['sha256'];refs.append(candidate_path)
 out=BASE/BATCH;capture_scope=out/'delta-inputs.json';save(capture_scope,dict(oldParent=dict(path=str(old_path.relative_to(ROOT)),sha256=old['sha256']),candidate=candidate,north=dict(path=north_ref['path'],sha256=north_ref['sha256']),rootBeforeFacets=root_before,inputRefs=[dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))for p in [manifest_path,fresh]]))
 tool=HERE/'source_floor_complete_terrain_delta_v1_20261103.mjs';geometry=LOCAL/'complete-terrain-before-after.json.gz';refs.append(tool)
 with(out/'worker.log').open('w')as log:subprocess.run(['node',str(tool),str(capture_scope.relative_to(ROOT)),str(geometry.relative_to(ROOT))],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=3600)
 data=read(geometry);refs.append(geometry)
 for path,sha in data['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha;refs.append(ROOT/path)
 before=np.asarray(data['before'],dtype='<f4');after=np.asarray(data['after'],dtype='<f4');a=canonical(before);b=canonical(after)
 unique,inv=np.unique(np.concatenate([a,b]),return_inverse=True);counts_a=np.bincount(inv[:len(a)],minlength=len(unique));counts_b=np.bincount(inv[len(a):],minlength=len(unique));delta_keys=unique[counts_a!=counts_b]
 delta=np.asarray([np.frombuffer(k.tobytes(),dtype='<f4').reshape(3,3)for k in delta_keys]);assert len(delta)>0
 save(out/'actual-changed-rendered-facets.json.gz',dict(triangles=delta.tolist(),beforeMultiplicity=counts_a[counts_a!=counts_b].tolist(),afterMultiplicity=counts_b[counts_a!=counts_b].tolist()))
 old_min=before[:,:,[0,2]].min(1);old_max=before[:,:,[0,2]].max(1);tree=shapely.STRtree(shapely.box(old_min[:,0],old_min[:,1],old_max[:,0],old_max[:,1]))
 dmin=delta[:,:,[0,2]].min(1);dmax=delta[:,:,[0,2]].max(1);rows=[]
 for uid in sorted(closure):
  r=by[uid];assert r['sourceSHA256']==models[uid]['sha256'];bounds=np.asarray(r['completeFourWorldBounds']);low=bounds[:,0].min(0)[[0,2]];high=bounds[:,1].max(0)[[0,2]]
  contacts=np.flatnonzero(np.all(dmax>=low,axis=1)&np.all(dmin<=high,axis=1));old_faces=tree.query(shapely.box(low[0],low[1],high[0],high[1]));assert len(old_faces)>0
  rows.append(dict(uid=uid,sourceSHA256=r['sourceSHA256'],requiredNative=uid in required,completeFourWorldBounds=r['completeFourWorldBounds'],completeIntersectingTerrainFaces=len(old_faces),intersectingChangedFacetIndices=contacts.tolist(),exactRenderedTerrainMultisetUnchanged=len(contacts)==0,fullMeshCheckStillRequired=len(contacts)>0,existingSourceOrSupportReaccepted=False))
 save(out/'complete-native-contexts.json.gz',dict(rows=rows))
 unresolved=[r['uid']for r in rows if r['fullMeshCheckStillRequired']]
 result=dict(uids=UIDS,currentManifestSHA256=scope['currentManifestSHA256'],allRequiredNativeUids=sorted(required),nativeDependencyClosure=sorted(closure),registeredBasicDependencyUids=sorted(basic),completeBeforeFaces=len(before),completeAfterFaces=len(after),changedFacetKeys=len(delta),allRequiredNativeBoundsChecked=True,exactUnchangedNativeContexts=sum(r['exactRenderedTerrainMultisetUnchanged']for r in rows),remainingFullMeshUids=unresolved,existingNativeReaccepted=False,sourceGeometryChanges=0,physicalAcceptance=False,installationApproved=False,publication=False,qualification='Exact complete rendered face-multiset delta, including multiplicities and new root masking, routed against every required original/literal/Float32 whole source bound plus native support closure. Unchanged contexts do not reapprove sources/supports. Intersecting contexts remain mandatory full mesh/support checks; full current actor source hashes are bound to the verified census.')
 save(out/'summary.json',result);assert reservations.owns(lease)and digest(manifest_path.read_bytes())==scope['currentManifestSHA256']
 module('pair_all_native_terrain_context_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-rendered-terrain-multiset-delta-all-native-whole-bounds',list(dict.fromkeys(refs)),result)
 print({k:result[k]for k in ['exactUnchangedNativeContexts','remainingFullMeshUids','changedFacetKeys','installationApproved']},flush=True)
if __name__=='__main__':
 if '--owned'in sys.argv:owned()
 else:
  assert not LOCAL.exists()and not(BASE/BATCH).exists();claim=reservations.claim('pair-all-native-terrain-context-'+str(uuid.uuid4()),['building:'+u for u in UIDS]+['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok']
  execute_reserved(claim['reservation'],LOCAL/'reservation.json',[sys.executable,__file__,'--owned'])
