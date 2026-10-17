"""Account for every failed original Tower1 rim point against complete installed supports."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from fu_tor_loy_nearest_interfaces_v1_20261017 import nearest
BASE=ROOT/'docs/astra-city/government-import';PREV=BASE/'government-xl-twin-tower1-installed-support-v1-20261017';BATCH='government-xl-twin-tower1-nearest-support-v1-20261017';DOC=BASE/BATCH

def main():
 assert not DOC.exists();r=read(PREV/'result.json')
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 refs=[Path(__file__),HERE/'fu_tor_loy_nearest_interfaces_v1_20261017.py',PREV/'result.json'];pins={q['path']:q['sha256']for q in r['evidenceRefs']}
 for f in ['input.json.gz','interfaces.json.gz']:
  p=PREV/f;assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p)
 data=read(PREV/'input.json.gz');supports={s['uid']:np.asarray(s['triangles'])for s in data['supports']};proof=read(PREV/'interfaces.json.gz')['rows'][-1]['proof'];rows=[]
 for f in proof['unresolved']:
  pos=np.asarray(f['position']);found=[]
  for uid,tri in supports.items():
   i,q,dist=nearest(pos,tri);found.append(dict(uid=uid,face=i,position=q.tolist(),distanceM=dist))
  winner=min(found,key=lambda x:x['distanceM']);rows.append(dict(originalFailure=f,allSupportDistances=found,nearest=winner,withinHalfMetre=winner['distanceM']<=.5,withinMillimetre=winner['distanceM']<=.001))
 summary=dict(failedSamples=len(rows),withinHalfMetre=sum(r['withinHalfMetre']for r in rows),withinMillimetre=sum(r['withinMillimetre']for r in rows),minimumDistanceM=min(r['nearest']['distanceM']for r in rows),maximumDistanceM=max(r['nearest']['distanceM']for r in rows),sourceTriangles=len(data['source']['triangles']),supportTriangles={u:len(t)for u,t in supports.items()},fullAcceptance=False,newlyInstalled=0)
 DOC.mkdir();save(DOC/'nearest.json.gz',dict(rows=rows,sourceSHA256=data['source']['sourceSHA256'],supportSHA256ByUid={s['uid']:s['sourceSHA256']for s in data['supports']},qualification='Complete original-support triangle nearest distances, nomination only. No current rendered geometry or terrain/identity/support acceptance; no geometry edits.'));save(DOC/'summary.json',summary)
 out=module('twin_nearest_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'remaining-original-twin-tower1-complete-support-distance-v1',refs,dict(uids=['landsd/223207:0'],summary=summary,fullAcceptance=False,newlyInstalled=0));print(dict(jobId=out['jobId'],summary=summary),flush=True)
if __name__=='__main__':main()
