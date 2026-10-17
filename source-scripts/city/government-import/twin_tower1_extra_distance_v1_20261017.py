"""Resolve the full-sheet extra nomination using cached unchanged original triangles."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from fu_tor_loy_nearest_interfaces_v1_20261017 import nearest
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-twin-tower1-extra-distance-v1-20261017';DOC=BASE/BATCH;PREV=BASE/'government-xl-twin-tower1-sheet-candidates-v1-20261017';NEAR=BASE/'government-xl-twin-tower1-nearest-support-v1-20261017'
def main():
 assert not DOC.exists();refs=[Path(__file__),HERE/'exact_packed_world_geometry_20261009.py',HERE/'fu_tor_loy_nearest_interfaces_v1_20261017.py'];pins={}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for d in [PREV,NEAR,BASE/'government-xl-thirty-spatial-original-closures-20261008']:
   p=d/'result.json';r=read(p);assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(p)
   for q in r['evidenceRefs']:pins.setdefault(q['path'],set()).add(q['sha256'])
 p=PREV/'gap-candidates.json.gz';assert digest(p.read_bytes())in pins[str(p.relative_to(ROOT))];refs.append(p);extra=read(p)['extraModels'];assert len(extra)==1;m=extra[0];asset=HERE/'local/government-xl-thirty-spatial-original-closures-20261008'/m['asset']['asset'];assert digest(asset.read_bytes())==m['asset']['sha256']and digest(asset.read_bytes())in pins[str(asset.relative_to(ROOT))];refs.append(asset);tri=decode_original_world_triangles(asset.read_bytes());assert len(tri)==m['triangles']==223
 p=NEAR/'nearest.json.gz';assert digest(p.read_bytes())in pins[str(p.relative_to(ROOT))];refs.append(p);rows=[]
 for old in read(p)['rows']:
  pos=np.asarray(old['originalFailure']['position']);i,q,d=nearest(pos,tri);rows.append(dict(originalFailure=old['originalFailure'],priorNearest=old['nearest'],extraFace=i,extraPosition=q.tolist(),extraDistanceM=d,combinedNearestDistanceM=min(d,old['nearest']['distanceM'])))
 far=[r for r in rows if r['combinedNearestDistanceM']>.5];summary=dict(uid='landsd/223207:0',extraUid=m['candidate']['uid'],extraModelId=m['modelId'],extraSourceSHA256=m['asset']['sha256'],extraOriginalTriangles=len(tri),failedSamples=len(rows),remainingFartherThanHalfMetre=len(far),maximumCombinedDistanceM=max(r['combinedNearestDistanceM']for r in rows),minimumExtraDistanceM=min(r['extraDistanceM']for r in rows),fullAcceptance=False,newlyInstalled=0,qualification='Every original support triangle examined. Distances only, not contact/identity/terrain acceptance or a permanent corruption decision.')
 DOC.mkdir();save(DOC/'contacts.json.gz',dict(rows=rows));save(DOC/'summary.json',summary)
 result=module('twin_extra_distance_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'remaining-twin-tower1-extra-source-complete-distance-v1',refs,dict(uids=['landsd/223207:0'],summary=summary,fullAcceptance=False,newlyInstalled=0));print(dict(jobId=result['jobId'],summary=summary),flush=True)
if __name__=='__main__':main()
