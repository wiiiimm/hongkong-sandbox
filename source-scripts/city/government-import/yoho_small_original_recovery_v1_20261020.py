"""Recover two missing original cache files without geometry changes."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-yoho-small-original-recovery-v1-20261020';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH;SRC=BASE/'government-xl-yoho300857-neighbour-sources-v1-20261020'
assert not DOC.exists();r=read(SRC/'result.json');p=SRC/'nominations.json';pins={e['path']:e['sha256']for e in r['evidenceRefs']};assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs=[Path(__file__),SRC/'result.json',p,HERE/'xl-second-pass.py'];rows=[]
with connect()as c:
 c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for n in read(p)['rows']:
  if n['uid']not in ['landsd/300895:0','landsd/301659:0']:continue
  key=n['nativeStageKey'];sha,result=c.execute('SELECT result_sha,result FROM astra_modelling.native_stage_results WHERE cache_key=%s',(key,)).fetchone();assert sha==n['nativeStageSHA256'];m=next(x for x in result['models']if x['modelId']==n['model']['modelId']);assert m==n['model'];sheet=c.execute('SELECT sheet FROM astra_modelling.native_stage_inputs WHERE cache_key=%s',(key,)).fetchone()[0];assert sheet=='6-NW-10C';rows.append(dict(uid=n['uid'],modelId=m['modelId'],sourceSHA256=m['asset']['sha256'],native=dict(cacheKey=key,resultSha=sha,sheet=sheet,model=m)))
assert len(rows)==2
priorpath=HERE/'local/government-xl-terrain-sources-20260924/sheets/6-NW-10C/directory/result.json';prior=read(priorpath);refs.append(priorpath);helper=module('yoho_small_recovery',HERE/'xl-second-pass.py');helper.LOCAL=LOCAL;recovered=helper.source_sheet('6-NW-10C',rows,prior,{},[])
for row in rows:
 p=LOCAL/'assets'/(row['sourceSHA256']+'.glb.gz');assert digest(p.read_bytes())==row['sourceSHA256'];row['assetPath']=str(p.relative_to(ROOT))
save(DOC/'recovery.json',dict(rows=rows,recovery=recovered,installationApproved=False));refs.extend(p for p in LOCAL.rglob('*')if p.is_file()and p.name!='reservation.json');module('yoho_small_recovery_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-original-cache-recovery',refs,dict(uids=[r['uid']for r in rows],exactHashMatched=True,installationApproved=False,geometryChanges=0))
