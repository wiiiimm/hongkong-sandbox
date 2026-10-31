"""Check unchanged YOHO podium against authenticated original government TIN."""
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-yoho300857-original-terrain-v2-20261020';DOC=BASE/BATCH;SRC=BASE/'government-xl-yoho300857-podium-identity-v1-20261020';CAP=BASE/'government-xl-next-twenty-current-terrain-v2-20261020'
assert not DOC.exists();r=read(SRC/'result.json');pins={x['path']:x['sha256']for x in r['evidenceRefs']}
with connect()as c:
 c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
sel=CAP/'selection.json.gz';assert digest(sel.read_bytes())==pins[str(sel.relative_to(ROOT))];row=next(x for x in read(sel)['rows']if x['uid']=='landsd/301636:0');asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256'];t=decode_original_world_triangles(asset.read_bytes())
candidate=BASE/'government-xl-yoho300857-pair-terrain-candidate-v1-20261020'
cr=read(candidate/'result.json');cpins={x['path']:x['sha256']for x in cr['evidenceRefs']}
with connect()as c:
 c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(cr['jobId'],)).fetchone()==('complete',cr)
tp=candidate/'terrain.json';assert digest(tp.read_bytes())==cpins[str(tp.relative_to(ROOT))];files=read(tp)['sourceFiles'];refs=[Path(__file__),SRC/'result.json',candidate/'result.json',tp,sel,asset,HERE/'exact_packed_world_geometry_20261009.py',HERE/'xl-second-pass.py',HERE/'xl-final-script-pass.py']
for e in files:
 p=ROOT/e['path'];assert digest(p.read_bytes())==e['sha256']==cpins[e['path']];refs.append(p)
second=module('yoho_original_decode',HERE/'xl-second-pass.py');second.LOCAL=HERE/'local'/BATCH
terrain=np.concatenate([second.terrain_triangles(ROOT/e['path'])for e in files if e['path'].endswith('.gltf')]);final=module('yoho_original_foundation',HERE/'xl-final-script-pass.py');b=row['source']['building'];foundation=final.foundation_context(t,terrain,Polygon(b['rings'][0],b['rings'][1:]));save(DOC/'foundation.json',foundation)
refs.extend(p for p in (HERE/'local'/BATCH).rglob('*')if p.is_file())
module('yoho_original_terrain_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-government-terrain-foundation',refs,dict(uids=[row['uid']],sourceSHA256=row['sourceSHA256'],terrainFaces=len(terrain),foundation=foundation,installationApproved=False));print(foundation,flush=True)
