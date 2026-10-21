"""Check each unchanged source against its own actual drawn terrain in four modes."""
from pathlib import Path
import json,numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-tko-grandiose-ground-only-v1-20261021';DOC=BASE/BATCH
NAMES=dict(capture='government-xl-tko-grandiose-joint-capture-v1-20261021',foundation='government-xl-tko-grandiose-joint-foundations-v3-20261021',runtime='government-xl-tko-grandiose-joint-runtime-v2-20261021')
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={};used={}
 for key,name in NAMES.items():
  _,pins[key]=authenticate(BASE/name);refs.append(BASE/name/'result.json')
 def take(key,path):
  k=str(path.relative_to(ROOT));assert digest(path.read_bytes())==pins[key][k];used[k]=pins[key][k];refs.append(path);return read(path)
 rows=take('capture',BASE/NAMES['capture']/'selection.json.gz')['rows'];actual={r['uid']:r for r in take('runtime',HERE/'local'/NAMES['runtime']/'runtime-geometry.json.gz')['rows']}
 final=module('joint_ground_foundation',HERE/'xl-final-script-pass.py');reports=[]
 for mode in ['original','literal','leftF32','balancedF32']:
  for row in rows:
   uid=row['uid'];inp=take('foundation',BASE/NAMES['foundation']/mode/uid.split('/')[1]/'input.json.gz')['rows'][0];assert inp['uid']==uid
   tri=np.asarray(inp['position']).reshape(-1,3)[np.asarray(inp['index']).reshape(-1,3)];runtime=actual[uid];assert runtime['sourceSHA256']==row['sourceSHA256'];ground=np.asarray(runtime['drawnGroundGeometry']).reshape(-1,3,3);b=row['source']['building']
   proof=final.foundation_context(tri,ground,Polygon(b['rings'][0],b['rings'][1:]));save(DOC/mode/(uid.split('/')[1]+'.json'),proof)
   report=dict(uid=uid,mode=mode,sourceWorldSHA256=digest(tri.tobytes()),groundSHA256=digest(ground.tobytes()),triangles=len(tri),covered=proof['completeTerrainTriangles'],buried=proof['fullyBuriedTriangles']);report['passed']=report['covered']==report['triangles'] and report['buried']==0;reports.append(report);print(json.dumps(report),flush=True)
 result=dict(uids=[r['uid']for r in rows],rows=reports,allTerrainChecksPassed=all(r['passed']for r in reports),installationApproved=False,sourceGeometryChanges=0,qualification='Terrain-only foundation proof; original-podium internal roof projection warnings remain separate.')
 save(DOC/'summary.json',result)
 for p,h in used.items():assert digest((ROOT/p).read_bytes())==h
 refs.append(HERE/'xl-final-script-pass.py');module('joint_ground_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'complete-current-four-mode-terrain-only-foundation',refs,result)
if __name__=='__main__':main()
