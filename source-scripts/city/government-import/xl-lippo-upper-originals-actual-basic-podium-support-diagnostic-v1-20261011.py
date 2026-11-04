"""Exact upper-original/current-BASIC body contacts and genuine body rooting.
No absent government podium geometry participates in support or graph edges.
"""
from pathlib import Path
from fractions import Fraction
import importlib.util,json
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_shared_edge_component_census_v2_20261011 import census
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts
from exact_original_shell_intersections_20261009 import rational_face,intersection_points
from original_ordinary_rim_accounting_20261009 import verify as ordinary_rim
from original_wall_rim_accounting_20261009 import original_samples
BATCH='government-xl-lippo-upper-originals-actual-basic-podium-support-diagnostic-v1-20261011';DOC=ROOT/'docs/astra-city/government-import'/BATCH
INPUT=DOC.parent/'government-xl-lippo-current-basic-podium-support-inputs-v1-20261011'
GRAPH=DOC.parent/'government-xl-lippo-three-complete-original-edge-components-and-contacts-v1-20261011'
PHYS=DOC.parent/'government-xl-lippo-two-original-disjoint-current-parent-physical-v3-20261011'
RUNTIME=HERE/'local'/PHYS.name/'runtime-geometry.json.gz'
def main():
 assert not DOC.exists();inputs=read(INPUT/'input.json.gz');body=read(INPUT/'complete-current-basic-podium-geometry.json.gz');assert body['uid']=='landsd/231645:0' and not body['originalGovernmentPodiumUsedAsSupport']
 for path,pin in body['inputHashes'].items():assert digest((ROOT/path).read_bytes())==pin
 rawbody=body['completeCurrentRendererBody'];p=np.asarray(rawbody['position'],dtype='<f8').reshape(-1,3);idx=np.asarray(rawbody['index'],dtype=np.int64).reshape(-1,3);assert np.array_equal(p,p.astype('<f4').astype('<f8'));basic=p[idx]
 bc=census(basic,list(range(len(basic))));basic_groups=bc['sharedEdgeConnectedComponents'];assert sorted(f for g in basic_groups for f in g)==bc['completeRenderableFaceIds']
 ground=np.concatenate([np.asarray(r['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3) for r in read(RUNTIME)['rows']]);assert np.isfinite(ground).all()
 polygons=shapely.polygons(ground[:,:,[0,2]]);valid=shapely.area(polygons)>0;faces=ground[valid];tree=shapely.STRtree(polygons[valid]);rational={}
 def height(x,z):
  qx,qz=Fraction(float(x)),Fraction(float(z));values=[]
  for k in tree.query(shapely.Point(x,z)):
   k=int(k)
   if k not in rational:rational[k]=[[Fraction(float(v)) for v in p] for p in faces[k]]
   a,b,c=rational[k];den=(b[2]-c[2])*(a[0]-c[0])+(c[0]-b[0])*(a[2]-c[2])
   if not den:continue
   u=((b[2]-c[2])*(qx-c[0])+(c[0]-b[0])*(qz-c[2]))/den;v=((c[2]-a[2])*(qx-c[0])+(a[0]-c[0])*(qz-c[2]))/den;w=1-u-v
   if min(u,v,w)>=0:values.append(u*a[1]+v*b[1]+w*c[1])
  assert values,'Missing exact candidate drawn ground at actual BASIC sample'
  return float(max(values))
 roots=[];rootproofs=[]
 for k,ids in enumerate(basic_groups):
  vids=sorted(set(idx[ids].reshape(-1).tolist()));mapping={v:i for i,v in enumerate(vids)};cp=p[vids];ci=np.asarray([[mapping[int(v)] for v in f] for f in idx[ids]],dtype=np.uint32);bottom=float(cp[:,1].min());samples=original_samples(cp,ci,bottom)
  try:
   for sample in samples:
    g=height(sample['point'][0],sample['point'][2]);sample.update(ground=g,gap=sample['point'][1]-g)
   low=[r for r in samples if r['point'][1]<=bottom+.35]
   metric=dict(checks=len(samples),lowRimChecks=len(low),minSurfaceGap=min(r['gap'] for r in samples),minLowGap=min(r['gap'] for r in low),maxLowGap=max(r['gap'] for r in low))
   proof=dict(accepted=True,ordinaryRim=ordinary_rim(cp,ci,bottom,samples,expected_metric=metric),metric=metric);roots.append(k)
  except AssertionError as error:proof=dict(accepted=False,reason=str(error))
  rootproofs.append(dict(**proof,basicComponent=k,completeBasicFaceIDs=ids,completeSamples=samples))
  print(json.dumps(dict(basicComponent=k,genuineOrdinaryRoot=proof['accepted'],reason=proof.get('reason'))),flush=True)
 graph=read(GRAPH/'diagnostic.json.gz');whole=[];assets=[];actor_ranges={};cursor=0
 for row in sorted(inputs['rows'],key=lambda r:r['uid']):
  path=ROOT/row['candidate']['path'];raw=path.read_bytes();assert digest(raw)==row['sourceSHA256'];tri=decode_original_world_triangles(raw);assert len(tri)==row['triangles'];assets.append(path);actor_ranges[row['uid']]=[cursor,cursor+len(tri)];whole.append(tri);cursor+=len(tri)
 whole=np.concatenate(whole);assert len(whole)==13119;actors={a['uid']:a for a in graph['actors']};nodes=[]
 for node in graph['nodes']:
  if node['uid'] not in actor_ranges:continue
  oldstart=actors[node['uid']]['globalOriginalFaceRange'][0];newstart=actor_ranges[node['uid']][0];ids=[f-oldstart+newstart for f in node['globalOriginalFaces']]
  nodes.append(dict(component=len(nodes),previousThreeSourceComponent=node['component'],uid=node['uid'],completeOwnedSourceFaceIDs=[f-oldstart for f in node['globalOriginalFaces']],globalUpperSourceFaceIDs=ids))
 assert len(nodes)==10
 for uid,(lo,hi) in actor_ranges.items():
  c=census(whole,list(range(lo,hi)));assert c['sharedEdgeConnectedComponents']==[n['globalUpperSourceFaceIDs'] for n in nodes if n['uid']==uid]
 pairs=[];direct=[]
 for n in nodes:
  for k,ids in enumerate(basic_groups):
   contact=exact_finite_contacts(whole,n['globalUpperSourceFaceIDs'],basic,ids);assert contact['allPairsExamined']
   positive=[v for v in contact['contacts'] if v['dimension']>0 and v['sourcePrimitiveDimensionA']==v['sourcePrimitiveDimensionB']==2]
   pairs.append(dict(upperComponent=n['component'],actualBasicComponent=k,completeFiniteContactProof=contact,positiveRealFacetInterfaces=positive))
   if positive and k in roots:direct.append(n['component'])
  save(DOC/'contact-progress.json.gz',dict(nodes=nodes,pairs=pairs))
  print(json.dumps(dict(upperComponent=n['component'],uid=n['uid'],positiveContactToGenuinelyRootedActualBasic=n['component'] in direct)),flush=True)
 previous_to_new={n['previousThreeSourceComponent']:n['component'] for n in nodes};membership={f:n['component'] for n in nodes for f in n['globalUpperSourceFaceIDs']};adj={n['component']:set() for n in nodes};internal=[]
 for pair in graph['completePairRecords']:
  oa,ob=pair['components']
  if oa not in previous_to_new or ob not in previous_to_new or not pair['positiveDimensionInterface']:continue
  olda,oldb=graph['nodes'][oa],graph['nodes'][ob];ca=pair['positiveAreaFacetInterfaces'][0];fa=ca['sourceFaceA']-actors[olda['uid']]['globalOriginalFaceRange'][0]+actor_ranges[olda['uid']][0];fb=ca['sourceFaceB']-actors[oldb['uid']]['globalOriginalFaceRange'][0]+actor_ranges[oldb['uid']][0];a,b=previous_to_new[oa],previous_to_new[ob]
  assert membership[fa]==a and membership[fb]==b;points=intersection_points(rational_face(whole[fa]),rational_face(whole[fb]));assert len(points)>=2
  adj[a].add(b);adj[b].add(a);internal.append(dict(components=[a,b],globalUpperSourceFaceIDs=[fa,fb],exactContactPoints=[[str(v) for v in p] for p in sorted(points)]))
 reached=set(direct);todo=list(direct)
 while todo:
  for b in sorted(adj[todo.pop()]):
   if b not in reached:reached.add(b);todo.append(b)
 result=dict(actualBasicUID=body['uid'],completeActualBasicFaces=len(basic),actualBasicWorldSHA256=digest(basic.tobytes()),completeBasicNonzeroAreaEdgeCensus=bc,genuineOrdinaryBasicRootComponents=roots,completeBasicRootProofs=rootproofs,completeUpperOriginalFaces=len(whole),wholeUpperOriginalWorldSHA256=digest(whole.tobytes()),nodes=nodes,allUpperActualBasicPairs=pairs,internalExactUpperSourceContacts=internal,directUpperComponentsTouchingGenuineBasicRoot=sorted(set(direct)),upperSourceComponentsReachingGenuineBasicRoot=sorted(reached),unresolvedUpperSourceComponents=sorted(set(adj)-reached),originalGovernmentPodiumUsedAsSupport=False,zeroAreaRootOrBridgeCredit=False,currentCandidateGroundOnly=True,groundSupportAccepted=False,identityAccepted=False,physicalAccepted=False,installationApproved=False,qualification='Exact complete unchanged upper originals against complete actual current BASIC podium body and separately genuine ordinary current candidate-ground roots. No absent government podium face supplies support. Full source/literal/F32 finite clearance, complete current BASIC/native/foreign actors/collisions, fresh standalone terrain/current footprints/runtime/browser and explicit component roles remain mandatory.')
 save(DOC/'diagnostic.json.gz',result)
 refs=[Path(__file__),INPUT/'result.json',INPUT/'input.json.gz',INPUT/'complete-current-basic-podium-geometry.json.gz',GRAPH/'result.json',GRAPH/'diagnostic.json.gz',PHYS/'result.json',RUNTIME,HERE/'exact_original_shared_edge_component_census_v2_20261011.py',HERE/'exact_original_finite_triangle_contacts_20261010.py',HERE/'exact_original_shell_intersections_20261009.py',HERE/'exact_packed_world_geometry_20261009.py',HERE/'original_ordinary_rim_accounting_20261009.py',HERE/'original_wall_rim_accounting_20261009.py',*assets]
 sp=importlib.util.spec_from_file_location('lippo_actual_basic_contact_fence',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
 receipt=m.freeze(BATCH,'upper-originals-actual-basic-podium-genuine-ground-contact-diagnostic-v1',refs,dict(uids=['landsd/231645:0','landsd/237843:0','landsd/239465:0'],completeUpperOriginalFaces=len(whole),completeActualBasicFaces=len(basic),genuineBasicRootComponents=roots,resolvedUpperSourceComponents=sorted(reached),unresolvedUpperSourceComponents=sorted(set(adj)-reached),originalGovernmentPodiumUsedAsSupport=False,zeroAreaRootOrBridgeCredit=False,groundSupportAccepted=False,physicalAccepted=False,installationApproved=False))
 print(json.dumps(dict(jobId=receipt['jobId'],genuineBasicRoots=roots,resolvedUpperComponents=sorted(reached),unresolvedUpperComponents=sorted(set(adj)-reached))),flush=True)
if __name__=='__main__':main()
