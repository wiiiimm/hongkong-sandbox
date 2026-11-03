"""Exact private graph diagnostic: all seams and ordinary native surface guards.

No publication route, source acceptance or renewed historical marker is created.
"""
import copy,sys,uuid
from pathlib import Path
from contextlib import contextmanager
import shapely
from run import ROOT,HERE,read,save,digest,reservations
from china_ferry_current_foundations_v1_20261020 import authenticate
from observed_reserved_runner_v4_20261103 import execute_reserved
from primrose_compound_foundation_v2_20261015 import module
import nested_coordinated_native_boundary_v1_20261027 as nested
import nested_native_terrain_validation_v1_20261027 as native
from fuying_whole_parent_five_boundary_v1_20261029 import finite_callback
from one_peking_nested_cycle_boundary_v3_20261101 import declare_roundoff
BASE=ROOT/'docs/astra-city/government-import'
BATCH='government-xl-silvercord-lippo-graph-surface-diagnostic-v4-20261103'
CANDIDATE='government-xl-silvercord-lippo-complete-floor-candidate-v4-20261103'
LOCAL=HERE/'local'/BATCH
UIDS=['landsd/233997:0','landsd/231645:0']

def owned():
 lease=read(LOCAL/'reservation.json');assert reservations.owns(lease)
 proposal,pins=authenticate(BASE/CANDIDATE);path=ROOT/proposal['candidate']['path'];assert digest(path.read_bytes())==proposal['candidate']['sha256'];parent=read(path)
 old=ROOT/'3d-viewer'/proposal['replacedParent']['url'];assert digest(old.read_bytes())==proposal['replacedParent']['sha256']
 # Bind the entire old parent and exact constructed successor, regardless of
 # unrelated live June Garden catalogue transitions. This diagnostic cannot
 # grant current-scene source/actor/publication approval.
 ids=[12,15,17]+list(range(18,len(parent['patches'])));assert len(ids)>12
 nodes={str(i):copy.deepcopy(parent['patches'][i]) for i in ids}
 north_ref=proposal['additionalTopLevelPatch'];north_path=ROOT/north_ref['path'];assert digest(north_path.read_bytes())==north_ref['sha256'];nodes['north']=read(north_path)
 root_path=ROOT/'3d-viewer/city/data/terrain.json';assert digest(root_path.read_bytes())==north_ref['parentSHA256'];root_parent=read(root_path)
 for name,node in nodes.items():
  node['nativeMesh']['source'].pop('coordinatedBoundary',None)
  node['nativeMesh']['source'].pop('numericalCoverageGap',None)
  declare_roundoff(node)
 rectangles={n:shapely.box(*nested.bounds(p)) for n,p in nodes.items()};edges=[];callbacks={n:[] for n in nodes};failures=[]
 for i,a in enumerate(sorted(nodes)):
  for b in sorted(nodes)[i+1:]:
   assert rectangles[a].intersection(rectangles[b]).area==0
   shared=rectangles[a].boundary.intersection(rectangles[b].boundary)
   if shared.is_empty or shared.geom_type=='Point':continue
   assert shared.geom_type=='LineString' and shared.length>0
   row=dict(members=[a,b],sharedLengthM=shared.length,passed=False)
   try:
    pair={a:nodes[a],b:nodes[b]}
    callbacks[a].append(finite_callback(pair,a));callbacks[b].append(finite_callback(pair,b));row['passed']=True
   except AssertionError as error:row['error']=str(error);failures.append(row)
   edges.append(row)
 assert set(n for row in edges for n in row['members'])==set(nodes)
 out=BASE/BATCH;save(out/'finite-seams.json',edges);checks=[]
 original=nested.coordinated_boundary
 try:
  for name,node in nodes.items():
   candidate=copy.deepcopy(node);candidate['nativeMesh']['source']['coordinatedBoundary']={'diagnosticMember':name}
   expected=copy.deepcopy(candidate);current_parent=root_parent if name=='north'else parent
   def dispatch(actual,actual_parent):
    assert actual==expected and actual_parent is current_parent
    return lambda x,y,z:any(f(x,y,z)for f in callbacks[name])
   nested.coordinated_boundary=dispatch
   check=dict(member=name,passed=False)
   try:native.validate_native_mesh(candidate,current_parent);check['passed']=True
   except AssertionError as error:check['error']=str(error)
   checks.append(check)
 finally:nested.coordinated_boundary=original
 save(out/'native-surface-checks.json',checks)
 result=dict(uids=UIDS,candidate=proposal['candidate'],replacedParent=proposal['replacedParent'],allConnectedMembersAccountedFor=True,connectedMemberCount=len(nodes),edges=edges,surfaceChecks=checks,allFiniteSeamsPassed=all(r['passed']for r in edges),allMemberSurfaceChecksPassed=all(r['passed']for r in checks),historicalCycleApprovalTransferred=False,sourceGeometryChanges=0,terrainValidatorPassed=False,physicalAcceptance=False,installationApproved=False,publication=False,next='Fresh exact graph admission/whole-parent validation and full current native/BASIC/source/runtime/browser checks remain mandatory. Diagnostic callbacks are private; no production validator changed.')
 save(out/'summary.json',result);assert reservations.owns(lease)
 refs=[north_path,root_path,Path(__file__),BASE/CANDIDATE/'result.json',path,old,HERE/'nested_native_terrain_validation_v1_20261027.py',HERE/'nested_coordinated_native_boundary_v1_20261027.py',HERE/'one_peking_nested_cycle_boundary_v3_20261101.py',HERE/'fuying_whole_parent_five_boundary_v1_20261029.py',HERE/'coordinated_native_boundary_v1_20261023.py',HERE/'finite_native_boundary_strip_v1_20261023.py',HERE/'float32_coverage.py']
 module('silvercord_lippo_graph_surface_freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py').freeze(BATCH,'private-complete-work-envelope-finite-graph-surface-diagnostic',refs,result)
 print({k:result[k]for k in ['allFiniteSeamsPassed','allMemberSurfaceChecksPassed','installationApproved']},flush=True)

if __name__=='__main__':
 if '--owned' in sys.argv:owned()
 else:
  assert not LOCAL.exists() and not(BASE/BATCH).exists()
  parent=read(BASE/CANDIDATE/'summary.json')['replacedParent'];retained=read(ROOT/'3d-viewer'/parent['url'])['meta']['targetUids'];keys={'building:'+u for u in retained+UIDS}|{'terrain:'+parent['url'],'immutable-source-proof:'+BATCH}
  claim=reservations.claim('pair-private-full-graph-'+str(uuid.uuid4()),sorted(keys),batch=BATCH,ttl=3600);assert claim['ok']
  execute_reserved(claim['reservation'],LOCAL/'reservation.json',[sys.executable,__file__,'--owned'])
