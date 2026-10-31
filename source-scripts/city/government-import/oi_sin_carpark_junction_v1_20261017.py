"""Exact saved car-park junction evidence; no acceptance override."""
from pathlib import Path
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from primrose_compound_foundation_v2_20261015 import module
from fu_tor_loy_nearest_interfaces_v1_20261017 import nearest
from exact_original_facet_orthogonal_finite_host_band_diagnostic_v1_20261011 import verify as orthogonal
from exact_original_facet_piecewise_finite_host_edge_band_diagnostic_v1_20261011 import verify as edge
BASE=ROOT/'docs/astra-city/government-import';PHYS=BASE/'government-xl-oi-sin-four-originals-physical-v1-20261017';FACES=BASE/'government-xl-oi-sin-buried-faces-v1-20261017';RT=HERE/'local'/PHYS.name/'runtime-geometry.json.gz';BATCH='government-xl-oi-sin-carpark-junction-v1-20261017';DOC=BASE/BATCH;U='landsd/256457:0';P='landsd/91128:0'
def main():
 assert not DOC.exists();needed=[RT,PHYS/'support-checks.json.gz',FACES/'faces.json',PHYS/'selection.json.gz'];pins={};refs=[Path(__file__)]
 with connect()as c:
  c.execute('SET TRANSACTION READ ONLY')
  for folder in [PHYS,FACES]:
   r=read(folder/'result.json');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r);refs.append(folder/'result.json')
   for e in r['evidenceRefs']:
    if ROOT/e['path']in needed:
     assert e['path']not in pins or pins[e['path']]==e['sha256'];pins[e['path']]=e['sha256']
 for p in needed:assert digest(p.read_bytes())==pins[str(p.relative_to(ROOT))];refs.append(p)
 geo={g['uid']:np.asarray(g['position'],float).reshape(-1,3)[np.asarray(g['index']).reshape(-1,3)]for g in read(RT)['rows']};source=geo[U];host=geo[P];assert len(source)==175 and len(host)==7849
 contact=next(r for r in read(PHYS/'support-checks.json.gz')['rows']if r['uid']==U);failures=contact['interface']['unresolved'];assert len(failures)==19;points=[]
 for f in failures:
  i,q,d=nearest(np.asarray(f['position']),host);cross=np.cross(host[i,1]-host[i,0],host[i,2]-host[i,0]);n=cross/np.linalg.norm(cross)if np.linalg.norm(cross)else cross;points.append(dict(rawFailure=f,nearestHostFace=int(i),nearestPoint=q.tolist(),distanceM=float(d),hostNormal=n.tolist()))
 facets=[];original=read(FACES/'faces.json')['rows'];assert sorted(r['faceIndex']for r in original)==[68,69]
 for r in original:
  i=r['faceIndex'];assert np.array_equal(source[i],r['vertices']);a=orthogonal(source[i],host);b=None if a['wholeFacetAssociated']else edge(source[i],host);facets.append(dict(face=i,orthogonal=a,edge=b,wholeFacetWithinBand=a['wholeFacetAssociated']or bool(b and b['wholeFacetFiniteEdgeUnionAssociated'])))
 save(DOC/'junction.json.gz',dict(uid=U,sourceSHA256=contact['sourceSHA256'],hostSHA256=contact['supportSHA256'],points=points,facets=facets,rawInterface=contact['interface'],fullAcceptance=False,geometryChanges=0));summary=dict(failedContacts=len(points),maximumNearestDistanceM=max(p['distanceM']for p in points),contactsOutsideFixedBand=sum(p['distanceM']>.1 for p in points),wholeFailedFacetsWithinBand=sum(r['wholeFacetWithinBand']for r in facets),fullAcceptance=False);save(DOC/'summary.json',summary)
 refs.extend(HERE/name for name in ['fu_tor_loy_nearest_interfaces_v1_20261017.py','exact_original_facet_orthogonal_finite_host_band_diagnostic_v1_20261011.py','exact_original_facet_piecewise_finite_host_edge_band_diagnostic_v1_20261011.py'])
 out=module('oi_carpark_junction_freezer',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'oi-sin-carpark-original-junction-distance-v1',refs,dict(uids=[U,P],summary=summary,nextStep='Inspect exact remaining finite-face/contact gaps and source functions; no contact or foundation acceptance from proximity alone.'));print(dict(jobId=out['jobId'],summary=summary),flush=True)
if __name__=='__main__':main()
