"""Recover three identified government originals byte-for-byte; no model redesign."""
from pathlib import Path
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-plaza-ascot-three-neighbour-recovery-v2-20261020';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
SRC=BASE/'government-xl-plaza-ascot-five-neighbour-registry-v1-20261020';GROUND=BASE/'government-xl-next-three-adjoining-ground-v1-20261020'
def main():
 assert not DOC.exists()and not LOCAL.exists();refs=[Path(__file__),HERE/'xl-second-pass.py'];pins={}
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY')
  for d in [SRC,GROUND]:
   r=read(d/'result.json');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(d/'result.json');pins[d]={e['path']:e['sha256']for e in r['evidenceRefs']}
  p=SRC/'registry.json.gz';assert digest(p.read_bytes())==pins[SRC][str(p.relative_to(ROOT))];refs.append(p);record=read(p);rows=[]
  for r in record['rows']:
   assert len(r['exactOfficialCandidates'])==1;m=r['native']['model'];sha,result=db.execute('SELECT result_sha,result FROM astra_modelling.native_stage_results WHERE cache_key=%s',(r['native']['cacheKey'],)).fetchone();assert sha==r['native']['resultSha']and next(x for x in result['models']if x['modelId']==r['modelId'])==m
   rows.append(dict(uid=r['uid'],modelId=r['modelId'],sourceSHA256=m['asset']['sha256'],triangles=m['triangles'],native=r['native']))
 assert len(rows)==3 and len({r['uid']for r in rows})==3
 helper=module('plaza_three_source_recovery',HERE/'xl-second-pass.py');helper.LOCAL=LOCAL;recovery=[]
 for sheet in sorted({r['native']['sheet']for r in rows}):
  p=HERE/'local'/GROUND.name/'sheets'/sheet/'directory/result.json';assert digest(p.read_bytes())==pins[GROUND][str(p.relative_to(ROOT))];refs.append(p)
  recovery.append(helper.source_sheet(sheet,[r for r in rows if r['native']['sheet']==sheet],read(p),{},[]))
 for r in rows:
  p=LOCAL/'assets'/(r['sourceSHA256']+'.glb.gz');assert digest(p.read_bytes())==r['sourceSHA256'];r['assetPath']=str(p.relative_to(ROOT))
 save(DOC/'recovery.json',dict(rows=rows,recovery=recovery,installationApproved=False));refs.extend(p for p in LOCAL.rglob('*')if p.is_file())
 result=dict(uids=sorted(r['uid']for r in rows),originalAssets=3,exactHashMatched=True,installationApproved=False,sourceGeometryChanges=0)
 module('plaza_three_recovery_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'three-retained-neighbour-exact-original-recovery',list(dict.fromkeys(refs)),result)
if __name__=='__main__':main()
