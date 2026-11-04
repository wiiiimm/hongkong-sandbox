"""Complete two original corner edges in captured renderer arithmetic modes."""
from pathlib import Path
from fractions import Fraction as F
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_original_edge_any_finite_distance_band_v1_20261010 import verify
BASE=ROOT/'docs/astra-city/government-import';CAP=BASE/'government-xl-orchards-four-world-capture-v1-20261017';EDGE=BASE/'government-xl-orchards-original-corner-edges-v1-20261017';SPLIT=BASE/'government-xl-orchards-corner-edge-subdivision-v1-20261017';BATCH='government-xl-orchards-four-world-corner-boundary-v1-20261017';DOC=BASE/BATCH;T='landsd/254629:0';P='landsd/233002:0'
def main():
 assert not DOC.exists();refs=[Path(__file__)]
 for folder in [CAP,EDGE,SPLIT]:
  r=read(folder/'result.json')
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  refs.append(folder/'result.json')
  for e in r['evidenceRefs']:assert digest((ROOT/e['path']).read_bytes())==e['sha256'];refs.append(ROOT/e['path'])
 worlds={m:{u:np.asarray(t,float)for u,t in w.items()}for m,w in read(CAP/'world-triangles.json.gz').items()};edges=read(EDGE/'edges.json.gz');hostids=edges['horizontalHostOriginalFaceIDs'];bindings=[]
 for e in edges['rows']:
  matches=[(f,a,b)for f in e['sourceFaces']for a in range(3)for b in range(3)if a!=b and np.array_equal(worlds['original'][T][f,[a,b]],e['segment'])];assert matches;bindings.append(matches[0])
 results=[]
 for mode,w in worlds.items():
  host=w[P][hostids]
  for i,(f,a,b)in enumerate(bindings):
   segment=w[T][f,[a,b]];proof=verify(segment,host);parts=[]
   if not proof['verifiedCompleteOriginalEdgeFiniteFacadeBand']:
    va,vb=[[F(float(v))for v in p]for p in segment]
    for k in range(8):
     exact=[[va[j]+(vb[j]-va[j])*F(n,8)for j in range(3)]for n in [k,k+1]];s=np.asarray([[float(v)for v in p]for p in exact]);assert all(F(float(s[n,j]))==exact[n][j]for n in range(2)for j in range(3));parts.append(dict(interval=[str(F(k,8)),str(F(k+1,8))],proof=verify(s,host)))
   passed=proof['verifiedCompleteOriginalEdgeFiniteFacadeBand']or bool(parts)and all(p['proof']['verifiedCompleteOriginalEdgeFiniteFacadeBand']for p in parts);results.append(dict(mode=mode,edge=i,sourceFace=f,vertexSlots=[a,b],segment=segment.tolist(),complete=passed,wholeProof=proof,subdivision=parts));print(dict(mode=mode,edge=i,passed=passed),flush=True)
 save(DOC/'proofs.json.gz',dict(rows=results,horizontalOriginalHostFaceIDs=hostids,allModesComplete=all(r['complete']for r in results),fixedBandM=.1,fullAcceptance=False))
 refs.extend([HERE/'exact_original_edge_any_finite_distance_band_v1_20261010.py',HERE/'exact_original_perpendicular_any_facet_band_v1_20261010.py'])
 out=module('orchards_corner_modes_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'orchards-complete-original-corner-horizontal-band-all-render-modes-v1',list(set(refs)),dict(uids=[T,P],allModesComplete=all(r['complete']for r in results),fullAcceptance=False,nextStep='Review exact same-source boundary detail with preserved raw contact failure; podium identity and complete original-terrain assembly remain required.'));print(out['jobId'])
if __name__=='__main__':main()
