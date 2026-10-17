"""Locate actual gaps versus conservative full-edge proof failures; diagnostic only."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from fu_tor_loy_nearest_interfaces_v1_20261017 import nearest
BASE=ROOT/'docs/astra-city/government-import';PRIOR=BASE/'government-xl-oi-sin-original-edges-v1-20261017';OLD=BASE/'government-xl-coverage-assembly-closure-20261007-256280-0'
BATCH='government-xl-oi-sin-unproved-edge-distances-v1-20261017';DOC=BASE/BATCH
UID='landsd/256280:0';SUPPORT='landsd/91128:0'
def main():
 assert not DOC.exists();r=read(PRIOR/'result.json')
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for ref in r['evidenceRefs']:assert digest((ROOT/ref['path']).read_bytes())==ref['sha256']
 decoder=module('oi_sin_probe_decoder',HERE/'xl-second-pass.py');decoder.LOCAL=HERE/'local/government-xl-oi-sin-original-interfaces-v1-20261017'
 source=next(x for x in read(OLD/'support-inputs.json')['sources']if x['uid']==SUPPORT);tri=decoder.glb_triangles(source);results=[]
 for n,e in enumerate(read(PRIOR/'edges.json.gz')['rows']):
  if e['proof']['verifiedCompleteOriginalEdgeFiniteFacadeBand']:continue
  a,b=np.asarray(e['segment']);samples=[]
  for k in range(33):
   p=a+(b-a)*(k/32);i,q,d=nearest(p,tri);samples.append(dict(parameterNumerator=k,parameterDenominator=32,position=p.tolist(),distanceM=d,supportFace=i))
  results.append(dict(edge=n,sourceFaces=e['sourceFaces'],maximumSample=max(samples,key=lambda x:x['distanceM']),samples=samples))
 summary=dict(unprovedEdges=len(results),edgesWithSampleBeyondFixedBand=sum(x['maximumSample']['distanceM']>.1 for x in results),maximumSampleDistanceM=max(x['maximumSample']['distanceM']for x in results),fixedBandM=.1,fullAcceptance=False,qualification='Floating-point full-support nearest-distance samples locate potential negative witnesses. Samples under the band do not certify a whole edge. No support or identity approval.')
 save(DOC/'probes.json.gz',dict(summary=summary,rows=results));refs=[Path(__file__),PRIOR/'result.json',PRIOR/'edges.json.gz',OLD/'support-inputs.json',ROOT/source['candidate']['path'],HERE/'xl-second-pass.py',HERE/'fu_tor_loy_nearest_interfaces_v1_20261017.py']
 out=module('oi_sin_probe_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'oi-sin-unproved-original-edge-distance-probes-v1',refs,dict(uids=[UID,SUPPORT],summary=summary,nextStep='Use exact source-face and component context to distinguish authored overhangs from missing source support; do not widen distance limits or claim permanent corruption.'))
 print(dict(jobId=out['jobId'],summary=summary),flush=True)
if __name__=='__main__':main()
