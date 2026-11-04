"""Recover seven exact original tower assets for mall assembly diagnostics only."""
from pathlib import Path
from collections import defaultdict
import json,sys,uuid,subprocess
from run import ROOT,HERE,read,save,digest,connect,reservations
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-yoho-mall-i-tower-recovery-v1-20261020';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;SRC=BASE/'government-xl-yoho-mall-i-tower-sources-v1-20261020'
def owned():
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease)and not DOC.exists();receipt=read(SRC/'result.json');pins={e['path']:e['sha256']for e in receipt['evidenceRefs']};p=SRC/'nominations.json';assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs=[Path(__file__),SRC/'result.json',p,HERE/'xl-second-pass.py'];rows=[]
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
  for n in read(p)['rows']:
   key=n['nativeStageKey'];sha,result=db.execute('SELECT result_sha,result FROM astra_modelling.native_stage_results WHERE cache_key=%s',(key,)).fetchone();assert sha==n['nativeStageSHA256'];m=next(x for x in result['models']if x['modelId']==n['model']['modelId']);assert m==n['model'];sheet=db.execute('SELECT sheet FROM astra_modelling.native_stage_inputs WHERE cache_key=%s',(key,)).fetchone()[0];rows.append(dict(uid=n['uid'],modelId=m['modelId'],sourceSHA256=m['asset']['sha256'],triangles=m['triangles'],native=dict(cacheKey=key,resultSha=sha,sheet=sheet,model=m)))
 assert len(rows)==7 and len({r['uid']for r in rows})==7;grouped=defaultdict(list)
 for r in rows:grouped[r['native']['sheet']].append(r)
 wanted={r['sourceSHA256']for r in rows};cache={};retained=defaultdict(list)
 names=subprocess.check_output(['rg','--files','--hidden','--no-ignore','-g','*.glb.gz','-g','download.json','source-scripts/city','3d-viewer/city/data'],cwd=ROOT,text=True).splitlines()
 for n in names:
  f=ROOT/n
  if f.name=='download.json':
   try:
    d=read(f)
    if d.get('sheet')in grouped:retained[d['sheet']].append((f,d))
   except(ValueError,OSError):pass
  elif f.name.removesuffix('.glb.gz')in wanted and digest(f.read_bytes())==f.name.removesuffix('.glb.gz'):cache[f.name.removesuffix('.glb.gz')]=f
 helper=module('yoho_tower_recovery',HERE/'xl-second-pass.py');helper.LOCAL=LOCAL;recoveries=[]
 for sheet,group in grouped.items():
  assert reservations.owns(lease);prior=HERE/'local/government-xl-terrain-sources-20260924/sheets'/sheet/'directory/result.json';refs.append(prior);recoveries.append(helper.source_sheet(sheet,group,read(prior),cache,retained[sheet]))
 for r in rows:
  f=LOCAL/'assets'/(r['sourceSHA256']+'.glb.gz');assert digest(f.read_bytes())==r['sourceSHA256'];r['assetPath']=str(f.relative_to(ROOT))
 save(DOC/'recovery.json',dict(rows=rows,recoveries=recoveries,installationApproved=False));refs.extend(f for f in LOCAL.rglob('*')if f.is_file()and f.name!='reservation.json');refs.extend(cache.values());assert reservations.owns(lease)
 module('yoho_tower_recovery_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'seven-exact-original-companion-cache-recovery',list(dict.fromkeys(refs)),dict(uids=[r['uid']for r in rows],exactHashMatched=True,originalAssets=7,installationApproved=False,sourceGeometryChanges=0))
def main():
 if '--owned'in sys.argv:return owned()
 assert not DOC.exists();uids=sorted({r['uid']for r in read(SRC/'nominations.json')['rows']});claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['building:'+u for u in uids],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];p=LOCAL/'reservation.json';save(p,json.loads(json.dumps(lease,default=str)))
 try:subprocess.run([sys.executable,str(HERE.parent/'shared-modelling/reservations.py'),'run','--lease-file',str(p),'--ttl','3600','--',sys.executable,__file__,'--owned'],cwd=ROOT,check=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
