"""Capture the complete existing world across the full bounded floor-return domain."""
import sys,uuid,subprocess
from pathlib import Path
from collections import Counter
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from observed_reserved_runner_v4_20261103 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from retained_bounded_floor_work_v1_20261102 import inset
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-silvercord-lippo-complete-floor-work-v3-20261103'
OLD='government-xl-silvercord-lippo-private-source-floor-trial-v1-20261103'
RUNTIME='government-xl-silvercord-lippo-current-floor-sequence-v1-20261103-runtime'
LOCAL=HERE/'local'/BATCH
UIDS=['landsd/233997:0','landsd/231645:0']

def owned():
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease);refs=[Path(__file__)];pins={}
 def take(batch,name):
  if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
  path=BASE/batch/name;assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 previous=take(OLD,'231645-0/private-ground.json.gz');row=next(r for r in take(RUNTIME,'selection.json.gz')['rows']if r['uid']=='landsd/231645:0')
 asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256'];refs.append(asset)
 original=decode_original_world_triangles(asset.read_bytes());faces=original[previous['sourceFaceIndices']]
 outer=shapely.union_all(shapely.polygons(faces[:,:,[0,2]])).buffer(1.,join_style='mitre').buffer(3.,join_style='mitre')
 out=BASE/BATCH;scope=out/'full-work-capture-scope.json';save(scope,dict(bounds=list(outer.bounds),sourceFaceIndices=previous['sourceFaceIndices'],coreBufferM=1,returnBufferM=3))
 capture=LOCAL/'full-world-parent-facets.json';tool=HERE/'source_floor_complete_world_capture_v2_20261103.mjs';refs.append(tool)
 with (out/'worker.log').open('w')as log:subprocess.run(['node',str(tool),str(scope.relative_to(ROOT)),str(capture.relative_to(ROOT))],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=1800)
 data=read(capture);refs.append(capture)
 for path,sha in data['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha;refs.append(ROOT/path)
 before=np.asarray([r['triangle']for r in data['rows']]);after,proof=inset(before,faces)
 save(out/'231645-0/private-ground.json.gz',dict(before=before.tolist(),after=after.tolist(),sourceFaceIndices=previous['sourceFaceIndices']))
 save(out/'231645-0/return-proof.json.gz',proof)
 changed=proof['changedTerrainFaceIndices'];owners=[dict(capturedFace=i,**{k:data['rows'][i][k]for k in ['url','meshPath','meshName','renderedFace']})for i in changed]
 save(out/'changed-parent-facets.json',dict(rows=owners,inputHashes=data['inputHashes']))
 counts=dict(Counter(r['url']for r in owners));result=dict(uids=UIDS,fullFloorWorkEnvelope=list(outer.bounds),inputFaces=len(before),outputFaces=len(after),changedParentFaces=len(changed),changedByParent=counts,fullWorkCapturedAcrossAllCurrentParents=True,outsideWorkFacesLiteral=proof['outsideWorkFacesLiteral'],sourceGeometryChanges=0,sourcePoseChanges=0,terrainValidatorPassed=False,physicalAcceptance=False,installationApproved=False,publication=False)
 save(out/'summary.json',result);assert reservations.owns(lease)
 refs.extend([HERE/'retained_bounded_floor_work_v1_20261102.py',HERE/'source_floor_return_with_existing_seabed_v1_20261102.py',HERE/'bounded_original_upward_floor_return_v1_20261029.py'])
 module('pair_complete_floor_work_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-current-world-bounded-original-floor-return',list(dict.fromkeys(refs)),result)
 print(result,flush=True)

if __name__=='__main__':
 if '--owned'in sys.argv:owned()
 else:
  assert not LOCAL.exists() and not(BASE/BATCH).exists()
  # Read-only all-world capture: source reservations plus exact end-of-run
  # terrain/manifest byte checks; no terrain writes or acceptance is performed.
  keys={'building:'+u for u in UIDS}|{'immutable-source-proof:'+BATCH}
  claim=reservations.claim('pair-full-floor-world-'+str(uuid.uuid4()),sorted(keys),batch=BATCH,ttl=3600);assert claim['ok']
  execute_reserved(claim['reservation'],LOCAL/'reservation.json',[sys.executable,__file__,'--owned'])
