"""Partition the same source facet analytically; never alter model geometry."""
from fractions import Fraction as F
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_original_facet_orthogonal_finite_host_band_diagnostic_v1_20261011 import verify as orthogonal
from exact_original_facet_piecewise_finite_host_edge_band_diagnostic_v1_20261011 import verify as edge
BASE=ROOT/'docs/astra-city/government-import';PRIOR=BASE/'government-xl-aqua272788-complete-conflict-facets-v1-20261017';BATCH='government-xl-aqua272788-facet32-subdivision-v1-20261017';DOC=BASE/BATCH

def main():
 assert not DOC.exists();r=read(PRIOR/'result.json')
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 pins={e['path']:e['sha256']for e in r['evidenceRefs']}
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 rt=HERE/'local/government-xl-aqua272788-current-pair-v1-20261017/runtime-geometry.json.gz';g=next(g for g in read(rt)['rows']if g['uid']=='landsd/193086:0');host=np.asarray(g['position'],float).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)]
 prior=read(PRIOR/'association.json.gz');face=next(x for x in prior['rows']if x['sourceFace']==32);assert not face['wholeFacetAssociated'];original=[[F(float(v))for v in p]for p in face['sourceVertices']];nodes=[]
 def visit(t,depth):
  index=len(nodes);node=dict(id=index,depth=depth,exactVertices=[[str(v)for v in p]for p in t]);nodes.append(node)
  a=np.array([[float(v)for v in p]for p in t]);exact=all(F(float(a[i,j]))==t[i][j]for i in range(3)for j in range(3));node['floatInputExactlyRepresentable']=exact
  if not exact:node['complete']=False;node['reason']='Exact subdivision cannot be represented by existing float-input verifier';return index,False
  o=orthogonal(a,host);e=None if o['wholeFacetAssociated']else edge(a,host);passed=o['wholeFacetAssociated']or bool(e and e['wholeFacetFiniteEdgeUnionAssociated']);node.update(orthogonalProof=o,edgeProof=e,complete=passed)
  if passed or depth==4:return index,passed
  x,y,z=t;xy=[(x[j]+y[j])/2 for j in range(3)];yz=[(y[j]+z[j])/2 for j in range(3)];zx=[(z[j]+x[j])/2 for j in range(3)]
  children=[visit(child,depth+1)for child in [[x,xy,zx],[xy,y,yz],[zx,yz,z],[xy,yz,zx]]];node['children']=[i for i,_ in children];node['complete']=all(ok for _,ok in children);return index,node['complete']
 _,passed=visit(original,0);save(DOC/'proof-tree.json.gz',dict(sourceFace=32,nodes=nodes,complete=passed,sourceGeometryChanges=0,subdivisionIsAnalyticOnly=True,qualification='Four exact midpoint subtriangles partition each original triangle completely. Only exact-representable verifier inputs are evaluated; all leaf interiors must pass unchanged 0.1m finite-host band. No model remeshing or placement approval.'))
 refs=[Path(__file__),PRIOR/'result.json',*[ROOT/p for p in pins]]
 out=module('aqua_subdivision_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'aqua272788-complete-facet32-exact-midpoint-partition-v1',refs,dict(uids=['landsd/272788:0'],sourceFace=32,completeFacetAssociated=passed,proofNodes=len(nodes),fullAcceptance=False,nextStep='Inspect exact source-junction role and retain original physical failures; this source association alone is not installation approval.'))
 print(dict(jobId=out['jobId'],complete=passed,nodes=len(nodes)),flush=True)
if __name__=='__main__':main()
