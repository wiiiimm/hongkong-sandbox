"""Replay exact graph plus source-bound full-facet/zero-area accounting."""
import json,uuid,numpy as np,shapely
from pathlib import Path
from run import ROOT,HERE,read,save,digest,reservations
from original_multi_actor_support_graph_20261009 import verify
from original_nonrendering_component_accounting_20261009 import verify as verify_nonrendering
from exact_original_source_surface_contact_band_20261009 import verify_contact
from original_degenerate_ground_context_20261009 import degenerate_ground_context
from exact_projection_coverage_fallback_context_20261009 import apply_exact_coverage
BATCH='xl-terrain-recovery-20261009-market-six-complete-support-accounting-v2'
DOC=ROOT/'docs/astra-city/government-import'/BATCH
GRAPH=ROOT/'docs/astra-city/government-import/xl-terrain-recovery-20261009-market-six-exact-assembly-support/diagnostic.json.gz'
GEOMETRY=HERE/'local/government-xl-terrain-recovery-market-six-original-physical-v5-20261009/runtime-geometry.json.gz'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();d=read(GRAPH);g=read(GEOMETRY);runtime={r['uid']:r for r in g['rows']}
 claim=reservations.claim('codex-market-full-support-'+str(uuid.uuid4()),['building:'+a['uid'] for a in d['actors']],batch=BATCH);assert claim['ok'],claim
 lease=json.loads(json.dumps(claim['reservation'],default=str));save(DOC/'reservation.json',lease)
 try:
  assert digest((ROOT/'3d-viewer/city/data/manifest.json').read_bytes())==d['manifestSHA256']
  for r in d['evidenceRefs']:assert ref(ROOT/r['path'])==r
  ts=[]
  for a in d['actors']:
   r=runtime[a['uid']];t=np.asarray(r['position'],float).reshape(-1,3)[np.asarray(r['index']).reshape(-1,3)];assert digest(t.tobytes())==a['originalWorldTrianglesSHA256'];ts.append(t)
  tri=np.concatenate(ts);graph=verify(tri,d['actors'],d['components'],d['groundInterfaces'],d['contactWitnesses'],expected_binding=d['binding'],current_binding=d['binding']);assert graph['reasons']==d['reasons']
  # Independently pinned source-specific original details, never automatic
  # arbitrary caller classification or a credit to nonzero detached geometry.
  assert d['components'][72]['actorUID']=='landsd/313116:0' and d['components'][72]['globalOriginalFaces']==[34722]
  ground=np.asarray(runtime['landsd/313116:0']['drawnGroundGeometry'],float).reshape(-1,3,3)
  polygons=shapely.polygons(ground[:,:,[0,2]]);valid=shapely.area(polygons)>1e-10;ground,polygons=ground[valid],polygons[valid];tree=shapely.STRtree(polygons)
  c=apply_exact_coverage(degenerate_ground_context(tri[34722],ground,polygons,tree),tri[34722],ground);contexts={'34722':dict(c,sourceFace=34722)}
  binding=dict(completeOriginalWorldTrianglesSHA256=digest(tri.tobytes()),originalBytesAndIndicesUnchanged=True,currentDrawnGroundSHA256=digest(ground.tobytes()),completeOriginalSourceBindingSHA256=digest(json.dumps(d['actors'],sort_keys=True,separators=(',',':')).encode()),continuousNonrenderingContextsSHA256=digest(json.dumps(contexts,sort_keys=True,separators=(',',':'),allow_nan=False).encode()))
  zero=verify_nonrendering(tri,[d['components'][72]],contexts,expected_binding=binding,current_binding=binding)
  assert d['components'][12]['actorUID']=='landsd/313033:0' and d['components'][12]['globalOriginalFaces']==[6415,6416,6417]
  root_component=next(i for i,c in enumerate(d['components']) if 17723 in c['globalOriginalFaces']);assert root_component in graph['resolvedOriginalComponents']
  assert d['components'][root_component]['actorUID']=='landsd/313033:0'
  # Whole finite surfaces remain within the existing strict contact band to
  # the independently ground-rooted original authored roof. No nearby-plane
  # sample, source transformation, area omission or widened band is allowed.
  bands=[dict(originalFace=i,groundRootedOriginalSupportFace=17723,proof=verify_contact(tri[i],tri[17723:17724],.1)) for i in [6415,6416,6417]]
  assert all(b['proof']['verifiedCompleteFacetContactBand'] for b in bands)
  vertex_witnesses=[]
  for i in [6415,6416,6417]:
   for j in [16325,16326]:
    points=set(map(tuple,tri[i]))&set(map(tuple,tri[j]))
    if points:vertex_witnesses.append(dict(originalFaces=[i,j],sharedUnchangedOriginalVertices=[list(p) for p in sorted(points)]))
  assert vertex_witnesses and all(j in d['components'][root_component]['globalOriginalFaces'] for v in vertex_witnesses for j in v['originalFaces'][1:])
  resolved=sorted(set(graph['resolvedOriginalComponents'])|{12,72});assert len(resolved)==d['completeOriginalComponentCount']==84
  paths=[Path(__file__),GRAPH,GEOMETRY,HERE/'original_multi_actor_support_graph_20261009.py',HERE/'test_original_multi_actor_support_graph_20261009.py',HERE/'original_nonrendering_component_accounting_20261009.py',HERE/'test_original_nonrendering_component_accounting_20261009.py',HERE/'exact_original_source_surface_contact_band_20261009.py',HERE/'test_exact_original_source_surface_contact_band_20261009.py',HERE/'original_degenerate_ground_context_20261009.py',HERE/'exact_projection_coverage_fallback_context_20261009.py']
  result=dict(contract='source-bound-complete-original-market-six-support-accounting-v2',supportAccountingAccepted=True,actors=d['actors'],components=d['components'],completeOriginalFaces=len(tri),completeOriginalComponentCount=84,strictGroundRootedOriginalContactGraph=graph,originalNonrenderingAccounting=zero,continuousOriginalNonrenderingContexts=contexts,nonrenderingBinding=binding,sourceSpecificUnderDeckFacetBands=bands,exactOriginalVertexAttachments=vertex_witnesses,resolvedOriginalComponents=resolved,rawGraphUnresolvedComponentsRetained=[12,72],manifestSHA256=d['manifestSHA256'],evidenceRefs=d['evidenceRefs']+[ref(p) for p in paths],sourceGeometryChanges=0,facesOmitted=0,installationApproved=False,publication=False,qualification='Complete40100 original faces:82 components use exact positive-dimensional ground-rooted original support graph; one original nonrendering zero-area triangle retains strict full current continuous ground clearance; one original3-facet under-deck detail has exact original vertex attachment plus certified whole finite-facet support within unchanged±.1 band to the independently grounded authored original roof. No closed-solid/structural certification or independent physical/source/foreign/runtime/browser/publication waiver.')
  assert reservations.owns(lease);save(DOC/'diagnostic.json.gz',result);print(json.dumps(dict(supportAccountingAccepted=True,originalComponents=84,wholeOriginalFaces=len(tri),zeroAreaFaces=zero['originalNonrenderingFaces'],strictBandFacets=len(bands))),flush=True)
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
