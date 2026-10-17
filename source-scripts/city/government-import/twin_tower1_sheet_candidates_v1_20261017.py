"""Nominate additional unchanged government parts near unresolved Tower1 support points."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-twin-tower1-sheet-candidates-v1-20261017';DOC=BASE/BATCH;PRIOR=BASE/'government-xl-twin-tower1-nearest-support-v1-20261017';INPUT=BASE/'government-xl-twin-tower1-installed-support-v1-20261017';OLD=BASE/'government-xl-extended-223207-20261005'
def main():
 assert not DOC.exists();r=read(PRIOR/'result.json');old=read(OLD/'selection.json.gz')['rows'];row=next(r for r in old if r['uid']=='landsd/223207:0');key=row['native']['cacheKey'];expected=row['native']['resultSha'];refs=[Path(__file__),PRIOR/'result.json',PRIOR/'nearest.json.gz',INPUT/'input.json.gz',OLD/'selection.json.gz']
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  sha,native=c.execute('SELECT result_sha,result FROM astra_modelling.native_stage_results WHERE cache_key=%s',(key,)).fetchone();assert sha==expected
 for q in r['evidenceRefs']:assert digest((ROOT/q['path']).read_bytes())==q['sha256']
 src=read(INPUT/'input.json.gz');known={row['modelId']}|{s['entry']['modelId']for s in src['supports']};hashes={row['modelId']:src['source']['sourceSHA256'],**{s['entry']['modelId']:s['sourceSHA256']for s in src['supports']}}
 models=native['models'];assert all(m.get('worldBounds')for m in models)
 for mid,h in hashes.items():assert next(m for m in models if m['modelId']==mid)['asset']['sha256']==h
 output=[];extra={}
 for f in read(PRIOR/'nearest.json.gz')['rows']:
  if f['withinHalfMetre']:continue
  pos=np.asarray(f['originalFailure']['position']);possible=[]
  for m in models:
   if m['modelId']in known:continue
   lo,hi=np.asarray(m['worldBounds']);distance=float(np.linalg.norm(np.maximum(np.maximum(lo-pos,pos-hi),0)))
   if distance<=.5:possible.append(dict(modelId=m['modelId'],boundsDistanceM=distance));extra[m['modelId']]=m
  output.append(dict(position=pos.tolist(),knownSupportDistanceM=f['nearest']['distanceM'],otherSheetCandidates=possible))
 summary=dict(sheet=row['native']['sheet'],cacheKey=key,resultSHA=sha,totalSheetSources=len(models),knownModelIds=sorted(known),farGapPoints=len(output),pointsWithAdditionalCandidate=sum(bool(x['otherSheetCandidates'])for x in output),extraModelIds=sorted(extra),allIndexedBoundsPresent=True,fullAcceptance=False,newlyInstalled=0,qualification='Complete frozen sheet bounding-box nomination only. No adjacent-sheet exclusion, model corruption or permanent rejection inferred.')
 DOC.mkdir();save(DOC/'sheet-native-result.json.gz',dict(cacheKey=key,resultSHA=sha,result=native));save(DOC/'gap-candidates.json.gz',dict(rows=output,extraModels=list(extra.values())));save(DOC/'summary.json',summary)
 result=module('twin_sheet_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'remaining-twin-tower1-original-sheet-support-nominations-v1',refs,dict(uids=['landsd/223207:0'],summary=summary,fullAcceptance=False,newlyInstalled=0));print(dict(jobId=result['jobId'],summary=summary),flush=True)
if __name__=='__main__':main()
