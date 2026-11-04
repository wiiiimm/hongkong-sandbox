"""Read-only complete Lippo real-facet ordinary-root diagnosis.
Every source face remains inventoried. Exact zero-area faces never supply graph
bridges or ground anchors; current foundation/finite/foreign gates are separate.
"""
from pathlib import Path
from fractions import Fraction
import gzip,struct,importlib.util,json
import numpy as np,shapely
from run import ROOT,HERE,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_shared_edge_component_census_v2_20261011 import census
from exact_original_shell_intersections_20261009 import rational_face,intersection_points
from original_ordinary_rim_accounting_20261009 import verify as ordinary_rim
from original_wall_rim_accounting_20261009 import original_samples
BATCH='government-xl-lippo-three-real-facet-ordinary-ground-diagnostic-v1-20261011';DOC=ROOT/'docs/astra-city/government-import'/BATCH
GRAPH=DOC.parent/'government-xl-lippo-three-complete-original-edge-components-and-contacts-v1-20261011'
PHYS=DOC.parent/'government-xl-lippo-two-original-disjoint-current-parent-physical-v3-20261011'
RUNTIME=HERE/'local'/PHYS.name/'runtime-geometry.json.gz'
INPUT=DOC.parent/'government-xl-lippo-two-original-current-physical-inputs-v2-20261011'
LANGHAM=DOC.parent/'government-xl-lippo-langham-current-original-recovery-v1-20261011'
def indexed(raw,tri):
 data=gzip.decompress(raw);size,kind=struct.unpack_from('<II',data,12);assert kind==0x4e4f534a;gltf=json.loads(data[20:20+size]);binary=data[28+size:]
 assert len(gltf['meshes'])==1 and len(gltf['meshes'][0]['primitives'])==1
 primitive=gltf['meshes'][0]['primitives'][0];assert primitive.get('mode',4)==4
 a=gltf['accessors'][primitive['indices']];v=gltf['bufferViews'][a['bufferView']];dt=np.dtype({5123:'<u2',5125:'<u4'}[a['componentType']])
 assert a['type']=='SCALAR' and not a.get('sparse') and not a.get('normalized') and v['buffer']==0 and v.get('byteStride',dt.itemsize)==dt.itemsize
 idx=np.frombuffer(binary,dtype=dt,count=a['count'],offset=v.get('byteOffset',0)+a.get('byteOffset',0)).astype(np.uint32).reshape(-1,3)
 count=gltf['accessors'][primitive['attributes']['POSITION']]['count'];position=np.empty((count,3));assigned={}
 assert len(idx)==len(tri)
 for ix,face in zip(idx,tri):
  for vertex,point in zip(ix,face):
   vertex=int(vertex)
   if vertex in assigned:assert np.array_equal(assigned[vertex],point)
   else:assigned[vertex]=point;position[vertex]=point
 assert set(assigned)==set(range(count)) and np.array_equal(position[idx],tri)
 return position,idx

def main():
 assert not DOC.exists();graph=read(GRAPH/'diagnostic.json.gz');assert graph['allPairsAccounted'] and graph['completeOriginalFaces']==26844
 rows=sorted(read(INPUT/'check-selection.json.gz')['rows']+read(LANGHAM/'check-selection.json.gz')['rows'],key=lambda r:r['uid'])
 pieces=[];decoded={};assets=[];cursor=0
 for row,actor in zip(rows,graph['actors']):
  assert row['uid']==actor['uid'];path=ROOT/row['candidate']['path'];raw=path.read_bytes();assert digest(raw)==row['sourceSHA256']==actor['sourceSHA256'];assets.append(path)
  tri=decode_original_world_triangles(raw);assert digest(tri.tobytes())==actor['originalWorldTrianglesSHA256'] and actor['globalOriginalFaceRange']==[cursor,cursor+len(tri)]
  cp,ci=indexed(raw,tri);decoded[row['uid']]=(cp,ci,cursor);pieces.append(tri);cursor+=len(tri)
 whole=np.concatenate(pieces);nodes=graph['nodes'];assert len(nodes)==28
 render=[]
 for actor,record in zip(graph['actors'],graph['completeNonzeroAreaEdgeCensuses']):
  lo,hi=actor['globalOriginalFaceRange'];actual=census(whole,list(range(lo,hi)));assert actual==record['completeNonzeroAreaAndEdgeCensus'];render+=actual['completeRenderableFaceIds']
 assert sorted(render)==sorted(f for node in nodes for f in node['globalOriginalFaces'])
 assert sorted(render+graph['completeNonrenderingOriginalFaceIDs'])==list(range(len(whole)))
 runtime=read(RUNTIME)['rows'];assert {r['uid'] for r in runtime}=={'landsd/231645:0','landsd/239465:0'}
 ground=np.concatenate([np.asarray(r['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3) for r in runtime]);assert np.isfinite(ground).all()
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
  assert values,'Missing exact drawn ground at real original component sample'
  return float(max(values))
 roots=[];proofs=[]
 for node in nodes:
  k=node['component'];p,idx,start=decoded[node['uid']];local=np.asarray(node['globalOriginalFaces'])-start;vertex_ids=sorted(set(idx[local].reshape(-1).tolist()));mapping={v:i for i,v in enumerate(vertex_ids)}
  cp=p[vertex_ids];ci=np.asarray([[mapping[int(v)] for v in f] for f in idx[local]],dtype=np.uint32);bottom=float(cp[:,1].min());samples=original_samples(cp,ci,bottom)
  try:
   for sample in samples:
    g=height(sample['point'][0],sample['point'][2]);sample.update(ground=g,gap=sample['point'][1]-g)
   low=[r for r in samples if r['point'][1]<=bottom+.35]
   metric=dict(checks=len(samples),lowRimChecks=len(low),minSurfaceGap=min(r['gap'] for r in samples),minLowGap=min(r['gap'] for r in low),maxLowGap=max(r['gap'] for r in low))
   proof=dict(accepted=True,ordinaryRim=ordinary_rim(cp,ci,bottom,samples,expected_metric=metric),metric=metric);roots.append(k)
  except AssertionError as error:proof=dict(accepted=False,reason=str(error))
  proofs.append(dict(**proof,component=k,uid=node['uid'],completeOriginalFaces=node['globalOriginalFaces'],originalRuntimeVertexIds=vertex_ids,completeSamples=samples))
  print(json.dumps(dict(component=k,uid=node['uid'],ordinaryRoot=proof['accepted'],reason=proof.get('reason'))),flush=True)
 adjacency={i:set() for i in range(len(nodes))};contacts=[];membership={f:n['component'] for n in nodes for f in n['globalOriginalFaces']}
 for pair in graph['completePairRecords']:
  if not pair['positiveDimensionInterface']:continue
  c=pair['positiveAreaFacetInterfaces'][0];fa,fb=c['sourceFaceA'],c['sourceFaceB'];a,b=pair['components'];assert membership[fa]==a and membership[fb]==b
  points=intersection_points(rational_face(whole[fa]),rational_face(whole[fb]));assert len(points)>=2
  adjacency[a].add(b);adjacency[b].add(a);contacts.append(dict(components=[a,b],globalOriginalFaces=[fa,fb],exactContactPoints=[[str(v) for v in p] for p in sorted(points)]))
 reached=set(roots);todo=list(roots);parents={i:None for i in roots}
 while todo:
  a=todo.pop()
  for b in sorted(adjacency[a]):
   if b not in reached:reached.add(b);parents[b]=a;todo.append(b)
 unresolved=sorted(set(adjacency)-reached)
 result=dict(completeOriginalFaces=len(whole),completeRealFacetComponents=len(nodes),completeNonrenderingOriginalFaceIDs=graph['completeNonrenderingOriginalFaceIDs'],wholeSourceWorldSHA256=digest(whole.tobytes()),completeDrawnGroundFacets=len(ground),completeDrawnGroundSHA256=digest(ground.tobytes()),sourceRuntimeReceiptSHA256=digest(RUNTIME.read_bytes()),ordinaryGroundRoots=roots,ordinaryRootProofs=proofs,exactPositiveOriginalContacts=contacts,resolvedRealFacetComponents=sorted(reached),unresolvedRealFacetComponents=unresolved,groundRootedComponentParents=parents,zeroAreaRootOrBridgeCredit=False,sourceGeometryChanges=0,currentCandidateGroundOnly=True,groundSupportAccepted=False,identityAccepted=False,physicalAccepted=False,installationApproved=False,qualification='Read-only diagnostic of all real facets and full original inventory. Genuine ordinary roots use unchanged -.5m/1m rim and +/- .1m anchors; all exact zero-area records remain present separately and confer no root/contact/bridge credit. Entire source/literal finite/foundation/foreign/runtime proof and current role review remain mandatory.')
 save(DOC/'diagnostic.json.gz',result)
 refs=[Path(__file__),GRAPH/'result.json',GRAPH/'diagnostic.json.gz',PHYS/'result.json',RUNTIME,INPUT/'check-selection.json.gz',LANGHAM/'check-selection.json.gz',HERE/'exact_original_shared_edge_component_census_v2_20261011.py',HERE/'exact_packed_world_geometry_20261009.py',HERE/'original_ordinary_rim_accounting_20261009.py',HERE/'original_wall_rim_accounting_20261009.py',HERE/'exact_original_shell_intersections_20261009.py',*assets]
 sp=importlib.util.spec_from_file_location('lippo_real_ground_fence',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
 receipt=m.freeze(BATCH,'three-source-real-facet-ordinary-ground-diagnostic-v1',refs,dict(uids=[r['uid'] for r in rows],completeOriginalFaces=len(whole),completeRealFacetComponents=len(nodes),ordinaryGroundRoots=roots,resolvedRealFacetComponents=sorted(reached),unresolvedRealFacetComponents=unresolved,zeroAreaRootOrBridgeCredit=False,groundSupportAccepted=False,physicalAccepted=False,installationApproved=False))
 print(json.dumps(dict(jobId=receipt['jobId'],roots=roots,resolved=len(reached),unresolved=unresolved)),flush=True)
if __name__=='__main__':main()
