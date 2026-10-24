"""Check unchanged YOHO podium against authenticated original government TIN."""
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-yoho300857-original-terrain-v1-20261020';DOC=BASE/BATCH;SRC=BASE/'government-xl-yoho300857-podium-identity-v1-20261020';CAP=BASE/'government-xl-next-twenty-current-terrain-v2-20261020'
assert not DOC.exists();r=read(SRC/'result.json');pins={x['path']:x['sha256']for x in r['evidenceRefs']}
with connect()as c:
 c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
sel=CAP/'selection.json.gz';assert digest(sel.read_bytes())==pins[str(sel.relative_to(ROOT))];row=next(x for x in read(sel)['rows']if x['uid']=='landsd/301636:0');asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256'];t=decode_original_world_triangles(asset.read_bytes())
folder=HERE/'local/government-xl-yoho-fu-tor-loy-adjoining-ground-v1-20261018/sheets/6-NW-10D';proof=read(folder/'original/download.json');directory=read(folder/'directory/result.json');assert proof['directorySHA256']==directory['directorySHA256'];assert proof['terrainGeometryIncluded'] and proof['sheet']==directory['sheet']==folder.name
refs=[Path(__file__),SRC/'result.json',sel,asset,folder/'original/download.json',folder/'directory/result.json',HERE/'exact_packed_world_geometry_20261009.py',HERE/'xl-second-pass.py',HERE/'xl-final-script-pass.py']
files=[e for e in proof['entries']if e['name'].startswith('TERRAIN') and e['name'].endswith(('.gltf','.bin'))];assert any(e['name'].endswith('.gltf')for e in files)
for e in files:
 p=folder/'terrain'/e['name'];assert digest(p.read_bytes())==e['sha256'];refs.append(p)
second=module('yoho_original_decode',HERE/'xl-second-pass.py');second.LOCAL=HERE/'local'/BATCH
terrain=np.concatenate([second.terrain_triangles(folder/'terrain'/e['name'])for e in files if e['name'].endswith('.gltf')]);final=module('yoho_original_foundation',HERE/'xl-final-script-pass.py');b=row['source']['building'];foundation=final.foundation_context(t,terrain,Polygon(b['rings'][0],b['rings'][1:]));save(DOC/'foundation.json',foundation)
refs.extend(p for p in (HERE/'local'/BATCH).rglob('*')if p.is_file())
module('yoho_original_terrain_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-government-terrain-foundation',refs,dict(uids=[row['uid']],sourceSHA256=row['sourceSHA256'],terrainFaces=len(terrain),foundation=foundation,installationApproved=False));print(foundation,flush=True)
