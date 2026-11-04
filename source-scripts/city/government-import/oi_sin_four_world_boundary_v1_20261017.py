"""Complete original Oi Sin boundary bands in distinct renderer coordinate modes."""
from pathlib import Path
from fractions import Fraction as F
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_original_edge_any_finite_distance_band_v1_20261010 import verify
BASE=ROOT/'docs/astra-city/government-import';CAP=BASE/'government-xl-oi-sin-four-world-capture-v1-20261017';ROLE=BASE/'government-xl-oi-sin-certified-host-roles-v1-20261017';EDGE=BASE/'government-xl-oi-sin-original-edges-v1-20261017'
BATCH='government-xl-oi-sin-four-world-boundary-v1-20261017';DOC=BASE/BATCH;T='landsd/256280:0';P='landsd/91128:0'
def main():
 assert not DOC.exists();refs=[Path(__file__)];pins={}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in [CAP,ROLE]:
   r=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
   for e in r['evidenceRefs']:
    assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p;refs.append(ROOT/p)
 worlds={mode:{u:np.asarray(t,float)for u,t in w.items()}for mode,w in read(CAP/'world-triangles.json.gz').items()};old=read(EDGE/'edges.json.gz')['rows'];roles=read(ROLE/'roles.json.gz');assert roles['summary']['completeHorizontalSurfaceBand']==len(old)==92
 bindings=[]
 for e in old:
  segment=np.asarray(e['segment']);found=[]
  for i in e['sourceFaces']:
   for a in range(3):
    for b in range(3):
     if a!=b and np.array_equal(worlds['original'][T][i,[a,b]],segment):found.append((i,a,b))
  assert found;bindings.append(found[0])
 DOC.mkdir();save(DOC/'edge-bindings.json',dict(rows=[dict(edge=i,sourceFace=f,vertexSlots=[a,b])for i,(f,a,b)in enumerate(bindings)]));results={};seen={}
 for mode,w in worlds.items():
  key=(digest(w[T].tobytes()),digest(w[P].tobytes()))
  if key in seen:results[mode]=dict(reusedMode=seen[key],complete=results[seen[key]]['complete']);continue
  seen[key]=mode
  if mode=='original':results[mode]=dict(complete=True,reusedCertificate=str((ROLE/'roles.json.gz').relative_to(ROOT)),edges=92);continue
  host=w[P];ids=np.flatnonzero(np.all(host[:,:,1]==host[:,0,1,None],axis=1));horizontal=host[ids];rows=[]
  for i,(face,a,b)in enumerate(bindings):
   segment=w[T][face,[a,b]];proof=verify(segment,horizontal);pieces=[]
   if not proof['verifiedCompleteOriginalEdgeFiniteFacadeBand']:
    va,vb=[[F(float(v))for v in x]for x in segment]
    for k in range(8):
     exact=[[va[j]+(vb[j]-va[j])*F(t,8)for j in range(3)]for t in [k,k+1]];s=np.asarray([[float(x)for x in p]for p in exact]);assert all(F(float(s[n,j]))==exact[n][j]for n in range(2)for j in range(3));pr=verify(s,horizontal);pieces.append(dict(parameterInterval=[str(F(k,8)),str(F(k+1,8))],proof=pr))
   complete=proof['verifiedCompleteOriginalEdgeFiniteFacadeBand']or all(x['proof']['verifiedCompleteOriginalEdgeFiniteFacadeBand']for x in pieces)
   rows.append(dict(edge=i,segment=segment.tolist(),complete=complete,wholeProof=proof,pieces=pieces));print(dict(mode=mode,edge=i,complete=complete),flush=True)
  results[mode]=dict(complete=all(x['complete']for x in rows),edges=len(rows),unproved=[x['edge']for x in rows if not x['complete']]);save(DOC/(mode+'-proofs.json.gz'),dict(rows=rows,horizontalSubsetOriginalFaceIds=ids.tolist(),sourceWorldSHA256=key[0],hostWorldSHA256=key[1]))
 save(DOC/'summary.json',dict(modes=results,allModesComplete=all(x['complete']for x in results.values()),geometryChanges=0,fullAcceptance=False))
 refs.extend([HERE/'exact_original_edge_any_finite_distance_band_v1_20261010.py',HERE/'exact_original_perpendicular_any_facet_band_v1_20261010.py'])
 out=module('oi_boundary_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'oi-sin-complete-horizontal-boundary-four-worlds-v1',list(set(refs)),dict(uids=[T,P],modes=results,fullAcceptance=False,nextStep='Qualify exact authored boundary role; retain raw contact failures, fresh foundations and compound identity. Complete current neighbours and browser checks remain.'));print(out['jobId'],flush=True)
if __name__=='__main__':main()
