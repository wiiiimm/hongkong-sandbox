"""Classify every extra captured face as actual retained production root grid.
No terrain construction, replacement, source approval or publication.
"""
from collections import Counter
from pathlib import Path
import subprocess
import numpy as np
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-one-peking-after-twin-root-grid-classification-v1-20261101';CAP='government-xl-one-peking-after-twin-two-leaf-parent-capture-v2-20261101'
def key(face):
 f=[tuple(map(float,p))for p in face];return min(tuple(f[i:]+f[:i])for i in range(3))
def main():
 out=BASE/BATCH;local=HERE/'local'/BATCH;assert not out.exists()and not local.exists();receipt,pins=authenticate(BASE/CAP);refs=[Path(__file__),BASE/CAP/'result.json']
 def take(path):
  assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))];refs.append(path);return read(path)
 summary=take(BASE/CAP/'summary.json');capture=take(HERE/'local'/CAP/'parent.json');parentpath=ROOT/'3d-viewer'/summary['parentURL'];parent=take(parentpath);expected=Counter()
 for i in [12,15]:
  node=parent['patches'][i];mesh=node['nativeMesh'];v=np.asarray(mesh['position'],dtype='<f4').astype('<f8').reshape(-1,3);tri=v[np.asarray(mesh['index']).reshape(-1,3)].copy()
  for face in tri:
   a,b,c=face;y=(b[2]-a[2])*(c[0]-a[0])-(b[0]-a[0])*(c[2]-a[2])
   if y<0:face[[1,2]]=face[[2,1]]
  expected.update(key(f)for f in tri)
 actual=Counter(key(f)for f in capture['triangles']);assert not expected-actual and sum(expected.values())==48782
 out.mkdir();save(out/'scope.json',dict(bounds=summary['bounds'],parentURL=summary['parentURL'],publication=False));tool=HERE/'one_peking_root_grid_capture_v1_20261101.mjs';target=local/'root-grid.json'
 with(out/'worker.log').open('w')as log:subprocess.run(['node',str(tool),str((out/'scope.json').relative_to(ROOT)),str(target.relative_to(ROOT))],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
 grid=read(target);assert grid['domain']==summary['bounds'];counts=Counter(key(f)for f in grid['triangles']);assert counts==actual-expected,'Extra faces do not exactly match current root grid';assert sum(counts.values())==1146
 for path,sha in grid['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha;refs.append(ROOT/path)
 result=dict(uids=receipt['uids'],currentManifestSHA256=summary['currentManifestSHA256'],parentURL=summary['parentURL'],parentSHA256=digest(parentpath.read_bytes()),bounds=summary['bounds'],oldLeafFaces=48782,rootGridFaces=1146,completeCapturedFaces=sum(actual.values()),completeFaceAndMultiplicityPartition=True,rootGridUnchanged=True,sourceGeometryChanges=0,terrainReplacementConstructed=False,physicalAcceptance=False,installationApproved=False,publication=False,qualification=__doc__)
 save(out/'summary.json',result);refs.extend([tool,target]);module('one_peking_root_grid_classification_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-current-two-leaf-and-root-grid-exact-face-partition',list(dict.fromkeys(refs)),result)
if __name__=='__main__':main()
