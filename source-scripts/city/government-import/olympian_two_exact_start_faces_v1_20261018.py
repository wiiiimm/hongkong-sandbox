"""Resolve source-face query numerical ambiguity with exact rational distances."""
from fractions import Fraction as F
from pathlib import Path
import subprocess
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_point_triangle_distance_20261018 import squared_distance
BASE=ROOT/'docs/astra-city/government-import';PRIOR=BASE/'government-xl-olympian-two-source-face-paths-v3-20261018';INPUT=BASE/'government-xl-olympian-two-canonical-contacts-v1-20261018';BATCH='government-xl-olympian-two-exact-start-faces-v1-20261018';DOC=BASE/BATCH

def main():
 assert not DOC.exists();r=read(PRIOR/'result.json');pins={e['path']:e['sha256']for e in r['evidenceRefs']}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 rows=[];limit=F(1e-8)**2
 for row in read(INPUT/'support-checks.json.gz')['rows']:
  details=[]
  for d in row['unresolved']:
   faces=[dict(faceIndex=f['faceIndex'],exactSquaredDistance=str(squared_distance(d['position'],f['vertices'])))for f in d['originalSourceFaces']]
   details.append(dict(position=d['position'],faces=faces,exactStartFaces=[f['faceIndex']for f in faces if F(f['exactSquaredDistance'])<=limit]))
  summary=dict(uid=row['uid'],samples=len(details),withoutExactStart=sum(not x['exactStartFaces']for x in details));rows.append(dict(**summary,details=details));print(summary,flush=True)
 save(DOC/'exact-start-faces.json.gz',dict(rows=rows,squaredTolerance=str(limit),qualification='Exact rational point-to-finite-triangle distances on original binary coordinates. No snapping, source edits or support approval.'))
 refs=[Path(__file__),HERE/'exact_point_triangle_distance_20261018.py',PRIOR/'result.json',*[ROOT/p for p in pins]]
 out=module('olympian_exact_start_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'olympian-exact-rational-original-start-face-membership-v1',list(set(refs)),dict(uids=[x['uid']for x in rows],fullAcceptance=False,newlyInstalled=0));print(out['jobId'],flush=True)
if __name__=='__main__':main()
