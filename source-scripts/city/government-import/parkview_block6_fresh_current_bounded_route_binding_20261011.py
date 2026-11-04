"""Reuse exact bounded route only after complete fresh current tuple equality."""
import numpy as np
from pathlib import Path
from run import ROOT,HERE,read,save,digest
from exact_packed_world_geometry_20261009 import decode_original_world_triangles
B=ROOT/'docs/astra-city/government-import';BATCH='government-xl-parkview-block6-fresh-current-bounded-route-binding-v1-20261011';DOC=B/BATCH
P=B/'government-xl-parkview-block6-fresh-current-physical-capture-v1-20261011';C=B/'government-xl-parkview-block6-fresh-current-carrier-capture-v1-20261011';R=B/'government-xl-parkview-block6-bounded-eligible-native-route-v2-20261011';CAP=B/'government-xl-parkview-block6-bounded-original-clear-cap-probe-v1-20261011'
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p.read_bytes()))
def streams(doc):
 r=read(doc/'selection.json.gz')['rows'][0];asset=ROOT/r['candidate']['path'];assert digest(asset.read_bytes())==r['sourceSHA256'];a=read(doc/'actual-render-geometry.json.gz')['row'];assert a['sourceSHA256']==r['sourceSHA256'];idx=np.asarray(a['completeOriginalIndex']).reshape(-1,3)
 return [decode_original_world_triangles(asset.read_bytes())]+[np.asarray(a[k]).reshape(-1,3)[idx]for k in ['completeLiteralWorldPosition','completeExplicitLeftAssociatedFloat32WorldPosition','completeExplicitBalancedFloat32WorldPosition']]
def main():
 assert not DOC.exists();r=read(R/'diagnostic.json.gz');cap=read(CAP/'diagnostic.json.gz');paired=read(CAP/'paired-cap-refinement.json.gz');rt=read(HERE/'local'/C.name/'runtime-geometry.json.gz')['rows'][0];ground=np.asarray(rt['drawnGroundGeometry'],float).reshape(-1,3,3);assert len(ground)==r['completePinnedGroundFaces']==cap['completeCurrentGroundFaces']==25167;assert digest(ground.tobytes())==r['completePinnedGroundSHA256']==cap['completeCurrentGroundSHA256'];assert r['boundedOriginalPathProved'];rows=[]
 for mode,owned,carrier in zip(['providerOriginal','actualLiteral','explicitLeftAssociatedF32ModelMatrix','explicitBalancedF32ModelMatrix'],streams(P),streams(C)):
  oh=digest(owned.tobytes());ch=digest(carrier.tobytes());assert oh==cap['completeOriginalOwnedWorldSHA256'];assert ch==r['completeOriginalNativeWorldSHA256']==cap['completeOriginalNativeWorldSHA256'];rows.append(dict(mode=mode,completeOwnedWorldSHA256=oh,completeCarrierWorldSHA256=ch,completeCurrentGroundSHA256=digest(ground.tobytes()),exactCompleteTupleEqualToFrozenRouteAndCap=True,allBoundedRouteProofsReusedWithoutRecomputation=True,allWholeCapPairedFiniteProofsReusedWithoutRecomputation=True,allCompleteOriginalOwnedToCapContactProofsReusedWithoutRecomputation=True))
 refs=[ref(p)for p in [Path(__file__),P/'source-preflight.json',P/'selection.json.gz',P/'actual-render-geometry.json.gz',C/'selection.json.gz',C/'actual-render-geometry.json.gz',C/'capture-scope.json',HERE/'local'/C.name/'runtime-geometry.json.gz',R/'result.json',R/'diagnostic.json.gz',CAP/'result.json',CAP/'diagnostic.json.gz',CAP/'paired-cap-refinement.json.gz']]
 save(DOC/'diagnostic.json.gz',dict(uids=['landsd/255438:0','landsd/254491:0'],currentManifest=read(P/'source-preflight.json')['currentManifest'],rows=rows,completeCurrentCarrierGroundFaces=len(ground),qualifiedGradeFace=r['qualifiedGenuineGradeFace'],qualifiedOriginalPath=r['qualifiedOriginalPathToStrictCap'],capFace=58400,exactTupleEqualityAllowsProofReuse=True,noWholeCarrierReacceptance=True,preservedExcludedCoverageGapFace=r['explicitExcludedCoverageGapFace'],preservedExcludedPartlyBuriedEdge=r['explicitExcludedPartlyBuriedEdge'],currentAcceptance=False,installationApproved=False,newlyInstalled=0,evidenceRefs=refs))
 print('Complete fresh current tuples equal all frozen exact route/cap inputs in four streams.')
if __name__=='__main__':main()
