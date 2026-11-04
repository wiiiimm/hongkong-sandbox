"""Exact 76-face source-specific visual proposal; grounded hosts still needed.

Preserves four unmatched single faces, box91, all other source details, old
whole-facet interior negatives and the actual literal body565 contact failure.
No structural roots, bridges, native reapproval or import acceptance.
"""
from pathlib import Path
import hashlib,importlib.util,time,uuid
from run import ROOT,HERE,read,save,digest,connect,reservations
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
from original_triangular_opening_panel_source_role_v1_20261011 import verify,canonical
BASE=ROOT/'docs/astra-city/government-import'
BATCH='xl-terrain-recovery-20261011-langham-original-76-opening-panel-source-proposal-v1';DOC=BASE/BATCH
LOOPS=BASE/'xl-terrain-recovery-20261011-langham-single-panel-original-host-boundary-loops-v1'
GRAPH=BASE/'xl-terrain-recovery-20261011-langham-complete-original-edge-contact-graph-v1'
VISUAL=BASE/'xl-terrain-recovery-20261011-langham-panel-original-loop-context-v1'
PATHS=BASE/'xl-terrain-recovery-20261011-langham-owned-bounded-carrier-paths-v1'
LITERAL=BASE/'xl-terrain-recovery-20261011-langham-565-complete-literal-rooted-host-search-v1'
UID='landsd/79318:0'
SHA='1be9a6399ce7e447ae734182f278bef08e7bbb58aa97cb8a468b133d175c00e4'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def main():
 assert not DOC.exists();refs=[ref(Path(__file__))]
 for folder in [LOOPS,GRAPH,VISUAL,PATHS,LITERAL]:
  receipt=read(folder/'result.json')
  with connect()as c:
   c.execute('SET TRANSACTION READ ONLY');assert c.execute('SELECT status,result FROM astra_modelling.jobs WHERE id=%s',(receipt['jobId'],)).fetchone()==('complete',receipt)
  refs.extend(ref(folder/p)for p in ['result.json','diagnostic.json.gz']if(folder/p).exists())
 d=read(LOOPS/'diagnostic.json.gz');g=read(GRAPH/'diagnostic.json.gz')
 asset=next(ROOT/r['path']for r in d['evidenceRefs']if r['sha256']==SHA)
 assert digest(asset.read_bytes())==SHA
 world=decode_original_world_triangles(asset.read_bytes());assert world.shape==(18086,3,3)
 assert digest(world.tobytes())==d['completeOriginalWorldSHA256']
 refs.extend(ref(p)for p in [asset,VISUAL/'original-panel-host-loop-context-1800x1000.png',
  HERE/'original_triangular_opening_panel_source_role_v1_20261011.py',
  HERE/'test_original_triangular_opening_panel_source_role_v1_20261011.py',
  HERE/'exact_original_closed_boundary_loop_band_diagnostic_v1_20261011.py',
  HERE/'exact_original_shared_edge_component_census_v2_20261011.py',
  HERE/'exact_original_shell_intersections_20261009.py',HERE/'exact_packed_world_geometry_20261009.py',
  HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py'])
 panels=[r for r in d['allDisconnectedSinglePanels']if r['completeReciprocalBoundaryMatches']]
 assert len(panels)==76 and all(len(r['completeReciprocalBoundaryMatches'])==1 for r in panels)
 claim=reservations.claim('langham76-original-opening-proposal-'+str(uuid.uuid4()),['immutable-source-proof:'+BATCH],batch=BATCH,ttl=3600)
 assert claim['ok'];lease=claim['reservation'];last=time.monotonic();records=[]
 try:
  for r in panels:
   f=r['sourceFace'];assert g['components'][r['body']]['globalOriginalFaces']==[f]
   group=d['completeOriginalHostBoundaryGroups'][r['completeReciprocalBoundaryMatches'][0]]
   edges=[e['originalEdge']for e in group['allOriginalHostBoundaryEdges']]
   binding=dict(completeOriginalWorldSHA256=digest(world.tobytes()),completeOriginalFaces=18086,
    sourceFace=f,completeOriginalSourceFacetSHA256=digest(world[f].tobytes()),completeClaimedHostLoopSHA256=canonical(edges))
   proof=verify(world,source_face=f,host_loop_edges=edges,expected_source_binding=binding)
   assert proof['completeHostOriginalBodyFaces']==g['components'][proof['hostOriginalBody']]['globalOriginalFaces']
   records.append(dict(originalBody=r['body'],sourceFace=f,originalHostBoundaryGroup=r['completeReciprocalBoundaryMatches'][0],proof=proof))
   if time.monotonic()-last>=20:assert reservations.heartbeat(lease)['ok'];print(dict(panelsProcessed=len(records),total=76),flush=True);last=time.monotonic()
  assert reservations.heartbeat(lease)['ok'];assert all(ref(ROOT/r['path'])==r for r in refs)
  out=dict(uids=[UID],sourceSHA256=SHA,completeOriginalWorldSHA256=digest(world.tobytes()),
   completeOriginalFaces=18086,complete76ConditionalSourcePanelProposals=records,
   fourUnmatchedSingleFacesPreserved=[r for r in d['allDisconnectedSinglePanels']if not r['completeReciprocalBoundaryMatches']],
   allOtherOriginalSourcePartsAndRawInteriorNegativesRetained=True,
   actualLiteral565ContactNegativePreserved=ref(LITERAL/'diagnostic.json.gz'),
   independentlyGroundedActualHostProofStillRequired=True,allFourStreamSourceAndCurrentChecksStillRequired=True,
   allOriginalFacesRetained=True,sourceOnly=True,currentAcceptance=False,visualRoleAccepted=False,
   structuralRootCredit=False,structuralBridgeCredit=False,nativeReacceptance=False,newlyInstalled=0,evidenceRefs=refs)
  save(DOC/'diagnostic.json.gz',out)
  s=importlib.util.spec_from_file_location('freeze',HERE/'xl-popcorn-source-investigations-checkpoints-20261009.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
  m.freeze(BATCH,'conditional-langham76-authored-triangular-opening-panel-whole-original-loop-proposal-v1',
   [ROOT/r['path']for r in refs]+[DOC/'diagnostic.json.gz'],dict(uids=[UID],sourceOnly=True,
    proposedVisualPanels=76,unmatchedSingleFaces=4,actualHostProofStillRequired=True,currentAcceptance=False,newlyInstalled=0))
 finally:assert reservations.release(lease)['ok']
if __name__=='__main__':main()
