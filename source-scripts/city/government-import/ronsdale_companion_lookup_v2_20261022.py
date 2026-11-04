"""Find the exact native-stage originals for remaining Ronsdale basic companions."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-ronsdale-companion-lookup-v2-20261022';DOC=BASE/BATCH
IDS=[256898,256900,307560]
def main():
 assert not DOC.exists();prior=BASE/'government-xl-ronsdale-podium-original-ground-v1-20261022';_,pins=authenticate(prior);p=prior/'selection.json.gz';assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];source=read(p)['rows'][0];key=source['native']['cacheKey'];expected=source['native']['resultSha']
 formsdoc=BASE/'government-xl-ronsdale-regional-scope-v1-20261022';_,formpins=authenticate(formsdoc);formpath=formsdoc/'form-obligations.json.gz';assert digest(formpath.read_bytes())==formpins[str(formpath.relative_to(ROOT))];form=next(r for r in read(formpath)if r['uid']=='landsd/307560:0');prefix='B'+form['buildingCSUID'][:10];assert prefix=='B3821015077'
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');sha=c.execute('SELECT result_sha FROM astra_modelling.native_stage_results WHERE cache_key=%s',(key,)).fetchone()[0];assert sha==expected
  rows=[r[0]for r in c.execute("SELECT m FROM astra_modelling.native_stage_results s CROSS JOIN LATERAL jsonb_array_elements(s.result->'models') m WHERE s.cache_key=%s AND (EXISTS (SELECT 1 FROM jsonb_array_elements(m->'matching'->'officialCandidates') e WHERE (e->>'objectId')::bigint=ANY(%s)) OR m->>'modelId' LIKE %s)",(key,IDS,prefix+'%')).fetchall()]
 result=dict(uids=['landsd/'+str(i)+':0'for i in IDS],nativeCacheKey=key,nativeResultSHA256=sha,models=rows,installationApproved=False,qualification='Exact cached native-stage candidates and a geographic-prefix lookup only (the latter does not approve identity); identity, availability, physical and publication checks remain required.')
 save(DOC/'models.json',result);module('ronsdale_lookup_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-original-companion-stage-lookup',[Path(__file__),prior/'result.json',p,formsdoc/'result.json',formpath],result);print(dict(models=len(rows),matches=[dict(modelId=r['modelId'],candidates=[c['objectId']for c in r['matching']['officialCandidates']if c['objectId']in IDS])for r in rows]),flush=True)
if __name__=='__main__':main()
