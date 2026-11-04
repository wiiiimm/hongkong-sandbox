"""Reuse exact original-edge minimax paths for the seven saved support warnings."""
import argparse
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from original_face_attachment_minimax_v2_20261024 import attachment_paths
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-elegant-garden-seven-witness-paths-v1-20261027'
OLD='government-xl-elegant-garden-block2-four-world-support-v1-20261027'
CONTACT='government-xl-elegant-garden-seven-witness-contacts-v1-20261027'
UID,SUPPORT='landsd/173532:0','landsd/236170:0'
def main():
 p=argparse.ArgumentParser();p.add_argument('--lease',required=True);a=p.parse_args();lease=read(Path(a.lease))
 assert reservations.owns(lease)and {'building:'+u for u in [UID,SUPPORT]}<=set(lease['resources'])
 out=BASE/BATCH;assert not out.exists();refs=[Path(__file__)];pins={}
 def take(batch,name):
  if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
  path=BASE/batch/name;assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 strict=take(OLD,'summary.json');contacts=take(CONTACT,'summary.json');assert strict['sourceSHA256ByUid']==contacts['sourceSHA256ByUid']
 rows=[]
 for original in strict['rows']:
  assert reservations.owns(lease);mode=original['mode'];data=take(OLD,mode+'/input.json.gz');g=data['rows'][0]
  tri=np.asarray(g['position'],dtype='<f8').reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];assert digest(tri.tobytes())==original['sourceWorldSHA256ByUid'][UID]
  record=take(CONTACT,mode+'.json.gz');assert [r['witness']for r in record['targets']]==original['support']['unresolved']
  targets=[dict(witness=r['witness'],incidentFaces=r['incidentSourceFaces'])for r in record['targets']]
  paths=attachment_paths(tri,dict(targets=targets,proof=record['proof']),[])
  assert len(paths)==7
  result=dict(mode=mode,witnesses=7,finitePaths=sum(r['hasUnrestrictedFiniteAttachment']for r in paths),pathsWithinExistingEndpointHeight=sum(r.get('passesExistingEndpointHeight',False)for r in paths),rawSupportPassed=original['passed'])
  save(out/(mode+'.json.gz'),dict(**result,rows=paths));rows.append(result);print(result,flush=True)
 result=dict(uids=[UID,SUPPORT],sourceSHA256ByUid=strict['sourceSHA256ByUid'],rows=rows,physicalSupportAccepted=False,installationApproved=False,sourceGeometryChanges=0,qualification='Exact original full-edge traversal and positive finite original podium intersections. Existing endpoint height and0.001m residual gates unchanged. Raw strict support/foundation failures preserved. No new join, embedding allowance, source role or installation approval.')
 save(out/'summary.json',result);assert reservations.owns(lease)
 refs.append(HERE/'original_face_attachment_minimax_v2_20261024.py')
 module('elegant_seven_path_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'seven-rim-witness-exact-original-edge-paths',refs,result)
if __name__=='__main__':main()
