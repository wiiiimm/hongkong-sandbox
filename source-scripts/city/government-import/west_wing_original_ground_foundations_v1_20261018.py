"""Complete original-source burial/coverage checks on immutable government ground.

This is source context, not current runtime terrain or installation acceptance.
"""
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-west-wing-original-ground-foundations-v1-20261018';DOC=BASE/BATCH
ASSEMBLY=BASE/'government-xl-west-wing26195-original-assembly-projection-v2-20261015';SHEET=BASE/'government-xl-west-wing26195-missing-sheet-candidates-v2-20261017';CONTACT=BASE/'government-xl-west-wing-cgo-original-ground-contacts-v1-20261018'
def check(args):
 worker=module('west_original_foundation',HERE/'olympian_two_four_world_foundations_v1_20261018.py');worker.DOC=DOC;return worker.check(args)
def main():
 assert not DOC.exists();receipt=read(CONTACT/'result.json')
 with connect() as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for r in receipt['evidenceRefs']:assert digest((ROOT/r['path']).read_bytes())==r['sha256'],r['path']
 t=read(SHEET/'sheet-result.json.gz')['result']['terrain'][0];refs=[Path(__file__),CONTACT/'result.json',CONTACT/'contacts.json',ASSEMBLY/'projection.json',SHEET/'sheet-result.json.gz',HERE/'xl-second-pass.py',HERE/'exact_packed_world_geometry_20261009.py',HERE/'olympian_two_four_world_foundations_v1_20261018.py',HERE/'xl-final-script-pass.py'];paths={}
 for f in t['preparedFiles']:
  if f['path']=='manifest.json':continue
  p=HERE.parent/'central-completion/staged/11-SW-9C'/f['path'];assert digest(p.read_bytes())==f['sha256'];refs.append(p);paths[p.suffix]=p
 helper=module('west_foundation_ground_decode',HERE/'xl-second-pass.py');ground=np.asarray(helper.context.triangles(paths['.gltf']),dtype='<f8');assert digest(ground.tobytes())==read(CONTACT/'contacts.json')['originalTerrainWorldSHA256']
 tile=ROOT/'3d-viewer/city/data/tiles/0_0.json';forms={f['uid']:f for f in read(tile)['buildings']};refs.append(tile);assembly=read(ASSEMBLY/'projection.json');work=[]
 for row in assembly['rows']:
  q=next(q for q in assembly['inputRefs'] if q['sha256']==row['sourceSHA256']);p=ROOT/q['path'];assert digest(p.read_bytes())==q['sha256'];refs.append(p);tri=np.asarray(decode_original_world_triangles(p.read_bytes()),dtype='<f8');assert len(tri)==row['completeFaces'];work.append((row['uid'],'original',tri,ground,forms[row['uid']]))
 assert len(work)==4;DOC.mkdir()
 with ProcessPoolExecutor(max_workers=2) as pool:results=list(pool.map(check,work))
 summary=dict(rows=results,originalGroundOnly=True,completeSources=4,sourceGeometryChanges=0,physicalAccepted=False,identityAccepted=False,publication=False,qualification='Complete source-face coverage and burial test against original terrain only. These checks do not establish rim support, renderer coordinate parity, current installed terrain equivalence, or acceptance.')
 save(DOC/'summary.json',summary)
 out=module('west_original_foundation_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'west-wing-four-original-ground-foundations-v1',refs,dict(uids=[r['uid'] for r in assembly['rows']],**summary));print(out['jobId'],flush=True)
if __name__=='__main__':main()
