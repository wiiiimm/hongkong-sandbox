"""Source-bound neighbour nomination across the complete pinned native run.

No model/terrain edits or approvals. Null candidate UIDs and unknown bounds stay
explicit; a single sheet never substitutes for territorial source coverage.
"""
import argparse
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect,reservations,NATIVE_RUN
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
def main():
 p=argparse.ArgumentParser();p.add_argument('--batch',required=True);p.add_argument('--uid',required=True);p.add_argument('--lease',required=True);p.add_argument('--nomination',required=True);a=p.parse_args();assert a.batch.startswith('government-xl-')and '/'not in a.batch
 lease=read(Path(a.lease));assert reservations.owns(lease)and 'building:'+a.uid in lease['resources'];out=BASE/a.batch;assert not out.exists();_,pins=authenticate(BASE/a.nomination);path=BASE/a.nomination/'summary.json';assert digest(path.read_bytes())==pins[str(path.relative_to(ROOT))];old=read(path);assert old['uid']==a.uid;key,model_id=old['sourceKey'].split('/',1);lo,hi=old['targetModel']['worldBounds'];pad=old['paddingM']
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY')
  totals=db.execute("SELECT count(*),count(r.cache_key),sum(jsonb_array_length(r.result->'models')) FROM astra_modelling.native_stage_members s LEFT JOIN astra_modelling.native_stage_results r USING(cache_key) WHERE s.run_id=%s",(NATIVE_RUN,)).fetchone();assert totals[0]==totals[1]and totals[2]>0
  matches=db.execute("""SELECT i.sheet,r.cache_key,r.result_sha,n
   FROM astra_modelling.native_stage_members s
   JOIN astra_modelling.native_stage_results r USING(cache_key)
   JOIN astra_modelling.native_stage_inputs i USING(cache_key)
   CROSS JOIN LATERAL jsonb_array_elements(r.result->'models') n
   WHERE s.run_id=%s AND NOT(r.cache_key=%s AND n->>'modelId'=%s)
   AND jsonb_typeof(n->'worldBounds')='array'
   AND(n->'worldBounds'->0->>0)::double precision<=%s
   AND(n->'worldBounds'->1->>0)::double precision>=%s
   AND(n->'worldBounds'->0->>2)::double precision<=%s
   AND(n->'worldBounds'->1->>2)::double precision>=%s
   ORDER BY i.sheet,n->>'modelId'""",(NATIVE_RUN,key,model_id,hi[0]+pad,lo[0]-pad,hi[2]+pad,lo[2]-pad)).fetchall()
  unknown=db.execute("""SELECT i.sheet,count(*) FROM astra_modelling.native_stage_members s
   JOIN astra_modelling.native_stage_results r USING(cache_key)
   JOIN astra_modelling.native_stage_inputs i USING(cache_key)
   CROSS JOIN LATERAL jsonb_array_elements(r.result->'models') n
   WHERE s.run_id=%s AND jsonb_typeof(n->'worldBounds')IS DISTINCT FROM'array'
   GROUP BY i.sheet ORDER BY i.sheet""",(NATIVE_RUN,)).fetchall()
  assert db.execute('SELECT result_sha FROM astra_modelling.native_stage_results WHERE cache_key=%s',(key,)).fetchone()==(old['nativeResultSHA256'],)
 rows=[dict(sheet=sheet,sourceKey=cache+'/'+m['modelId'],nativeResultSHA256=sha,candidateUid=(m.get('candidate')or {}).get('uid'),model=m,sourceHeightBelowTargetFloor=m['worldBounds'][1][1]-lo[1],supportApproved=False,identityApproved=False)for sheet,cache,sha,m in matches]
 result=dict(uids=[a.uid],uid=a.uid,nativeRun=NATIVE_RUN,targetSourceKey=old['sourceKey'],indexedSourceSHA256=old['indexedSourceSHA256'],targetBounds=old['targetModel']['worldBounds'],paddingM=pad,preparedSheets=totals[1],completeNativeUnitsScanned=totals[2],nearbyOriginalCandidates=rows,candidates=len(rows),unknownBoundsBySheet=[dict(sheet=s,models=n)for s,n in unknown],unknownBounds=sum(n for s,n in unknown),sourceGeometryChanges=0,installationApproved=False,qualification='Full pinned native run searched by source geometry metadata bounds inXZ, noYfilter. Null/unknown bounds remain explicit and cannot be excluded by this search. A nominated source is not an accepted support or identity, and no revision is declared invalid.')
 save(out/'summary.json',result);assert reservations.owns(lease);module('territorial_neighbour_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(a.batch,'complete-pinned-native-run-original-neighbour-nomination',[Path(__file__),BASE/a.nomination/'result.json',path],result);print(dict(sheets=totals[1],units=totals[2],candidates=len(rows),unknownBounds=result['unknownBounds']),flush=True)
if __name__=='__main__':main()
