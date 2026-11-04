"""Fresh complete existing identity predicates on four unchanged originals; no overrides."""
from pathlib import Path
from copy import deepcopy
from run import ROOT,HERE,read,save,digest,connect
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_georef_cell_identity_20261009 import verify_files
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-parkview-four-raw-identity-v1-20261021';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
assert not DOC.exists()and not LOCAL.exists();refs=[Path(__file__)]
def take(n,f):
 _,ps=authenticate(BASE/n);p=BASE/n/f;assert digest(p.read_bytes())==ps[str(p.relative_to(ROOT))];refs.extend([BASE/n/'result.json',p]);return read(p)
selection=take('government-xl-parkview-12-15-shared-runtime-v2-20261021','selection.json.gz');native=take('government-xl-parkview-12-15-original-recovery-v1-20261021','native-sources.json');manifest=ROOT/'3d-viewer/city/data/manifest.json';assert digest(manifest.read_bytes())==selection['manifestSHA256'];refs.append(manifest)
with connect()as c:
 c.execute('SET TRANSACTION READ ONLY');sha,cache=c.execute('SELECT result_sha,result FROM astra_modelling.native_stage_results WHERE cache_key=%s',(native['cacheKey'],)).fetchone();assert sha==native['resultSHA256']
models={m['candidate']['uid']:m for m in cache['models']if m.get('candidate')};final=module('parkview_four_raw_identity_forms',HERE/'xl-final-script-pass.py');rows=[];proofs=[]
for row in selection['rows']:
 uid=row['uid']
 if uid=='landsd/254491:0':continue
 row=deepcopy(row);m=models[uid];assert m['asset']['sha256']==row['sourceSHA256']and m['modelId']==row['modelId'];row['native']=dict(cacheKey=native['cacheKey'],resultSha=sha,model=m);rows.append(row)
 p=ROOT/row['candidate']['path'];assert digest(p.read_bytes())==row['sourceSHA256'];refs.append(p);tri=decode_original_world_triangles(p.read_bytes());lo,hi=tri.min((0,1)),tri.max((0,1));near=final.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2]);assert next(b for b,_,_ in near if b['uid']==uid)==row['source']['building'];tiles={url:digest((ROOT/'3d-viewer'/url).read_bytes())for _,_,url in near};context=dict(uid=uid,sourceSHA256=row['sourceSHA256'],identity=final.identity_context(row,tri,near),neighbourTileHashes=tiles)
 proof=verify_files(row,context,LOCAL/uid.split('/')[1]);save(DOC/(uid.split('/')[1]+'-identity.json'),proof);save(DOC/(uid.split('/')[1]+'-context.json'),context);proofs.append(dict(uid=uid,sourceSHA256=row['sourceSHA256'],passed=proof['passed'],reasons=proof['reasons']));refs.extend(ROOT/'3d-viewer'/u for u in tiles)
 for url,h in tiles.items():assert digest((ROOT/'3d-viewer'/url).read_bytes())==h
save(DOC/'selection.json.gz',dict(rows=rows,manifestSHA256=selection['manifestSHA256']));summary=dict(uids=[r['uid']for r in rows],rows=proofs,installationApproved=False);save(DOC/'summary.json',summary);assert digest(manifest.read_bytes())==selection['manifestSHA256'];refs.extend(p for p in LOCAL.rglob('*')if p.is_file());refs.extend(HERE/n for n in ['xl-final-script-pass.py','exact_original_georef_cell_identity_20261009.py','exact_packed_world_geometry_20261009.py','routed_original_cell_identity.py']);module('parkview_four_raw_identity_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'fresh-unchanged-four-source-identity-predicates',list(dict.fromkeys(refs)),summary);print(summary,flush=True)
