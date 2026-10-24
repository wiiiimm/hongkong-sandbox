"""Independent nonzero-edge census for all historical58 original groups."""
from pathlib import Path
import importlib.util,json
import numpy as np
from run import ROOT,HERE,read,save,digest
from exact_original_shared_edge_component_census_20261011 import census
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
BATCH='government-xl-one-peking-complete-original-and-literal-nonzero-edge-census-v1-20261011';DOC=ROOT/'docs/astra-city/government-import'/BATCH
BASE=DOC.parent;GRAPH=BASE/'government-xl-one-peking-original-ordinary-ground-graph-diagnostic-v2-20261010';PHYS=BASE/'government-xl-one-peking-two-original-retained-hullett-child-current-physical-v5-20261010';RT=HERE/'local'/PHYS.name/'runtime-geometry.json.gz'
def main():
 assert not DOC.exists();g=read(GRAPH/'diagnostic.json.gz');rows=sorted(read(PHYS/'selection.json.gz')['rows'],key=lambda r:r['uid']);assets=[ROOT/r['candidate']['path'] for r in rows]
 for p,r in zip(assets,rows):assert digest(p.read_bytes())==r['sourceSHA256']
 original=np.concatenate([decode_original_world_triangles(p.read_bytes()) for p in assets]);runtime={r['uid']:r for r in read(RT)['rows']}
 literal=np.concatenate([np.asarray(runtime[r['uid']]['position'],dtype='<f8').reshape(-1,3)[np.asarray(runtime[r['uid']]['index']).reshape(-1,3)] for r in rows])
 assert original.shape==literal.shape and digest(original.tobytes())==g['binding']['completeOriginalWorldTrianglesSHA256']
 results=[]
 for kind,a in [('completeOriginal',original),('actualLiteralRendered',literal)]:
  by=[]
  for k,c in enumerate(g['components']):
   p=census(a,sorted(c['globalOriginalFaces']));by.append(dict(historicalComponent=k,actorUID=c['actorUID'],completeNonzeroEdgeCensus=p))
  allgroups=[ids for r in by for ids in r['completeNonzeroEdgeCensus']['sharedEdgeConnectedComponents']]
  assert sorted(f for v in allgroups for f in v)==list(range(len(a)))
  results.append(dict(representation=kind,completeWorldSHA256=digest(a.tobytes()),complete58HistoricalGroupCensuses=by,completeNonzeroEdgeComponents=allgroups,componentCount=len(allgroups),anyHistoricalComponentSplit=any(len(r['completeNonzeroEdgeCensus']['sharedEdgeConnectedComponents'])!=1 for r in by)))
 out=dict(uids=[r['uid'] for r in rows],completeOriginalAndLiteralFaces=len(original),historicalVertexGroups=38,historicalEdgeGroups=58,completeOriginalAndLiteralCensuses=results,allFaceOwnershipAccounted=True,collapsedEdgeGlueExcluded=True,sourceGeometryChanges=0,groundRootsAccepted=False,physicalAccepted=False,installationApproved=False,qualification='Independent exact nonzero-edge census of every original/literal face in all58 historical groups. Collapsed edges give zero connectivity credit. Existing historical ordinary-root output is not promoted; any split requires distinct recomputed component/support proof. No solid, structural support, current foreign/foundation/installation credit.')
 save(DOC/'diagnostic.json.gz',out)
 refs=[Path(__file__),GRAPH/'result.json',GRAPH/'diagnostic.json.gz',PHYS/'result.json',PHYS/'selection.json.gz',RT,HERE/'exact_original_shared_edge_component_census_20261011.py',HERE/'test_exact_original_shared_edge_component_census_20261011.py',HERE/'exact_packed_world_geometry_20261009.py',*assets]
 sp=importlib.util.spec_from_file_location('peking_nonzero_census_fence',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);r=m.freeze(BATCH,'complete-original-and-literal58group-nonzero-edge-census-diagnostic-v1',refs,out)
 print(json.dumps(dict(jobId=r['jobId'],results=[dict(representation=v['representation'],components=v['componentCount'],anySplit=v['anyHistoricalComponentSplit']) for v in results])),flush=True)
if __name__=='__main__':main()
