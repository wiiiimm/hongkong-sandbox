"""Reuse completed original stages for twenty unfinished XL sources; identity diagnostics only."""
from pathlib import Path
import subprocess
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_georef_cell_identity_20261009 import verify_files
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-yoho-mall-i-tower-identity-v1-20261020';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
UIDS=['landsd/294811:0','landsd/294810:0','landsd/294854:0','landsd/294855:0','landsd/294857:0','landsd/294856:0','landsd/294858:0']
def safe_verify(row,context,local):
 try:return verify_files(row,context,local)
 except StopIteration:
  # Existing verifier cannot nominate this target from mesh bounds. Preserve as
  # a failed diagnostic, never turn missing geometry/context into approval.
  return dict(passed=False,reasons=['exact-identity-target-outside-source-query'],uid=row['uid'],sourceSHA256=row['sourceSHA256'],installationApproved=False)
def main():
 assert not DOC.exists();manifestpath=ROOT/'3d-viewer/city/data/manifest.json';manifestsha=digest(manifestpath.read_bytes());refs=[Path(__file__),manifestpath];stages={};rows=[]
 recovery=BASE/'government-xl-yoho-mall-i-tower-recovery-v1-20261020';receipt=read(recovery/'result.json');rp=recovery/'recovery.json'
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
  assert digest(rp.read_bytes())==next(e['sha256']for e in receipt['evidenceRefs']if e['path']==str(rp.relative_to(ROOT)));refs.extend([recovery/'result.json',rp]);nominees=read(rp)['rows'];assert len(nominees)==7 and {r['uid']for r in nominees}==set(UIDS)
  for n in nominees:
   key=n['native']['cacheKey'];sha,result=c.execute('SELECT result_sha,result FROM astra_modelling.native_stage_results WHERE cache_key=%s',(key,)).fetchone();assert sha==n['native']['resultSha'];m=next(x for x in result['models']if x['modelId']==n['modelId']);assert m==n['native']['model'];stages[key]=sha;rows.append(dict(uid=n['uid'],modelId=m['modelId'],triangles=m['triangles'],sourceSHA256=m['asset']['sha256'],native=dict(cacheKey=key,resultSha=sha,model=m)))
 manifest=read(manifestpath);forms={}
 for tile in manifest['tiles']:
  path=ROOT/'3d-viewer'/tile['url'];data=read(path)
  for b in data['buildings']:
   if b['uid']in UIDS:
    assert b['uid']not in forms;forms[b['uid']]=dict(building=b,tile=tile['url'],tileSHA256=digest(path.read_bytes()));refs.append(path)
 assert set(forms)==set(UIDS)
 cache={r['sourceSHA256']:ROOT/r['assetPath']for r in nominees}
 for sha,path in cache.items():assert digest(path.read_bytes())==sha
 final=module('yoho_tower_identity_context',HERE/'xl-final-script-pass.py');summary=[]
 for row in rows:
  uid=row['uid'];row['source']=forms[uid];sha=row['sourceSHA256'];key=uid.split('/')[1]
  if sha not in cache:summary.append(dict(uid=uid,status='source-cache-missing',sourceSHA256=sha));print(summary[-1],flush=True);continue
  path=cache[sha];row['candidate']=dict(path=str(path.relative_to(ROOT)));refs.append(path);tri=decode_original_world_triangles(path.read_bytes());assert len(tri)==row['triangles'];lo,hi=tri.min((0,1)),tri.max((0,1));own_points=[point for ring in row['source']['building']['rings'] for point in ring];near=final.load_forms([min(lo[0],min(x[0] for x in own_points))-2,min(lo[2],min(x[1] for x in own_points))-2,max(hi[0],max(x[0] for x in own_points))+2,max(hi[2],max(x[1] for x in own_points))+2]);tiles={tile:digest((ROOT/'3d-viewer'/tile).read_bytes())for _,_,tile in near};context=dict(sourceSHA256=sha,identity=final.identity_context(row,tri,near),neighbourTileHashes=tiles);save(DOC/key/'context.json',context);proof=safe_verify(row,context,LOCAL/key);save(DOC/key/'identity.json',proof);refs.extend(ROOT/'3d-viewer'/t for t in tiles);summary.append(dict(uid=uid,name=row['source']['building'].get('name'),status='identity-passed'if proof['passed']else'identity-review-required',reasons=proof['reasons'],triangles=len(tri)));print(summary[-1],flush=True)
 assert digest(manifestpath.read_bytes())==manifestsha
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for key,sha in stages.items():assert c.execute('SELECT result_sha FROM astra_modelling.native_stage_results WHERE cache_key=%s',(key,)).fetchone()==(sha,)
 save(DOC/'selection.json.gz',dict(rows=rows,manifestSHA256=manifestsha,nativeResultSHA256ByKey=stages));save(DOC/'summary.json',dict(rows=summary,installationApproved=False,geometryChanges=0));refs.extend(p for p in LOCAL.rglob('*')if p.is_file());refs.extend([HERE/'exact_original_georef_cell_identity_20261009.py',HERE/'xl-final-script-pass.py'])
 r=module('next_five_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'twenty-existing-original-source-identity-diagnostics',list(dict.fromkeys(refs)),dict(uids=UIDS,rows=summary,installationApproved=False,newlyInstalled=0));print(r['jobId'],flush=True)
if __name__=='__main__':main()
