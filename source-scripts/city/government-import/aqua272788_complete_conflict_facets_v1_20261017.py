"""Whole-facet proximity proof for two original Aqua Marine/podium junction faces."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from exact_original_facet_orthogonal_finite_host_band_diagnostic_v1_20261011 import verify as orthogonal
from exact_original_facet_piecewise_finite_host_edge_band_diagnostic_v1_20261011 import verify as edge
BASE=ROOT/'docs/astra-city/government-import';PRIOR=BASE/'government-xl-aqua272788-unproved-edges-resolution-v1-20261017';BATCH='government-xl-aqua272788-complete-conflict-facets-v1-20261017';DOC=BASE/BATCH

def main():
 assert not DOC.exists();r=read(PRIOR/'result.json')
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
 pins={}
 for x in r['evidenceRefs']:
  assert x['path']not in pins or pins[x['path']]==x['sha256'];pins[x['path']]=x['sha256']
 for p,h in pins.items():assert digest((ROOT/p).read_bytes())==h,p
 rt=HERE/'local/government-xl-aqua272788-current-pair-v1-20261017/runtime-geometry.json.gz';assert str(rt.relative_to(ROOT))in pins
 tri={g['uid']:np.asarray(g['position'],float).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)]for g in read(rt)['rows']};hosts=tri['landsd/193086:0'];source=tri['landsd/272788:0'];rows=[]
 for i in [32,1836]:
  a=orthogonal(source[i],hosts);b=None if a['wholeFacetAssociated']else edge(source[i],hosts);passed=a['wholeFacetAssociated']or bool(b and b['wholeFacetFiniteEdgeUnionAssociated']);rows.append(dict(sourceFace=i,sourceVertices=source[i].tolist(),orthogonalProof=a,finiteEdgeProof=b,wholeFacetAssociated=passed));print(i,passed,flush=True)
 save(DOC/'association.json.gz',dict(sourceSHA256=digest(source.tobytes()),hostSHA256=digest(hosts.tobytes()),sourceFaces=len(source),hostFaces=len(hosts),rows=rows,allFacesAssociated=all(x['wholeFacetAssociated']for x in rows),fullAcceptance=False,sourceGeometryChanges=0,qualification='Complete original finite-facet proximity within unchanged 0.1m band. No whole-source placement, physical role or publication acceptance.'))
 refs=[Path(__file__),PRIOR/'result.json',*[ROOT/p for p in pins]]+[HERE/n for n in ['exact_original_facet_orthogonal_finite_host_band_diagnostic_v1_20261011.py','exact_original_facet_piecewise_finite_host_edge_band_diagnostic_v1_20261011.py','exact_original_surface_coordinate_band_20261010.py','exact_original_projection_coverage_20261009.py','exact_original_shared_edge_component_census_v2_20261011.py']]
 out=module('aqua_facets_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'aqua272788-complete-original-conflict-facet-association-v1',refs,dict(uids=['landsd/272788:0'],allFacesAssociated=all(x['wholeFacetAssociated']for x in rows),fullAcceptance=False,nextStep='Review complete wall/podium source role with exact whole-facet results; keep raw foundation failures until explicitly resolved and all current physical/runtime gates pass.'))
 print(out['jobId'],flush=True)
if __name__=='__main__':main()
