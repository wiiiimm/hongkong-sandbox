"""Exact recovered original podium identity, without publication."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_georef_cell_identity_20261009 import verify_files
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-tko-podium-identity-v2-20261021';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
PRIOR=BASE/'government-xl-tko-podium-current-terrain-v2-20261021'
def main():
 assert not DOC.exists();r=read(PRIOR/'result.json');refs=[Path(__file__),PRIOR/'result.json'];pins={}
 with connect() as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for e in r['evidenceRefs']:
  assert e['path'] not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 row=read(PRIOR/'selection.json.gz')['rows'][0];assert row['uid']=='landsd/265489:0'
 row['source']['tileSHA256']=pins['3d-viewer/'+row['source']['tile']]
 path=ROOT/row['candidate']['path'];assert digest(path.read_bytes())==row['sourceSHA256']
 tri=decode_original_world_triangles(path.read_bytes());assert len(tri)==row['triangles']
 final=module('tko_identity_context',HERE/'xl-final-script-pass.py');lo,hi=tri.min((0,1)),tri.max((0,1));near=final.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2]);tiles={tile:digest((ROOT/'3d-viewer'/tile).read_bytes()) for _,_,tile in near}
 context=dict(sourceSHA256=row['sourceSHA256'],identity=final.identity_context(row,tri,near),neighbourTileHashes=tiles);save(DOC/'context.json',context)
 proof=verify_files(row,context,LOCAL);save(DOC/'identity.json',proof)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 refs.extend(ROOT/p for p in pins);refs.extend(ROOT/'3d-viewer'/t for t in tiles);refs.extend(p for p in LOCAL.rglob('*') if p.is_file());refs.extend([HERE/'exact_original_georef_cell_identity_20261009.py',HERE/'xl-final-script-pass.py'])
 summary=dict(uids=[row['uid']],passed=proof['passed'],reasons=proof['reasons'],installationApproved=False,newlyInstalled=0)
 result=module('tko_identity_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-podium-identity',list(dict.fromkeys(refs)),summary);print(dict(jobId=result['jobId'],summary=summary),flush=True)
if __name__=='__main__':main()
