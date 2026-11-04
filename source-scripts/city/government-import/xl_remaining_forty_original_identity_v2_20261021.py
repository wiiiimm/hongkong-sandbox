"""Reuse completed original stages for forty unfinished XL sources; identity diagnostics only."""
from pathlib import Path
import subprocess
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_georef_cell_identity_20261009 import verify_files
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-remaining-forty-original-identity-v2-20261021';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
UIDS=['landsd/290803:0', 'landsd/177765:0', 'landsd/235568:0', 'landsd/229852:0', 'landsd/122702:0', 'landsd/61738:0', 'landsd/256702:0', 'landsd/256898:0', 'landsd/89917:0', 'landsd/60281:0', 'landsd/290981:0', 'landsd/176472:0', 'landsd/278234:0', 'landsd/268867:0', 'landsd/330243:0', 'landsd/56771:0', 'landsd/17633:0', 'landsd/314698:0', 'landsd/263644:0', 'landsd/276187:0', 'landsd/315414:0', 'landsd/238803:0', 'landsd/137130:0', 'landsd/285139:0', 'landsd/292155:0', 'landsd/258470:0', 'landsd/107382:0', 'landsd/81743:0', 'landsd/285509:0', 'landsd/240332:0', 'landsd/198440:0', 'landsd/255415:0', 'landsd/236354:0', 'landsd/226296:0', 'landsd/339808:0', 'landsd/295538:0', 'landsd/278458:0', 'landsd/255940:0', 'landsd/255531:0', 'landsd/59289:0'];COUNT=BASE/'government-xl-parkview-four-original-installed-v2-20261021'/'full-xl-current-count.json'
def checked_identity(row,context,local):
 try:
  return verify_files(row,context,local)
 except KeyError as error:
  # Unsupported evidence schema is unresolved, never approval or corruption.
  # Preserve the exact exception and any underlying routed proof in LOCAL.
  if error.args != ('precisionMetres',):
   raise
  return dict(uid=row['uid'],sourceSHA256=row['sourceSHA256'],passed=False,
              reasons=['identity-checker-missing-geographic-cell-precision'],
              checkerException=dict(type='KeyError',field='precisionMetres'),
              installationApproved=False,permanentRejection=False)

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
  path=cache[sha];row['candidate']=dict(path=str(path.relative_to(ROOT)));refs.append(path);tri=decode_original_world_triangles(path.read_bytes());assert len(tri)==row['triangles'];lo,hi=tri.min((0,1)),tri.max((0,1));near=final.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2]);tiles={tile:digest((ROOT/'3d-viewer'/tile).read_bytes())for _,_,tile in near};context=dict(sourceSHA256=sha,identity=final.identity_context(row,tri,near),neighbourTileHashes=tiles);save(DOC/key/'context.json',context);proof=checked_identity(row,context,LOCAL/key);save(DOC/key/'identity.json',proof);refs.extend(ROOT/'3d-viewer'/t for t in tiles);summary.append(dict(uid=uid,name=row['source']['building'].get('name'),status='identity-passed'if proof['passed']else'identity-review-required',reasons=proof['reasons'],triangles=len(tri)));print(summary[-1],flush=True)
 assert digest(manifestpath.read_bytes())==manifestsha
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for key,sha in stages.items():assert c.execute('SELECT result_sha FROM astra_modelling.native_stage_results WHERE cache_key=%s',(key,)).fetchone()==(sha,)
 save(DOC/'selection.json.gz',dict(rows=rows,manifestSHA256=manifestsha,nativeResultSHA256ByKey=stages));save(DOC/'summary.json',dict(rows=summary,installationApproved=False,geometryChanges=0));refs.extend(p for p in LOCAL.rglob('*')if p.is_file());refs.extend([HERE/'exact_original_georef_cell_identity_20261009.py',HERE/'xl-final-script-pass.py'])
 r=module('next_five_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'forty-existing-original-source-identity-diagnostics',list(dict.fromkeys(refs)),dict(uids=UIDS,rows=summary,installationApproved=False,newlyInstalled=0));print(r['jobId'],flush=True)
if __name__=='__main__':main()
