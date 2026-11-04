"""Compare complete original station to authenticated source TIN; no terrain publish."""
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';PRIOR=BASE/'government-xl-long-ping-current-physical-v1-20261017'
BATCH='government-xl-long-ping-source-terrain-v1-20261017';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
UID='landsd/107382:0';SHEET='6-NW-9B'
def main():
 assert not DOC.exists();r=read(PRIOR/'result.json')
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 pins={q['path']:q['sha256']for q in r['evidenceRefs']};rtpath=HERE/'local'/PRIOR.name/'runtime-geometry.json.gz';assert digest(rtpath.read_bytes())==pins[str(rtpath.relative_to(ROOT))]
 verifier=module('long_ping_terrain_cache',HERE/'xl-cell-indexed-terrain-continuation.py');decoder=module('long_ping_terrain_decoder',HERE/'xl-second-pass.py');decoder.LOCAL=LOCAL
 current=HERE/'local/government-xl-held-current-directory-audit-20261007/sheets'/SHEET/'directory/result.json';directory=read(current);found=None
 for folder in sorted((HERE/'local').glob('*/sheets/'+SHEET)):
  proof=verifier.verified_terrain(folder)
  if proof and proof[0]['directorySHA256']==directory['directorySHA256']:found=(folder,proof);break
 assert found,'Authenticated matching source terrain not available'
 folder,(receipt,files)=found;refs=[Path(__file__),PRIOR/'result.json',PRIOR/'selection.json.gz',rtpath,current,folder/'original/download.json',folder/'directory/result.json'];pieces=[]
 for f in files:
  p=folder/'terrain'/f['name'];assert digest(p.read_bytes())==f['sha256'];refs.append(p)
  if p.suffix=='.gltf':pieces.append(decoder.terrain_triangles(p))
 terrain=np.concatenate(pieces);g=next(x for x in read(rtpath)['rows']if x['uid']==UID);tri=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];row=next(x for x in read(PRIOR/'selection.json.gz')['rows']if x['uid']==UID);b=row['source']['building'];final=module('long_ping_tin_foundation',HERE/'xl-final-script-pass.py')
 foundation=final.foundation_context(tri,terrain,Polygon(b['rings'][0],b['rings'][1:]));summary=dict(uid=UID,sourceSHA256=g['sourceSHA256'],sheet=SHEET,directorySHA256=directory['directorySHA256'],wholeSourceTerrainFaces=len(terrain),strictSourceTerrainFoundationAccepted=foundation['completeTerrainTriangles']==foundation['triangles']and foundation['fullyBuriedUpwardTriangles']==0 and foundation['fullyBuriedAreaFraction']==0,foundation=foundation,fullAcceptance=False,qualification='Original terrain comparison only, not a replacement proposal. No current-neighbour or rendered-terrain acceptance. Matching retained October 7 directory provenance, not a live provider revision check.')
 save(DOC/'source-terrain-foundation.json',summary);refs.extend([HERE/'xl-cell-indexed-terrain-continuation.py',HERE/'xl-second-pass.py',HERE/'xl-final-script-pass.py']);refs.extend(p for p in LOCAL.rglob('*')if p.is_file())
 out=module('long_ping_tin_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'long-ping-authenticated-original-terrain-foundation-v1',refs,dict(uids=[UID],summary=summary,nextStep='If source terrain clears station foundation, prepare a bounded authentic terrain proposal and test the complete affected current neighbour extent; otherwise investigate exact source-TIN failures.'))
 print(dict(jobId=out['jobId'],strictSourceTerrainFoundationAccepted=summary['strictSourceTerrainFoundationAccepted'],buried=foundation['fullyBuriedTriangles'],upward=foundation['fullyBuriedUpwardTriangles'],minimumGapM=foundation['minimumGapM']),flush=True)
if __name__=='__main__':main()
