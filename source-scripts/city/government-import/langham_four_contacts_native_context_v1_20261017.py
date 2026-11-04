"""Complete nearest-source distances and frozen-sheet nominations for four contacts."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from fu_tor_loy_nearest_interfaces_v1_20261017 import nearest
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-langham-four-contacts-native-context-v1-20261017';DOC=BASE/BATCH
PAIR=BASE/'government-xl-langham-current-pair-v1-20261017';CHECK=BASE/'government-xl-langham-current-support-v1-20261017';RT=HERE/'local'/PAIR.name/'runtime-geometry.json.gz'
def main():
 assert not DOC.exists();r=read(CHECK/'result.json');selection=read(PAIR/'selection.json.gz');row=next(x for x in selection['rows']if x['uid']=='landsd/79318:0');key=row['native']['cacheKey'];expected=row['native']['resultSha']
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  sha,native=c.execute('SELECT result_sha,result FROM astra_modelling.native_stage_results WHERE cache_key=%s',(key,)).fetchone();assert sha==expected
 for q in r['evidenceRefs']:assert digest((ROOT/q['path']).read_bytes())==q['sha256']
 rt=read(RT);g=next(x for x in rt['rows']if x['uid']=='landsd/224399:0');support=np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)];assert len(support)==20260
 models=native['models'];assert all(x.get('worldBounds')for x in models);known={x['candidate']['entry']['modelId']:x['sourceSHA256']for x in selection['rows']}
 for mid,h in known.items():assert next(x for x in models if x['modelId']==mid)['asset']['sha256']==h
 failures=read(CHECK/'support-checks.json.gz')['rows'][0]['unresolved'];out=[];extra={}
 for failure in failures:
  p=np.asarray(failure['position']);i,q,d=nearest(p,support);possible=[]
  for m in models:
   if m['modelId']in known:continue
   lo,hi=np.asarray(m['worldBounds']);distance=float(np.linalg.norm(np.maximum(np.maximum(lo-p,p-hi),0)))
   if distance<=1:possible.append(dict(modelId=m['modelId'],boundsDistanceM=distance));extra[m['modelId']]=m
  out.append(dict(failure=failure,nearestInstalledSupportFace=i,nearestInstalledSupportPosition=q.tolist(),nearestInstalledSupportDistanceM=d,possibleAdditionalSourceParts=possible))
 summary=dict(sheet=row['native']['sheet'],cacheKey=key,resultSHA=sha,totalSheetSources=len(models),failedPoints=len(out),nearestDistancesM=[x['nearestInstalledSupportDistanceM']for x in out],extraModelIds=sorted(extra),sourceGeometryChanges=0,installationApproved=False,qualification='One complete frozen sheet nomination within1m and full20260-face support nearest-distance query. No adjacent-sheet exclusion, support acceptance, arbitrary tolerance change or permanent rejection.')
 save(DOC/'source-context.json.gz',dict(rows=out,extraModels=list(extra.values())));save(DOC/'sheet-native-result.json.gz',dict(cacheKey=key,resultSHA=sha,result=native));save(DOC/'summary.json',summary)
 refs=[Path(__file__),RT,CHECK/'result.json',CHECK/'support-checks.json.gz',PAIR/'selection.json.gz',HERE/'fu_tor_loy_nearest_interfaces_v1_20261017.py']
 for p,h in rt['inputHashes'].items():assert digest((ROOT/p).read_bytes())==h;refs.append(ROOT/p)
 result=module('langham_native_context_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'four-langham-failed-contact-complete-native-sheet-context-v1',refs,dict(uids=[row['uid']],summary=summary,fullAcceptance=False,nextStep='Inspect nominated original parts if present; otherwise examine measured original wall/support edge mismatch without replaying the same sheet or accepting nearest distance as contact.'))
 print(dict(jobId=result['jobId'],summary=summary),flush=True)
if __name__=='__main__':main()
