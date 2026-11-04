"""Source-path context using the existing interface face-membership tolerance."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from olympian_two_residual_surface_paths_v1_20261018 import verify
BASE=ROOT/'docs/astra-city/government-import';PRIOR=BASE/'government-xl-olympian-two-residual-verified-face-distance-v1-20261018';BATCH='government-xl-olympian-two-residual-existing-tolerance-paths-v1-20261018';DOC=BASE/BATCH

def main():
 assert not DOC.exists();r=read(PRIOR/'result.json');pins={e['path']:e['sha256']for e in r['evidenceRefs']};refs=[Path(__file__),PRIOR/'result.json']
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 policy=HERE/'support-interface.mjs';assert 'closest.distanceTo(point)>.001' in policy.read_text()
 meshes={s['uid']:np.asarray(s['position']).reshape(-1,3)[np.asarray(s['index']).reshape(-1,3)]for s in read(BASE/'government-xl-olympian-two-canonical-contacts-v1-20261018/geometry-inputs.json.gz')['rows']};tails={}
 for name in ['government-xl-olympian-two-source-face-paths-v4-20261018','government-xl-olympian-two-residual-surface-paths-v1-20261018']:
  for row in read(BASE/name/'paths.json.gz')['rows']:
   for d in row['details']:
    w=d['witness']
    if not w:continue
    path=w.get('continuousLowPath',w.get('path'));ceiling=w.get('contactRegionCeiling',w.get('ceiling'))
    for n,f in enumerate(w['faces']):tails.setdefault((row['uid'],f),dict(faces=w['faces'][n:],points=path[n+1:],contact=w['contact'],ceiling=ceiling))
 results=[]
 for d in read(PRIOR/'distances.json')['rows']:
  uid=d['uid'];tail=tails[uid,d['nearestVerifiedPathFace']];path=[d['position'],*tail['points']];error=verify(meshes[uid],np.asarray(path),tail['faces']);ceiling=max(p[1]for p in path);gap=tail['contact']['gap'];passed=error<=.001 and ceiling<=tail['ceiling']+1e-9 and -.1<=gap<=1
  results.append(dict(uid=uid,position=d['position'],faces=tail['faces'],path=path,contact=tail['contact'],ceiling=tail['ceiling'],maximumFiniteFaceResidualM=error,existingMembershipToleranceM=.001,pathContextVerified=passed,supportApproved=False))
 save(DOC/'paths.json.gz',dict(rows=results,fullAcceptance=False,qualification='Geometric path context only at the existing support-interface finite-face membership tolerance. Exact source seams remain; no welding or geometry changes. This does not automatically clear canonical support warnings or establish source-specific interface approval.'))
 summary=dict(points=len(results),verifiedPathContexts=sum(x['pathContextVerified']for x in results),maximumResidualM=max(x['maximumFiniteFaceResidualM']for x in results),fullAcceptance=False,newlyInstalled=0);save(DOC/'summary.json',summary);print(summary,flush=True)
 refs.extend(ROOT/p for p in pins);refs.extend([policy,HERE/'olympian_two_residual_surface_paths_v1_20261018.py'])
 out=module('olympian_existing_tolerance_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'olympian-residual-existing-interface-membership-path-context-v1',list(set(refs)),dict(uids=sorted({x['uid']for x in results}),**summary));print(out['jobId'],flush=True)
if __name__=='__main__':main()
