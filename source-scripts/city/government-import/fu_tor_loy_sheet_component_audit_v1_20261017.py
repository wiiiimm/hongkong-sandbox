"""Bounded original sheet completeness audit; nomination is not support acceptance."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';PREFIX='government-xl-fu-tor-loy-';BATCH=PREFIX+'sheet-component-audit-v1-20261017';DOC=BASE/BATCH
KEY='adf1d085a79951ff976393a3672cda66812a6fd2482559fc4b7435331c50964b';SHA='90fda1d21ed8497fd7ebdac6b3227d9aa3778671b2f7f84de91e9b3c54f9c249'
def main():
 assert not DOC.exists();prior=BASE/(PREFIX+'nearest-interfaces-v1-20261017');r=read(prior/'result.json')
 with connect()as db:
  db.execute('SET TRANSACTION READ ONLY');assert db.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  sha,native=db.execute('SELECT result_sha,result FROM astra_modelling.native_stage_results WHERE cache_key=%s',(KEY,)).fetchone();assert sha==SHA
 for q in r['evidenceRefs']:assert digest((ROOT/q['path']).read_bytes())==q['sha256']
 selected=read(BASE/(PREFIX+'original-group-v1-20261016')/'selection.json.gz')['rows'];known={x['modelId']for x in selected};models=native['models'];assert len(models)==492 and all(m.get('worldBounds')for m in models)
 for row in selected:
  assert row['native']['cacheKey']==KEY and row['native']['resultSha']==SHA
  m=next(m for m in models if m['modelId']==row['modelId']);assert m['asset']['sha256']==row['sourceSHA256'] and m['worldBounds']==row['candidate']['entry']['worldBounds']
 output=[];extras={}
 for row in read(prior/'nearest-surfaces.json.gz')['rows']:
  for f in row['rows']:
   if f['nearestDistanceM']<=.5:continue
   p=np.array(f['position']);possible=[]
   for m in models:
    if m['modelId']in known:continue
    lo,hi=np.array(m['worldBounds']);distance=float(np.linalg.norm(np.maximum(np.maximum(lo-p,p-hi),0)))
    if distance<=.5:
     possible.append(dict(modelId=m['modelId'],boundsDistanceM=distance));extras[m['modelId']]=m
   output.append(dict(uid=row['uid'],position=f['position'],nearestKnownPodiumM=f['nearestDistanceM'],otherSheetCandidates=possible))
 summary=dict(sheet='11-NW-19A',cacheKey=KEY,resultSHA=sha,totalSheetSources=492,allHaveIndexedBounds=True,selectedSourcesFromSameFrozenRevision=True,farGapPoints=len(output),pointsWithAdditionalCandidate=sum(bool(x['otherSheetCandidates'])for x in output),extraModelIds=sorted(extras),fullAcceptance=False,newlyInstalled=0,qualification='All models in this frozen sheet considered using complete indexed XYZ bounds as exclusion/nomination only. No adjacent-sheet exclusion, detailed contact proof or permanent rejection inferred.')
 DOC.mkdir();save(DOC/'sheet-native-result.json.gz',dict(cacheKey=KEY,resultSHA=sha,result=native));save(DOC/'gap-candidates.json.gz',dict(rows=output,extraModels=list(extras.values())));save(DOC/'summary.json',summary)
 refs=[Path(__file__),prior/'result.json',prior/'nearest-surfaces.json.gz',BASE/(PREFIX+'original-group-v1-20261016')/'selection.json.gz']
 out=module('fu_sheet_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-sheet-completeness-and-gap-source-nominations-v1',refs,dict(uids=[x['uid']for x in selected],fullAcceptance=False,newlyInstalled=0));print(dict(jobId=out['jobId'],summary=summary),flush=True)
if __name__=='__main__':main()
