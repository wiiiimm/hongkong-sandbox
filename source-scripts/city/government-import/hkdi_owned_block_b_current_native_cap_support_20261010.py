"""Narrow owned-B support accounting; never reaccept the retained native actor.

The source adapter independently reconstructs worlds, roots, contact intersections,
component partition and all current physical gates. This final accounting contract
requires the full source/literal proof and keeps every legacy native negative.
"""
from fractions import Fraction as F
import hashlib,json
OWNED='landsd/89613:0';NATIVE='landsd/22089:0'
CAPS={2563,3869,3884,3885,3886,3887,3890,3892,3893}
def canonical(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def verify(proof,components,roots,*,expected_binding,current_binding):
 assert expected_binding==current_binding
 for k,v in [('qualifiedCapProofSHA256',proof),('completeOriginalComponentsSHA256',components),('actualFourRootProofSHA256',roots)]:assert current_binding[k]==canonical(v)
 assert len(components)==502 and proof['completeOriginalParts']==502
 owned={i for i,c in enumerate(components)if c['actorUID']==OWNED};assert owned==set(range(157,502))
 assert components[131]['actorUID']==components[144]['actorUID']==NATIVE
 allnative={f for c in components[:157]for f in c['globalOriginalFaces']};assert allnative==set(range(3965))
 allowned=[f for c in components[157:]for f in c['globalOriginalFaces']];assert len(allowned)==11593 and set(allowned)==set(range(3965,15558))
 assert roots['rootComponents']==[134,135,144,156] and roots['strictLiteralRenderedRoots']is True and roots['existingNativeReacceptance']is False
 assert proof['allOwnedBPartsQualified']is True and proof['uninstalledOriginalAExcluded']is True and proof['native128NoBridgeCredit']is True and proof['failedFootings147155NoRootOrBridgeCredit']is True
 assert proof['nativeReacceptance']is False and proof['all3965RetainedNativeFacesAccounted']is True
 assert proof['completeQualifiedCarrierCapFaces']==sorted(CAPS) and proof['creditedCapsStrictlyAboveCompleteCurrentGround']is True
 assert len(proof['completeRaw61AffectedNativeFaceInventory'])==61
 bad=proof['retainedNativeUnprovedOriginalFacesPreserved'];assert len(bad)==len(set(bad))==61 and not CAPS&set(bad)
 assert [r['sourceFace']for r in proof['completeRaw61AffectedNativeFaceInventory']]==bad
 for mode in ['completeCarrierCapsSourceContexts','completeCarrierCapsActualContexts']:
  contexts=proof[mode];assert [c['sourceFace']for c in contexts]==sorted(CAPS)
  for c in contexts:assert c['groundProjectionCovered']is True and F(c['exactCertifiedLowerClearanceM'])>0
 parents={144:None};paths=proof['completeQualifiedOwnedBPaths'];assert len(paths)==346
 for c in paths:
  parent,child=c['parent'],c['child'];assert child not in parents and parent!=child and parent in owned|{131,144} and child in owned|{131}
  assert set(c['components'])=={parent,child}
  for k in ['sourceIntersectionVertices','literalIntersectionVertices']:
   points={tuple(F(v)for v in p)for p in c[k]};assert len(points)>=2
  for part,face in zip(c['components'],c['globalOriginalFaces']):assert face in components[part]['globalOriginalFaces']
  if 131 in c['components']:assert c['completeStrictCarrierCap']['sourceFace'] in CAPS
  else:assert c['completeStrictCarrierCap']is None
  parents[child]=parent
 assert set(parents)==owned|{131,144}
 for i in owned|{131}:
  reached=set()
  while i!=144:assert i not in reached;reached.add(i);i=parents[i]
 assert proof['rawWholeCollectionSupportAccepted']is False and proof['rawWholeCollectionReasonsPreserved']
 return dict(contract='hkdi-owned-block-b-qualified-installed-native-exposed-cap-accounting-v1',ownedUID=OWNED,completeOwnedFaces=11593,completeOwnedComponents=345,qualifiedNativeCarrier=131,independentSourceAndLiteralRoot=144,allOwnedComponentsSupported=True,nativeReacceptance=False,nativeLegacyNegativesPreserved=True,uninstalledOriginalAExcluded=True,native128NoBridgeCredit=True,failedFootings147155NoRootOrBridgeCredit=True,sourceGeometryChanges=0,groundOrStructuralCreditFromVisualRoles=False,fullAcceptance=False,binding=current_binding)
