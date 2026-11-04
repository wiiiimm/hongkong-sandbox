"""Attribute existing exact interval certificates to original host surfaces."""
from pathlib import Path
from fractions import Fraction as F
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BASE=ROOT/'docs/astra-city/government-import';BATCH='government-xl-oi-sin-certified-host-roles-v1-20261017';DOC=BASE/BATCH
EDGE=BASE/'government-xl-oi-sin-original-edges-v1-20261017';SUB=BASE/'government-xl-oi-sin-complete-edge-subdivision-v1-20261017';CONTEXT=BASE/'government-xl-oi-sin-interface-role-views-v1-20261017';PHYSICAL=BASE/'government-xl-oi-sin-four-originals-physical-v1-20261017'
def union(intervals):
 out=[]
 for a,b in sorted(intervals):
  if out and a<=out[-1][1]:out[-1]=(out[-1][0],max(b,out[-1][1]))
  else:out.append((a,b))
 return out
def main():
 assert not DOC.exists(); required=[EDGE/'edges.json.gz',SUB/'subdivision.json.gz',PHYSICAL/'selection.json.gz'];pins={};receipts=[]
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in [EDGE,SUB,CONTEXT]:
   r=read(folder/'result.json');receipts.append(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
   for e in r['evidenceRefs']:
    if ROOT/e['path'] in required:
     assert e['path'] not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p in required:assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))]
 source=next(r for r in read(PHYSICAL/'selection.json.gz')['rows']if r['uid']=='landsd/91128:0');asset=ROOT/source['candidate']['path'];assert digest(asset.read_bytes())==source['sourceSHA256'];host=decode_original_world_triangles(asset.read_bytes());assert len(host)==7849
 edges=read(EDGE/'edges.json.gz')['rows'];subs=read(SUB/'subdivision.json.gz');assert not subs['summary']['stillUnprovedEdges'];sub={r['edge']:r for r in subs['rows']};output=[];faces={}
 for index,edge in enumerate(edges):
  proofs=[(F(0),F(1),edge['proof'])] if edge['proof']['verifiedCompleteOriginalEdgeFiniteFacadeBand'] else [(F(r['parameterInterval'][0]),F(r['parameterInterval'][1]),r['proof'])for r in sub[index]['intervals']]
  groups={k:[]for k in ['all','horizontal','vertical','sloping']};records=[]
  for start,end,proof in proofs:
   assert proof['verifiedCompleteOriginalEdgeFiniteFacadeBand'] and proof['completeOriginalFacetCount']==len(host)
   for field,intervalkey in [('allFiniteOriginalFacetIntervals','exactProjectedFootCoverageInterval'),('exactFiniteOriginalEdgeIntervals','exactCoverageInterval')]:
    for r in proof[field]:
     if not r['entireIntervalWithinFixedBand']:continue
     face=r['originalSurfaceFace'];t=host[face];v=[[F(float(x)) for x in p]for p in t];u=[v[1][j]-v[0][j]for j in range(3)];w=[v[2][j]-v[0][j]for j in range(3)];n=[u[1]*w[2]-u[2]*w[1],u[2]*w[0]-u[0]*w[2],u[0]*w[1]-u[1]*w[0]];assert any(n)
     role='horizontal' if n[0]==n[2]==0 else 'vertical' if n[1]==0 else 'sloping'
     a,b=[start+(end-start)*F(x)for x in r[intervalkey]];assert 0<=a<=b<=1;groups['all'].append((a,b));groups[role].append((a,b))
     faces[face]=dict(face=face,role=role,vertices=t.tolist(),exactNormal=[str(x)for x in n],heightRange=[float(t[:,1].min()),float(t[:,1].max())]);records.append(dict(face=face,role=role,route=field,interval=[str(a),str(b)]))
  merged={k:union(v)for k,v in groups.items()};assert merged['all']==[(F(0),F(1))]
  output.append(dict(edge=index,segment=edge['segment'],sourceFaces=edge['sourceFaces'],completeHorizontalSurfaceBand=merged['horizontal']==[(F(0),F(1))],completeVerticalSurfaceBand=merged['vertical']==[(F(0),F(1))],coverage={k:[[str(a),str(b)]for a,b in v]for k,v in merged.items()},certificates=records))
 summary=dict(affectedEdges=len(edges),completeHorizontalSurfaceBand=sum(r['completeHorizontalSurfaceBand']for r in output),notCompletelyHorizontal=[r['edge']for r in output if not r['completeHorizontalSurfaceBand']],completeVerticalSurfaceBand=sum(r['completeVerticalSurfaceBand']for r in output),hostFacesByRole={role:sum(r['role']==role for r in faces.values())for role in ['horizontal','vertical','sloping']},fullAcceptance=False,sourceGeometryChanges=0,qualification='Exact original normal classification and exact unions reuse prior certificates. Horizontal proximity remains evidence, not canonical vertical contact or installation acceptance.')
 save(DOC/'roles.json.gz',dict(summary=summary,rows=output,hostFaces=list(faces.values()),hostSHA256=source['sourceSHA256']))
 refs=[Path(__file__),*required,*receipts,asset,HERE/'exact_packed_world_geometry_20261009.py']
 result=module('oi_host_role_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'oi-sin-certified-original-host-role-attribution-v1',refs,dict(uids=['landsd/256280:0','landsd/91128:0'],summary=summary,nextStep='Use exact host-role attribution to distinguish complete horizontal support-edge proximity from wall-only intervals; retain current canonical failures.'))
 print(dict(jobId=result['jobId'],summary=summary),flush=True)
if __name__=='__main__':main()
