"""Exact current original podium identity; no geometry changes or publication."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_georef_cell_identity_20261009 import verify_files
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-yoho300857-podium-identity-v1-20261020';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;CAP=BASE/'government-xl-next-twenty-current-terrain-v2-20261020'
def main():
 assert not DOC.exists();r=read(CAP/'result.json');pins={e['path']:e['sha256'] for e in r['evidenceRefs']}
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 sel=CAP/'selection.json.gz';assert digest(sel.read_bytes())==pins[str(sel.relative_to(ROOT))];row=next(x for x in read(sel)['rows'] if x['uid']=='landsd/301636:0')
 asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256'];t=decode_original_world_triangles(asset.read_bytes());assert len(t)==19952
 mp=ROOT/'3d-viewer/city/data/manifest.json';mh=digest(mp.read_bytes());final=module('yoho300857_podium_identity_context',HERE/'xl-final-script-pass.py');lo,hi=t.min((0,1)),t.max((0,1));forms=final.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2]);b,_,tile=next(f for f in forms if f[0]['uid']==row['uid']);assert b==row['source']['building']
 tiles={tile:digest((ROOT/'3d-viewer'/tile).read_bytes()) for _,_,tile in forms};context=dict(sourceSHA256=row['sourceSHA256'],identity=final.identity_context(row,t,forms),neighbourTileHashes=tiles);save(DOC/'context.json',context)
 proof=verify_files(row,context,LOCAL);save(DOC/'identity.json',proof)
 assert digest(mp.read_bytes())==mh
 refs=[Path(__file__),CAP/'result.json',sel,asset,mp,HERE/'xl-final-script-pass.py',HERE/'exact_original_georef_cell_identity_20261009.py',HERE/'exact_packed_world_geometry_20261009.py']+[ROOT/'3d-viewer'/p for p in tiles]+[p for p in LOCAL.rglob('*') if p.is_file()]
 result=module('yoho300857_podium_identity_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-podium-current-exact-source-identity',refs,dict(uids=[row['uid']],passed=proof['passed'],reasons=proof['reasons'],installationApproved=False));print(dict(jobId=result['jobId'],passed=proof['passed'],reasons=proof['reasons']),flush=True)
if __name__=='__main__':main()
