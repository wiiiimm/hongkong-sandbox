"""Find exact government originals for five ordinary-neighbour regressions."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect,NATIVE_RUN
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-manhattan-companion-sources-v1-20261021';DOC=BASE/BATCH;SRC=BASE/'government-xl-manhattan-neighbours-v2-20261021'
assert not DOC.exists();r=read(SRC/'result.json');pins={e['path']:e['sha256']for e in r['evidenceRefs']};p=SRC/'summary.json';assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];uids={'landsd/'+str(i)+':0' for i in [120103,213072,258271,260440,266799,271788,307773]};assert uids<=set(read(p)['ordinaryFlagged']);ids={int(u.split('/')[1].split(':')[0]):u for u in uids};refs=[Path(__file__),SRC/'result.json',p];found=[]
with connect()as c:
 c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 sheet=c.execute('SELECT sheet FROM astra_modelling.native_stage_inputs WHERE cache_key=%s',('dbffdf33c7302e7d9a2a7040d2cd34ca59a354043e351acb04037d3d94b46dd3',)).fetchone()[0]
 registries=c.execute('SELECT r.cache_key,r.result_sha,r.result FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_inputs i USING(cache_key) JOIN astra_modelling.native_stage_members m USING(cache_key) WHERE m.run_id=%s AND i.sheet IN (%s,%s) ORDER BY r.cache_key',(NATIVE_RUN,sheet,sheet)).fetchall()
 for key,sha,result in registries:
  hits=[]
  for model in result['models']:
   for candidate in model.get('matching',{}).get('officialCandidates',[]):
    if candidate.get('objectId')in ids:hits.append(dict(uid=ids[candidate['objectId']],model=model,candidate=candidate,nativeStageKey=key,nativeStageSHA256=sha))
  if hits:save(DOC/('registry-'+key+'.json.gz'),dict(cacheKey=key,resultSHA256=sha,result=result));found.extend(hits)
save(DOC/'nominations.json',dict(rows=found,missing=sorted(uids-{x['uid']for x in found}),installationApproved=False,qualification='Cached exact-object candidates only; source identity, physical and runtime acceptance remain required.'))
module('yoho_neighbour_source_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'seven-tower-original-source-discovery',refs,dict(uids=sorted(uids),found=sorted({x['uid']for x in found}),missing=sorted(uids-{x['uid']for x in found}),installationApproved=False));print([(x['uid'],x['model']['modelId'],x['model']['triangles'])for x in found],flush=True)
