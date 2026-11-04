"""Separate four authenticated lower-wall facets from the unchanged remainder.

Diagnostic only: keep every source facet and all ordinary foundation thresholds.
"""
import argparse
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-elegant-garden-four-wall-foundation-v1-20261027'
OLD='government-xl-elegant-garden-block2-four-world-support-v1-20261027';RUNTIME='government-xl-elegant-garden-private-inset-runtime-v1-20261027';UID,SUPPORT='landsd/173532:0','landsd/236170:0';FACES=[10385,10388,10389,10506]
def main():
 p=argparse.ArgumentParser();p.add_argument('--lease',required=True);a=p.parse_args();lease=read(Path(a.lease));assert reservations.owns(lease)and {'building:'+u for u in [UID,SUPPORT]}<=set(lease['resources'])
 out=BASE/BATCH;assert not out.exists();refs=[Path(__file__)];pins={}
 def take(batch,path):
  if batch not in pins:pins[batch]=authenticate(BASE/batch)[1];refs.append(BASE/batch/'result.json')
  assert digest(path.read_bytes())==pins[batch][str(path.relative_to(ROOT))];refs.append(path);return read(path)
 old=take(OLD,BASE/OLD/'summary.json');selection=take(RUNTIME,BASE/RUNTIME/'selection.json.gz');geometry=take(RUNTIME,HERE/'local'/RUNTIME/'runtime-geometry.json.gz');g=next(r for r in geometry['rows']if r['uid']==UID);row=next(r for r in selection['rows']if r['uid']==UID)
 assert g['sourceSHA256']==row['sourceSHA256']==old['sourceSHA256ByUid'][UID]
 ground=np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3);ground_sha=digest(ground.astype('<f8').tobytes());f=row['source']['building'];polygon=Polygon(f['rings'][0],f['rings'][1:]);final=module('elegant_four_wall_final',HERE/'xl-final-script-pass.py');rows=[]
 for mode in ['original','literal','leftF32','balancedF32']:
  assert reservations.owns(lease);data=take(OLD,BASE/OLD/mode/'input.json.gz');source=data['rows'][0];tri=np.asarray(source['position'],dtype='<f8').reshape(-1,3)[np.asarray(source['index']).reshape(-1,3)];podium=np.asarray(data['podium'],dtype='<f8');prior=next(r for r in old['rows']if r['mode']==mode)
  assert digest(tri.tobytes())==prior['sourceWorldSHA256ByUid'][UID]and digest(podium.tobytes())==prior['sourceWorldSHA256ByUid'][SUPPORT]
  if mode=='literal':assert np.array_equal(tri,np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)])
  rest=[i for i in range(len(tri))if i not in FACES];combined=np.concatenate([ground,podium]);ordinary=final.foundation_context(tri[rest],combined,polygon);wall=final.foundation_context(tri[FACES],combined,polygon)
  passed=ordinary['triangles']==ordinary['completeTerrainTriangles']==10889 and ordinary['fullyBuriedTriangles']==ordinary['fullyBuriedUpwardTriangles']==0 and ordinary['minimumGapM']>=-.5
  result=dict(mode=mode,excludedSourceFaces=FACES,ordinarySourceFaces=rest,ordinaryFoundation=ordinary,ordinaryFoundationPolicyPassed=passed,fourWallFoundation=wall,rawWholeFoundation=prior['compoundFoundation'],groundSHA256=ground_sha)
  save(out/(mode+'.json.gz'),result);rows.append({k:v for k,v in result.items()if k!='ordinarySourceFaces'});print(dict(mode=mode,ordinaryPassed=passed,ordinaryMinimumGapM=ordinary['minimumGapM'],ordinaryBuried=ordinary['fullyBuriedTriangles']),flush=True)
 result=dict(uids=[UID,SUPPORT],sourceSHA256ByUid=old['sourceSHA256ByUid'],rows=rows,allOtherFacesPassOrdinaryFoundation=all(r['ordinaryFoundationPolicyPassed']for r in rows),sourceGeometryChanges=0,physicalSupportAccepted=False,installationApproved=False,qualification='Exact original four-facet classification probe; every other10889face tested under unchanged ordinary foundation requirements using authenticated same private ground/podium. Raw whole-model foundation and support negatives retained. No facet removed from model or runtime, no new role/embedding/support/installation acceptance.')
 save(out/'summary.json',result);assert reservations.owns(lease);refs.append(HERE/'xl-final-script-pass.py');module('elegant_four_wall_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-four-lower-wall-versus-ordinary-source-foundation',refs,result)
if __name__=='__main__':main()
