"""Reuse completed original stages for twenty unfinished XL sources; identity diagnostics only."""
from pathlib import Path
import subprocess
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_georef_cell_identity_20261009 import verify_files
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-folkland-pair-current-identity-v1-20261020';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
UIDS=['landsd/225387:0','landsd/264677:0']
def main():
 assert not DOC.exists();manifestpath=ROOT/'3d-viewer/city/data/manifest.json';manifestsha=digest(manifestpath.read_bytes());refs=[Path(__file__),manifestpath];stages={};rows=[]
 nomination=BASE/'government-xl-china-ferry-neighbour-sources-v1-20261020';pair=BASE/'government-xl-folkland-pair-candidate-foundations-v1-20261020'
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for d,f in [(pair,'selection.json.gz')]:
   receipt=read(d/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt);pins={e['path']:e['sha256']for e in receipt['evidenceRefs']};assert digest((d/f).read_bytes())==pins[str((d/f).relative_to(ROOT))];refs.extend([d/'result.json',d/f])
  nominees=read(pair/'selection.json.gz')['rows']
  assert len(nominees)==2 and {r['uid']for r in nominees}==set(UIDS)
  for n in nominees:
   key=n['native']['cacheKey'];sha,result=c.execute('SELECT result_sha,result FROM astra_modelling.native_stage_results WHERE cache_key=%s',(key,)).fetchone();assert sha==n['native']['resultSha'];m=next(x for x in result['models']if x['modelId']==n['native']['model']['modelId']);assert m==n['native']['model'];stages[key]=sha;rows.append(dict(uid=n['uid'],modelId=m['modelId'],triangles=m['triangles'],sourceSHA256=m['asset']['sha256'],native=dict(cacheKey=key,resultSha=sha,model=m)))
 manifest=read(manifestpath);forms={}
 for tile in manifest['tiles']:
  path=ROOT/'3d-viewer'/tile['url'];data=read(path)
  for b in data['buildings']:
   if b['uid']in UIDS:
    assert b['uid']not in forms;forms[b['uid']]=dict(building=b,tile=tile['url'],tileSHA256=digest(path.read_bytes()));refs.append(path)
 assert set(forms)==set(UIDS)
 cache={}
 for n in nominees:
  p=ROOT/n['candidate']['path'];assert digest(p.read_bytes())==n['sourceSHA256'];cache[n['sourceSHA256']]=p
 final=module('next_five_identity_context',HERE/'xl-final-script-pass.py');summary=[]
 for row in rows:
  uid=row['uid'];row['source']=forms[uid];sha=row['sourceSHA256'];key=uid.split('/')[1]
  if sha not in cache:summary.append(dict(uid=uid,status='source-cache-missing',sourceSHA256=sha));print(summary[-1],flush=True);continue
  path=cache[sha];row['candidate']=dict(path=str(path.relative_to(ROOT)));refs.append(path);tri=decode_original_world_triangles(path.read_bytes());assert len(tri)==row['triangles'];lo,hi=tri.min((0,1)),tri.max((0,1));near=final.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2]);tiles={tile:digest((ROOT/'3d-viewer'/tile).read_bytes())for _,_,tile in near};context=dict(sourceSHA256=sha,identity=final.identity_context(row,tri,near),neighbourTileHashes=tiles);save(DOC/key/'context.json',context);proof=verify_files(row,context,LOCAL/key);save(DOC/key/'identity.json',proof);refs.extend(ROOT/'3d-viewer'/t for t in tiles);summary.append(dict(uid=uid,name=row['source']['building'].get('name'),status='identity-passed'if proof['passed']else'identity-review-required',reasons=proof['reasons'],triangles=len(tri)));print(summary[-1],flush=True)
 assert digest(manifestpath.read_bytes())==manifestsha
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for key,sha in stages.items():assert c.execute('SELECT result_sha FROM astra_modelling.native_stage_results WHERE cache_key=%s',(key,)).fetchone()==(sha,)
 save(DOC/'selection.json.gz',dict(rows=rows,manifestSHA256=manifestsha,nativeResultSHA256ByKey=stages));save(DOC/'summary.json',dict(rows=summary,installationApproved=False,geometryChanges=0));refs.extend(p for p in LOCAL.rglob('*')if p.is_file());refs.extend([HERE/'exact_original_georef_cell_identity_20261009.py',HERE/'xl-final-script-pass.py'])
 r=module('next_five_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'folkland-pair-current-original-source-identity',list(dict.fromkeys(refs)),dict(uids=UIDS,rows=summary,installationApproved=False,newlyInstalled=0));print(r['jobId'],flush=True)
if __name__=='__main__':main()
