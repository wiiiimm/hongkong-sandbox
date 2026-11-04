"""Test untouched recovered podium against all canonical tower support samples."""
from pathlib import Path
import subprocess
import numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-orchards-original-podium-support-v1-20261017';DOC=BASE/BATCH
TOWER=BASE/'government-xl-orchards-connection-overlap-terrain-v1-20261017';PODIUM=BASE/'government-xl-orchards-podium-original-recovery-v1-20261017'
def main():
 assert not DOC.exists();refs=[Path(__file__)]
 for d in [TOWER,PODIUM]:
  r=read(d/'result.json')
  with connect() as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  for e in r['evidenceRefs']:assert digest((ROOT/e['path']).read_bytes())==e['sha256'];refs.append(ROOT/e['path'])
  refs.append(d/'result.json')
 tower=read(TOWER/'selection.json.gz')['rows'][0];podium=read(PODIUM/'selection.json.gz')['rows'][0];assert tower['uid']=='landsd/254629:0' and podium['uid']=='landsd/233002:0'
 for row in [tower,podium]:assert digest((ROOT/row['candidate']['path']).read_bytes())==row['sourceSHA256'];refs.append(ROOT/row['candidate']['path'])
 save(DOC/'support-inputs.json',dict(pairs=[dict(uid=tower['uid'],supportUid=podium['uid'])],sources=[tower,podium]))
 tool=HERE/'original-support-closure-interfaces.mjs';subprocess.run(['node',str(tool),str(DOC.relative_to(ROOT))+'/'],cwd=ROOT,check=True)
 checks=read(DOC/'support-checks.json.gz');interface=checks['rows'][0]['interface']
 for p,h in checks['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 rtpath=HERE/'local'/TOWER.name/'runtime-geometry.json.gz';g=read(rtpath)['rows'][0];tri=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];ground=np.asarray(g['drawnGroundGeometry']).reshape(-1,3,3);support=decode_original_world_triangles((ROOT/podium['candidate']['path']).read_bytes())
 assert len(tri)==11517 and len(support)==1557
 final=module('orchards_podium_foundation',HERE/'xl-final-script-pass.py');b=tower['source']['building'];f=final.foundation_context(tri,np.concatenate([ground,support]),Polygon(b['rings'][0],b['rings'][1:]));strict=f['completeTerrainTriangles']==f['triangles'] and not f['fullyBuriedUpwardTriangles'] and f['fullyBuriedAreaFraction']==0
 save(DOC/'compound-foundation.json',dict(uid=tower['uid'],supportUid=podium['uid'],strictFoundationAccepted=strict,foundation=f,installationApproved=False))
 summary={k:interface.get(k)for k in ['passed','samples','strictContacts','wallIntersections']};summary.update(unresolved=len(interface['unresolved']),compoundFoundationPassed=strict,buriedTriangles=f['fullyBuriedTriangles'])
 refs.extend([rtpath,HERE/'xl-final-script-pass.py',HERE/'exact_packed_world_geometry_20261009.py',tool])
 result=module('orchards_support_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'orchards-original-podium-strict-support-and-compound-foundation-v1',list(set(refs)),dict(uids=[tower['uid'],podium['uid']],summary=summary,fullAcceptance=False,nextStep='Use exact unresolved samples to distinguish original podium support from terrain-only facade diagnostics; no installation until complete physical checks pass.'))
 print(dict(jobId=result['jobId'],summary=summary),flush=True)
if __name__=='__main__':main()
