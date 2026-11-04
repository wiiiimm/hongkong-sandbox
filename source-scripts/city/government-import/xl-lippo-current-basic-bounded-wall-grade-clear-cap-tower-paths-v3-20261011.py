"""Fresh unchanged-current literal BASIC exterior grade/cap paths to unchanged tower.
No whole BASIC reacceptance, absent original podium, source edits or new roots.
"""
from pathlib import Path
from fractions import Fraction as F
from collections import defaultdict,deque
import importlib.util,json
import numpy as np
from run import ROOT,HERE,read,save,digest,connect
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_shared_edge_component_census_v2_20261011 import census
from exact_original_face_conservative_clearance_v5_20261010 import verify as finite
from exact_original_upper_ground_interfaces_20261009 import exact_upper_ground_interfaces
from original_bound_facet_wall_context_v3_20261010 import best_original_vertex_exposure
from exact_original_rational_interface_segment_clearance_20261011 import verify as segment
from exact_original_shell_intersections_20261009 import rational_face,intersection_points
from exact_original_component_contacts_20261009 import contact_measure
BATCH='government-xl-lippo-current-basic-bounded-wall-grade-clear-cap-tower-paths-v3-20261011'
DOC=ROOT/'docs/astra-city/government-import'/BATCH;BASE=DOC.parent
INPUT=BASE/'government-xl-lippo-tower-only-current-complete-inputs-v3-20261011'
CONTACT=BASE/'government-xl-lippo-upper-originals-actual-basic-podium-support-diagnostic-v1-20261011'
OLD=BASE/'government-xl-lippo-actual-basic-whole-existing-parent-ground-comparison-v2-20261011'


def edge_census(tri,ids):
    edges=defaultdict(list)
    for i in ids:
        for a,b in zip(tri[i],np.roll(tri[i],-1,axis=0)):
            if not np.array_equal(a,b):edges[tuple(sorted((tuple(a),tuple(b))))].append(i)
    return edges

def main():
    assert not DOC.exists();refs=[Path(__file__)]
    for folder in [INPUT,CONTACT,OLD]:
        r=read(folder/'result.json')
        with connect() as c:
            c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(r['jobId'],)).fetchone()==('complete',r)
        refs.append(folder/'result.json')
    inputpath=INPUT/'input.json.gz';inputs=read(inputpath);manifestpath=ROOT/inputs['currentManifest']['path'];before=manifestpath.read_bytes();assert digest(before)==inputs['currentManifest']['sha256']
    geometrypath=INPUT/'complete-current-geometry.json.gz';geometry=read(geometrypath);assert geometry['startAndEndInputHashesVerified'] and geometry['sourceGeometryChanges']==geometry['terrainGeometryChanges']==0
    for path,sha in geometry['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha,path
    raw=next(r for r in geometry['completeCurrentBasicGeometry'] if r['uid']=='landsd/231645:0');body=dict(uid=raw['uid']);p=np.array(raw['position'],dtype='<f8').reshape(-1,3);idx=np.array(raw['index'],dtype=np.int64).reshape(-1,3);basic=p[idx]
    assert basic.shape==(284,3,3) and np.array_equal(p,p.astype('<f4').astype('<f8')) and raw['identityModelMatrix']==[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1]
    cs=census(basic,list(range(284)));assert len(cs['sharedEdgeConnectedComponents'])==1 and cs['completeRenderableFaceIds']==list(range(284))
    contactpath=CONTACT/'diagnostic.json.gz';contact=read(contactpath);assert contact['actualBasicWorldSHA256']==digest(basic.tobytes())
    assert contact['genuineOrdinaryBasicRootComponents']==[]
    ground_record=geometry['completeCurrentDrawnTerrain'];ground=np.array(ground_record['position'],dtype='<f8').reshape(-1,3)[np.array(ground_record['index'],dtype=np.int64).reshape(-1,3)];groundsha=digest(ground.tobytes());assert groundsha==ground_record['worldSHA256'] and np.isfinite(ground).all()
    normals=np.cross(basic[:,1]-basic[:,0],basic[:,2]-basic[:,0]);top=float(p[:,1].max());bottom=float(p[:,1].min());top_records=np.flatnonzero(np.all(basic[:,:,1]==top,axis=1)).tolist();bottoms=np.flatnonzero(np.all(basic[:,:,1]==bottom,axis=1)).tolist();caps=[i for i in top_records if normals[i,1]>0];walls=np.flatnonzero(normals[:,1]==0).tolist();reversed_top_records=[i for i in top_records if normals[i,1]<0];upward_wound_bottom_records=[i for i in bottoms if normals[i,1]>0]
    assert (len(top_records),len(walls),len(bottoms))==(70,144,70) and len(caps)==69 and len(reversed_top_records)==1 and len(upward_wound_bottom_records)==1
    assert sorted(top_records+walls+bottoms)==list(range(284))
    # Every actual BASIC roof cap is independently strictly clear over its
    # entire finite projection. The buried bottom inventory remains explicit.
    capproofs={};raw_basic=[]
    for i in range(284):
        proof=finite(basic[i],ground);raw_basic.append(dict(actualBasicFace=i,proof=proof))
        if i in top_records:
            assert proof['groundProjectionCovered'] is True and proof['existingOrdinaryClearanceBoundProved'] is True and F(proof['exactCertifiedLowerClearanceM'])>0
            if i in caps:capproofs[i]=proof
    save(DOC/'complete-actual-basic-finite-facets.json.gz',dict(faces=raw_basic,completeGroundSHA256=groundsha,topPlaneRecords=top_records,bottomPlaneRecords=bottoms,strictUpwardTopCapIDs=caps,reversedTopPlaneRecordsNoRootOrBridge=reversed_top_records,upwardWoundBottomRecordsNoRoofCredit=upward_wound_bottom_records,literalTopHeightM=top,literalBottomHeightM=bottom))
    print(json.dumps(dict(stage='actual-basic-complete-finite',faces=284,strictCaps=len(capproofs),rawNonclearFaces=[r['actualBasicFace'] for r in raw_basic if not r['proof']['existingOrdinaryClearanceBoundProved']])),flush=True)
    all_edges=edge_census(basic,list(range(284)));cap_adj={i:set() for i in caps};wall_cap=[];cap_cap=[]
    for endpoints,ids in sorted(all_edges.items()):
        capids=sorted(set(ids)&set(caps));wallids=sorted(set(ids)&set(walls))
        for a in capids:
            cap_adj[a].update(set(capids)-{a})
            for b in capids:
                if a<b:
                    assert F(capproofs[a]['exactCertifiedLowerClearanceM'])>0 and F(capproofs[b]['exactCertifiedLowerClearanceM'])>0
                    cap_cap.append(dict(caps=[a,b],exactLiteralSharedNonzeroEdge=[[str(F(float(v))) for v in q] for q in endpoints],completeFacetProofs=[capproofs[a],capproofs[b]],wholePositiveEdgeStrictlyExposedByBothCompleteFiniteFacets=True))
        for a in wallids:
            for b in capids:wall_cap.append(dict(wall=a,cap=b,exactLiteralSharedEdge=[[str(F(float(v))) for v in q] for q in endpoints],wholeCapStrictClearanceProof=capproofs[b]))
    interfaces=exact_upper_ground_interfaces(basic,walls,ground)
    grade_walls={r['sourceFace'] for r in interfaces};exposure={i:best_original_vertex_exposure(basic[i],ground) for i in sorted(grade_walls)}
    routes=[]
    for r in wall_cap:
        if r['wall'] not in grade_walls:continue
        assert F(exposure[r['wall']]['exactExposureLowerBoundM'])>0
        proof=segment(r['exactLiteralSharedEdge'],ground);assert proof['strictlyExposedWholePositiveInterface'] is True
        routes.append(dict(**r,wallExposedOriginalVertexProof=exposure[r['wall']],wholeWallCapPositiveInterface=proof,exactUpperGradeInterfaces=[v for v in interfaces if v['sourceFace']==r['wall']]))
    reached={r['cap'] for r in routes};previous={i:None for i in reached};todo=deque(sorted(reached))
    while todo:
        for j in sorted(cap_adj[todo.popleft()]):
            if j not in reached:reached.add(j);previous[j]='cap';todo.append(j)
    assert reached==set(caps),'Every claimed cap must have an exact positive roof path to an actually exposed grade wall'
    save(DOC/'bounded-basic-grade-roof-paths.json.gz',dict(completeWallCount=144,exactUpperGradeInterfaces=interfaces,allGradeWallOriginalVertexExposure=exposure,completeLiteralWallToCapEdges=wall_cap,strictlyExposedGradeWallToCapRoutes=routes,completeStrictCapGraph={k:sorted(v) for k,v in cap_adj.items()},completeRoofToRoofStrictlyExposedSharedEdges=cap_cap,allCapsReachBoundedExposedGrade=True))
    print(json.dumps(dict(stage='actual-basic-bounded-grade-cap-paths',gradeInterfaces=len(interfaces),gradeWalls=len(grade_walls),exposedWholeEdges=len(routes),allCapsReach=True)),flush=True)
    # Complete owned tower streams remain independent of BASIC rooting. This
    # diagnostic certifies actual positive interfaces only to strictly clear
    # whole participating facets; it does not reapprove BASIC bottom failures.
    row=inputs['rows'][0];assert row['uid']=='landsd/239465:0';asset=ROOT/row['candidate']['path'];assert digest(asset.read_bytes())==row['sourceSHA256']
    original=decode_original_world_triangles(asset.read_bytes());assert original.shape==(3597,3,3)
    render=geometry['row'];assert render['uid']==row['uid'] and render['sourceSHA256']==row['sourceSHA256'] and render['completeFaces']==3597
    renderidx=np.array(render['completeOriginalIndex'],dtype=np.int64).reshape(-1,3)
    worlds=[('providerOriginal',original),('actualLiteral',np.array(render['completeLiteralWorldPosition'],dtype='<f8').reshape(-1,3)[renderidx]),('explicitLeftAssociatedF32ModelMatrix',np.array(render['completeExplicitLeftAssociatedFloat32WorldPosition'],dtype='<f8').reshape(-1,3)[renderidx]),('explicitBalancedF32ModelMatrix',np.array(render['completeExplicitBalancedFloat32WorldPosition'],dtype='<f8').reshape(-1,3)[renderidx])]
    nodes=[n for n in contact['nodes'] if n['uid']==row['uid']];assert len(nodes)==5
    source_ranges={n['component']:n['completeOwnedSourceFaceIDs'] for n in nodes};upper_rows=[];computed={}
    for mode,world in worlds:
        key=digest(world.tobytes());assert world.shape==(3597,3,3) and np.isfinite(world).all()
        if key in computed:
            upper_rows.append(dict(mode=mode,completeOwnedWorldSHA256=key,exactByteIdenticalResultReused=True,**computed[key]));continue
        finite_owned=[]
        for i,face in enumerate(world):
            proof=finite(face,ground);assert proof['groundProjectionCovered'] is True and proof['existingOrdinaryClearanceBoundProved'] is True
            finite_owned.append(dict(sourceFace=i,proof=proof))
        save(DOC/('complete-tower-finite-'+mode+'.json.gz'),dict(uid=row['uid'],completeWorldSHA256=key,completeGroundSHA256=groundsha,allOwnedFaces=finite_owned))
        rawpairs=[];direct=[]
        for pair in contact['allUpperActualBasicPairs']:
            if pair['upperComponent'] not in source_ranges:continue
            proofs=[]
            for interface in pair['positiveRealFacetInterfaces']:
                cap=interface['sourceFaceB']
                if cap not in reached:continue
                # Actor order in the old contact diagnostic is Langham, then
                # tower; its complete owned source IDs bind the offset anew.
                sf=interface['sourceFaceA']-9522;assert sf in source_ranges[pair['upperComponent']]
                points=intersection_points(rational_face(world[sf]),rational_face(basic[cap]));measure=contact_measure(points) if points else dict(dimension=-1)
                if measure['dimension']<=0:continue
                ownedproof=finite_owned[sf]['proof'];assert F(ownedproof['exactCertifiedLowerClearanceM'])>0
                proofs.append(dict(ownedSourceFace=sf,actualBasicCapFace=cap,exactPositiveContactPoints=[[str(v) for v in q] for q in sorted(points)],measure=measure,wholeOwnedParticipatingFacetStrictlyClear=True,wholeActualBasicCapStrictlyClear=True))
            rawpairs.append(dict(ownedComponent=pair['upperComponent'],strictExposedCapInterfaces=proofs))
            if proofs:direct.append(pair['upperComponent'])
        adjacency={k:set() for k in source_ranges};internal=[]
        for pair in contact['internalExactUpperSourceContacts']:
            a,b=pair['components']
            if a not in adjacency or b not in adjacency:continue
            ia,ib=[i-9522 for i in pair['globalUpperSourceFaceIDs']];assert ia in source_ranges[a] and ib in source_ranges[b]
            points=intersection_points(rational_face(world[ia]),rational_face(world[ib]));measure=contact_measure(points) if points else dict(dimension=-1)
            assert measure['dimension']>0
            assert F(finite_owned[ia]['proof']['exactCertifiedLowerClearanceM'])>0 and F(finite_owned[ib]['proof']['exactCertifiedLowerClearanceM'])>0
            internal.append(dict(components=[a,b],sourceFaces=[ia,ib],exactPositiveContactPoints=[[str(v) for v in q] for q in sorted(points)],measure=measure));adjacency[a].add(b);adjacency[b].add(a)
        reached_owned=set(direct);todo=list(direct)
        while todo:
            for j in adjacency[todo.pop()]:
                if j not in reached_owned:reached_owned.add(j);todo.append(j)
        result=dict(completeOwnedFaceCount=3597,completeOwnedRealComponentCensus=census(world,list(range(3597))),directComponentsViaExposedBasicRoof=sorted(direct),completeExposedBasicCapContactProofs=rawpairs,exactInternalOwnedPositiveInterfaces=internal,componentsWithBoundedCarrierPaths=sorted(reached_owned),unresolvedComponents=sorted(set(source_ranges)-reached_owned),wholeOwnedFiniteClearanceProved=True)
        computed[key]=result;upper_rows.append(dict(mode=mode,completeOwnedWorldSHA256=key,exactByteIdenticalResultReused=False,**result));save(DOC/'upper-progress.json.gz',dict(rows=upper_rows))
        print(json.dumps(dict(mode=mode,wholeOwnedFaces=3597,boundedCarrierPaths=sorted(reached_owned),unresolved=result['unresolvedComponents'])),flush=True)
    refs += [inputpath,geometrypath,contactpath,asset,OLD/'diagnostic.json.gz',*[ROOT/path for path in geometry['inputHashes']]]
    helpers=['exact_packed_world_geometry_20261009.py','exact_original_shared_edge_component_census_v2_20261011.py','exact_original_face_conservative_clearance_v5_20261010.py','exact_original_projection_coverage_v2_20261010.py','exact_original_upper_ground_interfaces_20261009.py','original_bound_facet_wall_context_v3_20261010.py','original_bound_facet_wall_context_v2_20261010.py','exact_original_rational_interface_segment_clearance_20261011.py','exact_original_shell_intersections_20261009.py','exact_original_component_contacts_20261009.py']
    refs += [HERE/n for n in helpers]
    result=dict(uids=[body['uid'],row['uid']],currentCapturedManifest=inputs['currentManifest'],completeLiteralBasicWorldSHA256=digest(basic.tobytes()),completeActualBasicFaceCount=284,wholeActualBasicRawFiniteProofRef=str((DOC/'complete-actual-basic-finite-facets.json.gz').relative_to(ROOT)),rawOrdinaryBasicRootFailuresRetained=contact['completeBasicRootProofs'],oldParentRootFailureRetained=read(OLD/'diagnostic.json.gz')['existingParentRoot'],completeGroundSHA256=groundsha,completeGroundFaces=len(ground),boundedActualCarrierPathRef=str((DOC/'bounded-basic-grade-roof-paths.json.gz').relative_to(ROOT)),upperRows=upper_rows,originalGovernmentPodiumUsedAsSupport=False,wholeBasicReaccepted=False,currentGroundRootAccepted=False,physicalAccepted=False,installationApproved=False,newlyInstalled=0,qualification='Bounded exposed current BASIC wall/grade/strict roof paths only. Full actual BASIC bottom and ordinary rim failures remain. No missing government podium, legal ownership or load-bearing claim. Complete original/literal/left-associated/balanced declared Float32 upper-facet and exposed positive interfaces are independent. Fresh current identity, foreign BASIC/native/collision/support roles/runtime/foundation/browser remain mandatory before any acceptance.')
    assert manifestpath.read_bytes()==before
    for path,sha in geometry['inputHashes'].items():assert digest((ROOT/path).read_bytes())==sha,path
    save(DOC/'diagnostic.json.gz',result)
    sp=importlib.util.spec_from_file_location('lippo_bounded_basic_fence',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
    receipt=m.freeze(BATCH,'fresh-current-basic-bounded-exposed-grade-strict-roof-tower-four-stream-path-diagnostic-v3',refs,dict(uids=result['uids'],completeActualBasicFaces=284,completeTowerFaces=3597,originalGovernmentPodiumUsedAsSupport=False,wholeBasicReaccepted=False,currentGroundRootAccepted=False,physicalAccepted=False,installationApproved=False,newlyInstalled=0))
    print(json.dumps(dict(jobId=receipt['jobId'],towerRows=[dict(mode=r['mode'],boundedPaths=r['componentsWithBoundedCarrierPaths'],unresolved=r['unresolvedComponents']) for r in upper_rows])),flush=True)
if __name__=='__main__':main()
