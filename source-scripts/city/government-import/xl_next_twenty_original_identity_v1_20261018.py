"""Reuse completed original stages for twenty unfinished XL sources; identity diagnostics only."""
from pathlib import Path
import subprocess
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_georef_cell_identity_20261009 import verify_files
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-next-twenty-original-identity-v1-20261018';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
UIDS=['landsd/64856:0', 'landsd/232240:0', 'landsd/75643:0', 'landsd/162768:0', 'landsd/72354:0', 'landsd/289067:0', 'landsd/245792:0', 'landsd/275446:0', 'landsd/309823:0', 'landsd/167911:0', 'landsd/233227:0', 'landsd/99482:0', 'landsd/43101:0', 'landsd/337553:0', 'landsd/337552:0', 'landsd/273672:0', 'landsd/14395:0', 'landsd/228219:0', 'landsd/283036:0', 'landsd/204155:0'];COUNT=BASE/'government-xl-west-wing-original-installed-v1-20261018/full-xl-current-count.json'
def main():
 assert not DOC.exists();count=read(COUNT);manifestpath=ROOT/'3d-viewer/city/data/manifest.json';manifestsha=digest(manifestpath.read_bytes());assert count['manifestSHA256']==manifestsha
 frozen={r['uid']:r for r in count['rows']if r.get('uid')in UIDS};assert set(frozen)==set(UIDS)and all(not r['installedVerified']for r in frozen.values());refs=[Path(__file__),COUNT,manifestpath];stages={};rows=[]
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for uid in UIDS:
   key,mid=frozen[uid]['sourceKey'].split('/');sha,result=c.execute('SELECT result_sha,result FROM astra_modelling.native_stage_results WHERE cache_key=%s',(key,)).fetchone();m=next(m for m in result['models']if m['modelId']==mid);assert m['asset']['sha256']==frozen[uid]['indexedSourceSHA256'];stages[key]=sha;rows.append(dict(uid=uid,modelId=mid,triangles=m['triangles'],sourceSHA256=m['asset']['sha256'],native=dict(cacheKey=key,resultSha=sha,model=m)))
 manifest=read(manifestpath);forms={}
 for tile in manifest['tiles']:
  path=ROOT/'3d-viewer'/tile['url'];data=read(path)
  for b in data['buildings']:
   if b['uid']in UIDS:
    assert b['uid']not in forms;forms[b['uid']]=dict(building=b,tile=tile['url'],tileSHA256=digest(path.read_bytes()));refs.append(path)
 assert set(forms)==set(UIDS)
 wanted={r['sourceSHA256']for r in rows};paths=subprocess.check_output(['rg','--files','--hidden','--no-ignore','-g','*.glb.gz','source-scripts/city','3d-viewer/city/data'],cwd=ROOT,text=True).splitlines();cache={}
 for name in paths:
  p=ROOT/name;sha=p.name.removesuffix('.glb.gz')
  if sha in wanted and sha not in cache and digest(p.read_bytes())==sha:cache[sha]=p
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
 r=module('next_five_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'twenty-existing-original-source-identity-diagnostics',list(dict.fromkeys(refs)),dict(uids=UIDS,rows=summary,installationApproved=False,newlyInstalled=0));print(r['jobId'],flush=True)
if __name__=='__main__':main()
