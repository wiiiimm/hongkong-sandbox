"""Complete authored boundaries of the four remaining large-gap Opus components."""
from pathlib import Path
from collections import Counter
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_original_edge_any_finite_distance_band_v2_20261010 import verify
BASE=ROOT/'docs/astra-city/government-import';GRAPH=BASE/'government-xl-opus-original-component-graph-v1-20261017';WORLD=BASE/'government-xl-opus-four-world-contacts-v1-20261017';BATCH='government-xl-opus-remaining-boundary-v1-20261017';DOC=BASE/BATCH

def main():
 assert not DOC.exists();r=read(GRAPH/'result.json');pins={x['path']:x['sha256'] for x in r['evidenceRefs']};refs=[Path(__file__),GRAPH/'result.json']
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 def consume(p):
  assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p);return read(p)
 graph=consume(GRAPH/'graph.json.gz');worlds=consume(WORLD/'world-triangles.json.gz');uids=sorted(worlds['original']);tri=np.concatenate([np.array(worlds['original'][u]) for u in uids]);assert all(np.array_equal(tri,np.concatenate([np.array(w[u]) for u in uids])) for w in worlds.values())
 ids=[i for b in graph['positiveContactReachableFromPodium'] for i in graph['components'][b]['globalFaces']];hosts=tri[ids];rows=[]
 for component in [29,37,44,45]:
  faces=graph['components'][component]['globalFaces'];edges=Counter(tuple(sorted((tuple(tri[i,j]),tuple(tri[i,(j+1)%3])))) for i in faces for j in range(3));boundary=[e for e,n in edges.items() if n==1];proofs=[]
  for n,e in enumerate(sorted(boundary)):
   p=verify(np.array(e),hosts);proofs.append(dict(vertices=e,proof=p));print(component,n+1,len(boundary),p['verifiedCompleteOriginalEdgeFiniteFacadeBand'],flush=True)
  rows.append(dict(component=component,originalFaces=faces,boundaryEdges=len(boundary),nonmanifoldEdges=sum(n>2 for n in edges.values()),completeEdgesWithinBand=sum(x['proof']['verifiedCompleteOriginalEdgeFiniteFacadeBand'] for x in proofs),allEdgesWithinBand=bool(proofs) and all(x['proof']['verifiedCompleteOriginalEdgeFiniteFacadeBand'] for x in proofs),closedEdgeTopology=len(boundary)==0 and all(n==2 for n in edges.values()),edges=proofs))
 DOC.mkdir();save(DOC/'boundaries.json.gz',dict(rows=rows,hostGlobalFaces=ids,worldSHA256=digest(tri.tobytes()),coordinateModes=list(worlds),fullAcceptance=False,qualification='All original one-face boundary edges tested in full at the unchanged 10cm band. A boundary-free component receives no vacuous pass, role, closure-volume or support credit.'))
 summary=dict(rows=[{k:v for k,v in r.items() if k not in ('edges','originalFaces')} for r in rows],fullAcceptance=False,newlyInstalled=0);save(DOC/'summary.json',summary)
 refs += [HERE/n for n in ['exact_original_edge_any_finite_distance_band_v2_20261010.py','exact_original_edge_any_finite_distance_band_v1_20261010.py','exact_original_surface_coordinate_band_20261010.py']]
 out=module('opus_boundary_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-opus-four-component-complete-boundary-census-v1',refs,dict(uids=['landsd/322573:0'],**summary));print(dict(jobId=out['jobId'],**summary),flush=True)
if __name__=='__main__':main()
