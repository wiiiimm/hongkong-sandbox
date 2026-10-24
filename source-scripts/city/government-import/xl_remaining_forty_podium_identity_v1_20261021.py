"""Reuse completed original stages for forty unfinished XL sources; identity diagnostics only."""
from pathlib import Path
import subprocess
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_georef_cell_identity_20261009 import verify_files
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-remaining-forty-podium-identity-v1-20261021';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
NOM=BASE/'government-xl-remaining-forty-support-candidates-v1-20261021'
SOURCE=BASE/'government-xl-remaining-forty-podium-sources-v1-20261021'

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
 assert not DOC.exists()
 from china_ferry_current_foundations_v1_20261020 import authenticate
 sr,sp=authenticate(SOURCE);nr,npins=authenticate(NOM)
 sourcepath=SOURCE/'sources.json.gz';nompath=NOM/'nominations.json'
 for p,pins in [(sourcepath,sp),(nompath,npins)]:assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))]
 forms={c['uid']:c['source']for r in read(nompath)['rows']for c in r['candidates']}
 manifestpath=ROOT/'3d-viewer/city/data/manifest.json';manifestsha=digest(manifestpath.read_bytes());assert manifestsha==npins[str(manifestpath.relative_to(ROOT))]
 refs=[Path(__file__),sourcepath,nompath,SOURCE/'result.json',NOM/'result.json',manifestpath];stages={};rows=[]
 for r in read(sourcepath)['rows']:
  m=r['model'];matches=[(uid,f)for uid,f in forms.items()if any(c.get('objectId')==f['building']['objectId']and c.get('buildingCSUID')==f['building']['buildingCSUID']for c in m['matching']['officialCandidates'])]
  assert len(matches)==1,(m['modelId'],len(matches))
  uid,form=matches[0];path=ROOT/'3d-viewer'/form['tile'];form['tileSHA256']=digest(path.read_bytes());assert form['tileSHA256']==npins[str(path.relative_to(ROOT))];refs.append(path);stages[r['cacheKey']]=r['resultSha'];rows.append(dict(uid=uid,modelId=m['modelId'],triangles=m['triangles'],sourceSHA256=m['asset']['sha256'],native=dict(cacheKey=r['cacheKey'],resultSha=r['resultSha'],model=m)))
 assert len(rows)==8 and len({r['uid']for r in rows})==8
 UIDS=[r['uid']for r in rows]
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
 r=module('next_five_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'eight-original-podium-identity-diagnostics',list(dict.fromkeys(refs)),dict(uids=UIDS,rows=summary,installationApproved=False,newlyInstalled=0));print(r['jobId'],flush=True)
if __name__=='__main__':main()
