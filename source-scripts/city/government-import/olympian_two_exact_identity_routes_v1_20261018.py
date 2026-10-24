"""Resume original identity routing; no publication or geometry changes."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_original_georef_cell_identity_20261009 import verify_files
BASE=ROOT/'docs/astra-city/government-import'
PRIOR=BASE/'government-xl-olympian-two-current-identity-runtime-v1-20261018'
BATCH='government-xl-olympian-two-exact-identity-routes-v1-20261018'
DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH

def main():
 assert not DOC.exists()
 r=read(PRIOR/'result.json');pins={};refs=[Path(__file__),PRIOR/'result.json']
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for e in r['evidenceRefs']:
  assert e['path'] not in pins or pins[e['path']]==e['sha256']
  pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 rows=read(PRIOR/'selection.json.gz')['rows'];results=[]
 for row in rows:
  uid=row['uid'];previous=read(PRIOR/(uid.split('/')[1]+'-identity.json'))
  proof=verify_files(row,previous['context'],LOCAL/uid.split('/')[1])
  save(DOC/(uid.split('/')[1]+'-identity.json'),proof)
  item=dict(uid=uid,passed=proof['passed'],reasons=proof['reasons'],previousReasons=previous['proof']['reasons'])
  results.append(item);print(item,flush=True)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 save(DOC/'summary.json',dict(rows=results,fullAcceptance=False,newlyInstalled=0,aiGeometryModelling=False))
 refs.extend(ROOT/p for p in pins)
 refs.extend(HERE/n for n in ['exact_original_georef_cell_identity_20261009.py','routed_original_cell_identity.py','component_type_resolution.py','exact_original_projection_coverage_20261009.py'])
 refs.extend(p for p in LOCAL.rglob('*') if p.is_file())
 out=module('olympian_route_checkpoint',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'olympian-original-exact-current-identity-route-v1',list(set(refs)),dict(uids=[x['uid'] for x in rows],identity=results,fullAcceptance=False,newlyInstalled=0))
 print(out['jobId'],flush=True)
if __name__=='__main__':main()
