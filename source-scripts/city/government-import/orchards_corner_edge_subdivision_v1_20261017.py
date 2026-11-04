"""Certify whole original edges using exact dyadic parameter subdivision only."""
from fractions import Fraction as F
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_original_edge_any_finite_distance_band_v1_20261010 import verify
BASE=ROOT/'docs/astra-city/government-import';PRIOR=BASE/'government-xl-orchards-original-corner-edges-v1-20261017';OLD=BASE/'government-xl-orchards-original-podium-support-v1-20261017'
BATCH='government-xl-orchards-corner-edge-subdivision-v1-20261017';DOC=BASE/BATCH
UID='landsd/254629:0';SUPPORT='landsd/233002:0'
def main():
 assert not DOC.exists();r=read(PRIOR/'result.json')
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 for ref in r['evidenceRefs']:assert digest((ROOT/ref['path']).read_bytes())==ref['sha256']
 from exact_packed_world_geometry_20261009 import decode_original_world_triangles
 source=next(x for x in read(OLD/'support-inputs.json')['sources']if x['uid']==SUPPORT);tri=decode_original_world_triangles((ROOT/source['candidate']['path']).read_bytes());tri=tri[read(PRIOR/'edges.json.gz')['horizontalHostOriginalFaceIDs']];rows=read(PRIOR/'edges.json.gz')['rows'];results=[]
 for n,e in enumerate(rows):
  if e['proof']['verifiedCompleteOriginalEdgeFiniteFacadeBand']:continue
  a,b=[tuple(F(float(v))for v in p)for p in e['segment']];intervals=[]
  for k in range(8):
   exact=[tuple(a[j]+(b[j]-a[j])*F(t,8)for j in range(3))for t in [k,k+1]];segment=np.array([[float(v)for v in p]for p in exact])
   assert all(F(float(segment[i,j]))==exact[i][j]for i in range(2)for j in range(3)), 'Subdivision endpoint cannot be represented exactly'
   proof=verify(segment,tri);intervals.append(dict(parameterInterval=[str(F(k,8)),str(F(k+1,8))],exactEndpoints=[[str(v)for v in p]for p in exact],proof=proof))
  passed=all(x['proof']['verifiedCompleteOriginalEdgeFiniteFacadeBand']for x in intervals);results.append(dict(edge=n,sourceFaces=e['sourceFaces'],complete=passed,intervals=intervals));print(dict(edge=n,complete=passed),flush=True)
 summary=dict(affectedWholeEdges=len(rows),previouslyCertifiedEdges=len(rows)-len(results),additionalCompleteEdges=sum(x['complete']for x in results),stillUnprovedEdges=[x['edge']for x in results if not x['complete']],fixedBandM=.1,geometryEdits=0,fullAcceptance=False,qualification='Exact parameter subdivision of the same original edge, with every subinterval certified against complete original podium surfaces. No geometry tessellation, coordinate changes, contact acceptance or installation approval.')
 save(DOC/'subdivision.json.gz',dict(summary=summary,rows=results));refs=[Path(__file__),PRIOR/'result.json',PRIOR/'edges.json.gz',OLD/'support-inputs.json',ROOT/source['candidate']['path'],HERE/'xl-second-pass.py',HERE/'exact_original_edge_any_finite_distance_band_v1_20261010.py',HERE/'exact_original_perpendicular_any_facet_band_v1_20261010.py']
 out=module('oi_sin_split_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'orchards-whole-corner-edge-horizontal-exact-subdivision-v1',refs,dict(uids=[UID,SUPPORT],summary=summary,nextStep='Review the now bounded original seam against actual source roles and canonical physical gates; distance proof alone grants no support acceptance.'))
 print(dict(jobId=out['jobId'],summary=summary),flush=True)
if __name__=='__main__':main()
