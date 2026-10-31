"""Complete remaining details versus all five end-associated visual source parts.

Conditional visual hosts cannot root/bridge or approve another visual role.
Exact complete 3D bounds reject distant scopes; any possible within-band scope
gets all complete facet and closed-edge checks at the unchanged .1m limit.
Old complete865-host negatives remain immutable. No new current capture.
"""
from pathlib import Path
from collections import defaultdict
from fractions import Fraction as F
import importlib.util,time,uuid,json
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_facet_orthogonal_finite_host_band_diagnostic_v1_20261011 import verify as facet_verify
from exact_original_edge_any_finite_distance_band_v2_20261010 import verify as edge_verify
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261011-langham-remaining14-new-visual-hosts-four-stream-diagnostic-v1';DOC=BASE/BATCH
PROBE=BASE/'government-xl-terrain-recovery-langham-upper-complete-original-current-probe-v1-20261011';GRAPH=BASE/'xl-terrain-recovery-20261011-langham-complete-original-edge-contact-graph-v1';ACTUAL=BASE/'xl-terrain-recovery-20261011-langham-two-current-render-attribute-capture-v1';MOUNTS=BASE/'xl-terrain-recovery-20261011-langham-five-authored-end-mounts-four-stream-diagnostic-v2';PRIOR=BASE/'xl-terrain-recovery-20261011-langham-remaining-14-full-host-point-context-v2'
UID='landsd/79318:0';PARTS=(91,213,214,355,476,477,550,618,630,683,711,761,830,902);HOSTS=(10,20,21,29,95);MODES=('providerOriginal','actualLiteral','explicitLeftAssociatedF32ModelMatrix','explicitBalancedF32ModelMatrix')
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def lower_distance_squared(a,b):
    lowa=[F(float(v))for v in a.min((0,1))];higha=[F(float(v))for v in a.max((0,1))];lowb=[F(float(v))for v in b.min((0,1))];highb=[F(float(v))for v in b.max((0,1))]
    return sum(max(lowa[i]-highb[i],lowb[i]-higha[i],F(0))**2 for i in range(3))
def main():
    assert not DOC.exists();refs=[ref(Path(__file__))]
    for folder in(PROBE,GRAPH,ACTUAL,MOUNTS,PRIOR):
        r=read(folder/'result.json')
        with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
        refs.extend(ref(folder/n)for n in('result.json','diagnostic.json.gz')if(folder/n).is_file())
    row=next(r for r in read(PROBE/'selection.json.gz')['rows']if r['uid']==UID);a=next(r for r in read(ACTUAL/'actual-render-attributes.json.gz')['rows']if r['uid']==UID);asset=ROOT/row['candidate']['path'];assert row['uid']==a['uid']==UID and digest(asset.read_bytes())==row['sourceSHA256']==a['sourceSHA256'];index=np.asarray(a['completeOriginalIndex'],int).reshape(-1,3);worlds=[decode_original_world_triangles(asset.read_bytes())]+[np.asarray(a[k],float).reshape(-1,3)[index]for k in('completeLiteralWorldPosition','completeExplicitLeftAssociatedFloat32WorldPosition','completeExplicitBalancedFloat32WorldPosition')];assert all(w.shape==(18086,3,3)and np.isfinite(w).all()for w in worlds)
    g=read(GRAPH/'diagnostic.json.gz');mounts=read(MOUNTS/'diagnostic.json.gz');assert mounts['allFiveEndPatchSetsPositiveAllFourStreams']is True;hostids=sorted(f for b in HOSTS for f in g['components'][b]['globalOriginalFaces']);assert len(hostids)==566;sourceids=sorted(f for b in PARTS for f in g['components'][b]['globalOriginalFaces']);assert len(sourceids)==54 and not set(sourceids)&set(hostids)
    refs.extend(ref(p)for p in(asset,PROBE/'selection.json.gz',PROBE/'historical-current-manifest.json',ACTUAL/'actual-render-attributes.json.gz',HERE/'exact_packed_world_geometry_20261009.py',HERE/'exact_original_facet_orthogonal_finite_host_band_diagnostic_v1_20261011.py',HERE/'exact_original_surface_coordinate_band_20261010.py',HERE/'exact_original_projection_coverage_20261009.py',HERE/'exact_original_edge_any_finite_distance_band_v2_20261010.py',HERE/'exact_original_edge_any_finite_distance_band_v1_20261010.py',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py'))
    claim=reservations.claim('langham-remaining14-new-visual-hosts-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];last=time.monotonic()
    try:
        rows=[]
        for mode,w in zip(MODES,worlds):
            m=next(p for p in mounts['rows']if p['mode']==mode);assert m['completeOwnedWorldSHA256']==digest(w.tobytes());records=[]
            for body in PARTS:
                ids=g['components'][body]['globalOriginalFaces'];source=w[ids];bounds=[]
                for h in HOSTS:
                    hs=g['components'][h]['globalOriginalFaces'];distance=lower_distance_squared(source,w[hs]);bounds.append(dict(completeOriginalConditionalVisualHostBody=h,completeHostFaces=hs,completeHostSHA256=digest(w[hs].tobytes()),completeHostBounds=[w[hs].min((0,1)).tolist(),w[hs].max((0,1)).tolist()],exactConservative3DAABBDistanceSquaredM2=str(distance),exactEntireHostOutsideExistingBand=distance>F(.1)**2))
                candidates=[p for p in bounds if not p['exactEntireHostOutsideExistingBand']];facets=[];boundary=[]
                if candidates:
                    hs=sorted(f for p in candidates for f in p['completeHostFaces']);facets=[dict(sourceFace=i,completeFacetBand=facet_verify(w[i],w[hs]))for i in ids];inc=defaultdict(list)
                    for i in ids:
                        for u,v in zip(w[i],np.roll(w[i],-1,axis=0)):
                            if tuple(u)!=tuple(v):inc[tuple(sorted((tuple(u),tuple(v))))].append(i)
                    boundary=[dict(completeOriginalEdge=edge,completeOriginalSourceIncidences=fs,completeEdgeBand=edge_verify(np.asarray(edge),w[hs]))for edge,fs in sorted(inc.items())if len(fs)==1]
                records.append(dict(originalBody=body,completeOriginalSourceFaces=ids,completeActualSourceTrianglesSHA256=digest(source.tobytes()),completeActualSourceBounds=[source.min((0,1)).tolist(),source.max((0,1)).tolist()],allFiveCompleteConditionalVisualHostBounds=bounds,allFiveCompleteHostsOutsideExistingBand=not candidates,completeWholeFacetDiagnosticsIfRequired=facets,completeBoundaryDiagnosticsIfRequired=boundary,visualHostRootOrBridgeCredit=False));print(json.dumps(dict(mode=mode,body=body,allFiveHostsOutsideBand=not candidates,closestConservativeSquaredDistance=min(float(F(p['exactConservative3DAABBDistanceSquaredM2']))for p in bounds))),flush=True)
                if time.monotonic()-last>=20:assert reservations.heartbeat(lease)['ok'];last=time.monotonic()
            rows.append(dict(mode=mode,completeOwnedWorldSHA256=digest(w.tobytes()),complete54RemainingFacets=sourceids,complete566NewConditionalVisualHostFacets=hostids,completeFourteenSourceDetails=records));assert reservations.heartbeat(lease)['ok']
        assert all(ref(ROOT/r['path'])==r for r in refs);out=dict(uids=[UID],rows=rows,allFourRepresentationsAccounted=True,wholeComponentBoundsIncludeEveryOriginalReferencedVertex=True,conditionalHostsNotCurrentQualifiedHosts=True,strictBandM=.1,prior865HostNegativesPreserved=ref(PRIOR/'diagnostic.json.gz'),sourceOnlyFrozenBaseline=True,frozenBaselineManifest=ref(PROBE/'historical-current-manifest.json'),noFreshCurrentReacceptance=True,authoredVisualRoleAccepted=False,structuralRootCredit=False,structuralBridgeCredit=False,nativeReacceptance=False,currentAcceptance=False,newlyInstalled=0,evidenceRefs=refs);save(DOC/'diagnostic.json.gz',out);s=importlib.util.spec_from_file_location('freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.freeze(BATCH,'complete-langham14-source-details-versus-all5-conditional-endmounted-visual-hosts-four-stream-v1',[ROOT/r['path']for r in refs]+[DOC/'diagnostic.json.gz'],dict(uids=[UID],completeOriginalDetails=14,completeConditionalVisualHostParts=5,sourceOnly=True,currentAcceptance=False,newlyInstalled=0))
    finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
