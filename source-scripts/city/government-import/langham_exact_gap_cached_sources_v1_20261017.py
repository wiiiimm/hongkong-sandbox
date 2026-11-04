"""Nominate cached originals around the exact failed interior contact witness."""
from fractions import Fraction
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
BASE=ROOT/'docs/astra-city/government-import'
PRIOR=BASE/'government-xl-langham-surrounding-cached-sources-v1-20261017'
BATCH='government-xl-langham-exact-gap-cached-sources-v1-20261017'
DOC=BASE/BATCH

def main():
 assert not DOC.exists()
 receipt=read(PRIOR/'result.json');pins={}
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 for e in receipt['evidenceRefs']:
  assert e['path'] not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 witness=BASE/'government-xl-langham-rim-gap-witness-v1-20261017/witness.json'
 exact=read(witness)['summary']['exactWitnessCoordinates'];point=np.array([float(Fraction(v)) for v in exact]);hits=[];missing=[];count=0
 summary=read(PRIOR/'summary.json');assert not summary['missingSheets']
 for sheet in summary['foundSheets']:
  path=PRIOR/(sheet+'.json.gz');assert str(path.relative_to(ROOT)) in pins
  packet=read(path)
  for model in packet['result']['models']:
   count+=1;a=np.asarray(model.get('worldBounds'),float)
   if a.shape!=(2,3) or not np.isfinite(a).all() or (a[0]>a[1]).any():missing.append([sheet,model.get('modelId')]);continue
   distance=float(np.linalg.norm(np.maximum(np.maximum(a[0]-point,point-a[1]),0)))
   if distance<=1:hits.append(dict(sheet=sheet,modelId=model.get('modelId'),distanceM=distance,model=model))
 assert count==summary['totalModels']
 DOC.mkdir();save(DOC/'summary.json',dict(exactWitnessCoordinates=exact,modelsScanned=count,sheets=len(summary['foundSheets']),missingBounds=missing,nominees=hits,nominationRadiusM=1,installationApproved=False,qualification='Cached AABB nomination around one exact failed-contact witness, not full-edge exclusion, fresh provider verification or physical acceptance.'))
 save(PRIOR/'ROOT-VERIFIED.json',dict(jobId=receipt['jobId'],exactNeonResultVerified=True,distinctHashesVerified=len(pins)))
 out=module('langham_gap_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'langham-exact-gap-cached-source-nomination-v1',[__file__,PRIOR/'result.json',witness,*[ROOT/p for p in pins]],dict(uids=['landsd/79318:0'],modelsScanned=count,sheets=len(summary['foundSheets']),nominees=[dict(sheet=h['sheet'],modelId=h['modelId']) for h in hits],missingBounds=len(missing),fullAcceptance=False,nextStep='Inspect nominated original geometry; do not waive the exact support gap or infer permanent noninstallability.'))
 print(out['jobId'],flush=True)
if __name__=='__main__':main()
