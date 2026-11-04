"""Recover exact original neighbours needed to investigate the Parkview terrain warnings."""
from pathlib import Path
import uuid
from run import ROOT,HERE,read,save,digest,connect,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from primrose_compound_foundation_v2_20261015 import module
BATCH='government-xl-parkview-12-15-original-recovery-v1-20261021';BASE=ROOT/'docs/astra-city/government-import';DOC=BASE/BATCH;LOCAL=HERE/'local'/BATCH
UIDS={'landsd/255648:0','landsd/255440:0'}
def main():
 assert not DOC.exists() and not LOCAL.exists()
 previous='government-xl-parkview-14-companion-projection-v2-20261021';_,pins=authenticate(BASE/previous);refs=[Path(__file__),BASE/previous/'result.json']
 def take(p):
  assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p);return read(p)
 native=take(HERE/'local'/previous/'native-source.json');directory=take(HERE/'local'/previous/'pinned-directory.json')
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');sha,result=c.execute('SELECT result_sha,result FROM astra_modelling.native_stage_results WHERE cache_key=%s',(native['cacheKey'],)).fetchone();assert sha==native['resultSHA256']
 models=[m for m in result['models'] if m.get('candidate',{}).get('uid') in UIDS];assert {m['candidate']['uid'] for m in models}==UIDS
 claim=reservations.claim(BATCH+'-'+str(uuid.uuid4()),['building:'+u for u in sorted(UIDS)],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation']
 try:
  rows=[dict(uid=m['candidate']['uid'],modelId=m['modelId'],sourceSHA256=m['asset']['sha256'],native=dict(model=m,cacheKey=native['cacheKey'],sheet=directory['sheet'])) for m in models]
  save(DOC/'native-sources.json',dict(cacheKey=native['cacheKey'],resultSHA256=sha,rows=rows))
  recovery=module('parkview_neighbour_original_recovery',HERE/'xl-second-pass.py');recovery.LOCAL=LOCAL
  r=recovery.source_sheet(directory['sheet'],rows,directory,{},[]);save(DOC/'source-recovery.json',r)
  for row in rows:
   p=LOCAL/'assets'/(row['sourceSHA256']+'.glb.gz');assert digest(p.read_bytes())==row['sourceSHA256'];assert len(p.read_bytes())==row['native']['model']['asset']['bytes']
  refs.extend(p for p in LOCAL.rglob('*') if p.is_file());refs.extend([HERE/'xl-second-pass.py',HERE.parent/'citywide-native/convert.py',HERE.parent/'citywide-native/download.py',HERE.parent/'enhancement-screening/shape_prepare.py'])
  summary=dict(uids=sorted(UIDS),recovered=2,sourceGeometryChanges=0,installationApproved=False,purpose='Investigate two actual ordinary-neighbour terrain regressions; original recovery alone is not acceptance.')
  save(DOC/'summary.json',summary);assert reservations.owns(lease);receipt=module('parkview_neighbour_recovery_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'exact-original-neighbour-recovery',refs,summary);print(dict(jobId=receipt['jobId'],**summary),flush=True)
 finally:
  if reservations.owns(lease):assert reservations.release(lease)['ok']
if __name__=='__main__':main()
