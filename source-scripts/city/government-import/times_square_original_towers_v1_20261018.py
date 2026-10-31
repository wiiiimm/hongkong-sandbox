"""Recover the two original tower counterparts; exact frozen hashes required."""
from pathlib import Path
import re,traceback
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BATCH='government-xl-times-square-original-towers-v1-20261018';BASE=ROOT/'docs/astra-city/government-import';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
TARGETS=[('landsd/254824:0','B368551548301063C0','f6dd237c3db9ea044e3c67ac9eea0c56f27b3b8a41181e6422c15a608ccdd85a'),('landsd/266146:0','B367451548401063C0','5374dda233237d91d7890c58bd70fbbd21790f5257ad1299dd59a74dccc49bc6')]
def main():
 assert not DOC.exists();tile=ROOT/'3d-viewer/city/data/tiles/1_0.json';forms={b['uid']:b for b in read(tile)['buildings']};rows=[];refs=[Path(__file__),tile,HERE/'xl-second-pass.py'];helper=module('times_tower_recover',HERE/'xl-second-pass.py');helper.LOCAL=LOCAL;final=module('times_tower_identity_context',HERE/'xl-final-script-pass.py')
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for uid,mid,key in TARGETS:
   sha,result=c.execute('SELECT result_sha,result FROM astra_modelling.native_stage_results WHERE cache_key=%s',(key,)).fetchone();sheet=c.execute('SELECT sheet FROM astra_modelling.native_stage_inputs WHERE cache_key=%s',(key,)).fetchone()[0];m=next(m for m in result['models']if m['modelId']==mid);assert m['candidate']['uid']==uid and m['candidate']['buildingCSUID']==forms[uid]['buildingCSUID'];rows.append(dict(uid=uid,modelId=mid,triangles=m['triangles'],sourceSHA256=m['asset']['sha256'],native=dict(cacheKey=key,resultSha=sha,sheet=sheet,model=m),source=dict(building=forms[uid],tile=str(tile.relative_to(ROOT/'3d-viewer')),tileSHA256=digest(tile.read_bytes()))))
 save(DOC/'frozen-sources.json.gz',dict(rows=rows));out=[]
 for row in rows:
  sheet=row['native']['sheet'];priorpath=HERE/'local/government-xl-next-five-adjoining-ground-v1-20261018/sheets'/sheet/'directory/result.json';prior=read(priorpath);refs.append(priorpath)
  try:
   helper.source_sheet(sheet,[row],prior,{},[])
   p=LOCAL/'assets'/(row['sourceSHA256']+'.glb.gz');assert digest(p.read_bytes())==row['sourceSHA256'];entry=dict(row['native']['model']['candidate'],sourceTile=sheet,rootTranslation=[-834500,0,816500]);row['candidate']=dict(path=str(p.relative_to(ROOT)),entry=entry);tri=decode_original_world_triangles(p.read_bytes());assert len(tri)==row['triangles'];lo,hi=tri.min((0,1)),tri.max((0,1));near=final.load_forms([lo[0]-2,lo[2]-2,hi[0]+2,hi[2]+2]);context=dict(sourceSHA256=row['sourceSHA256'],identity=final.identity_context(row,tri,near),neighbourTileHashes={t:digest((ROOT/'3d-viewer'/t).read_bytes())for _,_,t in near});save(DOC/(row['uid'].split('/')[1]+'-context.json'),context);refs.extend(ROOT/'3d-viewer'/t for t in context['neighbourTileHashes']);out.append(dict(uid=row['uid'],exactOriginalRecovered=True,triangles=len(tri)));print(out[-1],flush=True)
  except Exception as exc:
   out.append(dict(uid=row['uid'],exactOriginalRecovered=False,error=re.sub(r'https?://\S+','[source URL]',str(exc))));save(DOC/(row['uid'].split('/')[1]+'-failure.json'),dict(error=out[-1]['error'],traceback=re.sub(r'https?://\S+','[source URL]',traceback.format_exc())));print(out[-1],flush=True)
 save(DOC/'selection.json.gz',dict(rows=[r for r in rows if 'candidate'in r],manifestSHA256=digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes())));save(DOC/'summary.json',dict(rows=out,installationApproved=False));refs.extend(p for p in LOCAL.rglob('*')if p.is_file());refs.extend([ROOT/'3d-viewer/city/data/manifest.json',HERE/'xl-final-script-pass.py'])
 module('times_tower_recovery_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'times-square-exact-original-tower-counterparts',list(dict.fromkeys(refs)),dict(uids=[r['uid']for r in rows],rows=out,installationApproved=False))
if __name__=='__main__':main()
