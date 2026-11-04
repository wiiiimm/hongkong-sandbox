"""Exact complete-facet 10cm association for Opus's tiny two-face component."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_original_facet_orthogonal_finite_host_band_diagnostic_v1_20261011 import verify as orthogonal
from exact_original_facet_piecewise_finite_host_edge_band_diagnostic_v1_20261011 import verify as edge
BASE=ROOT/'docs/astra-city/government-import';GRAPH=BASE/'government-xl-opus-original-component-graph-v1-20261017';WORLD=BASE/'government-xl-opus-four-world-contacts-v1-20261017';BATCH='government-xl-opus-small-facet-association-v1-20261017';DOC=BASE/BATCH

def main():
 assert not DOC.exists();r=read(GRAPH/'result.json');pins={x['path']:x['sha256'] for x in r['evidenceRefs']};refs=[Path(__file__),GRAPH/'result.json']
 with connect() as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 def consume(p):
  assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p);return read(p)
 graph=consume(GRAPH/'graph.json.gz');worlds=consume(WORLD/'world-triangles.json.gz');uids=sorted(worlds['original']);tri=np.concatenate([np.array(worlds['original'][u]) for u in uids]);assert all(np.array_equal(tri,np.concatenate([np.array(w[u]) for u in uids])) for w in worlds.values())
 ids=[i for b in graph['positiveContactReachableFromPodium'] for i in graph['components'][b]['globalFaces']];hosts=tri[ids];faces=graph['components'][32]['globalFaces'];assert faces==[3838,13449];rows=[]
 for i in faces:
  a=orthogonal(tri[i],hosts);b=None if a['wholeFacetAssociated'] else edge(tri[i],hosts);passed=a['wholeFacetAssociated'] or bool(b and b['wholeFacetFiniteEdgeUnionAssociated']);rows.append(dict(globalSourceFace=i,sourceVertices=tri[i].tolist(),orthogonalProof=a,finiteEdgeProof=b,wholeFacetAssociated=passed));print(i,passed,flush=True)
 DOC.mkdir();save(DOC/'association.json.gz',dict(component=32,sourceFaces=faces,hostGlobalFaces=ids,worldSHA256=digest(tri.tobytes()),hostSHA256=digest(hosts.tobytes()),coordinateModes=list(worlds),rows=rows,allFacesAssociated=all(r['wholeFacetAssociated'] for r in rows),fullAcceptance=False,visualRoleAccepted=False,newlyInstalled=0))
 refs += [HERE/n for n in ['exact_original_facet_orthogonal_finite_host_band_diagnostic_v1_20261011.py','exact_original_facet_piecewise_finite_host_edge_band_diagnostic_v1_20261011.py','exact_original_surface_coordinate_band_20261010.py','exact_original_projection_coverage_20261009.py','exact_original_shared_edge_component_census_v2_20261011.py']]
 result=module('opus_small_facet_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'original-opus-two-facet-complete-fixed-band-association-v1',refs,dict(uids=['landsd/322573:0'],component=32,allFacesAssociated=all(r['wholeFacetAssociated'] for r in rows),fullAcceptance=False,newlyInstalled=0));print(dict(jobId=result['jobId'],allFacesAssociated=all(r['wholeFacetAssociated'] for r in rows)),flush=True)
if __name__=='__main__':main()
