"""Every exact original/current point interface for 14 unresolved source details.

Complete54 facets versus complete conditional geometric host scope in all four
representations. Point-only contacts are evidence for potential visual mounting,
never a structural edge, root, bridge, function or actual role approval.
"""
from pathlib import Path
import importlib.util,time,uuid,json
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_shell_intersections_20261009 import rational_face,intersection_points
from exact_original_component_contacts_20261009 import contact_measure
from exact_original_shared_edge_component_census_v2_20261011 import exact_nonrendering
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261011-langham-remaining-14-full-host-point-context-v1';DOC=BASE/BATCH
PROBE=BASE/'government-xl-terrain-recovery-langham-upper-complete-original-current-probe-v1-20261011';GRAPH=BASE/'xl-terrain-recovery-20261011-langham-complete-original-edge-contact-graph-v1';ACTUAL=BASE/'xl-terrain-recovery-20261011-langham-two-current-render-attribute-capture-v1';HOSTS=BASE/'xl-terrain-recovery-20261011-langham-565-complete-literal-rooted-host-search-v1'
UIDS=('landsd/79318:0','landsd/224399:0');PARTS=(91,213,214,355,476,477,550,618,630,683,711,761,830,902);MODES=('providerOriginal','actualLiteral','explicitLeftAssociatedF32ModelMatrix','explicitBalancedF32ModelMatrix')
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
    assert not DOC.exists();refs=[ref(Path(__file__))]
    for folder in(PROBE,GRAPH,ACTUAL,HOSTS):
        r=read(folder/'result.json')
        with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
        refs.extend(ref(folder/n)for n in('result.json','diagnostic.json.gz')if(folder/n).is_file())
    selection={r['uid']:r for r in read(PROBE/'selection.json.gz')['rows']};actual={r['uid']:r for r in read(ACTUAL/'actual-render-attributes.json.gz')['rows']};worlds={m:[]for m in MODES}
    for uid,count in zip(UIDS,(18086,20260)):
        row=selection[uid];a=actual[uid];asset=ROOT/row['candidate']['path'];assert row['uid']==a['uid']==uid and digest(asset.read_bytes())==row['sourceSHA256']==a['sourceSHA256'];index=np.asarray(a['completeOriginalIndex'],int).reshape(-1,3);worlds[MODES[0]].append(decode_original_world_triangles(asset.read_bytes()))
        for mode,key in zip(MODES[1:],('completeLiteralWorldPosition','completeExplicitLeftAssociatedFloat32WorldPosition','completeExplicitBalancedFloat32WorldPosition')):worlds[mode].append(np.asarray(a[key],float).reshape(-1,3)[index])
        assert all(w[-1].shape==(count,3,3)and np.isfinite(w[-1]).all()for w in worlds.values());refs.append(ref(asset))
    worlds={m:np.concatenate(p)for m,p in worlds.items()};graph=read(GRAPH/'diagnostic.json.gz');h=read(HOSTS/'diagnostic.json.gz');hosts=h['completeAllowedLiteralHostFaces'];assert len(hosts)==19759 and hosts==sorted(set(hosts));membership={f:i for i,p in enumerate(graph['components'])for f in p['globalOriginalFaces']};partfaces={b:graph['components'][b]['globalOriginalFaces']for b in PARTS};faces=sorted(f for fs in partfaces.values()for f in fs);assert len(faces)==54 and all(f<18086 for f in faces)and not set(faces)&set(hosts);assert digest(worlds['actualLiteral'].tobytes())==h['completeActualLiteralWorldSHA256']
    refs.extend(ref(p)for p in(PROBE/'selection.json.gz',PROBE/'historical-current-manifest.json',ACTUAL/'actual-render-attributes.json.gz',HERE/'exact_packed_world_geometry_20261009.py',HERE/'exact_original_shell_intersections_20261009.py',HERE/'exact_original_component_contacts_20261009.py',HERE/'exact_original_shared_edge_component_census_v2_20261011.py',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py'))
    claim=reservations.claim('langham-14-point-context-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];last=time.monotonic()
    try:
        rows=[]
        for mode,w in worlds.items():
            hosttri=w[hosts];tree=shapely.STRtree(shapely.box(hosttri[:,:,0].min(1),hosttri[:,:,2].min(1),hosttri[:,:,0].max(1),hosttri[:,:,2].max(1)));rational={};contacts=[];tested=0
            def exact(i):
                if i not in rational:rational[i]=rational_face(w[i])
                return rational[i]
            for face in faces:
                t=w[face];assert not exact_nonrendering(t)
                for j in tree.query(shapely.box(t[:,0].min(),t[:,2].min(),t[:,0].max(),t[:,2].max())):
                    host=hosts[int(j)];u=w[host]
                    if np.any(t.min(0)>u.max(0))or np.any(u.min(0)>t.max(0))or exact_nonrendering(u):continue
                    p=contact_measure(intersection_points(exact(face),exact(host)));tested+=1
                    if p['dimension']>=0:contacts.append(dict(sourceFace=face,sourceBody=membership[face],hostFace=host,originalHostBody=membership[host],exactContact=p))
                    if time.monotonic()-last>=20:assert reservations.heartbeat(lease)['ok'];last=time.monotonic();print(json.dumps(dict(mode=mode,exactPairsTested=tested,rawInterfaces=len(contacts))),flush=True)
            summary=[dict(originalBody=b,completeOriginalSourceFaces=partfaces[b],allExactPointInterfaces=[p for p in contacts if p['sourceBody']==b and p['exactContact']['dimension']==0],allPositiveDimensionalInterfaces=[p for p in contacts if p['sourceBody']==b and p['exactContact']['dimension']>0])for b in PARTS];rows.append(dict(mode=mode,completeCombinedWorldSHA256=digest(w.tobytes()),complete54SourceFaces=faces,completeConditionalHostFaces=hosts,exactCandidatePairsTested=tested,allOriginalSourceToConditionalHostContacts=contacts,perCompleteOriginalBody=summary));print(json.dumps(dict(mode=mode,exactPairsTested=tested,pointContacts=sum(p['exactContact']['dimension']==0 for p in contacts),positiveContacts=sum(p['exactContact']['dimension']>0 for p in contacts),bodiesWithAnyPointContact=[r['originalBody']for r in summary if r['allExactPointInterfaces']])),flush=True);assert reservations.heartbeat(lease)['ok']
        assert all(ref(ROOT/r['path'])==r for r in refs);out=dict(uids=list(UIDS),rows=rows,completeOriginalUnresolvedBodies=list(PARTS),completeEveryRenderableCandidatePairAccounted=True,rawPositiveGraphAndPreviousFiniteFailuresPreserved=True,conditionalHostScopeIsNotIndependentCurrentRootApproval=True,pointOnlyContactsCannotRootOrBridge=True,sourceOnlyFrozenBaseline=True,frozenBaselineManifest=ref(PROBE/'historical-current-manifest.json'),noFreshCurrentReacceptance=True,noArchitecturalFunctionInferred=True,authoredVisualRoleAccepted=False,structuralRootCredit=False,structuralBridgeCredit=False,nativeReacceptance=False,currentAcceptance=False,newlyInstalled=0,evidenceRefs=refs);save(DOC/'diagnostic.json.gz',out);s=importlib.util.spec_from_file_location('freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.freeze(BATCH,'complete-langham14-unresolved54-facet-four-stream-exact-point-context-no-rootcredit-v1',[ROOT/r['path']for r in refs]+[DOC/'diagnostic.json.gz'],dict(uids=list(UIDS),completeSourceDetailFacets=54,completeOriginalBodies=14,pointOnlyCannotRoot=True,sourceOnly=True,currentAcceptance=False,newlyInstalled=0))
    finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
