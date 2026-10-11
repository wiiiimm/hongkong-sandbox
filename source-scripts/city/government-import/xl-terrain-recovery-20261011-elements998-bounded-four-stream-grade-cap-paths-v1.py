"""Bounded native998 grade-to-exposed-interface diagnosis in four streams.

The complete184716-face native body supplies adjacency, not a root seed.
Only explicitly verified finite faces/edges/grade intervals are path witnesses.
Unqualified native geometry, exact-negative interactions and all owned bodies
remain separate obligations. No architecture/current/native acceptance.
"""
from pathlib import Path
from collections import defaultdict,deque
from fractions import Fraction as F
import importlib.util,time,uuid
import numpy as np
import shapely
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from exact_original_shared_edge_component_census_v2_20261011 import exact_nonrendering
from exact_original_shell_intersections_20261009 import rational_face,intersection_points
from exact_original_component_contacts_20261009 import contact_measure
from exact_original_face_conservative_clearance_v5_20261010 import verify as finite_verify
from exact_closed_ground_aabb_pruning_v1_20261011 import CompleteGround
BASE=ROOT/'docs/astra-city/government-import';BATCH='xl-terrain-recovery-20261011-elements998-bounded-four-stream-grade-cap-paths-v1';DOC=BASE/BATCH
GRAPH=BASE/'xl-terrain-recovery-20261011-elements-complete-owned-original-contact-graph-v1';PHYSICAL=BASE/'government-xl-terrain-recovery-elements-sun-star-unchanged-current-physical-v1-20261011';OWNATTR=BASE/'xl-terrain-recovery-20261011-elements-sun-star-two-current-render-attribute-capture-v1';NATIVEATTR=BASE/'xl-terrain-recovery-20261011-elements-two-native-current-render-ground-capture-v1'
OWN=['landsd/204145:0','landsd/204143:0'];NATIVE='landsd/273061:0';UIDS=OWN+[NATIVE,'landsd/204144:0'];OFFSETS=[0,12129,23809,227547]
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();refs=[ref(Path(__file__))]
 for folder in [GRAPH,PHYSICAL,OWNATTR,NATIVEATTR]:
  receipt=read(folder/'result.json')
  with connect()as c:c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
  refs.append(ref(folder/'result.json'))
 graph=read(GRAPH/'diagnostic.json.gz');native_rows=read(NATIVEATTR/'native-render-ground.json.gz')['rows'];assert[r['uid']for r in native_rows]==UIDS[2:];native={r['uid']:r for r in native_rows};owned_rows=read(OWNATTR/'actual-render-attributes.json.gz')['rows'];assert[r['uid']for r in owned_rows]==OWN;actual={r['uid']:r for r in owned_rows+native_rows};original={}
 for source in graph['binding']['completeSourceInputs']:
  asset=ROOT/source['asset']['path'];assert ref(asset)==source['asset'];original[source['uid']]=decode_original_world_triangles(asset.read_bytes());assert actual[source['uid']]['sourceSHA256']==source['sourceSHA256'];refs.append(ref(asset))
 assert digest(np.concatenate([original[u]for u in UIDS]).tobytes())==graph['binding']['completeOriginalWorldSHA256'];component=graph['components'][998];assert component['actorUID']==NATIVE;body=[i-23809 for i in component['globalOriginalFaces']];assert len(body)==184716 and len(original[NATIVE])==203738
 assert native[NATIVE]['rawCurrentNativeEntry']==graph['binding']['completeSourceInputs'][2]['rawCurrentNativeEntry'];ground=np.asarray(native[NATIVE]['drawnGroundGeometry'],float).reshape(-1,3,3);assert len(ground)>0
 contacts=[r for r in graph['oneExactPositiveWitnessPerOwnedInvolvingBodyPair']if r['components'][1]==998];assert len(contacts)==20 and all(r['components'][0]<998 for r in contacts)
 helpers=[HERE/n for n in ['exact_packed_world_geometry_20261009.py','exact_original_shared_edge_component_census_v2_20261011.py','exact_original_shell_intersections_20261009.py','exact_original_component_contacts_20261009.py','exact_original_face_conservative_clearance_v5_20261010.py','exact_original_projection_coverage_v2_20261010.py','exact_original_rational_interface_segment_clearance_20261011.py','exact_original_upper_ground_interfaces_20261009.py','exact_closed_ground_aabb_pruning_v1_20261011.py','test_exact_closed_ground_aabb_pruning_v1_20261011.py','xl-popcorn-source-investigations-checkpoints-20261009.py']];refs.extend(ref(p)for p in helpers);refs.extend(ref(p)for p in [GRAPH/'diagnostic.json.gz',OWNATTR/'actual-render-attributes.json.gz',NATIVEATTR/'native-render-ground.json.gz',NATIVEATTR/'native-render-inputs.json.gz',NATIVEATTR/'historical-current-manifest.json',PHYSICAL/'metrics.json',PHYSICAL/'foundation.json',PHYSICAL/'native-neighbour-checks.json'])
 claim=reservations.claim('elements998-bounded-paths-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600);assert claim['ok'];lease=claim['reservation'];last=time.monotonic()
 def pulse(force=False):
  nonlocal last
  if force or time.monotonic()-last>=20:assert reservations.heartbeat(lease)['ok']and reservations.owns(lease);last=time.monotonic()
 try:
  prepared_ground=CompleteGround(ground);assert np.array_equal(prepared_ground.ground,ground);ground_tree=shapely.STRtree(shapely.box(ground[:,:,0].min(axis=1),ground[:,:,2].min(axis=1),ground[:,:,0].max(axis=1),ground[:,:,2].max(axis=1)));results=[]
  for mode,field in [('providerOriginal',None),('actualLiteral','completeLiteralWorldPosition'),('explicitLeftFloat32','completeExplicitLeftAssociatedFloat32WorldPosition'),('explicitBalancedFloat32','completeExplicitBalancedFloat32WorldPosition')]:
   worlds={u:original[u]if field is None else np.asarray(actual[u][field],float).reshape(-1,3)[np.asarray(actual[u]['completeOriginalIndex'],int).reshape(-1,3)]for u in UIDS};assert[len(worlds[u])for u in UIDS]==[12129,11680,203738,11166];world=worlds[NATIVE];edgefaces=defaultdict(list);faceedges={};zeros=[];normal_y={}
   for i in body:
    if exact_nonrendering(world[i]):zeros.append(i);continue
    n=np.cross(world[i][1]-world[i][0],world[i][2]-world[i][0]);normal_y[i]=float(n[1]/np.linalg.norm(n));faceedges[i]=[]
    for a,b in zip(world[i],np.roll(world[i],-1,axis=0)):
     if tuple(a)==tuple(b):continue
     edge=tuple(sorted([tuple(a),tuple(b)]));edgefaces[edge].append(i);faceedges[i].append(edge)
    if i%2500==0:pulse()
   possible_cache={};finite_cache={};grade_cache={};edge_cache={};paths=[]
   def possible(i):
    if i not in possible_cache:
     t=world[i];ids=ground_tree.query(shapely.box(t[:,0].min(),t[:,2].min(),t[:,0].max(),t[:,2].max()));possible_cache[i]=bool(len(ids))and float(t[:,1].min())>float(ground[ids,:,1].max())
    return possible_cache[i]
   def finite(i):
    if i not in finite_cache:finite_cache[i]=finite_verify(world[i],ground);pulse()
    return finite_cache[i]
   def strict(i):
    proof=finite(i);return proof['groundProjectionCovered']is True and F(proof['exactCertifiedLowerClearanceM'])>0
   def edge_proof(edge):
    if edge not in edge_cache:edge_cache[edge]=prepared_ground.segment([[str(F(float(v)))for v in p]for p in edge]);pulse()
    return edge_cache[edge]
   for contact in contacts:
    owned_body=contact['components'][0];own_uid=graph['components'][owned_body]['actorUID'];source_offset=OFFSETS[UIDS.index(own_uid)];own_face=contact['globalOriginalFaces'][0]-source_offset;target=contact['globalOriginalFaces'][1]-23809;assert target in body;points=[]
    if not exact_nonrendering(world[target])and not exact_nonrendering(worlds[own_uid][own_face]):points=intersection_points(rational_face(worlds[own_uid][own_face]),rational_face(world[target]))
    measure=contact_measure(points)if points else None
    if field is None:assert measure==contact['exactContact'],'Original contact ordering/value must replay exactly'
    record=dict(ownedBody=owned_body,ownedUID=own_uid,ownedFace=own_face,nativeFace=target,originalContact=contact,actualExactContact=measure,actualPositiveDimensionalContact=bool(measure and measure['dimension']>0),diagnosticStrictGradeCapPath=False)
    if not record['actualPositiveDimensionalContact']or target not in faceedges or not possible(target)or not strict(target):record['reason']='exact-interface-or-full-strict-facet-unproved';paths.append(record);continue
    contact_edge=[measure['exactPoints'][0],measure['exactPoints'][-1]];interaction=prepared_ground.segment(contact_edge);record['wholeContactNativeFaceProof']=finite(target);record['exactContactDiagonalOrSegmentProof']=interaction
    if not interaction['strictlyExposedWholePositiveInterface']:record['reason']='whole-positive-interface-exposure-unproved';paths.append(record);continue
    start=(target,normal_y[target]>.15);queue=deque([start]);parents={start:None};chosen=None;selected_grade=None
    while queue and chosen is None:
     state=queue.popleft();i,cap_seen=state
     for edge in faceedges[i]:
      for j in edgefaces[edge]:
       if j==i:continue
       if possible(j):
        other=(j,cap_seen or normal_y[j]>.15)
        if other not in parents:parents[other]=(state,edge);queue.append(other)
       elif cap_seen and abs(normal_y[j])<=.15:
        if j not in grade_cache:grade_cache[j]=prepared_ground.grade(world,j);pulse()
        if grade_cache[j]['exactUpperGroundIntervals']and edge_proof(edge)['strictlyExposedWholePositiveInterface']:chosen=state;selected_grade=(j,edge);break
      if chosen is not None:break
     pulse()
    if chosen is None:record['reason']='no-bounded-conservatively-clear-edge-path-to-exact-grade-wall';paths.append(record);continue
    sequence=[];edges=[];cur=chosen
    while cur is not None:
     sequence.append(cur[0]);parent=parents[cur]
     if parent is None:break
     cur,edge=parent;edges.append(edge)
    sequence.reverse();edges.reverse();verified_faces=[dict(nativeFace=i,completeFiniteProof=finite(i))for i in sequence];verified_edges=[dict(exactEdge=[[str(F(float(v)))for v in p]for p in edge],completeEdgeProof=edge_proof(edge))for edge in edges];grade_face,grade_edge=selected_grade
    record.update(selectedNativeFacesFromContactToGrade=sequence,completeSelectedFiniteFaces=verified_faces,completeSelectedStrictEdges=verified_edges,gradeWall=dict(nativeFace=grade_face,exactUpperGroundIntervals=grade_cache[grade_face]['exactUpperGroundIntervals'],completeGroundSubsetWitness=grade_cache[grade_face],wholeRawFiniteProof=finite(grade_face),exactExposedSharedEdge=[[str(F(float(v)))for v in p]for p in grade_edge],wholeSharedEdgeProof=edge_proof(grade_edge)),upwardCapFaces=[i for i in sequence if normal_y[i]>.15]);record['diagnosticStrictGradeCapPath']=bool(record['upwardCapFaces'])and all(strict(i)for i in sequence)and all(p['completeEdgeProof']['strictlyExposedWholePositiveInterface']for p in verified_edges)and record['gradeWall']['wholeRawFiniteProof']['groundProjectionCovered']is True
    if not record['diagnosticStrictGradeCapPath']:record['reason']='selected-whole-facet-edge-or-grade-coverage-unproved'
    paths.append(record);pulse();print(dict(mode=mode,ownedBody=owned_body,path=record['diagnosticStrictGradeCapPath'],selectedFaces=len(sequence)),flush=True)
   results.append(dict(mode=mode,completeWorldSHA256={u:digest(worlds[u].tobytes())for u in UIDS},completeGroundSHA256=digest(ground.tobytes()),completeNativeBodyOriginalFaces=body,actualExactZeroNativeBodyFacesRetained=zeros,nonzeroActualNativeBodyFaces=len(faceedges),all20OriginalInterfacesAccounted=paths,provedSelectedPaths=sum(r['diagnosticStrictGradeCapPath']for r in paths),allOtherNativeFacesUnqualified=True));pulse(True)
  prepared_ground.verify_binding();assert all(ref(ROOT/r['path'])==r for r in refs);output=dict(uids=UIDS,rows=results,completeOriginalFaces=238713,completeOwnedBodies=998,completeOriginalNativeBodyFaces=184716,originalGraph=ref(GRAPH/'diagnostic.json.gz'),actualNativeCapture=ref(NATIVEATTR/'native-render-ground.json.gz'),allNativeLegacyFindingsPreserved=True,nativeBodyReceivesNoRootSeed=True,wholeNativeReacceptance=False,rootOrStructuralContactCredit=False,currentAcceptance=False,sourceGeometryChanges=0,terrainChanges=0,sourceOnly=True,arithmeticLimitations='Original/literal/two specified explicit F32 orders only; no universal GPU/camera guarantee.',frozenBaselineManifest=ref(NATIVEATTR/'historical-current-manifest.json'),evidenceRefs=refs);save(DOC/'diagnostic.json.gz',output);pulse(True)
  spec=importlib.util.spec_from_file_location('elements998_path_freeze',helpers[-1]);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.freeze(BATCH,'elements998-bounded-original-literal-explicit-float32-grade-cap-path-diagnosis-v1',[ROOT/r['path']for r in refs]+[DOC/'diagnostic.json.gz'],dict(uids=UIDS,provedSelectedPaths={r['mode']:r['provedSelectedPaths']for r in results},sourceOnly=True,rootOrStructuralContactCredit=False,nativeReacceptance=False,currentAcceptance=False,newlyInstalled=0))
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
