"""Fresh whole-source identities for the three unchanged West Wing assembly originals."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_georef_cell_identity_20261009 import verify_files
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-west-wing-other-original-identities-v1-20261018';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;CAP=BASE/'government-xl-west-wing-group-four-world-v1-20261018'
def main():
 assert not DOC.exists();receipt=read(CAP/'result.json');pins={r['path']:r['sha256']for r in receipt['evidenceRefs']};refs=[Path(__file__),CAP/'result.json']
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
  resultsha,result=c.execute('SELECT result_sha,result FROM astra_modelling.native_stage_results WHERE cache_key=%s',('828133bbea286a52de1484a5163766bfab7ee42b0b4c07a8be3e756f0cabe7e6',)).fetchone()
 assert resultsha=='9ef4f709c01591edac1bb64be27c347726ea68c401c0fc1f2806dc297994a2b9'
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 rows=[r for r in read(CAP/'selection.json.gz')['rows']if r['uid']!='landsd/26195:0'];final=module('west_assembly_identity_context',HERE/'xl-final-script-pass.py');summary=[]
 for r in rows:
  native=next(m for m in result['models']if m['modelId']==r['candidate']['entry']['modelId']);assert native['asset']['sha256']==r['sourceSHA256'];r['native']['model']=native;r.update(modelId=native['modelId'],triangles=native['triangles']);r['source']['tileSHA256']=digest((ROOT/'3d-viewer'/r['source']['tile']).read_bytes());r['native'].update(cacheKey='828133bbea286a52de1484a5163766bfab7ee42b0b4c07a8be3e756f0cabe7e6',resultSha=resultsha,sheet='11-SW-9C')
  raw=(ROOT/r['candidate']['path']).read_bytes();assert digest(raw)==r['sourceSHA256'];t=decode_original_world_triangles(raw);lo,hi=t.min((0,1)),t.max((0,1));forms=final.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2]);assert [b for b,_,_ in forms if b['uid']==r['uid']]==[r['source']['building']];tiles={tile:digest((ROOT/'3d-viewer'/tile).read_bytes())for _,_,tile in forms};context=dict(sourceSHA256=r['sourceSHA256'],identity=final.identity_context(r,t,forms),neighbourTileHashes=tiles)
  folder=DOC/r['uid'].split('/')[1];save(folder/'context.json',context);proof=verify_files(r,context,LOCAL/r['uid'].split('/')[1]);save(folder/'identity.json',proof);summary.append(dict(uid=r['uid'],passed=proof['passed'],reasons=proof['reasons']));refs.extend(ROOT/'3d-viewer'/tile for tile in tiles);print(summary[-1],flush=True)
 save(DOC/'selection.json.gz',dict(rows=rows,nativeResultSHA256=resultsha));save(DOC/'summary.json',dict(rows=summary,installationApproved=False));refs.extend(ROOT/p for p in pins);refs.extend(p for p in LOCAL.rglob('*')if p.is_file());refs.extend([HERE/'exact_original_georef_cell_identity_20261009.py',HERE/'xl-final-script-pass.py'])
 out=module('west_other_identity_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'west-wing-three-originals-current-identity-v1',list(dict.fromkeys(refs)),dict(uids=[r['uid']for r in rows],summary=summary,publication=False,installationApproved=False));print(out['jobId'],flush=True)
if __name__=='__main__':main()
