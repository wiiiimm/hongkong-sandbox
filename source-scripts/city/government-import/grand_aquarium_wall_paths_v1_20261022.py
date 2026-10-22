"""Original wall connectivity with exact same-ground coverage corrections only."""
from pathlib import Path
import numpy as np,copy
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from unchanged_open_exterior_paths_v2_20261009 import original_open_paths
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-grand-aquarium-original-wall-paths-v1-20261022'
def main():
 doc=BASE/BATCH;assert not doc.exists();refs=[Path(__file__)]
 def take(batch,name,local=False):
  folder=BASE/batch;_,pins=authenticate(folder);p=(HERE/'local'/batch if local else folder)/name;assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.extend([folder/'result.json',p]);return read(p)
 context=take('government-xl-grand-aquarium-crack-repaired-continuous-v1-20261022','93424:0.json.gz');exact=take('government-xl-grand-aquarium-crack-repaired-exact-coverage-v1-20261022','93424:0.json.gz');g=take('government-xl-grand-aquarium-crack-repaired-runtime-v1-20261022','runtime-geometry.json.gz',True)['rows'][0];tri=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];binding=context['sourceBinding'];assert exact['sourceBinding']==binding and digest(tri.tobytes())==binding['decodedWorldTrianglesSHA256'];faces=copy.deepcopy(context['faces'])
 for p in exact['proofs']:
  assert p['exactProjectionCovered']and p['completeGroundSHA256']==binding['drawnGroundSHA256'];i=p['sourceFace'];assert digest(tri[i].tobytes())==p['sourceFaceSHA256'];faces[i]['rawFloatingCoverageFalseRetained']=True;faces[i]['groundProjectionCovered']=True;faces[i]['exactSameGroundCoverageProof']=p
 assert all(f['groundProjectionCovered']for f in faces)
 paths=original_open_paths(tri,faces,context['affectedWallFaces'],range(len(tri)),expected_binding=binding,current_binding=binding);save(doc/'paths.json.gz',paths);rows=paths['faces'];result=dict(uids=['landsd/93424:0'],sourceSHA256=g['sourceSHA256'],affectedOriginalWallFaces=len(rows),qualifiedOriginalRoleNecessaryConditions=sum(r['verifiedRoleNecessaryConditions']for r in rows),unresolved=[r for r in rows if r['reasons']],sourceGeometryChanges=0,installationApproved=False,newlyInstalled=0,qualification='Original exact shared-edge wall/roof connectivity and exposure diagnostics only; no architectural, physical or publication approval. Whole current foreign scope remains independent.');save(doc/'summary.json',result);refs.append(HERE/'unchanged_open_exterior_paths_v2_20261009.py');module('aquarium_wall_paths_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'source-specific-original-wall-connectivity-diagnostic',refs,result);print(result)
if __name__=='__main__':main()
