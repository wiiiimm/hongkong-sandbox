"""Complete original owned bodies' edge topology in all four representations.

No body merging from quantization and no point-only connectivity credit. Every
original body is independently partitioned in each representation, including
exact nonrendering faces. Native scope remains only the complete original963
body; every other native body and its existing failures are unapproved.
"""
from pathlib import Path
import importlib.util, json, time, uuid
import numpy as np
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_shared_edge_component_census_v2_20261011 import census
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261011-langham-complete-owned-four-stream-edge-census-v1';DOC=BASE/BATCH
PROBE=BASE/'government-xl-terrain-recovery-langham-upper-complete-original-current-probe-v1-20261011';GRAPH=BASE/'xl-terrain-recovery-20261011-langham-complete-original-edge-contact-graph-v1';ACTUAL=BASE/'xl-terrain-recovery-20261011-langham-two-current-render-attribute-capture-v1'
UIDS=('landsd/79318:0','landsd/224399:0');MODES=('providerOriginal','actualLiteral','explicitLeftAssociatedF32ModelMatrix','explicitBalancedF32ModelMatrix')
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
    assert not DOC.exists();refs=[ref(Path(__file__))]
    for folder in(PROBE,GRAPH,ACTUAL):
        r=read(folder/'result.json')
        with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
        refs.extend(ref(folder/n)for n in('result.json','diagnostic.json.gz')if(folder/n).is_file())
    selection={r['uid']:r for r in read(PROBE/'selection.json.gz')['rows']};actual={r['uid']:r for r in read(ACTUAL/'actual-render-attributes.json.gz')['rows']};worlds={m:{}for m in MODES}
    for uid,count in zip(UIDS,(18086,20260)):
        row=selection[uid];a=actual[uid];asset=ROOT/row['candidate']['path'];assert row['uid']==a['uid']==uid and digest(asset.read_bytes())==row['sourceSHA256']==a['sourceSHA256'];index=np.asarray(a['completeOriginalIndex'],int).reshape(-1,3);worlds[MODES[0]][uid]=decode_original_world_triangles(asset.read_bytes())
        for mode,key in zip(MODES[1:],('completeLiteralWorldPosition','completeExplicitLeftAssociatedFloat32WorldPosition','completeExplicitBalancedFloat32WorldPosition')):worlds[mode][uid]=np.asarray(a[key],float).reshape(-1,3)[index]
        assert all(w[uid].shape==(count,3,3)and np.isfinite(w[uid]).all()for w in worlds.values());refs.append(ref(asset))
    graph=read(GRAPH/'diagnostic.json.gz');owned=[(i,p['globalOriginalFaces'])for i,p in enumerate(graph['components'])if p['actorUID']==UIDS[0]];assert len(owned)==961;body=graph['components'][963];assert body['actorUID']==UIDS[1];native=[int(i-18086)for i in body['globalOriginalFaces']];assert len(native)==2385
    refs.extend(ref(p)for p in(PROBE/'selection.json.gz',PROBE/'historical-current-manifest.json',ACTUAL/'actual-render-attributes.json.gz',HERE/'exact_packed_world_geometry_20261009.py',HERE/'exact_original_shared_edge_component_census_v2_20261011.py',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py'))
    claim=reservations.claim('langham-owned-four-edge-census-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];last=time.monotonic()
    try:
        rows=[]
        for mode in MODES:
            world=worlds[mode][UIDS[0]];complete=census(world,list(range(18086)));records=[]
            for body_id,ids in owned:
                record=census(world,ids);records.append(dict(originalBody=body_id,completeOriginalBodyFaces=ids,recomputedCompleteRepresentationEdgeCensus=record))
                if time.monotonic()-last>=20:assert reservations.heartbeat(lease)['ok'];last=time.monotonic();print(json.dumps(dict(mode=mode,ownedBodies=len(records),total=961)),flush=True)
            nativecensus=census(worlds[mode][UIDS[1]],native);split=[p['originalBody']for p in records if len(p['recomputedCompleteRepresentationEdgeCensus']['sharedEdgeConnectedComponents'])!=1]
            rows.append(dict(mode=mode,completeOwnedWorldSHA256=digest(world.tobytes()),completeOwnedGlobalCensus=complete,completeAll961OriginalBodyRepresentationCensuses=records,originalOwnedBodiesSplittingOrEntirelyNonrendering=split,native963CompleteOriginalBodyRepresentationCensus=nativecensus,otherNativeBodiesExcludedFromStructuralCredit=True));print(json.dumps(dict(mode=mode,ownedOriginalBodies=961,representationBodies=len(complete['sharedEdgeConnectedComponents']),originalBodiesSplitting=split,native963RepresentationBodies=len(nativecensus['sharedEdgeConnectedComponents']),ownedExactNonrendering=complete['exactNonrenderingOriginalFaces'])),flush=True);assert reservations.heartbeat(lease)['ok']
        assert all(ref(ROOT/r['path'])==r for r in refs);out=dict(uids=list(UIDS),rows=rows,completeOwnedFaces=18086,completeNativeBody963Faces=2385,originalAndCurrentTopologyDifferencesPreserved=True,sourceOnlyFrozenBaseline=True,frozenBaselineManifest=ref(PROBE/'historical-current-manifest.json'),noFreshCurrentReacceptance=True,noPointOnlyGlue=True,noQuantizedBodyMergeCredit=True,rootOrBridgeCredit=False,nativeReacceptance=False,currentAcceptance=False,newlyInstalled=0,evidenceRefs=refs);save(DOC/'diagnostic.json.gz',out);s=importlib.util.spec_from_file_location('freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.freeze(BATCH,'complete-langham-all961-owned-original-body-four-stream-nonzero-shared-edge-census-v1',[ROOT/r['path']for r in refs]+[DOC/'diagnostic.json.gz'],dict(uids=list(UIDS),completeOwnedFaces=18086,completeOriginalOwnedBodies=961,originalOwnedBodiesSplitting={r['mode']:r['originalOwnedBodiesSplittingOrEntirelyNonrendering']for r in rows},sourceOnly=True,nativeReacceptance=False,currentAcceptance=False,newlyInstalled=0))
    finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
