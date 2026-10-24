"""Named unchanged original roof/facade placement; no mount or structural credit.

Root reviewed complete source images. This is a bounded architectural visual
interpretation, preserving every prior .1m perimeter failure unchanged.
"""
import hashlib,json
import numpy as np
from king_cheung_named_embedded_foundation_skin_v2_20261011 import UID,SOURCE
NAMED=[35,36,37,38,849,856,858,859,860,861,862,863,866,867]
BINDINGS={'actualLiteral': {'world': 'c2ce44c1121a357256bfca027cf262b5d89a494ae3d67f6e50ba8bc9fc43fd12', 'records': '32dac994f30007a8ffafa3ce4a28bf4e2389ed8c71d11c80e7677db054dbbf61'}, 'explicitBalancedF32ModelMatrix': {'world': '534046e403d3eb70a384e56be5294b294e5469e48aea57b9e3edd8e5d4028a78', 'records': '21a735857f10c8af39e0201d115d7258580935b9f246c958be0e639aa43123b6'}, 'explicitLeftAssociatedF32ModelMatrix': {'world': '534046e403d3eb70a384e56be5294b294e5469e48aea57b9e3edd8e5d4028a78', 'records': '21a735857f10c8af39e0201d115d7258580935b9f246c958be0e639aa43123b6'}, 'providerOriginal': {'world': '534046e403d3eb70a384e56be5294b294e5469e48aea57b9e3edd8e5d4028a78', 'records': '21a735857f10c8af39e0201d115d7258580935b9f246c958be0e639aa43123b6'}}
IMAGES=[{'path': 'docs/astra-city/government-import/government-xl-king-cheung-95691-fourteen-source-visual-context-v2-20261011/lower-ten-source-context-2400x1800.png', 'sha256': '504a8e96e21e77b21122745b9aeb9de766a311380f6ce6b570600b1b41ba0a73'}, {'path': 'docs/astra-city/government-import/government-xl-king-cheung-95691-fourteen-source-visual-context-v2-20261011/roof-four-source-context-2400x1800.png', 'sha256': '00bbfa5b27299dd633c9a143b6896500ea22919e7c306d0c957a1e4b3683fb3e'}, {'path': 'docs/astra-city/government-import/government-xl-king-cheung-95691-fourteen-source-visual-context-v2-20261011/whole-building-all-fourteen-source-context-2400x1800.png', 'sha256': 'a9d3fe90e03e269d3152ae9565d53595773f834ac74f6ee79fc481e8ed01b35f'}]
def canonical(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def verify(*,context,mode,world,mounts,image_refs):
 assert context['uids']==[UID] and context['sourceSHA256']==SOURCE
 assert context['raw191MountFailurePreserved'] is True and context['sourceGeometryChanges']==context['terrainGeometryChanges']==0
 assert context['currentAcceptance'] is context['physicalAccepted'] is context['installationApproved'] is False
 assert image_refs==IMAGES
 rows=[r for r in context['rows']if r['arithmetic']==mode];assert len(rows)==1
 r=rows[0];binding=BINDINGS[mode];assert r['completeWorldSHA256']==binding['world']
 w=np.asarray(world,dtype='<f8');assert w.shape==(18742,3,3) and hashlib.sha256(w.tobytes()).hexdigest()==binding['world']
 records=r['complete14UnresolvedOriginalParts'];assert canonical(records)==binding['records'] and [x['originalComponent']for x in records]==NAMED
 assert mounts['unresolvedCompleteBoundaryComponents']==NAMED and mounts['all191CompleteBoundariesAssociated'] is False
 proofs=[]
 for record in records:
  component=record['originalComponent'];ids=record['completeOriginalFaces'];m=next(x for x in mounts['completeDetachedComponentDispositions']if x['originalComponent']==component)
  assert ids==m['completeOriginalFaces'] and np.array_equal(w[ids],np.asarray(record['completeOriginalGeometry']))
  assert record['completeOriginalClosedBoundaryLoops']==m['completeEveryOriginalClosedBoundaryLoop']
  assert record['complete177OtherVisualDetailsRemainSeparatelyQualified'] is True and record['structuralRootCredit'] is False
  assert m['completeBoundaryAssociated'] is False and m['structuralRootCredit'] is m['structuralBridgeCredit'] is False
  failed=[e for e in m['completeBoundaryEdgeFiniteHostBandProofs']if not e['fullEdgeAssociated']]
  assert failed and [e['originalBoundaryEdgeIndex']for e in failed]==[e['originalBoundaryEdgeIndex']for e in record['completeUnqualifiedBoundaryEdges']]
  for e,saved in zip(failed,record['completeUnqualifiedBoundaryEdges']):
   assert e['completeOriginalEdge']==saved['completeOriginalEdge']
   assert saved['unchangedFiniteBandTrials']==[dict(coordinatePermutation=x['coordinatePermutation'],verifiedCompleteOriginalEdgeFiniteFacadeBand=x['completeFiniteHostBandProof']['verifiedCompleteOriginalEdgeFiniteFacadeBand'],exactCertifiedMergedIntervals=x['completeFiniteHostBandProof']['exactFacetAndEdgeCertifiedMergedIntervals'],strictBandM=x['completeFiniteHostBandProof']['strictBandM'])for x in e['completeCoordinatePermutationTrials']]
  proofs.append(dict(originalComponent=component,completeOriginalFaces=ids,namedVisualPlacement='original-open-bottom-roof-box'if component<39 else'original-repeated-lower-facade-ledge-or-trim',rawUnqualifiedPerimeterRecordSHA256=canonical(m),completeSourceContextSHA256=binding['records'],nonstructuralVisualInterpretation=True,mountCertified=False,functionCertified=False,structuralRootCredit=False,structuralBridgeCredit=False))
 return dict(completeNamedOriginalVisualComponents=NAMED,complete14PlacementProofs=proofs,completeActualWorldSHA256=binding['world'],sourceImages=image_refs,priorFiniteBandNegativesPreserved=True,structuralRootCredit=False,structuralBridgeCredit=False)
