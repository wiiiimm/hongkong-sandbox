"""Historical v5 complete original graph with unchanged ordinary ground roots.

Strict JS failures stay preserved. This source-only graph never reaccepts current
catalogues, foreign actors, runtime or publication after the metadata repair.
"""
from pathlib import Path
import gzip,struct,importlib.util,json
import numpy as np
from run import ROOT,HERE,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from xl_source_stream_binding_20261009 import source_stream_binding
from original_ordinary_ground_root_graph_20261009 import verify
BATCH='government-xl-one-peking-original-ordinary-ground-graph-diagnostic-v1-20261010';DOC=ROOT/'docs/astra-city/government-import'/BATCH
PHYS=DOC.parent/'government-xl-one-peking-two-original-retained-hullett-child-current-physical-v5-20261010'
RUNTIME=HERE/'local'/PHYS.name/'runtime-geometry.json.gz'
GRAPH=DOC.parent/'government-xl-one-peking-two-all-original-part-interface-graph-v1-20261010'
FOOTINGS=DOC.parent/'government-xl-one-peking-podium-original-and-literal-component-footings-diagnostic-v1-20261010'
def main():
 assert not DOC.exists();rows=read(PHYS/'selection.json.gz')['rows'];rows=sorted(rows,key=lambda r:r['uid']);assert [r['uid'] for r in rows]==['landsd/233985:0','landsd/240487:0']
 actors=[];indexed=[];pieces=[];offsets={};assets=[];cursor=0
 for r in rows:
  p=ROOT/r['candidate']['path'];raw=p.read_bytes();assert digest(raw)==r['sourceSHA256'];assets.append(p);tri=decode_original_world_triangles(raw)
  data=gzip.decompress(raw);size,kind=struct.unpack_from('<II',data,12);assert kind==0x4e4f534a;gltf=json.loads(data[20:20+size]);binary=data[28+size:]
  assert len(gltf['meshes'])==1 and len(gltf['meshes'][0]['primitives'])==1
  primitive=gltf['meshes'][0]['primitives'][0];assert primitive.get('mode',4)==4
  a=gltf['accessors'][primitive['indices']];v=gltf['bufferViews'][a['bufferView']];dt=np.dtype({5123:'<u2',5125:'<u4'}[a['componentType']])
  assert a['type']=='SCALAR' and not a.get('sparse') and not a.get('normalized') and v['buffer']==0 and v.get('byteStride',dt.itemsize)==dt.itemsize
  ids=np.frombuffer(binary,dtype=dt,count=a['count'],offset=v.get('byteOffset',0)+a.get('byteOffset',0)).astype(np.uint32).reshape(-1,3)
  count=gltf['accessors'][primitive['attributes']['POSITION']]['count'];position=np.empty((count,3));assigned={}
  assert len(ids)==len(tri)
  for ix,face in zip(ids,tri):
   for vertex,point in zip(ix,face):
    vertex=int(vertex)
    if vertex in assigned:assert np.array_equal(assigned[vertex],point)
    else:assigned[vertex]=point;position[vertex]=point
  assert set(assigned)==set(range(count)) and np.array_equal(position[ids],tri)
  actors.append(dict(uid=r['uid'],sourceSHA256=digest(raw),originalStreamBindingSHA256=digest(json.dumps(source_stream_binding(raw),sort_keys=True,separators=(',',':')).encode()),globalFaceRange=[cursor,cursor+len(tri)],completeOriginalFaceCount=len(tri),originalWorldTrianglesSHA256=digest(tri.tobytes())))
  indexed.append(dict(uid=r['uid'],sourceSHA256=digest(raw),position=position.reshape(-1).tolist(),index=ids.reshape(-1).tolist()));offsets[r['uid']]=cursor;pieces.append(tri);cursor+=len(tri)
 whole=np.concatenate(pieces);graph=read(GRAPH/'diagnostic.json.gz');assert graph['totalParts']==38 and graph['allPartPairsAccounted']
 components=[dict(actorUID=n['uid'],globalOriginalFaces=[int(f)+offsets[n['uid']] for f in n['originalFaceIDs']]) for n in graph['nodes']]
 contacts=[]
 for edge in graph['completePartInterfacePairs']:
  if not edge['positiveTwoAreaPrimitiveInterfaces']:continue
  c=edge['positiveTwoAreaPrimitiveInterfaces'][0];ia,ib=edge['nodeA'],edge['nodeB']
  assert c['dimension']>0 and c['sourcePrimitiveDimensionA']==c['sourcePrimitiveDimensionB']==2
  contacts.append(dict(components=[ia,ib],globalOriginalFaces=[c['sourceFaceA']+offsets[graph['nodes'][ia]['uid']],c['sourceFaceB']+offsets[graph['nodes'][ib]['uid']]]))
 runtime=read(RUNTIME)['rows'];assert {r['uid'] for r in runtime}==set(offsets)
 ground=np.concatenate([np.asarray(r['drawnGroundGeometry'],dtype='<f8').reshape(-1,3,3) for r in runtime])
 save(DOC/'complete-indexed-original-sources.json.gz',dict(rows=indexed));save(DOC/'complete-historical-ground-facets.json.gz',dict(triangles=ground.tolist(),sourceRuntimeGeometrySHA256=digest(RUNTIME.read_bytes()),policy='Every literal drawn ground facet from both historical v5 actors retained, concatenated without clipping, deduplication, interpolation or height changes.'))
 binding=dict(completeOriginalWorldTrianglesSHA256=digest(whole.tobytes()),currentDrawnGroundSHA256=digest(ground.tobytes()),groundInterfacesInputSHA256=digest(RUNTIME.read_bytes()),originalIndexedSourcesSHA256=digest(json.dumps(indexed,sort_keys=True,separators=(',',':'),allow_nan=False).encode()),supportScope='complete-current-drawn-ground-only')
 result=verify(whole,actors,components,contacts,indexed,ground,expected_binding=binding,current_binding=binding)
 result.update(actors=actors,components=components,binding=binding,contactWitnesses=contacts,historicalCandidateGroundOnly=True,currentRegionalRebindRequired=True,identityAccepted=False,physicalAccepted=False,installationApproved=False,strictJSFootingNegativeReceipt=digest((FOOTINGS/'result.json').read_bytes()),qualification='Historical v5 candidate ground only; unchanged ordinary -.5m/1m rim and genuine±.1m anchors independently replayed. Every source part and exact positive area-facet contact retained. Strict JS negatives remain separate. No current identity/foreign/foundation/runtime/installation acceptance; metadata repair requires fresh current bindings.')
 save(DOC/'diagnostic.json.gz',result)
 refs=[Path(__file__),PHYS/'result.json',PHYS/'selection.json.gz',RUNTIME,GRAPH/'result.json',GRAPH/'diagnostic.json.gz',FOOTINGS/'result.json',FOOTINGS/'diagnostic.json.gz',HERE/'original_ordinary_ground_root_graph_20261009.py',HERE/'original_ordinary_rim_accounting_20261009.py',HERE/'original_multi_actor_support_graph_20261009.py',HERE/'original_wall_rim_accounting_20261009.py',HERE/'exact_original_shell_intersections_20261009.py',HERE/'exact_packed_world_geometry_20261009.py',HERE/'xl_source_stream_binding_20261009.py',*assets]
 sp=importlib.util.spec_from_file_location('peking_ordinary_fence',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
 receipt=m.freeze(BATCH,'complete-historical-original-ordinary-ground-root-graph-diagnostic-v1',refs,dict(uids=sorted(offsets),completeOriginalFaces=len(whole),completeOriginalParts=len(components),ordinaryGroundRoots=result['ordinaryGroundRootComponents'],resolvedOriginalComponents=result['resolvedOriginalComponents'],rawGraphReasons=result['reasons'],identityAccepted=False,physicalAccepted=False,installationApproved=False,sourceGeometryChanges=0,currentRegionalRebindRequired=True))
 print(json.dumps(dict(jobId=receipt['jobId'],roots=result['ordinaryGroundRootComponents'],resolved=result['resolvedOriginalComponents'],reasons=result['reasons'])),flush=True)
if __name__=='__main__':main()
