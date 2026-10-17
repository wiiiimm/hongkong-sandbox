"""Refine only three uncertified literal-edge intervals; no source geometry edits."""
from pathlib import Path
from fractions import Fraction as F
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_original_edge_any_finite_distance_band_v1_20261010 import verify
BASE=ROOT/'docs/astra-city/government-import';OLD=BASE/'government-xl-oi-sin-four-world-boundary-v1-20261017';CAP=BASE/'government-xl-oi-sin-four-world-capture-v1-20261017';BATCH='government-xl-oi-sin-literal-boundary-refinement-v2-20261017';DOC=BASE/BATCH

def main():
 assert not DOC.exists();r=read(OLD/'result.json');pins={e['path']:e['sha256']for e in r['evidenceRefs']}
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 old=read(OLD/'literal-proofs.json.gz');summary=read(OLD/'summary.json');assert summary['modes']['literal']['unproved']==[15,19,77]
 host=np.asarray(read(CAP/'world-triangles.json.gz')['literal']['landsd/91128:0'],float);ids=old['horizontalSubsetOriginalFaceIds'];horizontal=host[ids];rows=[]
 for row in old['rows']:
  if row['complete']:continue
  a,b=[[F(float(v))for v in p]for p in row['segment']];nodes=[];pending=[]
  for piece in row['pieces']:
   l,r=map(F,piece['parameterInterval']);n=dict(interval=[str(l),str(r)],depth=3,reusedPriorPiece=True,proof=piece['proof'],complete=piece['proof']['verifiedCompleteOriginalEdgeFiniteFacadeBand']);nodes.append(n)
   if not n['complete']:pending.append(len(nodes)-1)
  while pending:
   index=pending.pop();n=nodes[index];l,r=map(F,n['interval'])
   if n['depth']>=7:continue
   mid=(l+r)/2;n['children']=[]
   for lo,hi in [(l,mid),(mid,r)]:
    exact=[[a[j]+(b[j]-a[j])*t for j in range(3)]for t in [lo,hi]];s=np.asarray([[float(x)for x in p]for p in exact]);assert all(F(float(s[i,j]))==exact[i][j]for i in range(2)for j in range(3));proof=verify(s,horizontal);child=dict(interval=[str(lo),str(hi)],depth=n['depth']+1,proof=proof,complete=proof['verifiedCompleteOriginalEdgeFiniteFacadeBand']);n['children'].append(len(nodes));nodes.append(child)
    if not child['complete']:pending.append(len(nodes)-1)
  unresolved=[i for i,n in enumerate(nodes)if not n.get('children')and not n['complete']];rows.append(dict(edge=row['edge'],complete=not unresolved,nodes=nodes,unprovedLeaves=unresolved));print(dict(edge=row['edge'],nodes=len(nodes),unprovedLeaves=unresolved),flush=True)
 literal=all(r['complete']for r in rows);resultSummary=dict(previouslyCertifiedLiteralEdges=89,refinedEdges=[r['edge']for r in rows],completeLiteralEdges=89+sum(r['complete']for r in rows),allModesComplete=literal and all(v['complete']for k,v in summary['modes'].items()if k!='literal'),geometryChanges=0,fullAcceptance=False)
 save(DOC/'refinement.json.gz',dict(summary=resultSummary,rows=rows,horizontalSubsetOriginalFaceIds=ids));refs=[Path(__file__),OLD/'result.json',*[ROOT/p for p in pins],HERE/'exact_original_edge_any_finite_distance_band_v1_20261010.py',HERE/'exact_original_perpendicular_any_facet_band_v1_20261010.py']
 out=module('oi_refinement_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'oi-sin-three-literal-original-interval-refinement-v2',refs,dict(uids=['landsd/256280:0','landsd/91128:0'],summary=resultSummary,nextStep='Only if complete, continue foundation and exact-source role checks. Unproved bounded intervals are not evidence of a real gap.'));print(out['jobId'],flush=True)
if __name__=='__main__':main()
