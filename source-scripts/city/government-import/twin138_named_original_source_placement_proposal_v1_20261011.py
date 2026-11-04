"""Draft named original visual-placement layer; never mounting or support.

Complete original parts and exhaustive situated source context are bound to
specific review images. Failed .1m facet/mount/free-edge results remain raw
negatives. This layer cannot seed, bridge, or qualify a visual host. The file
adapter independently decodes both original assets and verifies every frozen
four-stream/actual-ground/context input. Root visual review is required before
executing its source-only proposal producer; current acceptance stays separate.
"""
from pathlib import Path
from fractions import Fraction as F
import json
import numpy as np
from twin155_named_complete_boundary_visual_assembly_proposal_v1_20261011 import MODES,SOURCE_SHA,canonical,world_sha
from exact_original_shared_edge_component_census_v2_20261011 import census

CONTEXT_BATCH='xl-terrain-recovery-20261011-twin138-whole-original-placement-context-v1'
PIN_FILE=Path(__file__).with_name('twin138_original_source_placement_pins_v1_20261011.json')
PIN_FILE_SHA256='95a0da2a0c5a3d367bb7a79295a865585e538c3cf204f9dea5a41e7a53eca793'
def pins():
 raw=PIN_FILE.read_bytes()
 import hashlib
 assert hashlib.sha256(raw).hexdigest()==PIN_FILE_SHA256,'Named source-placement pins changed'
 return json.loads(raw)

def verify(part,uid,source_sha,worlds,context,qualified_nonvisual_faces):
 p=pins();fixed=p['parts'].get(str(part));assert fixed is not None,'Not a named original source-placement candidate'
 assert canonical(context)==fixed['completeContextSHA256'],'Source context, finite proof or mounting negatives changed'
 ids=context['completeOriginalFaces'];assert ids==fixed['completeOriginalFaces']==sorted(set(ids))
 actor='landsd/222465:0'if max(ids)<13063 else'landsd/223206:0'
 assert uid==actor==context['actorUID'] and source_sha==SOURCE_SHA[actor]==context['sourceSHA256']
 assert context['originalBody']==part and context['visualRoleAccepted']is False and context['sourceFunctionInferred']is False and context['structuralRootOrBridgeCredit']is False
 assert context['greyContextDoesNotQualifyVisualHosts']is True
 assert set(worlds)==set(qualified_nonvisual_faces)==set(MODES)
 arrays={m:np.asarray(worlds[m],np.float64)for m in MODES}
 assert all(w.shape==(13519,3,3)and np.isfinite(w).all()and world_sha(w)==p['completeFourWorldSHA256'][m]for m,w in arrays.items()),'Original/literal/F32 source pose changed'
 original=arrays['providerOriginal'];assert world_sha(original[ids])==fixed['completeOriginalPartWorldSHA256']==context['completeOriginalPartWorldSHA256']
 offset,total=(0,13063)if actor=='landsd/222465:0'else(13063,456)
 assert context['completeActorContextOriginalFaces']==list(range(offset,offset+total))
 lo=original[ids].min((0,1));hi=original[ids].max((0,1));assert context['completeOriginalBounds']==dict(min=lo.tolist(),max=hi.tolist())
 margin=np.maximum((hi-lo)*.6,[8.,5.,8.]);own=original[offset:offset+total]
 surrounding=[offset+int(i)for i in np.flatnonzero(np.all(own.max(1)>=lo-margin,axis=1)&np.all(own.min(1)<=hi+margin,axis=1))]
 assert surrounding==context['completeWideContextOriginalFaces'] and context['wideContextBounds']==dict(min=(lo-margin).tolist(),max=(hi+margin).tolist())
 rows=context['allFourStreamCompleteFiniteFindings'];assert len(rows)==4 and {r['mode']for r in rows}==set(MODES)
 negatives=context['allPriorMountingAndFreeEdgeNegativesVerbatim'];assert len(negatives)==4 and {r['mode']for r in negatives}==set(MODES)
 proofs=[]
 for mode in MODES:
  w=arrays[mode];q=qualified_nonvisual_faces[mode]
  assert q==sorted(set(q))and canonical(q)==p['qualifiedNonvisualFaceSHA256'][actor][mode]
  assert q==context['completeQualifiedNonvisualFacesByMode'][mode] and not set(q)&set(ids)
  assert all(offset<=f<offset+total for f in q),'Foreign actor substituted as situated context'
  situated=sorted(set(surrounding)&set(q));assert situated,'No qualified same-actor source surroundings'
  r=next(r for r in rows if r['mode']==mode);assert r['completeActorWorldSHA256']==world_sha(w[offset:offset+total])
  findings=r['completePartFiniteFindings'];assert [x['globalOriginalFace']for x in findings]==ids
  for face,x in zip(ids,findings):
   f=x['completeFiniteProofVerbatim'];c=x['completeFacetContextVerbatim']
   assert f['sourceFace']==c['sourceFace']==face-offset and c['sourceFaceSHA256']==world_sha(w[face])
   assert f['completeOriginalBoundProved']is True and c['groundProjectionCovered']is True and F(c['exactCertifiedLowerClearanceM'])>0,'Visual placement is not a ground/clearance exemption'
  topology=census(w,ids)
  assert topology==r['completePartActualEdgeCensus'] and topology['sharedEdgeConnectedComponents']==[ids]and not topology['exactNonrenderingOriginalFaces']
  raw=next(r for r in negatives if r['mode']==mode)['allAssociationAndMountingFindingsVerbatim']
  assert raw['originalBody']==part and raw['actorUID']==actor and raw['completeOriginalFaceIds']==ids
  assert raw['allFacetsWithinFixedBand']is False,'Raw failed mounting result relabelled'
  proofs.append(dict(mode=mode,completeWorldSHA256=p['completeFourWorldSHA256'][mode],completeCapturedGroundSHA256=r['completeActualDrawnGroundSHA256'],completeSourceTopologyVerbatim=topology,allCompletePartFiniteFindingsVerbatim=findings,independentlyQualifiedSameActorSurroundingFaces=situated))
 return dict(contract='twin138-named-original-source-placement-visual-proposal-v1',originalBody=part,uid=uid,sourceSHA256=source_sha,completeOriginalFaces=ids,namedOriginalVisualInterpretation=fixed['proposedOriginalVisualInterpretation'],completeReviewedSourceContextCanonicalSHA256=fixed['completeContextSHA256'],contextImages=context['contextImages'],allFourStreamCompleteProofs=proofs,allPriorMountingAndFreeEdgeNegativesVerbatim=negatives,conditionalSourceVisualRoleProposal=True,sourceContextIsPlacementEvidenceNotMount=True,finiteMountingCertified=False,wholeInteriorProximityCertified=False,originalOpeningOrFunctionCertified=False,structuralRootCredit=False,structuralBridgeCredit=False,visualPartsNeverQualifyHosts=True,nativeReacceptance=False,currentAcceptance=False,sourceGeometryChanges=0,newlyInstalled=0)
