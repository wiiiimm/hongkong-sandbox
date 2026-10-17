"""Whole low-rim finite-host diagnostic for the unchanged carpark; no admission override."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_original_edge_any_finite_distance_band_v1_20261010 import verify
BASE=ROOT/'docs/astra-city/government-import';PHYS=BASE/'government-xl-oi-sin-four-originals-physical-v2-20261017'
BATCH='government-xl-oi-sin-carpark-complete-rim-v2-20261017';DOC=BASE/BATCH
RT=HERE/'local'/PHYS.name/'runtime-geometry.json.gz'
def main():
 assert not DOC.exists()
 receipt=read(PHYS/'result.json');pins={e['path']:e['sha256'] for e in receipt['evidenceRefs']}
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 needed=[RT,PHYS/'support-checks.json.gz',PHYS/'selection.json.gz']
 for p in needed:assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))]
 geo={g['uid']:np.asarray(g['position']).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)] for g in read(RT)['rows']}
 source=geo['landsd/256457:0'];host=geo['landsd/91128:0'];bottom=source[:,:,1].min()
 horizontal=(np.ptp(host[:,:,1],axis=1)==0)&(np.linalg.norm(np.cross(host[:,1]-host[:,0],host[:,2]-host[:,0]),axis=1)>0)
 ids=np.flatnonzero(horizontal);fail=next(x['interface']['unresolved'] for x in read(needed[1])['rows'] if x['uid']=='landsd/256457:0');edges={}
 for i,t in enumerate(source):
  for a,b in [(0,1),(1,2),(2,0)]:
   if max(t[a,1],t[b,1])>bottom+.35 or np.array_equal(t[a],t[b]):continue
   k=tuple(sorted(map(tuple,t[[a,b]])));edges.setdefault(k,[]).append(i)
 out=[];accounted=set()
 prior=BASE/'government-xl-oi-sin-carpark-complete-rim-v1-20261017'
 pr=read(prior/'result.json')
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(pr['jobId'],)).fetchone()==('complete',pr)
 for e in pr['evidenceRefs']:assert digest((ROOT/e['path']).read_bytes())==e['sha256']
 old={tuple(map(tuple,r['segment'])):r for r in read(prior/'rim.json.gz')['rows']}
 for key,faces in edges.items():
  seg=np.asarray(key);a,b=seg;delta=b-a;matches=[]
  for i,f in enumerate(fail):
   p=np.asarray(f['position']);u=np.clip(np.dot(p-a,delta)/np.dot(delta,delta),0,1)
   if np.linalg.norm(p-(a+u*delta))<=.001:matches.append(i)
  if not matches:continue
  proof=old[key]['proof']
  if not proof['verifiedCompleteOriginalEdgeFiniteFacadeBand']:
   pieces=[verify(np.asarray([a+delta*(j/8),a+delta*((j+1)/8)]),host[ids]) for j in range(8)]
   proof=dict(verifiedCompleteOriginalEdgeFiniteFacadeBand=all(x['verifiedCompleteOriginalEdgeFiniteFacadeBand']for x in pieces),pieces=pieces,subdivisions=8,originalProof=proof)
  out.append(dict(segment=seg.tolist(),sourceFaces=faces,failurePoints=matches,proof=proof));accounted.update(matches)
  print('edge',len(out),proof['verifiedCompleteOriginalEdgeFiniteFacadeBand'],flush=True)
 summary=dict(unresolvedSamples=len(fail),accountedSamples=len(accounted),unaccountedSamples=sorted(set(range(len(fail)))-accounted),wholeEdges=len(out),wholeEdgesWithinHorizontalHostBand=sum(x['proof']['verifiedCompleteOriginalEdgeFiniteFacadeBand']for x in out),fullAcceptance=False,geometryChanges=0)
 save(DOC/'rim.json.gz',dict(summary=summary,hostOriginalFaceIds=ids.tolist(),rows=out))
 refs=[Path(__file__),prior/'result.json',prior/'rim.json.gz',PHYS/'result.json',*needed,HERE/'exact_original_edge_any_finite_distance_band_v1_20261010.py',HERE/'exact_original_perpendicular_any_facet_band_v1_20261010.py']
 r=module('oi_carpark_rim_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'oi-sin-carpark-whole-rim-horizontal-host-diagnostic-v2',refs,dict(uids=['landsd/256457:0','landsd/91128:0'],summary=summary,nextStep='Use complete rim association to distinguish a lower original support layer from the highest-roof sampler; preserve strict failures, resolve two buried junction facets separately.'))
 print(dict(jobId=r['jobId'],summary=summary),flush=True)
if __name__=='__main__':main()
