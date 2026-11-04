"""Complete Lee Kong independent original bodies against authenticated source TIN.

Source-only ordinary ground candidates and exact same-actor attachment paths.
No current terrain/identity/foreign/runtime or installation acceptance. Every
nonrendering source face stays separately inventoried, uncredited as graph glue.
"""
from fractions import Fraction
import importlib.util,json
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_shared_edge_component_census_v2_20261011 import census
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts
from original_wall_rim_accounting_20261009 import original_samples
from original_ordinary_rim_accounting_20261009 import verify as ordinary_rim
BATCH='government-xl-lee-kong-two-independent-original-tin-body-graph-diagnostic-v1-20261011'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
INPUT=DOC.parent/'government-xl-lee-kong-four-original-source-recovery-v1-20261011'
FINITE=DOC.parent/'xl-terrain-recovery-20261011-lee-kong-two-independent-original-authentic-tin-finite-v1'
GROUND=HERE/'local'/FINITE.name/'complete-authentic-source-tin-ground.json.gz'
def height(point,ground):
 x,z=map(Fraction.from_float,map(float,(point[0],point[2])));values=[]
 keep=(ground[:,:,0].max(1)>=float(x))&(ground[:,:,0].min(1)<=float(x))&(ground[:,:,2].max(1)>=float(z))&(ground[:,:,2].min(1)<=float(z))
 for f in ground[keep]:
  a,b,c=[[Fraction.from_float(float(v))for v in p]for p in f]
  den=(b[2]-c[2])*(a[0]-c[0])+(c[0]-b[0])*(a[2]-c[2])
  if not den:continue
  u=((b[2]-c[2])*(x-c[0])+(c[0]-b[0])*(z-c[2]))/den
  v=((c[2]-a[2])*(x-c[0])+(a[0]-c[0])*(z-c[2]))/den;w=1-u-v
  if min(u,v,w)>=0:values.append(u*a[1]+v*b[1]+w*c[1])
 assert values,'Missing exact original source-TIN facet at complete component sample'
 return float(max(values))
def main():
 assert not DOC.exists();receipt=read(FINITE/'result.json')
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
 frozen=read(FINITE/'diagnostic.json.gz');g=read(GROUND);ground=np.asarray(g['completeSelectedFacets'],dtype='<f8')
 assert digest(ground.tobytes())==g['completeSelectedFacetSHA256'] and len(ground)==67
 selection=read(INPUT/'selection.json.gz');rows={r['uid']:r for r in selection['rows']};outrows=[]
 refs=[Path(__file__),GROUND,INPUT/'selection.json.gz',FINITE/'result.json',FINITE/'diagnostic.json.gz']
 for uid in ['landsd/145527:0','landsd/147956:0']:
  row=rows[uid];asset=ROOT/row['candidate']['path'];raw=asset.read_bytes();assert digest(raw)==row['sourceSHA256'];refs.append(asset)
  tri=decode_original_world_triangles(raw);topology=census(tri,list(range(len(tri))));assert topology==frozen['completeOriginalNonzeroEdgeBodyCensus'][uid]
  groups=topology['sharedEdgeConnectedComponents'];parts=[];contacts=[];adj={i:set()for i in range(len(groups))};roots=[]
  for k,faces in enumerate(groups):
   part=tri[faces];position,inverse=np.unique(part.reshape(-1,3),axis=0,return_inverse=True);index=inverse.reshape(-1,3)
   assert np.array_equal(position[index],part);bottom=float(position[:,1].min());samples=original_samples(position,index,bottom);missing=[]
   for j,sample in enumerate(samples):
    try:sample['ground']=height(sample['point'],ground);sample['gap']=sample['point'][1]-sample['ground']
    except AssertionError as error:missing.append(dict(sample=j,reason=str(error)))
   proof=None;reason=None;metric=None
   if missing:reason='missing-complete-component-source-TIN-samples'
   else:
    low=[s for s in samples if s['point'][1]<=bottom+.35]
    metric=dict(checks=len(samples),lowRimChecks=len(low),minSurfaceGap=min(s['gap']for s in samples),minLowGap=min(s['gap']for s in low),maxLowGap=max(s['gap']for s in low))
    try:proof=ordinary_rim(position,index,bottom,samples,expected_metric=metric);roots.append(k)
    except AssertionError as error:reason=str(error)
   parts.append(dict(component=k,completeOriginalFaceIds=faces,completeOriginalComponentWorldSHA256=digest(part.tobytes()),bottomHKPD=bottom,completeSamples=samples,missingSamples=missing,ordinaryMetric=metric,ordinarySourceTINRootCandidate=proof,rawOrdinaryFailure=reason,currentGroundRootAccepted=False))
  for a in range(len(groups)):
   pa=tri[groups[a]];lo,hi=pa.min((0,1)),pa.max((0,1))
   for b in range(a+1,len(groups)):
    pb=tri[groups[b]]
    if np.any(hi<pb.min((0,1)))or np.any(pb.max((0,1))<lo):
     contacts.append(dict(components=[a,b],completeFinitePairProvedDisjointByClosed3DBounds=True));continue
    proof=exact_finite_contacts(tri,groups[a],tri,groups[b]);assert proof['allPairsExamined']
    positive=[r for r in proof['contacts']if r['dimension']>0 and r['sourcePrimitiveDimensionA']==r['sourcePrimitiveDimensionB']==2]
    if positive:adj[a].add(b);adj[b].add(a)
    contacts.append(dict(components=[a,b],completeFinitePair=proof,positiveAreaFacetContacts=positive))
  reached=set(roots);todo=list(roots);parents={i:None for i in roots}
  while todo:
   a=todo.pop()
   for b in sorted(adj[a]):
    if b not in reached:reached.add(b);parents[b]=a;todo.append(b)
  outrows.append(dict(uid=uid,sourceSHA256=row['sourceSHA256'],completeWorldSHA256=digest(tri.tobytes()),completeOriginalFaces=len(tri),completeOriginalTopology=topology,components=parts,completeComponentPairContacts=contacts,ordinarySourceTINRootCandidates=roots,sourceTINReachableRealComponents=sorted(reached),sourceTINAttachmentParents=parents,unresolvedRealComponents=sorted(set(adj)-reached),allOriginalNonrenderingFacesUncredited=topology['exactNonrenderingOriginalFaces'],currentRootOrSupportAccepted=False))
  print(json.dumps(dict(uid=uid,rootCandidates=roots,reached=sorted(reached),unresolved=sorted(set(adj)-reached))),flush=True)
 out=dict(rows=outrows,completeGround=GROUND.relative_to(ROOT).as_posix(),completeGroundSHA256=digest(GROUND.read_bytes()),sourceOnly=True,currentTerrain=False,identityAccepted=False,physicalAccepted=False,structuralSupportAccepted=False,installationApproved=False,sourceGeometryChanges=0,qualification='Exact source-TIN ordinary roots and complete same-actor nonzero-area component contact paths are candidates only. Every complete original face and genuine raw failure is retained; no cross-actor root, ownership, current renderer, identity, foundation, foreign collision or installation credit.')
 save(DOC/'diagnostic.json.gz',out)
 for name in ['exact_packed_world_geometry_20261009.py','exact_original_shared_edge_component_census_v2_20261011.py','exact_original_finite_triangle_contacts_20261010.py','original_wall_rim_accounting_20261009.py','original_ordinary_rim_accounting_20261009.py']:
  refs.append(HERE/name)
 spec=importlib.util.spec_from_file_location('lee_source_tin_graph_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 m.freeze(BATCH,'complete-lee-kong-independent-original-source-tin-body-ground-contact-diagnostic-v1',refs,dict(uids=[r['uid']for r in outrows],sourceOnly=True,completeOriginalFaces=1253,currentRootOrSupportAccepted=False,unresolvedByUID={r['uid']:r['unresolvedRealComponents']for r in outrows},installationApproved=False,newlyInstalled=0))
if __name__=='__main__':main()
