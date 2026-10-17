"""Complete unchanged source pair topology and finite contacts; no root credit."""
from pathlib import Path
import importlib.util,json
import numpy as np
from run import ROOT,HERE,read,save,digest
from exact_original_shared_edge_component_census_v2_20261011 import census
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_finite_triangle_contacts_20261010 import exact_finite_contacts
from xl_source_stream_binding_20261009 import source_stream_binding
BATCH='government-xl-lippo-two-complete-original-edge-components-and-contacts-v1-20261011';DOC=ROOT/'docs/astra-city/government-import'/BATCH
INPUT=DOC.parent/'government-xl-lippo-two-original-current-physical-inputs-v1-20261011'
def main():
 assert not DOC.exists()
 rows=sorted(read(INPUT/'check-selection.json.gz')['rows'],key=lambda r:r['uid']);assert [r['uid'] for r in rows]==['landsd/231645:0','landsd/239465:0']
 parts=[];actors=[];nodes=[];assets=[];cursor=0
 for r in rows:
  p=ROOT/r['candidate']['path'];raw=p.read_bytes();assert digest(raw)==r['sourceSHA256'];assets.append(p);t=decode_original_world_triangles(raw);parts.append(t)
  actors.append(dict(uid=r['uid'],sourceSHA256=r['sourceSHA256'],completeOriginalFaces=len(t),originalWorldTrianglesSHA256=digest(t.tobytes()),sourceStreams=source_stream_binding(raw),globalOriginalFaceRange=[cursor,cursor+len(t)]));cursor+=len(t)
 whole=np.concatenate(parts);assert len(whole)==17322
 censuses=[]
 for a in actors:
  lo,hi=a['globalOriginalFaceRange'];c=census(whole,list(range(lo,hi)));censuses.append(dict(uid=a['uid'],completeNonzeroAreaAndEdgeCensus=c))
  for faces in c['sharedEdgeConnectedComponents']:
   t=whole[faces];nodes.append(dict(component=len(nodes),uid=a['uid'],globalOriginalFaces=faces,completeFaces=len(faces),worldBounds=[t.min((0,1)).tolist(),t.max((0,1)).tolist()]))
 render=sorted(f for c in censuses for f in c['completeNonzeroAreaAndEdgeCensus']['completeRenderableFaceIds']);nonrender=sorted(f for c in censuses for f in c['completeNonzeroAreaAndEdgeCensus']['exactNonrenderingOriginalFaces'])
 assert sorted(render+nonrender)==list(range(len(whole))) and not set(render)&set(nonrender)
 pairs=[];skipped=[]
 for i,a in enumerate(nodes):
  alo,ahi=np.asarray(a['worldBounds'])
  for j in range(i+1,len(nodes)):
   b=nodes[j];blo,bhi=np.asarray(b['worldBounds'])
   if np.any(ahi<blo) or np.any(bhi<alo):skipped.append(dict(components=[i,j],exactWholeBoundsDisjoint=True));continue
   p=exact_finite_contacts(whole,a['globalOriginalFaces'],whole,b['globalOriginalFaces']);assert p['allPairsExamined']
   positive=[c for c in p['contacts'] if c['dimension']>0 and c['sourcePrimitiveDimensionA']==c['sourcePrimitiveDimensionB']==2]
   pairs.append(dict(components=[i,j],completeFiniteContactProof=p,positiveAreaFacetInterfaces=positive,positiveDimensionInterface=bool(positive)))
  save(DOC/'diagnostic-progress.json.gz',dict(nodes=nodes,actors=actors,completePairRecords=pairs,exactWholeBoundsDisjointPairs=skipped))
  print(json.dumps(dict(component=i,completeComponents=len(nodes),overlappingPairChecks=len(pairs))),flush=True)
 assert len(pairs)+len(skipped)==len(nodes)*(len(nodes)-1)//2
 result=dict(actors=actors,nodes=nodes,completeNonzeroAreaEdgeCensuses=censuses,completePairRecords=pairs,exactWholeBoundsDisjointPairs=skipped,completeOriginalFaces=len(whole),completeRenderableOriginalFaces=len(render),completeNonrenderingOriginalFaceIDs=nonrender,allPairsAccounted=True,sourceGeometryChanges=0,groundRootAccepted=False,physicalAccepted=False,installationApproved=False,qualification='Complete source-only exact positive-dimensional finite interfaces among real source facets. No zero-area or point-only component glue. Every nonrendering source record remains accounted and retained for independent full terrain/runtime proof. No grounding, ownership, shared-permit, foreign-collision or installation credit.')
 save(DOC/'diagnostic.json.gz',result)
 refs=[Path(__file__),INPUT/'result.json',INPUT/'check-selection.json.gz',HERE/'exact_original_shared_edge_component_census_v2_20261011.py',HERE/'exact_original_finite_triangle_contacts_20261010.py',HERE/'exact_packed_world_geometry_20261009.py',HERE/'xl_source_stream_binding_20261009.py',*assets]
 s=importlib.util.spec_from_file_location('lippo_original_graph_fence',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
 receipt=m.freeze(BATCH,'two-complete-original-nonzero-area-edge-components-and-finite-contacts-v1',refs,dict(uids=[a['uid'] for a in actors],completeOriginalFaces=len(whole),completeRenderableComponents=len(nodes),completeNonrenderingFaces=len(nonrender),positiveComponentPairInterfaces=sum(p['positiveDimensionInterface'] for p in pairs),sourceGeometryChanges=0,physicalAccepted=False,installationApproved=False,currentHeldReason='complete-current-original-and-rendered-ground-support-foreign-runtime-required'))
 print(json.dumps(dict(jobId=receipt['jobId'],components=len(nodes),physicalAccepted=False)),flush=True)
if __name__=='__main__':main()
