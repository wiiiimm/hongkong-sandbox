"""Complete original support-surface distances, preserving all failed interface points."""
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from fu_tor_loy_nearest_interfaces_v1_20261017 import nearest
BASE=ROOT/'docs/astra-city/government-import';PRIOR=BASE/'government-xl-park-avenue239350-six-foundations-contacts-v1-20261018';BATCH='government-xl-park-avenue239350-six-nearest-interfaces-v1-20261018';DOC=BASE/BATCH

def check(args):
 row,support,supports=args;details=[]
 for f in row['unresolved']:
  p=np.asarray(f['position']);i,q,d=nearest(p,support);offset=0;owner=None
  for s in supports:
   if offset<=i<offset+s['faces']:owner=dict(uid=s['uid'],sourceSHA256=s['sourceSHA256'],faceIndex=i-offset);break
   offset+=s['faces']
  assert owner
  details.append(dict(position=f['position'],originalReason=f['reason'],originalGapM=f.get('gap'),nearestPoint=q.tolist(),distanceM=d,support=owner,incidentSourceFaces=f['originalSourceFaces']))
 return dict(mode=row['coordinateMode'],uid=row['uid'],sourceSHA256=row['sourceSHA256'],failedSamples=len(details),withinHalfMetre=sum(x['distanceM']<=.5 for x in details),exactSurfaceContacts=sum(x['distanceM']<=.001 for x in details),maximumDistanceM=max(x['distanceM'] for x in details),rows=details)

def main():
 assert not DOC.exists();r=read(PRIOR/'result.json');pins={e['path']:e['sha256']for e in r['evidenceRefs']}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 jobs=[];all_uids=set();all_meta={}
 for mode in ['original','literal','left','balanced']:
  d=read(PRIOR/mode/'geometry-inputs.json.gz');supports=[x for x in d['rows'] if x['uid'] not in d['towerUIDs']];tri=np.concatenate([np.asarray(x['position']).reshape(-1,3)[np.asarray(x['index']).reshape(-1,3)] for x in supports]);meta=[dict(uid=x['uid'],sourceSHA256=x['sourceSHA256'],faces=len(x['index'])//3) for x in supports];all_meta[mode]=meta;all_uids.update(x['uid'] for x in d['rows'])
  for row in read(PRIOR/mode/'support-checks.json.gz')['rows']:jobs.append(({**row,'coordinateMode':mode},tri,meta))
 with ProcessPoolExecutor(max_workers=4) as pool:rows=list(pool.map(check,jobs))
 assert len(rows)==12
 save(DOC/'nearest-surfaces.json.gz',dict(rows=rows,supports=all_meta,fullAcceptance=False,qualification='Complete original support triangle distances. Proximity alone is not contact acceptance; all original strict failures retained. No source geometry or pose edits.'))
 summary=[{k:v for k,v in row.items()if k!='rows'}for row in rows];save(DOC/'summary.json',dict(rows=summary));print(summary,flush=True)
 out=module('olympian_nearest_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'park-avenue-six-original-nearest-support-four-modes-v1',[Path(__file__),HERE/'fu_tor_loy_nearest_interfaces_v1_20261017.py',PRIOR/'result.json',*[ROOT/p for p in pins]],dict(uids=sorted(all_uids),fullAcceptance=False,newlyInstalled=0));print(out['jobId'],flush=True)
if __name__=='__main__':main()
