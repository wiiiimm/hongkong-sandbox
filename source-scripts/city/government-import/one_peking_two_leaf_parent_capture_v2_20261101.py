"""Capture a closed current envelope for two exact native leaves; no replacement/approval.
Every original drawn face of both leaves must survive with exact multiplicity.
"""
from pathlib import Path
from collections import Counter
import numpy as np
import subprocess
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-one-peking-after-twin-two-leaf-parent-capture-v2-20261101';P='government-xl-one-peking-after-twin-';URL='city/data/government-xl-academy69025-nested-original-terrain-20261029.json'
def main():
 out=BASE/BATCH;local=HERE/'local'/BATCH;assert not out.exists()and not local.exists();refs=[Path(__file__)];pins={}
 def take(batch,name):
  if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
  path=BASE/batch/name;assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 scope=take(P+'private-inset-current-scope-v1-20261101','scope.json');assert scope['positiveAreaTerrainOverlaps']==1;contact=scope['terrainContacts'][0];assert contact['url']==URL and [c['hierarchy']for c in contact['packedContacts']]==[[12],[15]]
 parentpath=ROOT/'3d-viewer'/URL;assert digest(parentpath.read_bytes())==pins[P+'private-inset-current-scope-v1-20261101'][str(parentpath.relative_to(ROOT))];refs.append(parentpath);parent=read(parentpath);assert len(parent['patches'])==17 and not parent.get('nativeMesh');indices=[12,15];selected=[parent['patches'][i]for i in indices]
 def extent(node):
  g=node['meta']['georef'];return [g['bE']-834500,816500-g['bN'],g['bE']-834500+(node['w']-1)*g['aE'],816500-g['bN']-(node['h']-1)*g['aN']]
 boxes=[extent(n)for n in selected];bounds=[min(b[i]for b in boxes)if i<2 else max(b[i]for b in boxes)for i in range(4)];assert bounds==[492.5,-1037.5,1127.5,-592.5]
 for i,node in enumerate(parent['patches']):
  if i in indices:continue
  b=extent(node);assert max(0,min(bounds[2],b[2])-max(bounds[0],b[0]))*max(0,min(bounds[3],b[3])-max(bounds[1],b[1]))==0,'Another retained child intersects the proposed combined envelope'
 manifest=ROOT/'3d-viewer/city/data/manifest.json';msha=digest(manifest.read_bytes());assert msha==pins[P+'private-inset-current-scope-v1-20261101'][str(manifest.relative_to(ROOT))];refs.append(manifest);out.mkdir();save(out/'scope.json',dict(bounds=bounds,uids=['landsd/233985:0','landsd/240487:0'],parentURL=URL,parentSHA256=digest(parentpath.read_bytes()),selectedChildIndices=indices,other15ChildrenDisjoint=True,publication=False))
 tool=HERE/'selected_original_parent_capture_closed_v3_20261101.mjs';target=local/'parent.json'
 prior=HERE/'local/government-xl-one-peking-after-twin-two-leaf-parent-capture-v1-20261101/parent.json';capture=read(prior);assert capture['domain']==bounds
 for path,sha in capture['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha
 # Reuse the successful production capture; only the independent winding verifier failed.
 import shutil
 local.mkdir();shutil.copyfile(prior,target);assert target.read_bytes()==prior.read_bytes();refs.append(prior)
 failed=BASE/'government-xl-one-peking-after-twin-two-leaf-parent-capture-v1-20261101';refs.extend([failed/'scope.json',failed/'worker.log',HERE/'one_peking_two_leaf_parent_capture_v1_20261101.py'])
 for path,sha in capture['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha;refs.append(ROOT/path)
 def key(face):
  face=[tuple(float(v)for v in p)for p in face];return min(tuple(face[i:]+face[:i])for i in range(3))
 actual=Counter(key(f)for f in capture['triangles']);expected=Counter();leaves=[]
 for i,node in zip(indices,selected):
  assert node.get('nativeMesh')and not node.get('patches')and not node.get('hydro');mesh=node['nativeMesh'];v=np.asarray(mesh['position'],dtype='<f4').astype('<f8').reshape(-1,3);ix=np.asarray(mesh['index']).reshape(-1,3);tri=v[ix].copy()
  # The production renderer flips only negative projected winding before drawing.
  for f in tri:
   a,b,c=f;y=(b[2]-a[2])*(c[0]-a[0])-(b[0]-a[0])*(c[2]-a[2])
   if y<0:f[[1,2]]=f[[2,1]]
  counts=Counter(key(f)for f in tri);expected.update(counts);leaves.append(dict(childIndex=i,id=node['id'],allOriginalDrawnFaces=len(tri),sourcePositionSHA256=digest(v.astype('<f4').tobytes()),originalIndexSHA256=digest(np.asarray(mesh['index'],dtype='<u4').tobytes()),targetUids=node['meta']['targetUids']))
 missing=expected-actual;assert not missing,'Closed capture omitted or changed an original leaf facet/multiplicity'
 assert digest(manifest.read_bytes())==msha and digest(parentpath.read_bytes())==capture['inputHashes'][str(parentpath.relative_to(ROOT))]
 result=dict(uids=['landsd/233985:0','landsd/240487:0'],currentManifestSHA256=msha,parentURL=URL,parentSHA256=digest(parentpath.read_bytes()),bounds=bounds,leaves=leaves,completeRetainedLeafFaces=sum(expected.values()),capturedCurrentFaces=len(capture['triangles']),everyOriginalLeafDrawnFaceAndMultiplicityPreserved=True,other15ChildrenPositiveAreaDisjoint=True,sourceGeometryChanges=0,terrainReplacementConstructed=False,identityAccepted=False,physicalAcceptance=False,installationApproved=False,publication=False,successfulCaptureReusedWithEveryCurrentInputHashVerified=True,qualification=__doc__+' Actual production renderer, Float32 positions and effective winding; closed vertical-boundary faces retained. Capture is input evidence for possible bounded two-leaf composition, not an approved replacement or a claim that non-leaf extra faces have yet been classified.')
 save(out/'summary.json',result);refs.extend([tool,target,HERE/'clip_parent_terrain_triangle_v1.mjs']);module('one_peking_two_leaf_current_parent_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-closed-two-native-leaf-current-rendered-parent-input-capture',list(dict.fromkeys(refs)),result)
if __name__=='__main__':main()
