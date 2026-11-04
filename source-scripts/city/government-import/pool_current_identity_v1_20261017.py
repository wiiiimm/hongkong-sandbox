"""Fresh exact original identity diagnostics for all four Primrose sources."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';SOURCE=BASE/'government-xl-sham-shui-po-pool-original-group-v1-20261016'
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_georef_cell_identity_20261009 import verify_files
BATCH='government-xl-sham-shui-po-pool-current-identity-v1-20261017';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH

def main():
 assert not DOC.exists()and not LOCAL.exists();receipt=read(SOURCE/'result.json')
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for q in receipt['evidenceRefs']:assert digest((ROOT/q['path']).read_bytes())==q['sha256']
 sources=read(SOURCE/'selection.json.gz')['rows'];f=module('identity_current',HERE/'xl-final-script-pass.py');paths=[ROOT/q['path']for q in receipt['evidenceRefs']]+[SOURCE/'result.json',Path(__file__),HERE/'primrose_compound_foundation_v2_20261015.py'];results=[]
 DOC.mkdir();LOCAL.mkdir()
 for row in sources:
  asset=ROOT/row['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==row['sourceSHA256'];tri=decode_original_world_triangles(raw);lo=tri.min(axis=(0,1));hi=tri.max(axis=(0,1));forms=f.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2]);context=dict(uid=row['uid'],sourceSHA256=row['sourceSHA256'],identity=f.identity_context(row,tri,forms),neighbourTileHashes={url:digest((ROOT/'3d-viewer'/url).read_bytes())for _,_,url in forms})
  proof=verify_files(row,context,LOCAL/row['uid'].replace('/','-').replace(':','-'));save(DOC/(row['uid'].replace('/','-').replace(':','-')+'.json'),dict(context=context,proof=proof));results.append(dict(uid=row['uid'],passed=proof['passed'],reasons=proof['reasons']));paths.extend(ROOT/'3d-viewer'/url for _,_,url in forms);print(results[-1],flush=True)
 for q in receipt['evidenceRefs']:assert digest((ROOT/q['path']).read_bytes())==q['sha256']
 paths += [p for p in LOCAL.rglob('*')if p.is_file()]+[HERE/n for n in ['xl-final-script-pass.py','routed_original_cell_identity.py','exact_original_georef_cell_identity_20261009.py','exact_packed_world_geometry_20261009.py']]
 module('identity_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'two-original-current-exact-identity-v1',paths,dict(uids=[r['uid']for r in sources],rows=results,fullAcceptance=False))
if __name__=='__main__':main()
