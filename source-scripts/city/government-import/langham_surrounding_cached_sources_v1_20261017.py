"""Search surrounding retained source sheets for actual bounds near Langham's unresolved contacts."""
from pathlib import Path
from fractions import Fraction
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-langham-surrounding-cached-sources-v1-20261017';DOC=BASE/BATCH
PRIOR=BASE/'government-xl-langham-current-support-v1-20261017'
SHEETS=[f'11-NW-{n:02d}{letter}'for n in [13,14,15,18,19,20,23,24,25]for letter in 'ABCD']
def main():
 assert not DOC.exists();prior=read(PRIOR/'result.json')
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(prior['jobId'],)).fetchone()==('complete',prior)
 for e in prior['evidenceRefs']:assert digest((ROOT/e['path']).read_bytes())==e['sha256']
 points=np.asarray([r['position']for r in prior['interface']['unresolved']],float);assert points.shape==(4,3)
 witness=read(BASE/'government-xl-langham-rim-gap-witness-v1-20261017/witness.json')
 # Original unresolved points plus their per-point 1m nomination neighbourhood; no acceptance credit.
 DOC.mkdir();summaries=[];nominees=[]
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  cursor=c.cursor(name='langham_surrounding_native_sheets')
  cursor.execute('''SELECT DISTINCT ON(i.sheet) i.sheet,i.cache_key,i.source_sha,r.result_sha,r.result
     FROM astra_modelling.native_stage_inputs i JOIN astra_modelling.native_stage_results r USING(cache_key)
     WHERE i.sheet=ANY(%s) ORDER BY i.sheet,r.created_at DESC,i.cache_key''',(SHEETS,))
  for sheet,key,source_sha,result_sha,result in cursor:
   save(DOC/(sheet+'.json.gz'),dict(sheet=sheet,cacheKey=key,sourceSHA256=source_sha,resultSHA256=result_sha,result=result))
   missing=[];hits=[];models=result.get('models',[])
   for m in models:
    bounds=m.get('worldBounds')
    if not bounds:missing.append(dict(modelId=m.get('modelId'),state=m.get('state'),error=m.get('error')));continue
    a=np.asarray(bounds,float)
    if a.shape!=(2,3)or not np.isfinite(a).all()or (a[0]>a[1]).any():missing.append(dict(modelId=m.get('modelId'),state='invalid-bounds'));continue
    distances=np.linalg.norm(np.maximum(np.maximum(a[0]-points,points-a[1]),0),axis=1)
    if (distances<=1).any():
     row=dict(sheet=sheet,cacheKey=key,resultSHA256=result_sha,modelId=m.get('modelId'),boundsDistanceByPointM=distances.tolist(),model=m);hits.append(row);nominees.append(row)
   summaries.append(dict(sheet=sheet,cacheKey=key,resultSHA256=result_sha,models=len(models),boundsMissing=len(missing),missingModels=missing,nominatedModelIds=[m['modelId']for m in hits],terrainBounds=[t.get('worldBounds')for t in result.get('terrain',[])]))
   print(dict(sheet=sheet,models=len(models),missingBounds=len(missing),nominees=len(hits)),flush=True)
 found={r['sheet']for r in summaries};summary=dict(requestedSheets=SHEETS,foundSheets=sorted(found),missingSheets=sorted(set(SHEETS)-found),points=points.tolist(),sheets=summaries,totalModels=sum(s['models']for s in summaries),totalMissingBounds=sum(s['boundsMissing']for s in summaries),nominees=nominees,nominationDistanceM=1,sourceGeometryChanges=0,installationApproved=False,qualification='Retained-source metadata nomination only. Missing sheets/bounds remain explicit. Cached results are not fresh provider revision checks. AABB proximity is not support or identity acceptance; all actual nominated originals require full geometry validation.')
 save(DOC/'summary.json',summary)
 refs=[Path(__file__),PRIOR/'result.json',BASE/'government-xl-langham-rim-gap-witness-v1-20261017/witness.json',*[ROOT/e['path']for e in prior['evidenceRefs']]]
 out=module('langham_surrounding_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'langham-surrounding-retained-source-sheet-bound-nominations-v1',refs,dict(uids=['landsd/79318:0'],requestedSheets=len(SHEETS),foundSheets=len(found),missingSheets=summary['missingSheets'],modelsScanned=summary['totalModels'],missingBounds=summary['totalMissingBounds'],nominees=[dict(sheet=r['sheet'],modelId=r['modelId'])for r in nominees],fullAcceptance=False,nextStep='Inspect new source nominees; preserve unknown bounds/sheets and existing exact contact failures. No global exclusion or permanent rejection.'))
 print(out['jobId'],flush=True)
if __name__=='__main__':main()
