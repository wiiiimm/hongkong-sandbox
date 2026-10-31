"""Complete remaining-body proximity inventory, without authored role credit.

Only independently diagnosed 866 owned paths can nominate visual host facets.
All 132 bodies, all their facets and every actual incidence-one boundary edge
are tested in each arithmetic mode. Same-actor hosts only; no visual cycles,
native body seed, fabricated cap or function inference. Whole interior failures
and incomplete boundary unions remain failures under the existing .1m band.
"""
from pathlib import Path
from collections import defaultdict
import importlib.util,time,uuid
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_shared_edge_component_census_v2_20261011 import census
from exact_original_facet_orthogonal_finite_host_band_diagnostic_v1_20261011 import verify as facet_verify
from exact_original_facet_finite_edge_band_diagnostic_v1_20261011 import verify as facet_edge_verify
from exact_original_edge_any_finite_distance_band_v2_20261010 import verify as edge_verify
BASE=ROOT/'docs/astra-city/government-import'
BATCH='xl-terrain-recovery-20261011-elements132-four-stream-qualified-host-association-v1';DOC=BASE/BATCH
GRAPH=BASE/'xl-terrain-recovery-20261011-elements-complete-owned-original-contact-graph-v1'
PATHS=BASE/'xl-terrain-recovery-20261011-elements-bounded-owned-four-stream-path-replay-v1'
CONTEXT=BASE/'xl-terrain-recovery-20261011-elements132-remaining-original-bodies-context-v1'
FINITE=BASE/'xl-terrain-recovery-20261011-elements-owned-four-stream-complete-finite-v1'
ATTR=BASE/'xl-terrain-recovery-20261011-elements-sun-star-two-current-render-attribute-capture-v1'
UIDS=['landsd/204145:0','landsd/204143:0'];COUNTS=[12129,11680]
MODES=[('providerOriginal',None),('actualLiteral','completeLiteralWorldPosition'),('explicitLeftFloat32','completeExplicitLeftAssociatedFloat32WorldPosition'),('explicitBalancedFloat32','completeExplicitBalancedFloat32WorldPosition')]
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();refs=[ref(Path(__file__))];receipts={}
 for folder in [GRAPH,PATHS,CONTEXT,FINITE,ATTR]:
  r=read(folder/'result.json')
  with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
  receipts[folder.name]=r;refs.append(ref(folder/'result.json'))
 def bound(folder,name):
  p=folder/name;assert ref(p)in receipts[folder.name]['evidenceRefs'];refs.append(ref(p));return read(p)
 g=bound(GRAPH,'diagnostic.json.gz');paths=bound(PATHS,'diagnostic.json.gz');ctx=bound(CONTEXT,'diagnostic.json.gz');finite=bound(FINITE,'diagnostic.json.gz');attrs=bound(ATTR,'actual-render-attributes.json.gz')['rows']
 assert [a['uid']for a in attrs]==UIDS;assert len(g['components'])==1745
 assert [r['mode']for r in paths['rows']]==[m for m,_ in MODES]
 remaining=[r['originalBody']for r in ctx['all132Bodies']];assert len(remaining)==132 and sum(len(g['components'][i]['globalOriginalFaces'])for i in remaining)==3172
 assert all(r['unprovedOrdinaryFaces']==[]for r in finite['rows'])and len(finite['rows'])==8
 originals=[]
 for s,a,n in zip(g['binding']['completeSourceInputs'][:2],attrs,COUNTS):
  p=ROOT/s['asset']['path'];assert ref(p)==s['asset']and s['uid']==a['uid']and s['sourceSHA256']==a['sourceSHA256'];refs.append(ref(p));t=decode_original_world_triangles(p.read_bytes());assert len(t)==n;originals.append(t)
 original=np.concatenate(originals);assert len(original)==23809
 helpers=['exact_packed_world_geometry_20261009.py','exact_original_shared_edge_component_census_v2_20261011.py','exact_original_facet_orthogonal_finite_host_band_diagnostic_v1_20261011.py','exact_original_facet_finite_edge_band_diagnostic_v1_20261011.py','exact_original_surface_coordinate_band_20261010.py','exact_original_projection_coverage_20261009.py','exact_original_edge_any_finite_distance_band_v2_20261010.py','exact_original_edge_any_finite_distance_band_v1_20261010.py','exact_original_perpendicular_any_facet_band_v1_20261010.py','xl-popcorn-source-investigations-checkpoints-20261009.py'];refs.extend(ref(HERE/n)for n in helpers)
 claim=reservations.claim('elements132-hosts-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];last=time.monotonic();output_rows=[]
 def pulse(force=False):
  nonlocal last
  if force or time.monotonic()-last>=20:assert reservations.heartbeat(lease)['ok']and reservations.owns(lease);last=time.monotonic()
 try:
  for mode,field in MODES:
   parts=originals if field is None else [np.asarray(a[field],float).reshape(-1,3)[np.asarray(a['completeOriginalIndex'],np.uint32).reshape(-1,3)]for a in attrs]
   world=np.concatenate(parts);p=next(r for r in paths['rows']if r['mode']==mode);assert digest(world.tobytes())==p['completeWorldSHA256']
   qualified=p['qualifiedDiagnosticOwnedBodies'];assert len(qualified)==866 and set(qualified).isdisjoint(remaining)and sorted(qualified+remaining)==list(range(998))
   for u,t in zip(UIDS,parts):
    fr=next(r for r in finite['rows']if r['uid']==u and r['mode']==mode);assert digest(t.tobytes())==fr['completeWorldSHA256']
   hostmap={};face_body={f:i for i in qualified for f in g['components'][i]['globalOriginalFaces']}
   for uid in UIDS:
    ids=sorted(f for i in qualified if g['components'][i]['actorUID']==uid for group in p['completeActualCensusForEveryOriginalBody'][i]['completeActualBodyCensus']['sharedEdgeConnectedComponents']for f in group)
    assert ids and all(face_body[f]in qualified for f in ids);hostmap[uid]=np.asarray(ids,int)
   records=[]
   for body_id in remaining:
    body=g['components'][body_id];ids=body['globalOriginalFaces'];inv=census(world,ids);assert len(inv['sharedEdgeConnectedComponents'])==1 and not inv['exactNonrenderingOriginalFaces']
    hostids=hostmap[body['actorUID']];hosts=world[hostids];t=world[ids]
    lo=np.nextafter(t.min((0,1))-.1,-np.inf);hi=np.nextafter(t.max((0,1))+.1,np.inf)
    mask=np.all(hosts.max(1)>=lo,axis=1)&np.all(hosts.min(1)<=hi,axis=1);selected_ids=hostids[mask];excluded_ids=hostids[~mask];selected=world[selected_ids]
    assert np.all(np.any(hosts[~mask].max(1)<lo,axis=1)|np.any(hosts[~mask].min(1)>hi,axis=1))
    selection=dict(completeQualifiedSameActorHostFaces=hostids.tolist(),selectedGlobalHostFaces=selected_ids.tolist(),allOtherHostFacesStrictlyDisjointFromOutwardBandAABB=excluded_ids.tolist(),exactFixedBandM=.1,outwardEnclosingBodyBandBounds=[lo.tolist(),hi.tolist()],completeHostWorldSHA256=digest(hosts.tobytes()),actualSelectedHostWorldSHA256=digest(selected.tobytes()),allSelectedHostsBelongToNonvisualQualifiedPaths=True)
    facets=[]
    for f in ids:
     orthogonal=facet_verify(world[f],selected);edge=None
     if not orthogonal['wholeFacetAssociated']:edge=facet_edge_verify(world[f],selected)
     passed=orthogonal['wholeFacetAssociated']or(edge is not None and edge['wholeFacetFiniteEdgeAssociated'])
     facets.append(dict(globalOriginalFace=f,completeActualFacetSHA256=digest(world[f].tobytes()),actualSubsetOrthogonalHostProofVerbatim=orthogonal,actualSubsetSingleFiniteEdgeProofVerbatim=edge,wholeFacetWithinExistingFiniteHostBand=passed));pulse()
    edgefaces=defaultdict(list)
    for f in ids:
     for a,b in zip(world[f],np.roll(world[f],-1,axis=0)):
      if tuple(a)==tuple(b):continue
      edgefaces[tuple(sorted([tuple(a),tuple(b)]))].append(f)
    boundary=[]
    for e,incident in sorted(edgefaces.items()):
     if len(incident)!=1:continue
     segment=np.asarray(e,float)
     if len(selected):proof=edge_verify(segment,selected);passed=proof['verifiedCompleteOriginalEdgeFiniteFacadeBand']
     else:proof=dict(noSelectedFiniteHostFacet=True,verifiedCompleteOriginalEdgeFiniteFacadeBand=False);passed=False
     boundary.append(dict(completeActualBoundaryEdge=[list(a)for a in e],originalIncidentFace=incident[0],actualSubsetWholeEdgeHostProofVerbatim=proof,wholeEdgeWithinExistingFiniteHostBand=passed));pulse()
    good=[r['globalOriginalFace']for r in facets if r['wholeFacetWithinExistingFiniteHostBand']]
    r=dict(originalBody=body_id,actorUID=body['actorUID'],completeOriginalFaceIds=ids,completeActualEdgeCensus=inv,completeHostSelection=selection,allActualFacetProofs=facets,allActualIncidenceOneBoundaryEdgeProofs=boundary,allFacetsWithinFixedBand=len(good)==len(ids),allBoundaryEdgesWithinFixedBand=bool(boundary)and all(e['wholeEdgeWithinExistingFiniteHostBand']for e in boundary),completeAssociatedFacetPatchCensus=census(world,good),unprovedWholeFacets=[x['globalOriginalFace']for x in facets if not x['wholeFacetWithinExistingFiniteHostBand']],unprovedWholeBoundaryEdges=[i for i,e in enumerate(boundary)if not e['wholeEdgeWithinExistingFiniteHostBand']],visualRoleAccepted=False,structuralRootOrBridgeCredit=False,sourceFunctionInferred=False,closedSolidCredit=False)
    records.append(r);pulse();print(dict(mode=mode,body=body_id,associatedFacets=len(good),facets=len(ids),associatedBoundary=sum(e['wholeEdgeWithinExistingFiniteHostBand']for e in boundary),boundary=len(boundary)),flush=True)
   assert len(records)==132;output_rows.append(dict(mode=mode,completeWorldSHA256=digest(world.tobytes()),qualifiedHostOriginalBodies=qualified,all132OriginalBodyAssociations=records,complete3172RemainingFacesAccounted=True,wholeOwnedFiniteReceipt=ref(FINITE/'result.json'),boundedHostPathReceipt=ref(PATHS/'result.json'),nativeAvailabilityNeverUsedAsVisualHost=True));pulse(True)
  assert all(ref(ROOT/r['path'])==r for r in refs);output=dict(uids=UIDS,rows=output_rows,all132OriginalBodiesRetained=True,all3172RemainingFacetsRetained=True,all47OriginalZeroFacetsPreservedUncredited=True,strictBandM=.1,sourceOnly=True,noFreshCurrentReacceptance=True,visualRoleAccepted=False,structuralRootOrBridgeCredit=False,nativeReacceptance=False,sourceGeometryChanges=0,newlyInstalled=0,evidenceRefs=refs);save(DOC/'diagnostic.json.gz',output);pulse(True)
  spec=importlib.util.spec_from_file_location('elements132_association_freeze',HERE/helpers[-1]);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.freeze(BATCH,'elements132-complete-four-stream-same-actor-qualified-host-fixed-band-diagnostic-v1',[ROOT/r['path']for r in refs]+[DOC/'diagnostic.json.gz'],dict(uids=UIDS,sourceOnly=True,completeRemainingOriginalBodies=132,completeRemainingOriginalFaces=3172,wholeFacetBodyResults={r['mode']:[b['originalBody']for b in r['all132OriginalBodyAssociations']if b['allFacetsWithinFixedBand']]for r in output_rows},currentAcceptance=False,visualRoleAccepted=False,newlyInstalled=0))
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
