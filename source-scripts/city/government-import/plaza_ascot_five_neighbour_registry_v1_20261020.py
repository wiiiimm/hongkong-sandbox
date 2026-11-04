"""Locate exact georef candidates for five retained neighbours; no identity approval."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect,NATIVE_RUN
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-plaza-ascot-five-neighbour-registry-v1-20261020';DOC=BASE/BATCH
UIDS=['landsd/71638:0','landsd/164322:0','landsd/208229:0','landsd/247819:0','landsd/247821:0']
def main():
 assert not DOC.exists();tile=ROOT/'3d-viewer/city/data/tiles/2_-7.json';th=digest(tile.read_bytes());forms={b['uid']:b for b in read(tile)['buildings']if b['uid']in UIDS};assert len(forms)==5
 prefixes={u:'B'+b['buildingCSUID'][:10]for u,b in forms.items()};rows=[]
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY');db.execute("SET LOCAL statement_timeout='60s'")
  found=db.execute("SELECT r.cache_key,m,i.sheet,r.result_sha FROM astra_modelling.native_stage_results r JOIN astra_modelling.native_stage_inputs i USING(cache_key) JOIN astra_modelling.native_stage_members membership USING(cache_key), LATERAL jsonb_array_elements(r.result->'models')m WHERE membership.run_id=%s AND left(m->>'modelId',11)=ANY(%s) ORDER BY m->>'modelId'",(NATIVE_RUN,list(prefixes.values()))).fetchall()
  for key,m,sheet,sha in found:
   for uid,prefix in prefixes.items():
    if m['modelId'].startswith(prefix):
     official=[c for c in m.get('matching',{}).get('officialCandidates',[])if c.get('objectId')==forms[uid]['objectId']and c.get('buildingCSUID')==forms[uid]['buildingCSUID']]
     rows.append(dict(uid=uid,modelId=m['modelId'],native=dict(cacheKey=key,resultSha=sha,sheet=sheet,model=m),exactOfficialCandidates=official,identityAccepted=False))
 assert digest(tile.read_bytes())==th
 save(DOC/'registry.json.gz',dict(nativeRun=NATIVE_RUN,forms=forms,prefixes=prefixes,rows=rows))
 result=dict(uids=UIDS,candidates=[dict(uid=r['uid'],modelId=r['modelId'],sheet=r['native']['sheet'],exactOfficialCandidate=bool(r['exactOfficialCandidates']))for r in rows],noGeorefCandidates=sorted(set(UIDS)-{r['uid']for r in rows}),installationApproved=False,sourceGeometryChanges=0)
 save(DOC/'summary.json',result);module('plaza_five_neighbours_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'five-retained-neighbour-georef-source-registry-lookup',[Path(__file__),tile],result);print(result,flush=True)
if __name__=='__main__':main()
