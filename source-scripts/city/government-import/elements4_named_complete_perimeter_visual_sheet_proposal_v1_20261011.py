"""Four complete source-defined visual sheets, no opening or structural claim.

The complete original perimeter is associated with independently qualified
same-actor hosts in the unchanged finite .1m band. Interiors may be free and
their old negatives stay explicit. The caller must independently pin actual
source assets, completed current-ground jobs and their expected bindings.
"""
import numpy as np
from elements24_named_original_mounted_visual_surface_proposal_v1_20261011 import (
 MODES,SOURCE_SHA,canonical,world_sha,edges,key)
from exact_original_shared_edge_component_census_v2_20261011 import census
from exact_original_body_boundary_group_census_v1_20261011 import census as boundary_census
from exact_original_edge_any_finite_distance_band_v2_20261010 import verify as finite_edge

NAMED_SOURCE_PART_FACES={
 70:[2336,2337,2338],890:[16019],
 904:[20259,20260,20261,20922,20923,20924],
 918:[21349,21350,21351,21352,21353,21354,21355,21356,21357]}

def binding(part,uid,source_sha,worlds,contexts,qualified_hosts):
 return dict(part=part,uid=uid,sourceSHA256=source_sha,
  originalFaceIds=NAMED_SOURCE_PART_FACES.get(part),
  completeOwnedWorldSHA256={m:world_sha(worlds[m])for m in MODES},
  completedPartContextSHA256={m:canonical(contexts[m])for m in MODES},
  qualifiedNonvisualHostFacesSHA256={m:canonical(sorted(qualified_hosts[m]))for m in MODES})

def verify(part,uid,source_sha,worlds,contexts,qualified_hosts,*,expected_binding):
 assert part in NAMED_SOURCE_PART_FACES,'Not a named original visual sheet'
 faces=NAMED_SOURCE_PART_FACES[part]
 actor='landsd/204145:0'if max(faces)<12129 else'landsd/204143:0'
 assert uid==actor and source_sha==SOURCE_SHA[actor]
 assert set(worlds)==set(contexts)==set(qualified_hosts)==set(MODES)
 arrays={m:np.asarray(worlds[m],np.float64)for m in MODES}
 assert all(w.shape==(23809,3,3)and np.isfinite(w).all()for w in arrays.values())
 bound=binding(part,uid,source_sha,arrays,contexts,qualified_hosts)
 assert bound==expected_binding,'Frozen source/current/host binding changed'
 original=arrays['providerOriginal'];_,source_boundary=edges(original,faces)
 assert source_boundary,'Original visual sheet has no complete boundary'
 results=[]
 for mode in MODES:
  w=arrays[mode];ctx=contexts[mode];a=ctx['association'];f=ctx['allCompletePartFiniteFaces']
  assert ctx['completeOwnedWorldSHA256']==world_sha(w)
  assert a['originalBody']==part and a['actorUID']==actor and a['completeOriginalFaceIds']==faces
  c=census(w,faces)
  assert c['sharedEdgeConnectedComponents']==[faces]and not c['exactNonrenderingOriginalFaces']
  b=boundary_census(w,faces);groups=b['completeIncidenceOneBoundaryGroups']
  assert len(groups)==1 and groups[0]['closedConnectedDegreeTwoLoop']is True,'Incomplete original perimeter'
  _,boundary=edges(w,faces);correspondence={}
  for orig,actual in zip(original[faces].reshape(-1,3),w[faces].reshape(-1,3)):
   o=tuple(orig);v=tuple(actual)
   if o in correspondence:assert correspondence[o]==v,'Original shared vertex split'
   correspondence[o]=v
  assert len(set(correspondence.values()))==len(correspondence),'Original nonzero vertices collapsed'
  assert {key([correspondence[x]for x in e])for e in source_boundary}==boundary
  hs=a['completeHostSelection'];selected=set(hs['selectedGlobalHostFaces']);qualified=set(qualified_hosts[mode])
  assert selected and selected<=qualified and not selected&set(faces)
  assert all((h<12129)==(actor=='landsd/204145:0')for h in selected)
  assert hs['exactFixedBandM']==.1 and hs['allSelectedHostsBelongToNonvisualQualifiedPaths']is True
  assert hs['actualSelectedHostWorldSHA256']==world_sha(w[sorted(selected)])
  assert hs['completeQualifiedSameActorHostFaces']==sorted(qualified)
  assert not census(w,sorted(selected))['exactNonrenderingOriginalFaces'],'Degenerate host credit'
  offset=0 if actor=='landsd/204145:0'else 12129
  assert [z['sourceFace']+offset for z in f]==faces
  assert all(z['closedProjectionCovered']is True and z['existingOrdinaryClearanceBoundProved']is True
   and z['strictlyExposedWholeFacet']is True for z in f)
  raw=a['allActualIncidenceOneBoundaryEdgeProofs']
  ep={key(e['completeActualBoundaryEdge']):e for e in raw}
  assert len(ep)==len(raw)and set(ep)==boundary,'Partial or duplicate perimeter proof'
  checked=[]
  for edge in sorted(boundary):
   prior=ep[edge]
   assert prior['wholeEdgeWithinExistingFiniteHostBand']is True
   assert prior['actualSubsetWholeEdgeHostProofVerbatim']['verifiedCompleteOriginalEdgeFiniteFacadeBand']is True
   proof=finite_edge(np.asarray(edge,float),w[sorted(selected)])
   assert proof['strictBandM']==.1 and proof['verifiedCompleteOriginalEdgeFiniteFacadeBand']is True,'Actual complete edge detached'
   checked.append(dict(completeActualEdge=edge,independentWholeFiniteEdgeProof=proof))
  results.append(dict(mode=mode,completeSourcePerimeterEdgeCount=len(boundary),
   independentCompletePerimeterProofs=checked,completePartFiniteClearance=True,
   originalInteriorFindingsVerbatim=a['allActualFacetProofs'],
   wholeInteriorBandPositive=a['allFacetsWithinFixedBand'],
   completeOriginalTopologyVerbatim=c,completeOriginalBoundaryInventory=b))
 return dict(contract='elements4-named-complete-perimeter-associated-original-visual-sheet-proposal-v1',
  binding=bound,originalBody=part,uid=uid,completeOriginalFaces=faces,
  namedSourceVisualInterpretation='original-whole-perimeter-associated-architectural-visual-sheet',
  allFourStreamProofs=results,conditionalSourceVisualRoleProposal=True,
  originalInteriorNegativesPreserved=True,wholeInteriorProximityNotCertified=True,
  originalOpeningOrHoleCertified=False,sourceFunctionInferred=False,
  structuralRootCredit=False,structuralBridgeCredit=False,visualPartsNeverQualifyHosts=True,
  nativeReacceptance=False,currentAcceptance=False,sourceGeometryChanges=0,newlyInstalled=0)
